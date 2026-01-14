"""Main pipeline entry point"""

import argparse
import logging
import sys
from pathlib import Path
import pandas as pd

from src.config import load_config, get_path, get_seed
from src.data.loaders import load_raw_data
from src.data.cleaners import clean_dataframe
from src.data.validators import add_completeness_scores, validate_schema, validate_cleaned_fields
from src.data.deduplicators import deduplicate_full_pipeline
from src.audits.dedup_auditor import audit_deduplication
from src.fit.tagger import tag_dataframe
from src.fit.auditor import generate_fit_tagging_audit, save_fit_tagging_audit

# Figure modules
from src.figures.annual_production import plot_annual_production
from src.figures.country_productivity import plot_country_productivity
from src.figures.author_production import plot_author_production_over_time
from src.figures.cocitation_network import plot_cocitation_network
from src.figures.wordclouds import plot_wordclouds_panel
from src.figures.mca_map import plot_mca_map
from src.figures.fit_trends import plot_fit_trends
from src.figures.fit_cooccurrence import plot_fit_cooccurrence_heatmap

# Table modules
from src.tables.fit_cooccurrence import calculate_fit_cooccurrence, save_fit_cooccurrence_table
from src.tables.fit_ranking import calculate_fit_ranking, save_fit_ranking_table

# VOSviewer modules
from src.vos.exporter import export_cocitation_data

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main pipeline function"""
    parser = argparse.ArgumentParser(description='Financial Inclusion Bibliometric Analysis Pipeline')
    parser.add_argument('--config', type=str, default='docs/PARAMETERS.yml',
                        help='Path to configuration file')
    parser.add_argument('--make-figures', type=str, nargs='+', default=[],
                        choices=['all', 'fig02', 'fig03', 'fig04', 'fig05', 'fig06', 'fig07', 'fig08', 'fig10'],
                        help='Figures to generate')
    parser.add_argument('--make-tables', type=str, nargs='+', default=[],
                        choices=['all', 'tab08', 'tab09'],
                        help='Tables to generate')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load configuration
    logger.info("Loading configuration")
    config = load_config(args.config)
    
    # Get paths (may be overridden by auto-detection)
    scopus_path = get_path(config, 'paths', 'raw_data', 'scopus')
    wos_path = get_path(config, 'paths', 'raw_data', 'wos')
    fit_dict_path = get_path(config, 'paths', 'fit_dictionary')
    output_audits = get_path(config, 'paths', 'outputs', 'audits')
    output_figures = get_path(config, 'paths', 'outputs', 'figures')
    output_tables = get_path(config, 'paths', 'outputs', 'tables')
    canonical_path = get_path(config, 'paths', 'processed_data', 'canonical')
    
    # Step 1: Load raw data (auto-detect if files don't exist at configured paths)
    logger.info("Step 1: Loading raw data")
    raw_data, file_paths = load_raw_data(
        str(scopus_path) if Path(scopus_path).exists() else None,
        str(wos_path) if Path(wos_path).exists() else None
    )
    scopus_df = raw_data['scopus']
    wos_df = raw_data['wos']
    
    if len(scopus_df) == 0 and len(wos_df) == 0:
        logger.error("No data loaded. Check file paths or place exports in data/raw/ or repository root.")
        sys.exit(1)
    
    # Step 2: Clean data
    logger.info("Step 2: Cleaning data")
    scopus_cleaned = clean_dataframe(scopus_df)
    wos_cleaned = clean_dataframe(wos_df)
    
    # Step 3: Add completeness scores
    logger.info("Step 3: Calculating completeness scores")
    scopus_cleaned = add_completeness_scores(scopus_cleaned)
    wos_cleaned = add_completeness_scores(wos_cleaned)
    
    # Step 4: Deduplicate
    logger.info("Step 4: Deduplicating")
    preferred_db = config['deduplication']['preferred_db']
    canonical_df, collisions_df = deduplicate_full_pipeline(
        scopus_cleaned,
        wos_cleaned,
        preferred_db=preferred_db
    )
    
    # Step 5: Generate deduplication audits
    logger.info("Step 5: Generating deduplication audits")
    # Calculate detailed dedup stats (simplified - in full implementation would track during dedup)
    within_source_doi_removed = {
        'scopus': len(scopus_df) - len(scopus_cleaned[scopus_cleaned['doi_clean'].notna()]),
        'wos': len(wos_df) - len(wos_cleaned[wos_cleaned['doi_clean'].notna()])
    }
    within_source_title_year_removed = {
        'scopus': 0,  # Would need to track during dedup
        'wos': 0
    }
    cross_source_doi_removed = 0  # Would need to track during dedup
    cross_source_title_year_removed = 0  # Would need to track during dedup
    
    audit_deduplication(
        scopus_original=scopus_df,
        wos_original=wos_df,
        scopus_cleaned=scopus_cleaned,
        wos_cleaned=wos_cleaned,
        canonical_df=canonical_df,
        collisions_df=collisions_df,
        output_dir=str(output_audits),
        file_paths=file_paths,
        within_source_doi_removed=within_source_doi_removed,
        within_source_title_year_removed=within_source_title_year_removed,
        cross_source_doi_removed=cross_source_doi_removed,
        cross_source_title_year_removed=cross_source_title_year_removed
    )
    
    # Step 6: FIT tagging
    logger.info("Step 6: FIT tagging")
    canonical_df = tag_dataframe(canonical_df, str(fit_dict_path))
    
    # Step 7: Generate FIT tagging audit
    logger.info("Step 7: Generating FIT tagging audit")
    fit_audit_df = generate_fit_tagging_audit(canonical_df)
    save_fit_tagging_audit(fit_audit_df, str(output_audits / 'fit_tagging_audit.csv'))
    
    # Step 8: Save canonical dataset
    logger.info("Step 8: Saving canonical dataset")
    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    canonical_df.to_csv(canonical_path, index=False, encoding='utf-8-sig')
    logger.info(f"Saved canonical dataset: {canonical_path} ({len(canonical_df)} records)")
    
    # Step 9: Generate figures
    if 'all' in args.make_figures or len(args.make_figures) > 0:
        logger.info("Step 9: Generating figures")
        seed = get_seed(config, 'figure_generation')
        fig_config = config['figures']
        
        figure_list = args.make_figures if 'all' not in args.make_figures else [
            'fig02', 'fig03', 'fig04', 'fig06', 'fig07', 'fig08', 'fig10'
        ]
        
        for fig_name in figure_list:
            if fig_name == 'fig02':
                plot_annual_production(
                    canonical_df,
                    str(output_figures / 'fig02_annual_production.png'),
                    figsize=fig_config['sizes']['standard'],
                    dpi=fig_config['dpi']
                )
                plot_annual_production(
                    canonical_df,
                    str(output_figures / 'fig02_annual_production.pdf'),
                    figsize=fig_config['sizes']['standard'],
                    dpi=fig_config['dpi']
                )
            
            elif fig_name == 'fig03':
                plot_country_productivity(
                    canonical_df,
                    str(output_figures / 'fig03_country_productivity.png'),
                    figsize=fig_config['sizes']['standard'],
                    dpi=fig_config['dpi']
                )
                plot_country_productivity(
                    canonical_df,
                    str(output_figures / 'fig03_country_productivity.pdf'),
                    figsize=fig_config['sizes']['standard'],
                    dpi=fig_config['dpi']
                )
            
            elif fig_name == 'fig04':
                plot_author_production_over_time(
                    canonical_df,
                    str(output_figures / 'fig04_author_production_over_time.png'),
                    figsize=fig_config['sizes']['wide'],
                    dpi=fig_config['dpi']
                )
                plot_author_production_over_time(
                    canonical_df,
                    str(output_figures / 'fig04_author_production_over_time.pdf'),
                    figsize=fig_config['sizes']['wide'],
                    dpi=fig_config['dpi']
                )
            
            elif fig_name == 'fig05':
                # Co-citation network (requires VOSviewer exports)
                cocitation_base = get_path(config, 'paths', 'vosviewer', 'cocitation_network')
                network_path = str(cocitation_base) + '.net'
                map_path = str(cocitation_base) + '.map'
                
                if Path(network_path).exists() and Path(map_path).exists():
                    plot_cocitation_network(
                        str(network_path),
                        str(map_path),
                        str(output_figures / 'fig05_cocitation_network.png'),
                        seed=seed,
                        figsize=fig_config['sizes']['square'],
                        dpi=fig_config['dpi']
                    )
                    plot_cocitation_network(
                        str(network_path),
                        str(map_path),
                        str(output_figures / 'fig05_cocitation_network.pdf'),
                        seed=seed,
                        figsize=fig_config['sizes']['square'],
                        dpi=fig_config['dpi']
                    )
                else:
                    logger.warning(f"VOSviewer exports not found. Skipping fig05. Run VOSviewer first.")
            
            elif fig_name == 'fig06':
                plot_wordclouds_panel(
                    canonical_df,
                    str(output_figures / 'fig06_wordclouds_panel.png'),
                    figsize=fig_config['sizes']['wide'],
                    dpi=fig_config['dpi'],
                    max_words=fig_config['wordcloud']['max_words']
                )
                plot_wordclouds_panel(
                    canonical_df,
                    str(output_figures / 'fig06_wordclouds_panel.pdf'),
                    figsize=fig_config['sizes']['wide'],
                    dpi=fig_config['dpi'],
                    max_words=fig_config['wordcloud']['max_words']
                )
            
            elif fig_name == 'fig07':
                plot_mca_map(
                    canonical_df,
                    str(output_figures / 'fig07_mca_map.png'),
                    seed=seed,
                    figsize=fig_config['sizes']['standard'],
                    dpi=fig_config['dpi']
                )
                plot_mca_map(
                    canonical_df,
                    str(output_figures / 'fig07_mca_map.pdf'),
                    seed=seed,
                    figsize=fig_config['sizes']['standard'],
                    dpi=fig_config['dpi']
                )
            
            elif fig_name == 'fig08':
                plot_fit_trends(
                    canonical_df,
                    str(output_figures / 'fig08_fit_trends.png'),
                    figsize=fig_config['sizes']['wide'],
                    dpi=fig_config['dpi']
                )
                plot_fit_trends(
                    canonical_df,
                    str(output_figures / 'fig08_fit_trends.pdf'),
                    figsize=fig_config['sizes']['wide'],
                    dpi=fig_config['dpi']
                )
            
            elif fig_name == 'fig10':
                # Requires co-occurrence table
                cooccurrence_df = calculate_fit_cooccurrence(canonical_df)
                plot_fit_cooccurrence_heatmap(
                    cooccurrence_df,
                    str(output_figures / 'fig10_fit_cooccurrence_heatmap.png'),
                    figsize=fig_config['sizes']['square'],
                    dpi=fig_config['dpi']
                )
                plot_fit_cooccurrence_heatmap(
                    cooccurrence_df,
                    str(output_figures / 'fig10_fit_cooccurrence_heatmap.pdf'),
                    figsize=fig_config['sizes']['square'],
                    dpi=fig_config['dpi']
                )
    
    # Step 10: Generate tables
    if 'all' in args.make_tables or len(args.make_tables) > 0:
        logger.info("Step 10: Generating tables")
        
        table_list = args.make_tables if 'all' not in args.make_tables else ['tab08', 'tab09']
        
        if 'tab08' in table_list:
            cooccurrence_df = calculate_fit_cooccurrence(canonical_df)
            save_fit_cooccurrence_table(
                cooccurrence_df,
                str(output_tables / 'tab08_fit_cooccurrence.csv')
            )
        
        if 'tab09' in table_list:
            ranking_df = calculate_fit_ranking(canonical_df)
            save_fit_ranking_table(
                ranking_df,
                str(output_tables / 'tab09_fit_ranking.csv')
            )
    
    logger.info("Pipeline completed successfully!")


if __name__ == '__main__':
    main()
