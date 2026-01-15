"""Co-authorship network figure (fig15)"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Check for networkx
NETWORKX_AVAILABLE = False
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    pass


def plot_coauthorship_network(
    G: Any,
    output_path: str,
    seed: int = 42,
    figsize: tuple = (14, 12),
    dpi: int = 300,
    max_nodes: int = 100,
    node_size_range: tuple = (50, 500),
    edge_width_range: tuple = (0.5, 3.0),
    show_labels: bool = True,
    min_label_degree: int = 3
) -> None:
    """
    Plot co-authorship network visualization.
    
    Args:
        G: networkx Graph from build_coauthorship_graph
        output_path: Output file path
        seed: Random seed for layout
        figsize: Figure size in inches
        dpi: DPI for PNG output
        max_nodes: Maximum nodes to display (filters by degree)
        node_size_range: (min, max) node size based on degree
        edge_width_range: (min, max) edge width based on weight
        show_labels: Whether to show node labels
        min_label_degree: Minimum degree to show label
    """
    if not NETWORKX_AVAILABLE:
        logger.warning("networkx not available, skipping co-authorship network plot")
        return
    
    if G is None or G.number_of_nodes() == 0:
        logger.warning("No network data available")
        return
    
    logger.info("Generating co-authorship network figure")
    
    # Filter to top nodes by degree if too many
    if G.number_of_nodes() > max_nodes:
        degrees = dict(G.degree())
        top_nodes = sorted(degrees.keys(), key=lambda x: degrees[x], reverse=True)[:max_nodes]
        G = G.subgraph(top_nodes).copy()
    
    if G.number_of_nodes() == 0:
        logger.warning("No nodes after filtering")
        return
    
    # Compute layout with seed
    np.random.seed(seed)
    pos = nx.spring_layout(G, k=2/np.sqrt(G.number_of_nodes()), 
                           iterations=50, seed=seed)
    
    # Node sizes based on degree
    degrees = dict(G.degree())
    max_degree = max(degrees.values()) if degrees else 1
    min_degree = min(degrees.values()) if degrees else 1
    
    def scale_size(degree):
        if max_degree == min_degree:
            return (node_size_range[0] + node_size_range[1]) / 2
        ratio = (degree - min_degree) / (max_degree - min_degree)
        return node_size_range[0] + ratio * (node_size_range[1] - node_size_range[0])
    
    node_sizes = [scale_size(degrees[n]) for n in G.nodes()]
    
    # Edge widths based on weight
    edge_weights = [G[u][v].get('weight', 1) for u, v in G.edges()]
    if edge_weights:
        max_weight = max(edge_weights)
        min_weight = min(edge_weights)
        
        def scale_width(weight):
            if max_weight == min_weight:
                return (edge_width_range[0] + edge_width_range[1]) / 2
            ratio = (weight - min_weight) / (max_weight - min_weight)
            return edge_width_range[0] + ratio * (edge_width_range[1] - edge_width_range[0])
        
        edge_widths = [scale_width(w) for w in edge_weights]
    else:
        edge_widths = [1]
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Draw edges
    nx.draw_networkx_edges(
        G, pos, ax=ax,
        width=edge_widths,
        alpha=0.3,
        edge_color='gray'
    )
    
    # Draw nodes
    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_size=node_sizes,
        node_color='steelblue',
        alpha=0.7,
        edgecolors='white',
        linewidths=1
    )
    
    # Draw labels for high-degree nodes
    if show_labels:
        labels = {n: n for n in G.nodes() if degrees[n] >= min_label_degree}
        if labels:
            nx.draw_networkx_labels(
                G, pos, labels, ax=ax,
                font_size=8,
                font_weight='bold'
            )
    
    ax.set_title(f'Co-authorship Network\n({G.number_of_nodes()} authors, {G.number_of_edges()} collaborations)',
                 fontsize=14, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    
    # Save
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    if output_path.endswith('.png'):
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    else:
        plt.savefig(output_path, bbox_inches='tight', facecolor='white')
    
    plt.close()
    
    logger.info(f"Saved co-authorship network figure: {output_path}")
