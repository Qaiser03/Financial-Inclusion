"""VOSviewer export preparation modules"""

import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def export_cocitation_data(
    df: pd.DataFrame,
    output_path: str,
    min_citations: int = 1
) -> None:
    """
    Export co-citation data for VOSviewer.
    
    Format: Tab-delimited with columns:
    - Cited Reference (first author, year)
    - Times Cited
    
    Args:
        df: Canonical DataFrame with references_raw
        output_path: Output file path
        min_citations: Minimum citations for inclusion
    """
    logger.info("Exporting co-citation data for VOSviewer")
    
    # Parse references from references_raw
    # Format varies by database, but typically: Author (Year) Title, Journal, etc.
    citation_records = []
    
    for _, row in df.iterrows():
        if pd.isna(row.get('references_raw')) or not row.get('references_raw'):
            continue
        
        references_str = str(row['references_raw'])
        
        # Split by common delimiters (semicolon, newline)
        references = references_str.split(';')
        if len(references) == 1:
            references = references_str.split('\n')
        
        for ref in references:
            ref = ref.strip()
            if not ref:
                continue
            
            # Extract first author and year (simplified parsing)
            # This is a basic implementation; may need refinement
            citation_records.append({
                'Cited Reference': ref,
                'Times Cited': 1,  # Each occurrence counts as 1
            })
    
    if not citation_records:
        logger.warning("No references found in dataset")
        return
    
    # Aggregate by citation
    citation_df = pd.DataFrame(citation_records)
    citation_df = citation_df.groupby('Cited Reference', as_index=False)['Times Cited'].sum()
    
    # Filter by minimum citations
    citation_df = citation_df[citation_df['Times Cited'] >= min_citations]
    
    # Sort by times cited
    citation_df = citation_df.sort_values('Times Cited', ascending=False)
    
    # Save as tab-delimited
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    citation_df.to_csv(output_file, sep='\t', index=False, encoding='utf-8')
    logger.info(f"Exported {len(citation_df)} citations to {output_file}")


def export_cooccurrence_data(
    df: pd.DataFrame,
    output_path: str,
    min_occurrences: int = 1
) -> None:
    """
    Export keyword co-occurrence data for VOSviewer.
    
    Format: Tab-delimited with columns:
    - Author Keywords (or Keywords Plus)
    - Occurrences
    
    Args:
        df: Canonical DataFrame with keywords_raw
        output_path: Output file path
        min_occurrences: Minimum occurrences for inclusion
    """
    logger.info("Exporting keyword co-occurrence data for VOSviewer")
    
    keyword_records = []
    
    for _, row in df.iterrows():
        if pd.isna(row.get('keywords_raw')) or not row.get('keywords_raw'):
            continue
        
        keywords_str = str(row['keywords_raw'])
        
        # Split by semicolon
        keywords = [k.strip() for k in keywords_str.split(';') if k.strip()]
        
        for keyword in keywords:
            keyword_records.append({
                'Author Keywords': keyword,
                'Occurrences': 1,
            })
    
    if not keyword_records:
        logger.warning("No keywords found in dataset")
        return
    
    # Aggregate by keyword
    keyword_df = pd.DataFrame(keyword_records)
    keyword_df = keyword_df.groupby('Author Keywords', as_index=False)['Occurrences'].sum()
    
    # Filter by minimum occurrences
    keyword_df = keyword_df[keyword_df['Occurrences'] >= min_occurrences]
    
    # Sort by occurrences
    keyword_df = keyword_df.sort_values('Occurrences', ascending=False)
    
    # Save as tab-delimited
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    keyword_df.to_csv(output_file, sep='\t', index=False, encoding='utf-8')
    logger.info(f"Exported {len(keyword_df)} keywords to {output_file}")
