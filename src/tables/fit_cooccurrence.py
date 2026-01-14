"""FIT co-occurrence table (tab08)"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def calculate_fit_cooccurrence(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate FIT co-occurrence matrix.
    
    Formulas:
    - O_ij = number of documents tagged with both FIT i and FIT j
    - E_ij = (N_i * N_j) / N (expected co-occurrence)
    - R_ij = (O_ij - E_ij) / sqrt(E_ij) (residual)
    
    Args:
        df: Canonical DataFrame with fit_labels column
        
    Returns:
        DataFrame with columns: FIT_i, FIT_j, O_ij, E_ij, R_ij
    """
    logger.info("Calculating FIT co-occurrence matrix")
    
    # Get all FIT categories
    all_fits = set()
    for fit_labels in df['fit_labels']:
        if isinstance(fit_labels, list):
            all_fits.update(fit_labels)
    
    all_fits = sorted(list(all_fits))
    N = len(df)
    
    # Count documents per FIT
    N_i_dict = {}
    for fit in all_fits:
        N_i_dict[fit] = df['fit_labels'].apply(
            lambda labels: fit in labels if isinstance(labels, list) else False
        ).sum()
    
    # Calculate co-occurrence
    cooccurrence_records = []
    
    for i, fit_i in enumerate(all_fits):
        for fit_j in all_fits[i:]:  # Upper triangle only
            # Observed co-occurrence
            O_ij = df['fit_labels'].apply(
                lambda labels: (
                    isinstance(labels, list) and
                    fit_i in labels and
                    fit_j in labels
                )
            ).sum()
            
            # Expected co-occurrence
            N_i = N_i_dict[fit_i]
            N_j = N_i_dict[fit_j]
            E_ij = (N_i * N_j) / N if N > 0 else 0
            
            # Residual
            if E_ij > 0:
                R_ij = (O_ij - E_ij) / np.sqrt(E_ij)
            else:
                R_ij = 0
            
            cooccurrence_records.append({
                'FIT_i': fit_i,
                'FIT_j': fit_j,
                'O_ij': O_ij,
                'E_ij': E_ij,
                'R_ij': R_ij,
            })
    
    cooccurrence_df = pd.DataFrame(cooccurrence_records)
    
    logger.info(f"Calculated co-occurrence for {len(all_fits)} FIT categories")
    
    return cooccurrence_df


def save_fit_cooccurrence_table(
    cooccurrence_df: pd.DataFrame,
    output_path: str
) -> None:
    """
    Save FIT co-occurrence table to CSV.
    
    Args:
        cooccurrence_df: Co-occurrence DataFrame
        output_path: Output file path
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    cooccurrence_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    logger.info(f"Saved FIT co-occurrence table: {output_file}")
