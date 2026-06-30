# core/analyzer.py
import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import io
import base64
import warnings
warnings.filterwarnings("ignore")

from sklearn.decomposition import PCA
from sklearn.covariance import MinCovDet
from sklearn.cluster import KMeans
from sklearn.manifold import MDS
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from factor_analyzer import FactorAnalyzer

from .transformations import clr_transform, ilr_transform, ilr_matrix_from_clr
from .utils import multiplicative_replace, detect_coordinate_columns, detect_element_columns

class GeochemicalAnalyzer:
    """Main class for all geochemical analyses."""

    def __init__(self):
        self.raw_data = None
        self.df = None
        self.coord_cols = []
        self.element_cols = []
        self.clr_df = None
        self.ilr_df = None
        self.V = None
        self.results = {}

    # ---------- DATA LOADING ----------
    def load_data(self, data: pd.DataFrame, coord_cols=None, element_cols=None):
        """
        Load data and auto‑detect columns unless manually specified.
        """
        self.raw_data = data
        self.df = data.copy()

        if coord_cols is not None:
            self.coord_cols = coord_cols
        else:
            x, y = detect_coordinate_columns(self.df)
            if x and y:
                self.coord_cols = [x, y]
            else:
                # Create synthetic coordinates
                self.df['X_synthetic'] = np.arange(len(self.df))
                self.df['Y_synthetic'] = np.random.uniform(0, 100, len(self.df))
                self.coord_cols = ['X_synthetic', 'Y_synthetic']

        if element_cols is not None:
            self.element_cols = element_cols
        else:
            self.element_cols = detect_element_columns(self.df, self.coord_cols)

        if not self.element_cols:
            # Fallback: use all numeric columns except coordinates
            self.element_cols = [
                c for c in self.df.select_dtypes(include=[np.number]).columns
                if c not in self.coord_cols
            ]

        return self

    # ---------- PREPROCESSING ----------
    def preprocess(self, zero_replace=True):
        """CLR and ILR transformations with optional zero replacement."""
        eps = 1e-10
        comp_df = self.df[self.element_cols].copy()
        if zero_replace:
            for col in comp_df.columns:
                comp_df[col] = multiplicative_replace(comp_df[col])
        comp_df = comp_df.fillna(eps).replace(0, eps)

        self.clr_df = clr_transform(comp_df)
        self.V = ilr_matrix_from_clr(self.clr_df)
        self.ilr_df = pd.DataFrame(
            np.dot(self.clr_df.values, self.V),
            columns=[f"ilr{i+1}" for i in range(self.V.shape[1])]
        )
        return self.clr_df

    # ---------- OUTLIER DETECTION ----------
    def robust_mahalanobis(self, data=None):
        if data is None:
            data = self.clr_df.values
        mcd = MinCovDet().fit(data)
        rmd = np.sqrt(mcd.mahalanobis(data))
        dof = data.shape[1]
        threshold = np.sqrt(stats.chi2.ppf(0.95, df=dof))
        outliers = rmd > threshold
        return {'rmd': rmd, 'threshold': threshold, 'outliers': outliers}

    def isolation_forest(self, data=None, contamination=0.05):
        if data is None:
            data = self.clr_df.values
        clf = IsolationForest(contamination=contamination, random_state=42)
        pred = clf.fit_predict(data)
        scores = clf.decision_function(data)
        return {'pred': pred, 'scores': scores, 'outliers': pred == -1}

    def lof(self, data=None, n_neighbors=20, contamination=0.05):
        if data is None:
            data = self.clr_df.values
        lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=contamination)
        pred = lof.fit_predict(data)
        scores = -lof.negative_outlier_factor_
        return {'pred': pred, 'scores': scores, 'outliers': pred == -1}

    def one_class_svm(self, data=None, nu=0.05, gamma=0.05):
        if data is None:
            data = self.clr_df.values
        clf = OneClassSVM(nu=nu, kernel='rbf', gamma=gamma)
        pred = clf.fit_predict(data)
        scores = clf.decision_function(data)
        return {'pred': pred, 'scores': scores, 'outliers': pred == -1}

    # ---------- PCA ----------
    def pca_analysis(self, variance_target=0.86):
        X = self.ilr_df.values
        pca = PCA()
        pca.fit(X)
        cum_var = np.cumsum(pca.explained_variance_ratio_)
        n_comp = max(1, np.argmax(cum_var >= variance_target) + 1)
        pca = PCA(n_components=n_comp)
        scores = pca.fit_transform(X)
        loadings_clr = np.dot(pca.components_, self.V.T)
        return {
            'scores': scores,
            'loadings_clr': loadings_clr,
            'explained_variance': pca.explained_variance_ratio_,
            'cumulative_variance': np.cumsum(pca.explained_variance_ratio_),
            'n_components': n_comp
        }

    # ---------- CLUSTERING ----------
    def kmeans_clustering(self, k=2):
        X = self.clr_df.values
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X)
        mds = MDS(n_components=2, random_state=42, dissimilarity='euclidean')
        mds_coords = mds.fit_transform(X)
        return {'labels': labels, 'mds_coords': mds_coords, 'k': k}

    # ---------- FACTOR ANALYSIS ----------
    def factor_analysis(self, n_factors=4, rotation='varimax'):
        X = self.ilr_df.values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        fa = FactorAnalyzer(n_factors=n_factors, rotation=rotation, method='minres')
        fa.fit(X_scaled)
        scores = fa.transform(X_scaled)
        loadings = fa.loadings_
        var_info = fa.get_factor_variance()
        # Transform loadings back to CLR space for interpretation
        loadings_clr = np.dot(loadings.T, self.V.T).T
        return {
            'scores': scores,
            'loadings': loadings,
            'loadings_clr': loadings_clr,
            'variance_prop': var_info[1],
            'cumulative': var_info[2]
        }

    # ---------- PROSPECTIVITY ----------
    def prospectivity_score(self, target_elements=None, weights=None):
        """Weighted sum of standardised target elements."""
        if target_elements is None:
            target_elements = self.element_cols[:min(6, len(self.element_cols))]
        if weights is None:
            weights = {e: 1.0 for e in target_elements}
        # Ensure all target elements exist
        present = [e for e in target_elements if e in self.df.columns]
        if not present:
            return None
        # Use raw data (or CLR) – we'll standardise
        X = self.df[present].values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        # Normalise weights
        w = np.array([weights.get(e, 1.0) for e in present])
        w = w / w.sum()
        score = np.dot(X_scaled, w)
        # Normalise score to 0-1
        score = (score - score.min()) / (score.max() - score.min())
        return {'score': score, 'elements': present, 'weights': dict(zip(present, w))}

    # ---------- PLOT HELPERS ----------
    def plot_to_base64(self, fig):
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')

    # ---------- COMPREHENSIVE ANALYSIS ----------
    def run_full_analysis(self):
        """Run all core analyses and store results."""
        self.preprocess()
        self.results['pca'] = self.pca_analysis()
        self.results['clustering'] = self.kmeans_clustering(k=2)
        self.results['outliers'] = self.robust_mahalanobis()
        self.results['factor'] = self.factor_analysis()
        self.results['prospectivity'] = self.prospectivity_score()
        return self.results