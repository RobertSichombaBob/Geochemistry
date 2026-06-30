import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import json
import pandas as pd

st.set_page_config(page_title="Report", layout="wide")
st.title("📋 Comprehensive Report")

if 'analysis_results' not in st.session_state or st.session_state.analysis_results is None:
    st.warning("No analysis results found. Please upload data and run analysis first.")
    st.stop()

res = st.session_state.analysis_results
st.subheader("Analysis Summary")
st.write(f"**Samples:** {res.get('samples', 0)}")
st.write(f"**Elements detected:** {', '.join(res.get('elements_detected', []))}")
st.write(f"**Coordinate columns:** {', '.join(res.get('coord_cols', []))}")

if 'results' in res:
    st.subheader("Detailed Results")
    # Show each analysis result in expandable sections
    for key, value in res['results'].items():
        with st.expander(f"📊 {key.capitalize()}"):
            if isinstance(value, dict):
                # Convert numpy arrays to lists for display
                clean_value = {}
                for k, v in value.items():
                    if isinstance(v, np.ndarray):
                        clean_value[k] = v.tolist()
                    else:
                        clean_value[k] = v
                st.json(clean_value)
            else:
                st.write(value)

# Export options
st.subheader("📥 Export")
json_str = json.dumps(res, indent=2, default=lambda x: x.tolist() if isinstance(x, np.ndarray) else x)
st.download_button("Download Full Report (JSON)", data=json_str, file_name="geochem_report.json", mime="application/json")

# Also allow download of raw data with appended results
if st.session_state.analyzer_data is not None:
    df = st.session_state.analyzer_data.copy()
    # Add prospectivity and cluster columns if available
    if 'prospectivity' in res.get('results', {}):
        prosp = res['results']['prospectivity']
        if 'score' in prosp:
            df['Prospectivity'] = prosp['score']
    if 'clustering' in res.get('results', {}):
        clust = res['results']['clustering']
        if 'labels' in clust:
            df['Cluster'] = clust['labels']
    # Add outlier flag if available
    if 'outliers' in res.get('results', {}):
        out = res['results']['outliers']
        if 'outliers' in out:
            # Ensure length matches
            if len(out['outliers']) == len(df):
                df['Outlier'] = out['outliers']
    csv = df.to_csv(index=False)
    st.download_button("Download Data with Results (CSV)", data=csv, file_name="geochem_data_with_results.csv", mime="text/csv")