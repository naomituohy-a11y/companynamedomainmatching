import re
import io
import pandas as pd
from rapidfuzz import fuzz
import streamlit as st

# ------------------ constants ------------------
SUFFIXES = {
    "ltd","limited","co","company","corp","corporation","inc","incorporated",
    "plc","public","llc","lp","llp","ulc","pc","pllc","sa","ag","nv","se","bv",
    "oy","ab","aps","as","kft","zrt","rt","sarl","sas","spa","gmbh","ug","bvba",
    "cvba","nvsa","pte","pty","bhd","sdn","kabushiki","kaisha","kk","godo","dk",
    "dmcc","pjsc","psc","jsc","ltda","srl","s.r.l","group","holdings","limitedpartnership"
}

THRESHOLD = 70

# ------------------ helpers ------------------
def _normalize_tokens(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    parts = [w for w in text.split() if w not in SUFFIXES]
    return " ".join(parts).strip()

def _clean_domain(domain: str) -> str:
    if not isinstance(domain, str):
        return ""
    domain = domain.lower().strip()
    domain = re.sub(r"^https?://", "", domain)
    domain = re.sub(r"/.*$", "", domain)
    domain = re.sub(r"^www\.", "", domain)
    parts = domain.split(".")
    return parts[-2] if len(parts) >= 2 else domain

def _extract_domain_from_email(email: str) -> str:
    if not isinstance(email, str) or "@" not in email:
        return ""
    domain = email.split("@")[-1].lower().strip()
    domain = re.sub(r"^www\.", "", domain)
    domain = re.sub(r"/.*$", "", domain)
    return domain

def compare_company_domain(company: str, domain: str):
    """Return (status, score, reason)."""
    if not isinstance(company, str) or not isinstance(domain, str) or not company or not domain:
        return "Unsure – Please Check", 0, "missing input"

    c = _normalize_tokens(company)
    d_raw = domain.lower().strip()
    d_email = _extract_domain_from_email(d_raw)
    d_raw = d_email or d_raw
    d = _clean_domain(d_raw)

    # exact or direct containment
    if d and (d in c.replace(" ", "") or c.replace(" ", "") in d):
        return "Likely Match", 100, "direct containment"

    # token containment
    if any(word in c for word in d.split()) or any(word in d for word in c.split()):
        score = fuzz.partial_ratio(c, d)
        if score >= 70:
            return "Likely Match", score, "token containment"

    # brand suffix check
    BRAND_TERMS = {"tx","bio","pharma","therapeutics","labs","health","med","rx","group","holdings"}
    if any(t in c.split() for t in BRAND_TERMS) and any(t in d for t in BRAND_TERMS):
        if fuzz.partial_ratio(c, d) >= 70:
            return "Likely Match", 90, "brand suffix match"

    # fuzzy
    score_full = fuzz.token_sort_ratio(c, d)
    score_partial = fuzz.partial_ratio(c, d)
    score = max(score_full, score_partial)

    if score >= 85:
        return "Likely Match", score, "strong fuzzy"
    elif score >= THRESHOLD:
        return "Unsure – Please Check", score, "weak fuzzy"
    else:
        return "Likely NOT Match", score, "low similarity"


# ------------------ UI ------------------
st.set_page_config(page_title="Company ↔ Domain Matching", page_icon="🔎", layout="wide")

st.markdown(
    """
    <style>
      /* Overall dark theme */
      .stApp {background: #0b1220;}
      .block-container {max-width: 1200px;}
      h1, h2, h3, h4, h5, p, label, span, div {color: #e9eef7 !important;}
      .note {font-size: 0.92rem; color: #b9c3d6;}
      .good {background:#163d2a; padding:2px 6px; border-radius:6px}
      .bad {background:#44212a; padding:2px 6px; border-radius:6px}
      .maybe {background:#403514; padding:2px 6px; border-radius:6px}

      /* Dropdowns */
      div[data-baseweb="select"] > div {
        background-color: #1a2235 !important;
        color: #e9eef7 !important;
        border: 1px solid #2f3a56 !important;
      }
      div[role="listbox"] {
        background-color: #1a2235 !important;
        color: #e9eef7 !important;
        border: 1px solid #2f3a56 !important;
      }
      div[role="option"] {
        color: #e9eef7 !important;
      }
      div[role="option"]:hover {
        background-color: #2a3b5f !important;
      }

      /* Buttons */
      button[kind="primary"] {
        background: linear-gradient(90deg, #3557ff, #2cc9ff) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
      }

      /* File uploader */
      section[data-testid="stFileUploader"] {
        background-color: #1a2235;
        padding: 15px;
        border-radius: 10px;
        border: 1px dashed #3b4a6b;
      }

      /* Dataframe styling */
      .stDataFrame, .stDataFrame div {
        color: #d9e2f2 !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title
st.title("🔍 Company ↔ Domain Matching (Standalone)")

# File upload
uploaded = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])
if not uploaded:
    st.info("Upload a file to begin.")
    st.stop()

# Read file
try:
    if uploaded.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)
except Exception as e:
    st.error(f"Could not read file: {e}")
    st.stop()

if df.empty:
    st.warning("The file appears to be empty.")
    st.stop()

# Column selectors
st.subheader("Select Columns")
col1, col2 = st.columns(2)
with col1:
    company_col = st.selectbox("Company column", options=list(df.columns))
with col2:
    domain_col = st.selectbox("Domain column (can be domain or email)", options=list(df.columns))

run = st.button("🚀 Run Check")

if run:
    out = df.copy()
    statuses, scores, reasons = [], [], []

    for i in range(len(out)):
        comp = out.at[i, company_col]
        dom = out.at[i, domain_col]
        status, score, reason = compare_company_domain(comp, dom)
        statuses.append(status)
        scores.append(score)
        reasons.append(reason)

    out["Domain_Check_Status"] = statuses
    out["Domain_Check_Score"] = scores
    out["Domain_Check_Reason"] = reasons

    st.success("✅ Matching complete! Preview below.")
    styled = out.style.apply(
        lambda s: [
            "background-color:#163d2a" if (c and "likely" in str(c).lower() and "not" not in str(c).lower())
            else ("background-color:#44212a" if ("not" in str(c).lower()) else ("background-color:#403514" if ("unsure" in str(c).lower()) else ""))
            for c in s
        ],
        subset=["Domain_Check_Status"],
    )

    st.dataframe(styled, use_container_width=True, height=420)

    # Download
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        out.to_excel(writer, index=False, sheet_name="Results")
    st.download_button(
        "⬇️ Download results (Excel)",
        data=buffer.getvalue(),
        file_name="company_domain_check.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.caption(
        "Legend: "
        "<span class='good'>Likely Match</span> · "
        "<span class='maybe'>Unsure – Please Check</span> · "
        "<span class='bad'>Likely NOT Match</span>",
        unsafe_allow_html=True,
    )
