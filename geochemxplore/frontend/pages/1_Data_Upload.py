import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import pandas as pd
import requests
import json
from config import settings
from core.utils import detect_coordinate_columns, detect_element_columns

st.set_page_config(page_title="Data Upload", layout="wide")
st.title("📁 Data Upload")

# Initialize session state
if 'analyzer_data' not in st.session_state:
    st.session_state.analyzer_data = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'coord_cols' not in st.session_state:
    st.session_state.coord_cols = None
if 'elem_cols' not in st.session_state:
    st.session_state.elem_cols = None

# File upload
uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx', 'xls'])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        st.session_state.analyzer_data = df
        st.success(f"✅ Loaded {len(df)} samples with {len(df.columns)} columns.")

        st.subheader("🔍 Data Preview")
        st.dataframe(df.head())

        # Auto‑detection
        x, y = detect_coordinate_columns(df)
        if x and y:
            st.info(f"📍 Detected coordinates: X = **{x}**, Y = **{y}**")
            st.session_state.coord_cols = [x, y]
        else:
            st.warning("No coordinate columns detected. Spatial visualisations will be disabled.")
            st.session_state.coord_cols = None

        elements = detect_element_columns(df, [x, y] if x else [])
        if elements:
            st.info(f"🧪 Detected {len(elements)} element columns: {', '.join(elements[:10])}{'...' if len(elements)>10 else ''}")
            st.session_state.elem_cols = elements
        else:
            st.warning("No element columns detected. Please ensure your columns contain concentration data.")
            st.session_state.elem_cols = []

        # Manual override
        with st.expander("⚙️ Manual Column Selection"):
            all_cols = df.columns.tolist()
            coord_x = st.selectbox("X coordinate (Easting)", [''] + all_cols, index=0)
            coord_y = st.selectbox("Y coordinate (Northing)", [''] + all_cols, index=0)
            elem_manual = st.multiselect("Element columns", all_cols, default=elements)
            if st.button("Apply manual selection"):
                if coord_x and coord_y:
                    st.session_state.coord_cols = [coord_x, coord_y]
                else:
                    st.session_state.coord_cols = None
                st.session_state.elem_cols = elem_manual
                st.rerun()

        # Run analysis button
        if st.button("🚀 Run Full Analysis (via API)", type="primary"):
            if uploaded_file is None:
                st.error("Please upload a file first.")
            else:
                with st.spinner("Sending data to backend and processing..."):
                    files = {'file': uploaded_file.getvalue()}
                    methods = "pca,clustering,outliers,factor,prospectivity"
                    params = {'methods': methods}
                    try:
                        response = requests.post(
                            f"{settings.API_URL}/api/v1/analyze",
                            files=files,
                            data=params,
                            timeout=300
                        )
                        if response.status_code == 200:
                            st.session_state.analysis_results = response.json()
                            st.success("✅ Analysis complete! Results are now available in the other pages.")
                            # Display a quick summary
                            res = response.json()
                            st.json(res)
                        else:
                            st.error(f"❌ API error: {response.status_code} – {response.text}")
                    except Exception as e:
                        st.error(f"Could not reach API. Is the backend running? Error: {e}")
                        st.info("Start the backend with: `uvicorn backend.main:app --reload --port 8000`")

    except Exception as e:
        st.error(f"Error reading file: {e}")

else:
    st.info("👈 Please upload a CSV or Excel file to begin.")