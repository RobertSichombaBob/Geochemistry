# Geochem Analytics Platform

A scalable, cloud‑native geochemical data analysis platform for mineral exploration.

## Features

- **Universal data ingestion** – CSV, Excel (soil, rock, drill core)
- **Compositional Data Analysis (CoDA)** – CLR/ILR transformations
- **Outlier detection** – Robust Mahalanobis, LOF, Isolation Forest, One‑Class SVM
- **Dimensionality reduction** – PCA with CLR loadings
- **Clustering** – K‑means with elbow/silhouette + MDS visualisation
- **Factor Analysis** – Varimax rotation, score maps
- **Interactive mapping** – Plotly, Folium, spatial anomaly maps
- **Prospectivity scoring** – Weighted multi‑element targeting
- **Export** – Reports, CSV, plots

## Quick Start

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate` (Windows: `venv\Scripts\activate`)
4. Install: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and adjust if needed
6. Run the backend: `uvicorn backend.main:app --reload --port 8000`
7. In another terminal, run the frontend: `streamlit run frontend/streamlit_app.py`
8. Open http://localhost:8501 in your browser

## Deployment

- **Backend** – Deploy as a web service on Render, Railway, or AWS EC2.
- **Frontend** – Deploy on Streamlit Cloud (free) by connecting your GitHub repo.
- **Database** – Use Supabase (free tier) for multi‑tenancy and file storage.

## Licensing

Contact Robert Sichomba for commercial licensing.