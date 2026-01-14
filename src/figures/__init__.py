"""Figure generation modules

This package contains all visualization and figure generation code for the 
Financial Inclusion bibliometric analysis.

Key modules:
- registry.py: Central figure registry and helper utilities to eliminate duplication
- annual_production.py: Publication trends over time
- country_productivity.py: Geographic analysis by country
- author_production.py: Author output trends
- cocitation_network.py: Citation network visualization (requires VOSviewer)
- wordclouds.py: Keyword frequency visualization
- mca_map.py: Multiple Correspondence Analysis mapping
- fit_trends.py: Financial Inclusion Tool category trends
- fit_cooccurrence.py: FIT category co-occurrence analysis

Usage:
    from src.figures.registry import generate_figure, FIGURE_REGISTRY
    
    # Generate figure in both PNG and PDF
    generate_figure(
        plot_func=plot_annual_production,
        data=canonical_df,
        output_dir='outputs/figures',
        figure_name='fig02_annual_production',
        figure_config={'sizes': {...}, 'dpi': 300},
        figsize=(10, 6)
    )

Refactoring Note:
    The registry.py module was added to eliminate ~150 lines of duplicate 
    code for PNG/PDF generation. Each figure previously required two 
    nearly-identical function calls.
"""

