import re
import io
import pandas as pd
from rapidfuzz import fuzz
import streamlit as st

# ---------------- PAGE SETUP ----------------
st.set_page_config(
    page_title="🔍 Company ↔ Domain Matching (Standalone)",
    layout="wide",
    page_icon="🔍"
)

# ---------------- STYLING ----------------
st.markdown("""
<style>
  .stApp {background: #0b1220;}
  .block-container {max-width: 1200px;}
  h1, h2, h3, h4, h5, p, label, span, div {color: #e9eef7 !important;}

  /* Dropdowns */
  div[data-baseweb="select"] > div {
    background-color: #1a2235 !important;
    color: #e9eef7 !important;
    border: 1px solid #2f3a56 !important;
  }
  div[data-baseweb="popover"],
  ul[role="listbox"], div[role="listbox"] {
    background-color: #1a2235 !important;
    color: #e9eef7 !important;
    border: 1px solid #2f3a56 !important;
  }
  li[role="option"], div[role="option"] {
    background-color: #1a2235 !important;
    color: #e9eef7 !important;
  }
  li[role="option"]:hover, div[role="option"]:hover {
    background-color: #314d8b !important;
    color: white !important;
  }
  div[aria-selected="true"], li[aria-selected="true"] {
    background-color: #2a3b5f !important;
    color: white !important;
  }

  /* File uploader */
  section[data-testid="stFileUploader"] {
    background-color: #1a2235;
    padding: 15px;
    border-radius: 10px;
    border: 1px dashed #3b4a6b;
  }

  /* Buttons */
  button[kind="primary"], div[data-testid="stButton"] > button {
    background: linear-gradient(90deg, #3557ff, #2cc9ff) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.6em 1.2em !important;
  }

  .stDataFrame, .stDataFrame div { color: #d9e2f2 !important; }
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("## 🔍 Company ↔ Domain Matching (Standalone)")
st.write("Upload a dataset, select your company and domain columns, and this tool will classify whether the domain is a match, partial, or not related — using the same logic as your master matching tool.")

# ---------------- FILE UPLOAD ----------------
uploaded = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])
if not uploaded:
    st.info("⬆️ Upload a file to begin.")
    st.stop()

# ---------------- LOAD FILE ----------------
try:
    if uploaded.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)
except Exception as e:
    st.error(f"❌ Could not read file: {e}")
    st.stop()

if df.empty:
    st.warning("⚠️ The uploaded file appears empty.")
    st.stop()

# ---------------- COLUMN SELECTION ----------------
st.subheader("Select Columns")
col1, col2 = st.columns(2)
with col1:
    company_col = st.selectbox("Company column", options=list(df.columns))
with col2:
    domain_col = st.selectbox("Domain column (can be domain or email)", options=list(df.columns))

# ---------------- MATCHING LOGIC ----------------
SUFFIXES = {
    "ltd","limited","co","company","corp","corporation","inc","incorporated",
    "plc","public","llc","lp","llp","ulc","pc","pllc","sa","ag","nv","se","bv",
    "oy","ab","aps","as","kft","zrt","rt","sarl","sas","spa","gmbh","ug","bvba",
    "cvba","nvsa","pte","pty","bhd","sdn","kabushiki","kaisha","kk","godo","dk",
    "dmcc","pjsc","psc","jsc","ltda","srl","s.r.l","group","holdings","limitedpartnership"
}

def normalize(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r"[^a-zA-Z0-9\\s]", " ", text.lower())
    return " ".join([w for w in text.split() if w not in SUFFIXES])

def clean_domain(domain):
    if not isinstance(domain, str):
        return ""
    domain = domain.lower().strip()
    domain = re.sub(r"^https?://", "", domain)
    domain = re.sub(r"^www\\.", "", domain)
    domain = domain.split("/")[0]
    if "@" in domain:
        domain = domain.split("@")[-1]
    parts = domain.split(".")
    return parts[-2] if len(parts) >= 2 else domain

def compare(company, domain):
    if not isinstance(company, str) or not isinstance(domain, str) or not company or not domain:
        return "Unsure – Please Check", 0, "missing input"

    c = normalize(company)
    d = clean_domain(domain)

    # direct containment
    if d and (d in c.replace(" ", "") or c.replace(" ", "") in d):
        return "Likely Match", 100, "direct containment"

    # token overlap
    if any(t in c for t in d.split()) or any(t in d for t in c.split()):
        score = fuzz.partial_ratio(c, d)
        if score >= 75:
            return "Likely Match", score, "token containment"

    # fuzzy
    full = fuzz.token_sort_ratio(c, d)
    partial = fuzz.partial_ratio(c, d)
    score = max(full, partial)

    if score >= 85:
        return "Likely Match", score, "strong fuzzy"
    elif score >= 70:
        return "Unsure – Please Check", score, "weak fuzzy"
    else:
        return "Likely NOT Match", score, "low similarity"

# ---------------- RUN BUTTON ----------------
if st.button("🚀 Run Domain Match Check"):
    results = df.copy()
    statuses, scores, reasons = [], [], []

    with st.spinner("Running matching analysis..."):
        for _, row in results.iterrows():
            status, score, reason = compare(row[company_col], row[domain_col])
            statuses.append(status)
            scores.append(score)
            reasons.append(reason)

    results["Domain_Check_Status"] = statuses
    results["Domain_Check_Score"] = scores
    results["Domain_Check_Reason"] = reasons

    st.success("✅ Matching complete! Preview below.")
    st.dataframe(results[[company_col, domain_col, "Domain_Check_Status", "Domain_Check_Score", "Domain_Check_Reason"]].head(50))

    # download
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        results.to_excel(writer, index=False, sheet_name="Results")

    st.download_button(
        "⬇️ Download Results (Excel)",
        data=buffer.getvalue(),
        file_name="domain_check_results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.caption(
        "<span style='color:#66ff99'>Likely Match</span> · "
        "<span style='color:#ffcc66'>Unsure – Please Check</span> · "
        "<span style='color:#ff6666'>Likely NOT Match</span>",
        unsafe_allow_html=True
    )
