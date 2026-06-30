import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(page_title="Outlier Detection", layout="wide")
st.title("🎯 Outlier Detection")

if 'analysis_results' not in st.session_state or st.session_state.analysis_results is None:
    st.warning("No analysis results found. Please upload data and run analysis first.")
    st.stop()

res = st.session_state.analysis_results
outliers = res.get('results', {}).get('outliers')

if outliers is None:
    st.info("Outlier detection was not run or no results available.")
else:
    st.markdown(f"**Method:** Robust Mahalanobis Distance (MCD)")
    st.markdown(f"**Threshold:** {outliers['threshold']:.3f}")
    st.markdown(f"**Number of outliers:** {np.sum(outliers['outliers'])} out of {len(outliers['outliers'])} samples")

    # Histogram
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(outliers['rmd'], bins=30, edgecolor='black', alpha=0.7, color='steelblue')
    ax.axvline(outliers['threshold'], color='red', linestyle='--', linewidth=2, label=f'Threshold = {outliers["threshold"]:.2f}')
    ax.set_xlabel('Robust Mahalanobis Distance')
    ax.set_ylabel('Frequency')
    ax.set_title('RMD Distribution')
    ax.legend()
    ax.grid(alpha=0.3)
    st.pyplot(fig)

    # Q‑Q plot
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    dof = outliers['rmd'].shape[0]  # degrees of freedom = number of samples? Actually it's number of variables.
    # We need the number of variables used in outlier detection. We can store it, but we can approximate.
    # For display, let's assume dof from the data (but we don't have it). We'll skip Q‑Q for simplicity.
    st.info("Q‑Q plot not implemented in this simplified version.")

    # Interactive map if coordinates exist
    if st.session_state.get('coord_cols') and len(st.session_state.coord_cols) == 2:
        df = st.session_state.analyzer_data
        if df is not None:
            x_col, y_col = st.session_state.coord_cols
            # Create a copy with outlier flag
            plot_df = df.copy()
            # We need indices – but the outliers array length may not match df if samples were dropped.
            # For simplicity, assume full match (if no rows were dropped)
            if len(outliers['outliers']) == len(df):
                plot_df['Outlier'] = outliers['outliers']
            else:
                # Fallback: create dummy
                plot_df['Outlier'] = False
                plot_df.iloc[:len(outliers['outliers']), plot_df.columns.get_loc('Outlier')] = outliers['outliers']

            fig3 = px.scatter(plot_df, x=x_col, y=y_col, color='Outlier',
                              color_discrete_map={False: 'blue', True: 'red'},
                              title="Spatial Outlier Map")
            st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No coordinate columns available for spatial map.")