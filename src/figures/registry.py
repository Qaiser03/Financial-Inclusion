"""Figure generation registry and utilities"""

import logging
from pathlib import Path
from typing import Dict, List, Callable, Any

logger = logging.getLogger(__name__)


# Figure registry with metadata
FIGURE_REGISTRY = {
    'fig02': {
        'name': 'Annual Publication Trends',
        'function': 'plot_annual_production',
        'size': 'standard',
        'requires_vosviewer': False,
    },
    'fig03': {
        'name': 'Country Productivity Analysis',
        'function': 'plot_country_productivity',
        'size': 'standard',
        'requires_vosviewer': False,
    },
    'fig04': {
        'name': 'Author Production Over Time',
        'function': 'plot_author_production_over_time',
        'size': 'wide',
        'requires_vosviewer': False,
    },
    'fig05': {
        'name': 'Co-citation Network',
        'function': 'plot_cocitation_network',
        'size': 'square',
        'requires_vosviewer': True,
    },
    'fig06': {
        'name': 'Keyword Wordclouds Panel',
        'function': 'plot_wordclouds_panel',
        'size': 'wide',
        'requires_vosviewer': False,
    },
    'fig07': {
        'name': 'Multiple Correspondence Analysis Map',
        'function': 'plot_mca_map',
        'size': 'square',
        'requires_vosviewer': False,
    },
    'fig08': {
        'name': 'FIT Category Trends',
        'function': 'plot_fit_trends',
        'size': 'wide',
        'requires_vosviewer': False,
    },
    'fig10': {
        'name': 'FIT Co-occurrence Heatmap',
        'function': 'plot_fit_cooccurrence_heatmap',
        'size': 'square',
        'requires_vosviewer': False,
    },
    'fig13': {
        'name': 'Topic Evolution Over Time',
        'function': 'plot_topic_evolution',
        'size': 'wide',
        'requires_vosviewer': False,
        'requires_topic_model': True,
    },
    'fig14': {
        'name': 'Citation Surge Detection',
        'function': 'plot_citation_surge',
        'size': 'wide',
        'requires_vosviewer': False,
    },
    'fig15': {
        'name': 'Co-authorship Network',
        'function': 'plot_coauthorship_network',
        'size': 'large',
        'requires_vosviewer': False,
        'requires_networkx': True,
    },
    'fig16': {
        'name': 'Keyword Co-occurrence Network',
        'function': 'plot_keyword_cooccurrence_network',
        'size': 'large',
        'requires_vosviewer': False,
        'requires_networkx': True,
    },
}


def generate_figure(
    plot_func: Callable,
    data: Any,
    output_dir: Path,
    figure_name: str,
    figure_config: Dict,
    formats: List[str] = ['png', 'pdf'],
    **kwargs
) -> None:
    """
    Generate a figure in multiple formats (PNG, PDF).
    
    This utility function eliminates code duplication by handling both
    PNG and PDF generation in a single call.
    
    Args:
        plot_func: The plotting function to call
        data: Input data (usually DataFrame)
        output_dir: Output directory path
        figure_name: Base figure name (e.g., 'fig02_annual_production')
        figure_config: Figure configuration dict with 'sizes' and 'dpi'
        formats: List of formats to generate ['png', 'pdf']
        **kwargs: Additional arguments passed to plot_func
        
    Example:
        >>> generate_figure(
        ...     plot_func=plot_annual_production,
        ...     data=canonical_df,
        ...     output_dir=output_figures,
        ...     figure_name='fig02_annual_production',
        ...     figure_config={'sizes': {'standard': (10, 6)}, 'dpi': 300},
        ...     figsize=(10, 6)
        ... )
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for fmt in formats:
        try:
            output_path = output_dir / f"{figure_name}.{fmt}"
            plot_func(
                data,
                str(output_path),
                **kwargs
            )
            logger.info(f"Generated {figure_name}.{fmt}")
        except Exception as e:
            logger.error(f"Failed to generate {figure_name}.{fmt}: {e}")
            raise


def get_default_figure_list() -> List[str]:
    """Get list of all available figures (excluding VOSviewer-dependent)"""
    return [
        fig_id for fig_id, meta in FIGURE_REGISTRY.items()
        if not meta['requires_vosviewer']
    ]


def validate_figure_request(requested_figures: List[str]) -> List[str]:
    """
    Validate requested figures against registry.
    
    Args:
        requested_figures: List of figure IDs
        
    Returns:
        List of valid figure IDs
    """
    valid_figures = []
    for fig_id in requested_figures:
        if fig_id == 'all':
            return get_default_figure_list()
        elif fig_id in FIGURE_REGISTRY:
            valid_figures.append(fig_id)
        else:
            logger.warning(f"Unknown figure ID: {fig_id}. Skipping.")
    
    return valid_figures


def get_figure_info(figure_id: str) -> Dict:
    """Get metadata for a specific figure"""
    return FIGURE_REGISTRY.get(figure_id, {})
