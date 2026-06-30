import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(page_title="Clustering", layout="wide")
st.title("🔍 Clustering Analysis")

if 'analysis_results' not in st.session_state or st.session_state.analysis_results is None:
    st.warning("No analysis results found. Please upload data and run analysis first.")
    st.stop()

res = st.session_state.analysis_results
clust_res = res.get('results', {}).get('clustering')

if clust_res is None:
    st.info("Clustering results not available.")
else:
    st.subheader(f"K‑Means Clustering (k = {clust_res['k']})")
    labels = clust_res['labels']
    st.write(f"Number of samples: {len(labels)}")
    # Count per cluster
    unique, counts = np.unique(labels, return_counts=True)
    for u, c in zip(unique, counts):
        st.write(f"Cluster {u}: {c} samples ({c/len(labels)*100:.1f}%)")

    # MDS plot
    mds_coords = clust_res['mds_coords']
    fig, ax = plt.subplots(figsize=(10, 8))
    scatter = ax.scatter(mds_coords[:,0], mds_coords[:,1], c=labels, cmap='viridis', edgecolor='k', alpha=0.7)
    ax.set_xlabel('MDS Dimension 1')
    ax.set_ylabel('MDS Dimension 2')
    ax.set_title('MDS Projection of Samples')
    plt.colorbar(scatter, ax=ax, label='Cluster')
    ax.grid(alpha=0.3)
    st.pyplot(fig)

    # Spatial map if coordinates available
    if st.session_state.get('coord_cols') and len(st.session_state.coord_cols) == 2:
        df = st.session_state.analyzer_data
        if df is not None and len(labels) == len(df):
            x_col, y_col = st.session_state.coord_cols
            plot_df = df.copy()
            plot_df['Cluster'] = labels.astype(str)
            fig2 = px.scatter(plot_df, x=x_col, y=y_col, color='Cluster',
                              title="Spatial Clusters",
                              color_discrete_sequence=px.colors.qualitative.Set1)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("Data length mismatch or no coordinate data.")
    else:
        st.info("No spatial coordinates for mapping.")