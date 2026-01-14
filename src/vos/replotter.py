"""VOSviewer network replotting with deterministic layouts"""

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def create_network_from_vosviewer(
    nodes_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    map_df: Optional[pd.DataFrame] = None
) -> nx.Graph:
    """
    Create NetworkX graph from VOSviewer exports.
    
    Args:
        nodes_df: DataFrame with node information
        edges_df: DataFrame with edge information
        map_df: Optional DataFrame with node positions from map file
        
    Returns:
        NetworkX graph
    """
    G = nx.Graph()
    
    # Add nodes
    for _, node in nodes_df.iterrows():
        node_id = node['id']
        label = node.get('label', str(node_id))
        G.add_node(node_id, label=label)
    
    # Add edges
    for _, edge in edges_df.iterrows():
        source = edge['source']
        target = edge['target']
        weight = edge.get('weight', 1.0)
        G.add_edge(source, target, weight=weight)
    
    # Add positions from map if available
    if map_df is not None and 'x' in map_df.columns and 'y' in map_df.columns:
        for _, row in map_df.iterrows():
            node_id = row.get('id', row.get('node_id'))
            if node_id in G:
                G.nodes[node_id]['x'] = row['x']
                G.nodes[node_id]['y'] = row['y']
                if 'cluster' in row:
                    G.nodes[node_id]['cluster'] = row['cluster']
    
    logger.info(f"Created network with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    return G


def compute_deterministic_layout(
    G: nx.Graph,
    seed: int = 42,
    layout_algorithm: str = 'spring'
) -> dict:
    """
    Compute deterministic node positions.
    
    Args:
        G: NetworkX graph
        seed: Random seed for reproducibility
        layout_algorithm: Layout algorithm ('spring', 'kamada_kawai', 'circular')
        
    Returns:
        Dictionary mapping node_id to (x, y) position
    """
    np.random.seed(seed)
    
    if layout_algorithm == 'spring':
        pos = nx.spring_layout(G, seed=seed, k=1, iterations=50)
    elif layout_algorithm == 'kamada_kawai':
        pos = nx.kamada_kawai_layout(G)
    elif layout_algorithm == 'circular':
        pos = nx.circular_layout(G)
    else:
        # Use existing positions if available
        pos = {}
        for node_id in G.nodes():
            if 'x' in G.nodes[node_id] and 'y' in G.nodes[node_id]:
                pos[node_id] = (G.nodes[node_id]['x'], G.nodes[node_id]['y'])
            else:
                pos[node_id] = (0, 0)
    
    return pos


def plot_network(
    G: nx.Graph,
    pos: dict,
    output_path: str,
    node_size_range: Tuple[int, int] = (50, 500),
    edge_width_range: Tuple[float, float] = (0.5, 3.0),
    figsize: Tuple[int, int] = (12, 10),
    dpi: int = 300
) -> None:
    """
    Plot network with deterministic layout.
    
    Args:
        G: NetworkX graph
        pos: Node positions dictionary
        output_path: Output file path (PNG or PDF)
        node_size_range: (min, max) node sizes
        edge_width_range: (min, max) edge widths
        figsize: Figure size in inches
        dpi: DPI for PNG output
    """
    logger.info(f"Plotting network to {output_path}")
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Calculate node sizes based on degree or weight
    node_sizes = []
    for node_id in G.nodes():
        degree = G.degree(node_id)
        # Normalize to node_size_range
        if G.number_of_nodes() > 1:
            normalized = (degree - min(dict(G.degree()).values())) / (
                max(dict(G.degree()).values()) - min(dict(G.degree()).values()) + 1e-10
            )
        else:
            normalized = 0.5
        size = node_size_range[0] + normalized * (node_size_range[1] - node_size_range[0])
        node_sizes.append(size)
    
    # Calculate edge widths based on weight
    edge_widths = []
    for u, v in G.edges():
        weight = G[u][v].get('weight', 1.0)
        # Normalize to edge_width_range
        if len(edge_widths) > 0:
            max_weight = max([G[u2][v2].get('weight', 1.0) for u2, v2 in G.edges()])
            min_weight = min([G[u2][v2].get('weight', 1.0) for u2, v2 in G.edges()])
            if max_weight > min_weight:
                normalized = (weight - min_weight) / (max_weight - min_weight)
            else:
                normalized = 0.5
        else:
            normalized = 0.5
        width = edge_width_range[0] + normalized * (edge_width_range[1] - edge_width_range[0])
        edge_widths.append(width)
    
    # Draw edges
    nx.draw_networkx_edges(
        G, pos,
        width=edge_widths,
        alpha=0.3,
        edge_color='gray',
        ax=ax
    )
    
    # Draw nodes
    nx.draw_networkx_nodes(
        G, pos,
        node_size=node_sizes,
        node_color='lightblue',
        alpha=0.7,
        ax=ax
    )
    
    # Draw labels (only for important nodes to avoid clutter)
    # Select top nodes by degree
    degrees = dict(G.degree())
    top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:20]
    top_node_ids = {node_id for node_id, _ in top_nodes}
    
    labels = {node_id: G.nodes[node_id].get('label', str(node_id))
              for node_id in top_node_ids}
    
    nx.draw_networkx_labels(
        G, pos,
        labels=labels,
        font_size=8,
        ax=ax
    )
    
    ax.axis('off')
    plt.tight_layout()
    
    # Save
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    if output_path.endswith('.png'):
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    else:
        plt.savefig(output_path, bbox_inches='tight')
    
    plt.close()
    
    logger.info(f"Saved network plot: {output_path}")
