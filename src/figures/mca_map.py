"""Multiple Correspondence Analysis (MCA) map figure (fig07)"""

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def plot_mca_map(
    df: pd.DataFrame,
    output_path: str,
    seed: int = 42,
    figsize: tuple = (10, 8),
    dpi: int = 300
) -> None:
    """
    Plot MCA map (simplified using PCA on keyword co-occurrence).
    
    Note: Full MCA requires categorical variables. This is a simplified version
    using PCA on keyword presence/absence matrix.
    
    Args:
        df: Canonical DataFrame with keywords_raw
        output_path: Output file path
        seed: Random seed for reproducibility
        figsize: Figure size in inches
        dpi: DPI for PNG output
    """
    logger.info("Generating MCA map (simplified PCA version)")
    
    # Extract keywords
    all_keywords = set()
    keyword_lists = []
    
    for _, row in df.iterrows():
        if pd.isna(row.get('keywords_raw')) or not row.get('keywords_raw'):
            keyword_lists.append([])
            continue
        
        keywords_str = str(row['keywords_raw'])
        keywords = [k.strip().lower() for k in keywords_str.split(';') if k.strip()]
        keyword_lists.append(keywords)
        all_keywords.update(keywords)
    
    # Create binary matrix (documents x keywords)
    all_keywords = sorted(list(all_keywords))
    matrix = []
    
    for keywords in keyword_lists:
        row = [1 if kw in keywords else 0 for kw in all_keywords]
        matrix.append(row)
    
    matrix = np.array(matrix)
    
    # Select top keywords by frequency
    keyword_freq = matrix.sum(axis=0)
    top_kw_indices = np.argsort(keyword_freq)[-50:]  # Top 50 keywords
    matrix_top = matrix[:, top_kw_indices]
    top_keywords = [all_keywords[i] for i in top_kw_indices]
    
    # Apply PCA
    np.random.seed(seed)
    pca = PCA(n_components=2, random_state=seed)
    coords = pca.fit_transform(matrix_top)
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot documents
    ax.scatter(coords[:, 0], coords[:, 1], alpha=0.3, s=20, color='steelblue')
    
    # Plot top keywords (if space allows)
    # Scale keyword positions (simplified)
    for i, kw in enumerate(top_keywords[:20]):  # Show top 20
        # Position based on keyword vector
        kw_vector = matrix_top[:, i]
        if kw_vector.sum() > 0:
            doc_indices = np.where(kw_vector > 0)[0]
            if len(doc_indices) > 0:
                kw_pos = coords[doc_indices].mean(axis=0)
                ax.annotate(kw[:20], kw_pos, fontsize=8, alpha=0.7)
    
    ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)', fontsize=12)
    ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)', fontsize=12)
    ax.set_title('Multiple Correspondence Analysis Map (PCA-based)', fontsize=14, fontweight='bold')
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    
    # Save
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    if output_path.endswith('.png'):
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    else:
        plt.savefig(output_path, bbox_inches='tight')
    
    plt.close()
    
    logger.info(f"Saved MCA map: {output_path}")
