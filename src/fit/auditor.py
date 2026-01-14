"""FIT tagging audit generation"""

import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def generate_fit_tagging_audit(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate FIT tagging audit log.
    
    Args:
        df: DataFrame with fit_labels and fit_matched_terms columns
        
    Returns:
        DataFrame with columns: doc_id, matched_terms, fit_labels
    """
    audit_records = []
    
    for _, row in df.iterrows():
        doc_id = row.get('canonical_id', row.get('raw_record_id', ''))
        fit_labels = row.get('fit_labels', [])
        matched_terms = row.get('fit_matched_terms', {})
        
        # Flatten matched terms
        all_matched_terms = []
        for fit_key, terms in matched_terms.items():
            all_matched_terms.extend(terms)
        
        # Create audit record
        audit_records.append({
            'doc_id': doc_id,
            'matched_terms': '; '.join(all_matched_terms) if all_matched_terms else '',
            'fit_labels': '; '.join(fit_labels) if fit_labels else '',
            'fit_count': len(fit_labels),
        })
    
    audit_df = pd.DataFrame(audit_records)
    
    return audit_df


def save_fit_tagging_audit(audit_df: pd.DataFrame, output_path: str) -> None:
    """
    Save FIT tagging audit to CSV.
    
    Args:
        audit_df: Audit DataFrame
        output_path: Output file path
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    audit_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    logger.info(f"Saved FIT tagging audit: {output_file} ({len(audit_df)} records)")
