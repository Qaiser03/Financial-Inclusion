"""Deduplication modules for within-DB and cross-DB deduplication"""

import pandas as pd
import logging
from typing import Dict, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


def deduplicate_within_db(df: pd.DataFrame, source_db: str) -> pd.DataFrame:
    """
    Deduplicate records within a single database.
    
    Canvas specification:
    Rule A: Group by doi_clean (non-null) → keep one canonical
    Rule B: For doi_clean null → group by (title_norm, year_clean) → keep one canonical
    
    Args:
        df: DataFrame with cleaned fields (doi_clean, title_norm, year_clean, metadata_completeness_score)
        source_db: Database name ('scopus' or 'wos')
        
    Returns:
        Deduplicated DataFrame
    """
    logger.info(f"Deduplicating {source_db} records (n={len(df)})")
    
    if len(df) == 0:
        return df
    
    df = df.copy()
    
    # Rule A: Deduplicate by DOI
    has_doi = df['doi_clean'].notna()
    df_with_doi = df[has_doi].copy()
    df_without_doi = df[~has_doi].copy()
    
    if len(df_with_doi) > 0:
        # Group by doi_clean
        grouped = df_with_doi.groupby('doi_clean', as_index=False)
        
        def select_best_record(group):
            # Sort by: completeness score (desc), has references (desc), raw_record_id (asc)
            group = group.copy()
            group['has_references'] = group['references_raw'].notna() & (
                group['references_raw'].astype(str).str.strip() != ''
            )
            
            group = group.sort_values(
                by=['metadata_completeness_score', 'has_references', 'raw_record_id'],
                ascending=[False, False, True]
            )
            
            return group.iloc[0]
        
        df_with_doi_dedup = grouped.apply(select_best_record).reset_index(drop=True)
    else:
        df_with_doi_dedup = pd.DataFrame()
    
    # Rule B: Deduplicate by title_norm + year_clean for records without DOI
    if len(df_without_doi) > 0:
        # Filter: must have both title_norm and year_clean
        has_secondary_key = (
            df_without_doi['title_norm'].notna() &
            (df_without_doi['title_norm'] != '') &
            df_without_doi['year_clean'].notna()
        )
        
        df_with_secondary = df_without_doi[has_secondary_key].copy()
        df_without_secondary = df_without_doi[~has_secondary_key].copy()
        
        if len(df_with_secondary) > 0:
            # Create composite key
            df_with_secondary['secondary_key'] = (
                df_with_secondary['title_norm'] + '|' + 
                df_with_secondary['year_clean'].astype(str)
            )
            
            # Group by secondary key
            grouped = df_with_secondary.groupby('secondary_key', as_index=False)
            
            def select_best_record_secondary(group):
                # Sort by: completeness score (desc), has references (desc), raw_record_id (asc)
                group = group.copy()
                group['has_references'] = group['references_raw'].notna() & (
                    group['references_raw'].astype(str).str.strip() != ''
                )
                
                group = group.sort_values(
                    by=['metadata_completeness_score', 'has_references', 'raw_record_id'],
                    ascending=[False, False, True]
                )
                
                return group.iloc[0]
            
            df_with_secondary_dedup = grouped.apply(select_best_record_secondary).reset_index(drop=True)
            df_with_secondary_dedup = df_with_secondary_dedup.drop(columns=['secondary_key'])
        else:
            df_with_secondary_dedup = pd.DataFrame()
        
        # Combine: deduplicated secondary-key records + records without secondary key
        df_without_doi_dedup = pd.concat(
            [df_with_secondary_dedup, df_without_secondary],
            ignore_index=True
        )
    else:
        df_without_doi_dedup = pd.DataFrame()
    
    # Final merge
    df_dedup = pd.concat([df_with_doi_dedup, df_without_doi_dedup], ignore_index=True)
    
    removed = len(df) - len(df_dedup)
    logger.info(f"Removed {removed} duplicate records from {source_db} (kept {len(df_dedup)})")
    
    return df_dedup


def deduplicate_cross_db(
    scopus_df: pd.DataFrame,
    wos_df: pd.DataFrame,
    preferred_db: str = 'scopus'
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Merge and deduplicate across databases.
    
    Steps:
    1. Concatenate cleaned datasets
    2. Primary key dedup: group by doi_clean, keep best record
    3. Secondary key dedup: group by (title_norm, year_clean), keep best record
    4. Generate collision warnings for secondary-key matches
    
    Args:
        scopus_df: Cleaned Scopus DataFrame
        wos_df: Cleaned WoS DataFrame
        preferred_db: Preferred database for tie-breaking ('scopus' or 'wos')
        
    Returns:
        Tuple of (deduplicated DataFrame, collisions DataFrame)
    """
    logger.info("Merging and deduplicating across databases")
    
    # Step 1: Concatenate
    merged_df = pd.concat([scopus_df, wos_df], ignore_index=True)
    logger.info(f"Total records after merge: {len(merged_df)}")
    
    # Step 2: Primary key deduplication (by DOI)
    has_doi = merged_df['doi_clean'].notna()
    df_with_doi = merged_df[has_doi].copy()
    df_without_doi = merged_df[~has_doi].copy()
    
    collisions_primary = []
    
    if len(df_with_doi) > 0:
        # Group by doi_clean
        grouped = df_with_doi.groupby('doi_clean', as_index=False)
        
        def select_best_record_primary(group):
            if len(group) > 1:
                # Multiple records with same DOI - potential collision
                collision_info = {
                    'doi_clean': group.iloc[0]['doi_clean'],
                    'n_records': len(group),
                    'sources': group['source_db'].tolist(),
                    'record_ids': group['raw_record_id'].tolist(),
                }
                collisions_primary.append(collision_info)
            
            # Sort by: completeness score (desc), has references (desc), preferred DB, raw_record_id (asc)
            group = group.copy()
            group['has_references'] = group['references_raw'].notna() & (
                group['references_raw'].astype(str).str.strip() != ''
            )
            group['is_preferred'] = (group['source_db'] == preferred_db)
            
            group = group.sort_values(
                by=['metadata_completeness_score', 'has_references', 'is_preferred', 'raw_record_id'],
                ascending=[False, False, False, True]
            )
            
            return group.iloc[0]
        
        df_with_doi_dedup = grouped.apply(select_best_record_primary).reset_index(drop=True)
    else:
        df_with_doi_dedup = pd.DataFrame()
    
    # Step 3: Secondary key deduplication (by title_norm + year_clean)
    # Only for records without DOI
    collisions_secondary = []
    
    if len(df_without_doi) > 0:
        # Filter: must have both title_norm and year_clean
        has_secondary_key = (
            df_without_doi['title_norm'].notna() &
            (df_without_doi['title_norm'] != '') &
            df_without_doi['year_clean'].notna()
        )
        
        df_with_secondary = df_without_doi[has_secondary_key].copy()
        df_without_secondary = df_without_doi[~has_secondary_key].copy()
        
        if len(df_with_secondary) > 0:
            # Create composite key
            df_with_secondary['secondary_key'] = (
                df_with_secondary['title_norm'] + '|' + 
                df_with_secondary['year_clean'].astype(str)
            )
            
            # Group by secondary key
            grouped = df_with_secondary.groupby('secondary_key', as_index=False)
            
            def select_best_record_secondary(group):
                if len(group) > 1:
                    # Multiple records with same secondary key - potential collision
                    collision_info = {
                        'title_norm': group.iloc[0]['title_norm'],
                        'year_clean': group.iloc[0]['year_clean'],
                        'n_records': len(group),
                        'sources': group['source_db'].tolist(),
                        'record_ids': group['raw_record_id'].tolist(),
                        'titles': group['title_raw'].tolist(),
                    }
                    collisions_secondary.append(collision_info)
                
                # Sort by: completeness score (desc), has references (desc), preferred DB, raw_record_id (asc)
                group = group.copy()
                group['has_references'] = group['references_raw'].notna() & (
                    group['references_raw'].astype(str).str.strip() != ''
                )
                group['is_preferred'] = (group['source_db'] == preferred_db)
                
                group = group.sort_values(
                    by=['metadata_completeness_score', 'has_references', 'is_preferred', 'raw_record_id'],
                    ascending=[False, False, False, True]
                )
                
                return group.iloc[0]
            
            df_with_secondary_dedup = grouped.apply(select_best_record_secondary).reset_index(drop=True)
            df_with_secondary_dedup = df_with_secondary_dedup.drop(columns=['secondary_key'])
        else:
            df_with_secondary_dedup = pd.DataFrame()
        
        # Combine: deduplicated secondary-key records + records without secondary key
        df_without_doi_dedup = pd.concat(
            [df_with_secondary_dedup, df_without_secondary],
            ignore_index=True
        )
    else:
        df_without_doi_dedup = pd.DataFrame()
    
    # Final merge
    canonical_df = pd.concat([df_with_doi_dedup, df_without_doi_dedup], ignore_index=True)
    
    # Add source provenance flags (has_scopus, has_wos)
    canonical_df['has_scopus'] = canonical_df['source_db'] == 'scopus'
    canonical_df['has_wos'] = canonical_df['source_db'] == 'wos'
    
    # For records that came from cross-DB dedup, we need to check if they originated from both
    # This is simplified - in reality, we'd need to track which original records contributed
    # For now, we mark based on the kept record's source_db
    
    # Create collisions DataFrame
    collisions_df = pd.DataFrame(collisions_secondary) if collisions_secondary else pd.DataFrame()
    
    removed = len(merged_df) - len(canonical_df)
    logger.info(f"Removed {removed} duplicate records across databases (kept {len(canonical_df)})")
    logger.info(f"Found {len(collisions_secondary)} secondary-key collisions requiring review")
    
    return canonical_df, collisions_df


def deduplicate_full_pipeline(
    scopus_df: pd.DataFrame,
    wos_df: pd.DataFrame,
    preferred_db: str = 'scopus'
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Full deduplication pipeline: within-DB then cross-DB.
    
    Args:
        scopus_df: Cleaned Scopus DataFrame
        wos_df: Cleaned WoS DataFrame
        preferred_db: Preferred database for tie-breaking
        
    Returns:
        Tuple of (canonical DataFrame, collisions DataFrame)
    """
    logger.info("Starting full deduplication pipeline")
    
    # Step 1: Within-DB deduplication
    scopus_dedup = deduplicate_within_db(scopus_df, 'scopus')
    wos_dedup = deduplicate_within_db(wos_df, 'wos')
    
    # Step 2: Cross-DB deduplication
    canonical_df, collisions_df = deduplicate_cross_db(
        scopus_dedup,
        wos_dedup,
        preferred_db=preferred_db
    )
    
    # Add canonical ID
    canonical_df = canonical_df.reset_index(drop=True)
    canonical_df['canonical_id'] = 'FI_' + canonical_df.index.astype(str).str.zfill(6)
    
    logger.info(f"Canonical dataset: {len(canonical_df)} unique records")
    
    return canonical_df, collisions_df
