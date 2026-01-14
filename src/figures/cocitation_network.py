"""Co-citation network figure (fig05) - from VOSviewer exports"""

import pandas as pd
from pathlib import Path
import logging
from src.vos.importer import load_vosviewer_network, load_vosviewer_map
from src.vos.replotter import create_network_from_vosviewer, compute_deterministic_layout, plot_network

logger = logging.getLogger(__name__)


def plot_cocitation_network(
    network_path: str,
    map_path: str,
    output_path: str,
    seed: int = 42,
    figsize: tuple = (12, 10),
    dpi: int = 300
) -> None:
    """
    Plot co-citation network from VOSviewer exports.
    
    Args:
        network_path: Path to VOSviewer .net file
        map_path: Path to VOSviewer .map file
        output_path: Output file path
        seed: Random seed for layout
        figsize: Figure size in inches
        dpi: DPI for PNG output
    """
    logger.info("Generating co-citation network figure from VOSviewer exports")
    
    # Load VOSviewer exports
    nodes_df, edges_df = load_vosviewer_network(network_path)
    map_df = load_vosviewer_map(map_path)
    
    # Create network
    G = create_network_from_vosviewer(nodes_df, edges_df, map_df)
    
    # Compute deterministic layout
    pos = compute_deterministic_layout(G, seed=seed, layout_algorithm='spring')
    
    # Plot
    plot_network(
        G, pos, output_path,
        node_size_range=(50, 500),
        edge_width_range=(0.5, 3.0),
        figsize=figsize,
        dpi=dpi
    )
    
    logger.info(f"Saved co-citation network figure: {output_path}")
