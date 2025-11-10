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

      /* --- DROPDOWN FIXES --- */
      /* Input box */
      div[data-baseweb="select"] > div {
        background-color: #1a2235 !important;
        color: #e9eef7 !important;
        border: 1px solid #2f3a56 !important;
      }

      /* Dropdown popover container */
      div[data-baseweb="popover"] {
        background-color: #1a2235 !important;
        border: 1px solid #2f3a56 !important;
      }

      /* Dropdown list background */
      div[role="listbox"] {
        background-color: #1a2235 !important;
        color: #e9eef7 !important;
        border: 1px solid #2f3a56 !important;
      }

      /* Dropdown individual options */
      div[role="option"] {
        background-color: #1a2235 !important;
        color: #e9eef7 !important;
      }

      /* Hover highlight */
      div[role="option"]:hover {
        background-color: #2a3b5f !important;
        color: white !important;
      }

      /* Focused item */
      div[aria-selected="true"] {
        background-color: #314d8b !important;
        color: white !important;
      }

      /* --- BUTTONS --- */
      button[kind="primary"] {
        background: linear-gradient(90deg, #3557ff, #2cc9ff) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
      }

      /* --- FILE UPLOADER --- */
      section[data-testid="stFileUploader"] {
        background-color: #1a2235;
        padding: 15px;
        border-radius: 10px;
        border: 1px dashed #3b4a6b;
      }

      /* --- DATAFRAME --- */
      .stDataFrame, .stDataFrame div {
        color: #d9e2f2 !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)
