#!/bin/bash
# Start both backend and frontend in the same container (for development)
# For production you would run them separately.

# Start FastAPI in the background
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

# Start Streamlit
streamlit run frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0