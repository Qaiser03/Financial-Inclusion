"""Keyword co-occurrence network figure (fig16)"""

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


def plot_keyword_cooccurrence_network(
    G: Any,
    output_path: str,
    seed: int = 42,
    figsize: tuple = (14, 12),
    dpi: int = 300,
    max_nodes: int = 80,
    node_size_range: tuple = (100, 800),
    edge_width_range: tuple = (0.5, 4.0),
    show_labels: bool = True,
    min_label_count: int = 5,
    colormap: str = 'viridis'
) -> None:
    """
    Plot keyword co-occurrence network visualization.
    
    Args:
        G: networkx Graph from build_keyword_cooccurrence_graph
        output_path: Output file path
        seed: Random seed for layout
        figsize: Figure size in inches
        dpi: DPI for PNG output
        max_nodes: Maximum nodes to display
        node_size_range: (min, max) node size based on frequency
        edge_width_range: (min, max) edge width based on co-occurrence count
        show_labels: Whether to show node labels
        min_label_count: Minimum frequency to show label
        colormap: Matplotlib colormap for nodes
    """
    if not NETWORKX_AVAILABLE:
        logger.warning("networkx not available, skipping keyword network plot")
        return
    
    if G is None or G.number_of_nodes() == 0:
        logger.warning("No network data available")
        return
    
    logger.info("Generating keyword co-occurrence network figure")
    
    # Filter to top nodes by degree/count if too many
    if G.number_of_nodes() > max_nodes:
        # Use node count attribute if available, else degree
        if 'count' in next(iter(G.nodes(data=True)))[1]:
            counts = {n: G.nodes[n].get('count', 0) for n in G.nodes()}
        else:
            counts = dict(G.degree())
        
        top_nodes = sorted(counts.keys(), key=lambda x: counts[x], reverse=True)[:max_nodes]
        G = G.subgraph(top_nodes).copy()
    
    if G.number_of_nodes() == 0:
        logger.warning("No nodes after filtering")
        return
    
    # Compute layout with seed
    np.random.seed(seed)
    pos = nx.spring_layout(G, k=2.5/np.sqrt(G.number_of_nodes()), 
                           iterations=50, seed=seed)
    
    # Node sizes based on count/degree
    if 'count' in next(iter(G.nodes(data=True)))[1]:
        counts = {n: G.nodes[n].get('count', 1) for n in G.nodes()}
    else:
        counts = dict(G.degree())
    
    max_count = max(counts.values()) if counts else 1
    min_count = min(counts.values()) if counts else 1
    
    def scale_size(count):
        if max_count == min_count:
            return (node_size_range[0] + node_size_range[1]) / 2
        ratio = (count - min_count) / (max_count - min_count)
        return node_size_range[0] + ratio * (node_size_range[1] - node_size_range[0])
    
    node_sizes = [scale_size(counts[n]) for n in G.nodes()]
    node_colors = [counts[n] for n in G.nodes()]
    
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
        alpha=0.25,
        edge_color='gray'
    )
    
    # Draw nodes with color based on frequency
    nodes = nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_size=node_sizes,
        node_color=node_colors,
        cmap=plt.cm.get_cmap(colormap),
        alpha=0.8,
        edgecolors='white',
        linewidths=1.5
    )
    
    # Add colorbar
    cbar = plt.colorbar(nodes, ax=ax, shrink=0.6)
    cbar.set_label('Keyword Frequency', fontsize=10)
    
    # Draw labels
    if show_labels:
        labels = {n: n.title() for n in G.nodes() if counts[n] >= min_label_count}
        if labels:
            nx.draw_networkx_labels(
                G, pos, labels, ax=ax,
                font_size=7,
                font_weight='bold',
                font_color='black'
            )
    
    ax.set_title(f'Keyword Co-occurrence Network\n({G.number_of_nodes()} keywords, {G.number_of_edges()} connections)',
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
    
    logger.info(f"Saved keyword co-occurrence network figure: {output_path}")
