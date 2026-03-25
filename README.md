# Factor Analysis for Mineral Exploration – Inner Mongolia

## Introduction

Mineral exploration increasingly relies on multivariate statistical techniques to extract hidden signals from geochemical data. This project applies Compositional Data Analysis (CODA), Principal Component Analysis (PCA), and Factor Analysis (FA) to soil geochemistry data from Inner Mongolia, China, to identify anomalies related to silver polymetallic mineralization. The ultimate goal is to guide costly follow‑up steps such as geophysical surveys or deep drilling.

## Problem Statement

The study area is covered by grassland, and mineralization does not outcrop. Soil samples provide indirect geochemical signatures of underlying geology. We need to identify which elements or element ratios are associated with mineralization and to locate spatial anomalies that warrant further investigation.

## Questions

1. What are the key element associations (log‑ratios) that characterize the mineralizing process?
2. Which samples are compositional outliers and might represent mineralization?
3. How do clusters of samples relate to lithology and structure?
4. What do PCA and FA reveal about the underlying processes?
5. Where would we recommend drilling based on factor scores?

## Objectives

- Perform CODA‑based EDA (biplots, ternary diagrams) to understand element relationships.
- Detect outliers using robust Mahalanobis distance on clr‑transformed data.
- Cluster samples using k‑means on selected elements and assess spatial patterns.
- Apply PCA to clr‑transformed data and interpret loadings and scores.
- Apply Factor Analysis with 3 and 4 factors, map factor scores, and compare with PCA.
- Propose drilling targets based on the mineralization factor.

## Aim

To develop a systematic workflow that integrates CODA, PCA, and FA to support exploration decisions, reducing risk and focusing resources on high‑potential areas.

## Data Description

- **File**: `InnerMongolia_CompositionalData.csv`
- **Samples**: 968 soil samples collected at a density of 1–2 per km², from depths of 20–80 cm.
- **Elements**: 39 elements analyzed; 30 selected for analysis (Au, Ag, As, Ba, Be, Bi, Cd, Co, Cr, Cu, Mn, Nb, Ni, P, Pb, Rb, Sb, Sn, Ti, V, W, Zn, Zr, Si, Al, Fe, Mg, Ca, Na, K).
- **Geological setting**: Paleozoic tectono‑magmatic belt with Devonian, Permian, and Jurassic formations. Known Ag‑polymetallic deposits occur in the area.

## Methodology

1. **CODA EDA**  
   - Biplots and ternary diagrams to visualize log‑ratio relationships.
   - Focus on elements associated with mineralization (Ag, As, Sb, Pb, Zn).

2. **Outlier detection**  
   - Robust Mahalanobis distance on clr‑transformed data to identify samples with extreme compositions.

3. **Cluster analysis**  
   - Select top six elements based on EDA.
   - Use k‑means clustering with Euclidean distance on clr‑transformed data.
   - Visualize clusters in MDS plots and map them spatially.

4. **Principal Component Analysis (PCA)**  
   - Perform PCA on clr‑transformed data.
   - Scree plot to decide number of components.
   - Score plots colored by Ag concentration and by important log‑ratios.
   - Loadings plots to identify element associations.
   - Map first two PC scores to assess spatial patterns.

5. **Factor Analysis (FA)**  
   - Apply FA with 3 and 4 factors (varimax rotation).
   - Compare factor loadings with PCA loadings.
   - Map factor scores for interpretation.
   - Assess how additional factor changes interpretation.

6. **Target generation**  
   - Combine factor scores with geological map (faults, lithology) to select drilling locations.

## Mathematical Framework

### CLR Transformation
\[
\text{clr}(\mathbf{x})_i = \ln \frac{x_i}{g(\mathbf{x})}, \quad g(\mathbf{x}) = \left( \prod_{j=1}^D x_j \right)^{1/D}
\]

### Robust Mahalanobis Distance
\[
MD_{\text{robust}}(\mathbf{x}) = \sqrt{ (\mathbf{x} - \mathbf{T})^T \mathbf{C}^{-1} (\mathbf{x} - \mathbf{T}) }
\]
where \(\mathbf{T}\) and \(\mathbf{C}\) are robust estimates of location and scatter (e.g., minimum covariance determinant). Outliers are those with \(MD\) exceeding a threshold (e.g., \(\chi^2_{p,0.975}\)).

### Principal Component Analysis (PCA)
PCA finds linear combinations of the original variables that maximize variance. The loading vectors indicate variable contributions; scores represent sample positions in the reduced space.

### Factor Analysis (FA)
Factor model:
\[
\mathbf{x} = \mathbf{\Lambda} \mathbf{f} + \mathbf{\epsilon}
\]
where \(\mathbf{x}\) are observed variables (clr‑transformed), \(\mathbf{\Lambda}\) is the loading matrix, \(\mathbf{f}\) are common factors, and \(\mathbf{\epsilon}\) are unique errors. Rotation (e.g., varimax) simplifies loadings for interpretability.

## Tools

- Python (pandas, numpy, matplotlib, scikit‑learn, geopandas, pyproj)
- Google Colab (notebooks provided)
- CoDaPack (optional for initial EDA)

## Repository Structure
