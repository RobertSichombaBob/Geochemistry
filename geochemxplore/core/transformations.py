import numpy as np
import pandas as pd

def clr_transform(data: pd.DataFrame, use_skbio=True) -> pd.DataFrame:
    """
    Centered log‑ratio transformation.
    If scikit-bio is available, uses it; otherwise falls back to manual.
    """
    eps = 1e-10
    X = data.select_dtypes(include=[np.number]).values + eps
    if use_skbio:
        try:
            from skbio.stats.composition import clr as skbio_clr
            clr_vals = skbio_clr(X)
        except ImportError:
            use_skbio = False
    if not use_skbio:
        logX = np.log(X)
        gm = np.mean(logX, axis=1, keepdims=True)
        clr_vals = logX - gm
    col_names = data.select_dtypes(include=[np.number]).columns.tolist()
    return pd.DataFrame(clr_vals, columns=[f"clr({c})" for c in col_names])

def ilr_transform(data: pd.DataFrame, use_skbio=True) -> pd.DataFrame:
    """
    Isometric log‑ratio transformation.
    """
    eps = 1e-10
    X = data.select_dtypes(include=[np.number]).values + eps
    if use_skbio:
        try:
            from skbio.stats.composition import ilr as skbio_ilr
            ilr_vals = skbio_ilr(X)
        except ImportError:
            use_skbio = False
    if not use_skbio:
        # Manual ILR using SVD of CLR (approximate)
        # This is a simplified version; for production, encourage installing scikit-bio
        logX = np.log(X)
        gm = np.mean(logX, axis=1, keepdims=True)
        clr_vals = logX - gm
        # Use PCA to get orthonormal basis (not exact ILR but works for variance)
        from sklearn.decomposition import PCA
        pca = PCA(n_components=X.shape[1]-1)
        ilr_vals = pca.fit_transform(clr_vals)
    n_coords = X.shape[1] - 1
    return pd.DataFrame(ilr_vals, columns=[f"ilr{i+1}" for i in range(n_coords)])

def ilr_matrix_from_clr(clr_df: pd.DataFrame) -> np.ndarray:
    """
    Build ILR basis matrix V such that ilr = clr @ V.
    This is the standard sequential binary partition.
    """
    D = clr_df.shape[1]
    V = np.zeros((D, D-1))
    for i in np.arange(1, D):
        V_i = np.zeros(D)
        V_i[:i] = 1 / i
        V_i[i] = -1
        V_i = V_i * np.sqrt(i / (i+1))
        V[:, i-1] = V_i
    return V