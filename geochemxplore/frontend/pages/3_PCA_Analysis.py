import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(page_title="PCA Analysis", layout="wide")
st.title("📈 Principal Component Analysis")

if 'analysis_results' not in st.session_state or st.session_state.analysis_results is None:
    st.warning("No analysis results found. Please upload data and run analysis first.")
    st.stop()

res = st.session_state.analysis_results
pca_res = res.get('results', {}).get('pca')

if pca_res is None:
    st.info("PCA results not available.")
else:
    st.subheader("PCA Summary")
    st.write(f"**Components retained:** {pca_res['n_components']}")
    st.write(f"**Total variance explained:** {pca_res['cumulative_variance'][-1]*100:.1f}%")

    # Scree plot
    fig, ax = plt.subplots(figsize=(10, 5))
    exp_var = pca_res['explained_variance'] * 100
    cum_var = pca_res['cumulative_variance'] * 100
    x = np.arange(1, len(exp_var)+1)
    ax.bar(x, exp_var, alpha=0.6, label='Individual')
    ax.plot(x, cum_var, 'ro-', label='Cumulative')
    ax.axhline(y=86, color='green', linestyle='--', label='86% threshold')
    ax.set_xlabel('Principal Component')
    ax.set_ylabel('Explained Variance (%)')
    ax.set_title('Scree Plot')
    ax.legend()
    ax.grid(alpha=0.3)
    st.pyplot(fig)

    # Loadings (first two PCs)
    if pca_res.get('loadings_clr') is not None:
        loadings = pca_res['loadings_clr']
        # For display, we need the element names from the original columns
        # We have them in session_state?
        element_names = st.session_state.get('elem_cols', [f"Var{i+1}" for i in range(loadings.shape[1])])
        # But loadings shape is (n_components, n_elements)
        # We'll plot loadings for PC1 and PC2
        if loadings.shape[0] >= 2:
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            colors = ['red' if x < 0 else 'blue' for x in loadings[0]]
            ax2.barh(element_names, loadings[0], color=colors, alpha=0.7)
            ax2.set_xlabel('Loading (CLR space)')
            ax2.set_title(f'PC1 Loadings ({pca_res["explained_variance"][0]*100:.1f}%)')
            ax2.axvline(0, color='black', linewidth=0.5)
            plt.tight_layout()
            st.pyplot(fig2)

    # Biplot (PC1 vs PC2)
    st.subheader("Biplot (PC1 vs PC2)")
    # We can create a biplot using the scores and loadings
    scores = pca_res['scores']
    if scores.shape[1] >= 2 and loadings is not None:
        fig3, ax3 = plt.subplots(figsize=(10, 8))
        ax3.scatter(scores[:,0], scores[:,1], alpha=0.5, s=20, c='lightgray')
        # Add arrows for loadings (scaled)
        scale = 2.0
        for i, name in enumerate(element_names):
            ax3.arrow(0, 0, loadings[0,i]*scale, loadings[1,i]*scale,
                      head_width=0.05, head_length=0.05, fc='red', ec='red', alpha=0.7)
            ax3.text(loadings[0,i]*scale*1.1, loadings[1,i]*scale*1.1, name, fontsize=8)
        ax3.set_xlabel(f'PC1 ({pca_res["explained_variance"][0]*100:.1f}%)')
        ax3.set_ylabel(f'PC2 ({pca_res["explained_variance"][1]*100:.1f}%)')
        ax3.axhline(0, color='black', alpha=0.3)
        ax3.axvline(0, color='black', alpha=0.3)
        ax3.set_title('Biplot')
        ax3.grid(alpha=0.3)
        st.pyplot(fig3)