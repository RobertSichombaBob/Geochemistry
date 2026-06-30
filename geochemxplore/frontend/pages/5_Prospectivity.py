import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(page_title="Prospectivity", layout="wide")
st.title("⛏️ Mineral Prospectivity")

if 'analysis_results' not in st.session_state or st.session_state.analysis_results is None:
    st.warning("No analysis results found. Please upload data and run analysis first.")
    st.stop()

res = st.session_state.analysis_results
prosp_res = res.get('results', {}).get('prospectivity')

if prosp_res is None:
    st.info("Prospectivity results not available.")
else:
    st.subheader("Prospectivity Scoring")
    st.write(f"**Target elements:** {', '.join(prosp_res['elements'])}")
    st.write("**Weights:**")
    for elem, w in prosp_res['weights'].items():
        st.write(f"- {elem}: {w:.3f}")

    score = prosp_res['score']
    st.write(f"Score range: {score.min():.3f} – {score.max():.3f}")

    # Histogram
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(score, bins=30, edgecolor='black', alpha=0.7, color='gold')
    ax.set_xlabel('Prospectivity Score')
    ax.set_ylabel('Frequency')
    ax.set_title('Distribution of Prospectivity Scores')
    ax.grid(alpha=0.3)
    st.pyplot(fig)

    # Spatial map
    if st.session_state.get('coord_cols') and len(st.session_state.coord_cols) == 2:
        df = st.session_state.analyzer_data
        if df is not None and len(score) == len(df):
            x_col, y_col = st.session_state.coord_cols
            plot_df = df.copy()
            plot_df['Prospectivity'] = score
            fig2 = px.scatter(plot_df, x=x_col, y=y_col, color='Prospectivity',
                              color_continuous_scale='hot',
                              title="Prospectivity Map")
            st.plotly_chart(fig2, use_container_width=True)

            # Top prospects
            top_n = st.slider("Number of top prospects to highlight", 5, 50, 10)
            top_indices = np.argsort(score)[-top_n:]
            fig3, ax3 = plt.subplots(figsize=(8, 6))
            ax3.scatter(df[x_col], df[y_col], c='lightgray', s=30, alpha=0.5, label='All samples')
            ax3.scatter(df.iloc[top_indices][x_col], df.iloc[top_indices][y_col],
                        c='red', s=100, edgecolor='k', label=f'Top {top_n} prospects')
            ax3.set_xlabel(x_col)
            ax3.set_ylabel(y_col)
            ax3.set_title(f'Top {top_n} Prospect Locations')
            ax3.legend()
            ax3.grid(alpha=0.3)
            st.pyplot(fig3)
        else:
            st.warning("Data length mismatch for spatial mapping.")
    else:
        st.info("No spatial coordinates for mapping.")