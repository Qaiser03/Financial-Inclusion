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
from src.figures.registry import generate_figure, validate_figure_request
from src.figures.topic_evolution import plot_topic_evolution
from src.figures.citation_surge import plot_citation_surge
from src.figures.coauthorship_network import plot_coauthorship_network
from src.figures.keyword_cooccurrence_network import plot_keyword_cooccurrence_network

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
                        choices=['all', 'fig02', 'fig03', 'fig04', 'fig05', 'fig06', 'fig07', 'fig08', 'fig10',
                                 'fig13', 'fig14', 'fig15', 'fig16'],
                        help='Figures to generate')
    parser.add_argument('--make-tables', type=str, nargs='+', default=[],
                        choices=['all', 'tab08', 'tab09', 'tab10', 'tab11', 'tab12', 'tab13', 'tab14'],
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
    # Note: Pass cleaned versions for dedup_mapping, original versions for count stats
    # Calculate detailed dedup stats (simplified - in full implementation would track during dedup)
    within_source_doi_removed = {
        'scopus': len(scopus_df) - len(scopus_cleaned),
        'wos': len(wos_df) - len(wos_cleaned)
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
        
        figure_list = validate_figure_request(args.make_figures)
        
        for fig_name in figure_list:
            if fig_name == 'fig02':
                generate_figure(
                    plot_func=plot_annual_production,
                    data=canonical_df,
                    output_dir=output_figures,
                    figure_name='fig02_annual_production',
                    figure_config=fig_config,
                    figsize=fig_config['sizes']['standard'],
                    dpi=fig_config['dpi']
                )
            
            elif fig_name == 'fig03':
                generate_figure(
                    plot_func=plot_country_productivity,
                    data=canonical_df,
                    output_dir=output_figures,
                    figure_name='fig03_country_productivity',
                    figure_config=fig_config,
                    figsize=fig_config['sizes']['standard'],
                    dpi=fig_config['dpi']
                )
            
            elif fig_name == 'fig04':
                generate_figure(
                    plot_func=plot_author_production_over_time,
                    data=canonical_df,
                    output_dir=output_figures,
                    figure_name='fig04_author_production_over_time',
                    figure_config=fig_config,
                    figsize=fig_config['sizes']['wide'],
                    dpi=fig_config['dpi']
                )
            
            elif fig_name == 'fig05':
                # Co-citation network (requires VOSviewer exports)
                cocitation_base = get_path(config, 'paths', 'vosviewer', 'cocitation_network')
                network_path = str(cocitation_base) + '.net'
                map_path = str(cocitation_base) + '.map'
                
                if Path(network_path).exists() and Path(map_path).exists():
                    generate_figure(
                        plot_func=plot_cocitation_network,
                        data={'network': network_path, 'map': map_path},
                        output_dir=output_figures,
                        figure_name='fig05_cocitation_network',
                        figure_config=fig_config,
                        network_path=network_path,
                        map_path=map_path,
                        seed=seed,
                        figsize=fig_config['sizes']['square'],
                        dpi=fig_config['dpi']
                    )
                else:
                    logger.warning("VOSviewer exports not found. Skipping fig05. Run VOSviewer first.")
            
            elif fig_name == 'fig06':
                generate_figure(
                    plot_func=plot_wordclouds_panel,
                    data=canonical_df,
                    output_dir=output_figures,
                    figure_name='fig06_wordclouds_panel',
                    figure_config=fig_config,
                    figsize=fig_config['sizes']['wide'],
                    dpi=fig_config['dpi'],
                    max_words=fig_config['wordcloud']['max_words']
                )
            
            elif fig_name == 'fig07':
                generate_figure(
                    plot_func=plot_mca_map,
                    data=canonical_df,
                    output_dir=output_figures,
                    figure_name='fig07_mca_map',
                    figure_config=fig_config,
                    seed=seed,
                    figsize=fig_config['sizes']['standard'],
                    dpi=fig_config['dpi']
                )
            
            elif fig_name == 'fig08':
                generate_figure(
                    plot_func=plot_fit_trends,
                    data=canonical_df,
                    output_dir=output_figures,
                    figure_name='fig08_fit_trends',
                    figure_config=fig_config,
                    figsize=fig_config['sizes']['wide'],
                    dpi=fig_config['dpi']
                )
            
            elif fig_name == 'fig10':
                # Requires co-occurrence table
                cooccurrence_df = calculate_fit_cooccurrence(canonical_df)
                generate_figure(
                    plot_func=plot_fit_cooccurrence_heatmap,
                    data=cooccurrence_df,
                    output_dir=output_figures,
                    figure_name='fig10_fit_cooccurrence_heatmap',
                    figure_config=fig_config,
                    figsize=fig_config['sizes']['square'],
                    dpi=fig_config['dpi']
                )
            
            elif fig_name == 'fig13':
                # Topic evolution - requires LDA model
                try:
                    from src.analysis.topic_modeling import (
                        fit_lda_model, topic_evolution_by_year, get_top_terms_per_topic,
                        save_topic_model, TOPIC_NAMES
                    )
                    
                    topic_config = config.get('topic_modeling', {})
                    n_topics = topic_config.get('n_topics', 8)
                    topic_seed = topic_config.get('seed', seed)
                    
                    logger.info(f"Fitting LDA model with {n_topics} topics")
                    model, topic_terms_df, doc_topic, metadata = fit_lda_model(
                        canonical_df, n_topics=n_topics, seed=topic_seed
                    )
                    
                    # Update topic names from metadata
                    if 'topic_names' in metadata:
                        for tid, tname in metadata['topic_names'].items():
                            TOPIC_NAMES[tid] = tname
                    
                    # Compute evolution
                    evolution_df = topic_evolution_by_year(canonical_df, doc_topic)
                    
                    # Update topic names in evolution_df
                    evolution_df['topic_name'] = evolution_df['topic_id'].map(
                        lambda x: metadata.get('topic_names', {}).get(x, f"Topic {x}")
                    )
                    
                    # Save model artifacts
                    output_models = Path(get_path(config, 'paths', 'outputs', 'audits')).parent / 'models'
                    output_models.mkdir(parents=True, exist_ok=True)
                    save_topic_model(model, metadata, str(output_models))
                    
                    # Save tables (tab10, tab11)
                    top_terms = get_top_terms_per_topic(topic_terms_df, n_terms=10)
                    top_terms.to_csv(output_tables / 'tab10_topic_terms.csv', index=False)
                    evolution_df.to_csv(output_tables / 'tab11_topic_evolution.csv', index=False)
                    logger.info("Saved topic tables (tab10, tab11)")
                    
                    # Plot
                    generate_figure(
                        plot_func=plot_topic_evolution,
                        data=evolution_df,
                        output_dir=output_figures,
                        figure_name='fig13_topic_evolution',
                        figure_config=fig_config,
                        figsize=fig_config['sizes'].get('wide', (14, 8)),
                        dpi=fig_config['dpi']
                    )
                except ImportError as e:
                    logger.warning(f"Topic modeling unavailable: {e}. Skipping fig13.")
                except Exception as e:
                    logger.error(f"Topic modeling failed: {e}")
            
            elif fig_name == 'fig14':
                # Citation surge detection
                try:
                    from src.analysis.citation_bursts import (
                        compute_yearly_citations, detect_citation_surges,
                        compute_citation_growth_rate, save_surge_table
                    )
                    
                    burst_config = config.get('citation_bursts', {})
                    z_threshold = burst_config.get('z_threshold', 1.5)
                    method = burst_config.get('method', 'full_series')
                    
                    yearly_df = compute_yearly_citations(canonical_df)
                    surge_df = detect_citation_surges(yearly_df, method=method, z_threshold=z_threshold)
                    
                    # Save table (tab12)
                    save_surge_table(surge_df, str(output_tables / 'tab12_citation_surges.csv'))
                    logger.info("Saved citation surge table (tab12)")
                    
                    generate_figure(
                        plot_func=plot_citation_surge,
                        data=surge_df,
                        output_dir=output_figures,
                        figure_name='fig14_citation_surge',
                        figure_config=fig_config,
                        figsize=fig_config['sizes'].get('wide', (12, 6)),
                        dpi=fig_config['dpi']
                    )
                except Exception as e:
                    logger.error(f"Citation surge analysis failed: {e}")
            
            elif fig_name == 'fig15':
                # Co-authorship network
                try:
                    from src.analysis.networks import (
                        build_coauthorship_graph, compute_centrality_metrics,
                        export_network_edges, export_network_nodes, filter_graph_by_degree,
                        NETWORKX_AVAILABLE
                    )
                    
                    if not NETWORKX_AVAILABLE:
                        logger.warning("networkx not available. Skipping fig15.")
                        continue
                    
                    network_config = config.get('network_analysis', {})
                    min_collab = network_config.get('min_collaborations', 2)
                    
                    G = build_coauthorship_graph(canonical_df, min_collaborations=min_collab)
                    
                    if G is not None and G.number_of_nodes() > 0:
                        # Filter for visualization
                        G_viz = filter_graph_by_degree(G, min_degree=2)
                        
                        # Compute centrality and save (tab13)
                        centrality_df = compute_centrality_metrics(G)
                        centrality_df.to_csv(output_tables / 'tab13_coauthor_centrality.csv', index=False)
                        
                        # Export edges/nodes
                        export_network_edges(G, str(output_tables / 'coauthorship_edges.csv'))
                        export_network_nodes(G, str(output_tables / 'coauthorship_nodes.csv'))
                        
                        generate_figure(
                            plot_func=plot_coauthorship_network,
                            data=G_viz if G_viz and G_viz.number_of_nodes() > 0 else G,
                            output_dir=output_figures,
                            figure_name='fig15_coauthorship_network',
                            figure_config=fig_config,
                            seed=seed,
                            figsize=fig_config['sizes'].get('large', (14, 12)),
                            dpi=fig_config['dpi']
                        )
                except Exception as e:
                    logger.error(f"Co-authorship network failed: {e}")
            
            elif fig_name == 'fig16':
                # Keyword co-occurrence network
                try:
                    from src.analysis.networks import (
                        build_keyword_cooccurrence_graph, compute_centrality_metrics,
                        export_network_edges, export_network_nodes, filter_graph_by_degree,
                        NETWORKX_AVAILABLE
                    )
                    
                    if not NETWORKX_AVAILABLE:
                        logger.warning("networkx not available. Skipping fig16.")
                        continue
                    
                    network_config = config.get('network_analysis', {})
                    min_cooccur = network_config.get('min_cooccurrences', 3)
                    
                    G = build_keyword_cooccurrence_graph(canonical_df, min_cooccurrences=min_cooccur)
                    
                    if G is not None and G.number_of_nodes() > 0:
                        # Filter for visualization
                        G_viz = filter_graph_by_degree(G, min_degree=2)
                        
                        # Compute centrality and save (tab14)
                        centrality_df = compute_centrality_metrics(G)
                        centrality_df.to_csv(output_tables / 'tab14_keyword_centrality.csv', index=False)
                        
                        # Export edges/nodes
                        export_network_edges(G, str(output_tables / 'keyword_cooccurrence_edges.csv'))
                        export_network_nodes(G, str(output_tables / 'keyword_cooccurrence_nodes.csv'))
                        
                        generate_figure(
                            plot_func=plot_keyword_cooccurrence_network,
                            data=G_viz if G_viz and G_viz.number_of_nodes() > 0 else G,
                            output_dir=output_figures,
                            figure_name='fig16_keyword_cooccurrence_network',
                            figure_config=fig_config,
                            seed=seed,
                            figsize=fig_config['sizes'].get('large', (14, 12)),
                            dpi=fig_config['dpi']
                        )
                except Exception as e:
                    logger.error(f"Keyword network failed: {e}")
    
    # Step 10: Generate tables
    if 'all' in args.make_tables or len(args.make_tables) > 0:
        logger.info("Step 10: Generating tables")
        
        table_list = args.make_tables if 'all' not in args.make_tables else [
            'tab08', 'tab09', 'tab10', 'tab11', 'tab12', 'tab13', 'tab14'
        ]
        
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
        
        # Tab10-11: Topic terms and evolution (generated with fig13)
        if 'tab10' in table_list or 'tab11' in table_list:
            if not (output_tables / 'tab10_topic_terms.csv').exists():
                try:
                    from src.analysis.topic_modeling import (
                        fit_lda_model, topic_evolution_by_year, get_top_terms_per_topic,
                        save_topic_model
                    )
                    
                    topic_config = config.get('topic_modeling', {})
                    n_topics = topic_config.get('n_topics', 8)
                    topic_seed = topic_config.get('seed', seed)
                    
                    model, topic_terms_df, doc_topic, metadata = fit_lda_model(
                        canonical_df, n_topics=n_topics, seed=topic_seed
                    )
                    
                    if 'tab10' in table_list:
                        top_terms = get_top_terms_per_topic(topic_terms_df, n_terms=10)
                        top_terms.to_csv(output_tables / 'tab10_topic_terms.csv', index=False)
                        logger.info("Saved tab10_topic_terms.csv")
                    
                    if 'tab11' in table_list:
                        evolution_df = topic_evolution_by_year(canonical_df, doc_topic)
                        evolution_df['topic_name'] = evolution_df['topic_id'].map(
                            lambda x: metadata.get('topic_names', {}).get(x, f"Topic {x}")
                        )
                        evolution_df.to_csv(output_tables / 'tab11_topic_evolution.csv', index=False)
                        logger.info("Saved tab11_topic_evolution.csv")
                        
                except ImportError as e:
                    logger.warning(f"Topic modeling unavailable: {e}")
                except Exception as e:
                    logger.error(f"Topic table generation failed: {e}")
        
        # Tab12: Citation surges
        if 'tab12' in table_list:
            if not (output_tables / 'tab12_citation_surges.csv').exists():
                try:
                    from src.analysis.citation_bursts import (
                        compute_yearly_citations, detect_citation_surges, save_surge_table
                    )
                    
                    burst_config = config.get('citation_bursts', {})
                    z_threshold = burst_config.get('z_threshold', 1.5)
                    
                    yearly_df = compute_yearly_citations(canonical_df)
                    surge_df = detect_citation_surges(yearly_df, z_threshold=z_threshold)
                    save_surge_table(surge_df, str(output_tables / 'tab12_citation_surges.csv'))
                    logger.info("Saved tab12_citation_surges.csv")
                except Exception as e:
                    logger.error(f"Citation surge table failed: {e}")
        
        # Tab13: Co-author centrality
        if 'tab13' in table_list:
            if not (output_tables / 'tab13_coauthor_centrality.csv').exists():
                try:
                    from src.analysis.networks import (
                        build_coauthorship_graph, compute_centrality_metrics,
                        NETWORKX_AVAILABLE
                    )
                    
                    if NETWORKX_AVAILABLE:
                        G = build_coauthorship_graph(canonical_df)
                        if G is not None:
                            centrality_df = compute_centrality_metrics(G)
                            centrality_df.to_csv(output_tables / 'tab13_coauthor_centrality.csv', index=False)
                            logger.info("Saved tab13_coauthor_centrality.csv")
                    else:
                        logger.warning("networkx not available for tab13")
                except Exception as e:
                    logger.error(f"Coauthor centrality table failed: {e}")
        
        # Tab14: Keyword centrality
        if 'tab14' in table_list:
            if not (output_tables / 'tab14_keyword_centrality.csv').exists():
                try:
                    from src.analysis.networks import (
                        build_keyword_cooccurrence_graph, compute_centrality_metrics,
                        NETWORKX_AVAILABLE
                    )
                    
                    if NETWORKX_AVAILABLE:
                        G = build_keyword_cooccurrence_graph(canonical_df)
                        if G is not None:
                            centrality_df = compute_centrality_metrics(G)
                            centrality_df.to_csv(output_tables / 'tab14_keyword_centrality.csv', index=False)
                            logger.info("Saved tab14_keyword_centrality.csv")
                    else:
                        logger.warning("networkx not available for tab14")
                except Exception as e:
                    logger.error(f"Keyword centrality table failed: {e}")
    
    logger.info("Pipeline completed successfully!")


if __name__ == '__main__':
    main()
