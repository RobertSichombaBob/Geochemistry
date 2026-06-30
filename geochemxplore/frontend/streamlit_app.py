import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import plotly.express as px
import matplotlib.pyplot as plt
from config import settings

st.set_page_config(page_title="Geochem Analytics", layout="wide", page_icon="🔬")

st.title("🔬 Geochemical Analysis Platform")
st.markdown("Upload your geochemical data (soil, rock, core) and run advanced multivariate analyses.")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "📁 Data Upload",
    "🎯 Outlier Detection",
    "📈 PCA Analysis",
    "🔍 Clustering",
    "⛏️ Prospectivity",
    "📋 Report"
])

# Initialize session state for data
if 'analyzer_data' not in st.session_state:
    st.session_state.analyzer_data = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# ---------- Data Upload ----------
if page == "📁 Data Upload":
    st.header("📁 Upload Your Data")
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx', 'xls'])

    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file, engine='openpyxl')
            st.session_state.analyzer_data = df
            st.success(f"Loaded {len(df)} samples with {len(df.columns)} columns.")

            st.subheader("Data Preview")
            st.dataframe(df.head())

            # Detect potential coordinate and element columns
            from core.utils import detect_coordinate_columns, detect_element_columns
            x, y = detect_coordinate_columns(df)
            if x and y:
                st.info(f"Detected coordinates: X = {x}, Y = {y}")
            else:
                st.warning("No coordinate columns detected. Spatial visualisations will be disabled.")

            elements = detect_element_columns(df, [x, y] if x else [])
            if elements:
                st.info(f"Detected {len(elements)} element columns: {', '.join(elements[:10])}{'...' if len(elements)>10 else ''}")
            else:
                st.warning("No element columns detected. Please ensure your columns contain concentration data.")

            # Option to manually select columns
            with st.expander("Advanced: Manual Column Selection"):
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

        except Exception as e:
            st.error(f"Error reading file: {e}")

    # Run analysis button
    if st.session_state.analyzer_data is not None:
        if st.button("🚀 Run Full Analysis (via API)"):
            with st.spinner("Sending data to backend..."):
                # Prepare file for upload
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
                        st.success("Analysis complete!")
                        st.json(st.session_state.analysis_results)
                    else:
                        st.error(f"API error: {response.text}")
                except Exception as e:
                    st.error(f"Could not reach API. Is the backend running? Error: {e}")
                    st.info("You can run the backend with: uvicorn backend.main:app --reload")

# ---------- Other Pages ----------
# For simplicity, we'll implement placeholders that read from session_state.

elif page == "🎯 Outlier Detection":
    st.header("🎯 Outlier Detection")
    if st.session_state.analysis_results:
        res = st.session_state.analysis_results
        if 'results' in res and 'outliers' in res['results']:
            outliers = res['results']['outliers']
            st.write(f"Number of outliers: {np.sum(outliers['outliers'])}")
            st.write(f"Threshold: {outliers['threshold']:.2f}")
            # Histogram
            fig, ax = plt.subplots()
            ax.hist(outliers['rmd'], bins=30, edgecolor='black', alpha=0.7)
            ax.axvline(outliers['threshold'], color='red', linestyle='--', label='Threshold')
            ax.set_xlabel('Robust Mahalanobis Distance')
            ax.set_ylabel('Frequency')
            ax.legend()
            st.pyplot(fig)
        else:
            st.info("Run the analysis first from the Data Upload page.")
    else:
        st.info("No analysis results found. Upload data and run analysis first.")

elif page == "📈 PCA Analysis":
    st.header("📈 Principal Component Analysis")
    if st.session_state.analysis_results and 'results' in st.session_state.analysis_results:
        pca_res = st.session_state.analysis_results['results'].get('pca')
        if pca_res:
            st.write(f"Components retained: {pca_res['n_components']}")
            st.write(f"Explained variance: {pca_res['explained_variance']}")
            # Scree plot
            fig, ax = plt.subplots()
            ax.bar(range(1, len(pca_res['explained_variance'])+1), pca_res['explained_variance']*100, alpha=0.6)
            ax.plot(range(1, len(pca_res['explained_variance'])+1), pca_res['cumulative_variance']*100, 'ro-')
            ax.set_xlabel('Principal Component')
            ax.set_ylabel('Explained Variance (%)')
            ax.set_title('Scree Plot')
            st.pyplot(fig)
        else:
            st.info("PCA results not available.")
    else:
        st.info("No analysis results found.")

elif page == "🔍 Clustering":
    st.header("🔍 Clustering")
    if st.session_state.analysis_results and 'results' in st.session_state.analysis_results:
        clust = st.session_state.analysis_results['results'].get('clustering')
        if clust:
            st.write(f"Number of clusters: {clust['k']}")
            # MDS plot
            fig, ax = plt.subplots()
            ax.scatter(clust['mds_coords'][:,0], clust['mds_coords'][:,1], c=clust['labels'], cmap='tab10')
            ax.set_xlabel('MDS1')
            ax.set_ylabel('MDS2')
            ax.set_title('MDS Plot of Clusters')
            st.pyplot(fig)
        else:
            st.info("Clustering results not available.")
    else:
        st.info("No analysis results found.")

elif page == "⛏️ Prospectivity":
    st.header("⛏️ Mineral Prospectivity")
    if st.session_state.analysis_results and 'results' in st.session_state.analysis_results:
        prosp = st.session_state.analysis_results['results'].get('prospectivity')
        if prosp:
            st.write(f"Target elements: {prosp['elements']}")
            st.write(f"Weights: {prosp['weights']}")
            # Histogram of scores
            fig, ax = plt.subplots()
            ax.hist(prosp['score'], bins=30, edgecolor='black', alpha=0.7, color='gold')
            ax.set_xlabel('Prospectivity Score')
            ax.set_ylabel('Frequency')
            ax.set_title('Prospectivity Score Distribution')
            st.pyplot(fig)
        else:
            st.info("Prospectivity results not available.")
    else:
        st.info("No analysis results found.")

elif page == "📋 Report":
    st.header("📋 Comprehensive Report")
    if st.session_state.analysis_results:
        res = st.session_state.analysis_results
        st.json(res)
        # Option to download
        json_str = json.dumps(res, indent=2)
        st.download_button("Download Report as JSON", data=json_str, file_name="geochem_report.json", mime="application/json")
    else:
        st.info("No analysis results to report.")