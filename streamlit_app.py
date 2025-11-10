import streamlit as st
import pandas as pd
from rapidfuzz import fuzz

# ---------------- PAGE SETUP ----------------
st.set_page_config(
    page_title="🔍 Company ↔ Domain Matching (Standalone)",
    layout="wide",
    page_icon="🔍"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
  .stApp {background: #0b1220;}
  .block-container {max-width: 1200px;}
  h1, h2, h3, h4, h5, p, label, span, div {color: #e9eef7 !important;}

  /* Fix selectbox dropdown visibility */
  div[data-baseweb="select"] > div {
    background-color: #1a2235 !important;
    color: #e9eef7 !important;
    border: 1px solid #2f3a56 !important;
  }

  /* Popover container (the actual dropdown list) */
  div[data-baseweb="popover"] {
    background-color: #1a2235 !important;
    border: 1px solid #2f3a56 !important;
    color: #e9eef7 !important;
  }

  /* Listbox background and text */
  ul[role="listbox"], div[role="listbox"] {
    background-color: #1a2235 !important;
    color: #e9eef7 !important;
    border: 1px solid #2f3a56 !important;
  }

  /* Dropdown option items */
  li[role="option"], div[role="option"] {
    background-color: #1a2235 !important;
    color: #e9eef7 !important;
  }

  /* Hover effect for dropdown items */
  li[role="option"]:hover, div[role="option"]:hover {
    background-color: #314d8b !important;
    color: white !important;
  }

  /* Selected/focused item */
  div[aria-selected="true"], li[aria-selected="true"] {
    background-color: #2a3b5f !important;
    color: white !important;
  }

  /* File uploader box */
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

  /* Dataframe text */
  .stDataFrame, .stDataFrame div {
    color: #d9e2f2 !important;
  }

  /* Table scroll area */
  div[data-testid="stHorizontalBlock"] {
    overflow-x: auto !important;
  }
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("## 🔍 Company ↔ Domain Matching (Standalone)")
st.write("Upload a dataset, select your company and domain columns, and automatically classify the relationship between them.")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
        st.stop()

    st.write(f"✅ Loaded file: **{uploaded_file.name}** ({df.shape[0]} rows, {df.shape[1]} columns)")

    # ---------------- COLUMN SELECTION ----------------
    st.subheader("Select Columns")
    col1, col2 = st.columns(2)
    with col1:
        company_col = st.selectbox("Company column", options=df.columns)
    with col2:
        domain_col = st.selectbox("Domain column (can be domain or email)", options=df.columns)

    # ---------------- RUN CHECK ----------------
    if st.button("🚀 Run Check"):
        def domain_check_reason(company, domain):
            if pd.isna(company) or pd.isna(domain) or not str(domain).strip():
                return "missing input"

            company = str(company).lower().strip()
            domain = str(domain).lower().strip()

            # Extract domain part if it's an email
            if "@" in domain:
                domain = domain.split("@")[-1]

            # Rule 1: direct containment
            if company in domain or domain in company:
                return "direct containment"

            # Rule 2: fuzzy match
            ratio = fuzz.partial_ratio(company, domain)
            if ratio >= 80:
                return f"strong fuzzy ({ratio}%)"
            elif ratio >= 60:
                return f"weak fuzzy ({ratio}%)"

            # Rule 3: token containment
            company_tokens = set(company.replace(",", "").split())
            domain_tokens = set(domain.replace(".", "").split())
            if any(t in domain_tokens for t in company_tokens):
                return "token containment"

            return "no match"

        df["Domain_Check_Reason"] = df.apply(
            lambda x: domain_check_reason(x[company_col], x[domain_col]), axis=1
        )

        st.success("✅ Domain matching complete!")
        st.dataframe(df[["Domain_Check_Reason", company_col, domain_col]].head(50))

        # ---------------- DOWNLOAD RESULTS ----------------
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Results as CSV",
            data=csv,
            file_name="domain_check_results.csv",
            mime="text/csv",
        )
else:
    st.info("⬆️ Upload a CSV or Excel file to begin.")
