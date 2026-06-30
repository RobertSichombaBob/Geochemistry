from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import pandas as pd
import io
import tempfile
import os
from typing import Optional
from core.analyzer import GeochemicalAnalyzer
from config import settings

router = APIRouter()

@router.post("/analyze")
async def analyze_geochem_data(
    file: UploadFile = File(...),
    methods: str = Form("pca,clustering,outliers,factor,prospectivity"),
    variance_target: float = Form(0.86),
    n_clusters: int = Form(2),
    n_factors: int = Form(4)
):
    """
    Upload a CSV or Excel file and run selected geochemical analyses.
    Returns JSON with results (scores, loadings, outliers, etc.).
    """
    # Read file
    content = await file.read()
    ext = file.filename.split('.')[-1].lower()
    try:
        if ext == 'csv':
            df = pd.read_csv(io.BytesIO(content))
        elif ext in ['xls', 'xlsx']:
            df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use CSV or Excel.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")

    if df.empty:
        raise HTTPException(status_code=400, detail="File is empty.")

    # Initialize analyzer
    analyzer = GeochemicalAnalyzer()
    analyzer.load_data(df)
    analyzer.preprocess()

    # Parse methods
    method_list = [m.strip() for m in methods.split(',') if m.strip()]
    results = {}

    if 'pca' in method_list:
        results['pca'] = analyzer.pca_analysis(variance_target=variance_target)
    if 'clustering' in method_list:
        results['clustering'] = analyzer.kmeans_clustering(k=n_clusters)
    if 'outliers' in method_list:
        results['outliers'] = analyzer.robust_mahalanobis()
    if 'factor' in method_list:
        results['factor'] = analyzer.factor_analysis(n_factors=n_factors)
    if 'prospectivity' in method_list:
        results['prospectivity'] = analyzer.prospectivity_score()

    # Return summary
    return {
        "status": "success",
        "samples": len(analyzer.df),
        "elements_detected": analyzer.element_cols,
        "coord_cols": analyzer.coord_cols,
        "results": results
    }
