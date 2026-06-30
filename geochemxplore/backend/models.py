from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class AnalysisRequest(BaseModel):
    elements: Optional[List[str]] = None
    methods: List[str] = ["pca", "clustering", "outliers", "factor", "prospectivity"]
    variance_target: float = 0.86
    n_clusters: int = 2
    n_factors: int = 4

class AnalysisResponse(BaseModel):
    status: str
    samples: int
    elements_detected: List[str]
    coord_cols: List[str]
    results: Dict[str, Any]