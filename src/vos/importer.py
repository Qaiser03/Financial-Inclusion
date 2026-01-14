"""VOSviewer export import modules"""

import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def load_vosviewer_network(network_path: str) -> pd.DataFrame:
    """
    Load VOSviewer network file (.net format).
    
    VOSviewer .net format is Pajek format:
    *Vertices N
    1 "Node1" ...
    *Edges
    1 2 weight
    
    Args:
        network_path: Path to .net file
        
    Returns:
        DataFrame with nodes and edges
    """
    logger.info(f"Loading VOSviewer network from {network_path}")
    
    network_file = Path(network_path)
    if not network_file.exists():
        raise FileNotFoundError(f"Network file not found: {network_path}")
    
    nodes = []
    edges = []
    
    with open(network_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Parse vertices
    in_vertices = False
    in_edges = False
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('*Vertices'):
            in_vertices = True
            in_edges = False
            continue
        
        if line.startswith('*Edges') or line.startswith('*Arcs'):
            in_vertices = False
            in_edges = True
            continue
        
        if in_vertices and line:
            # Parse vertex: id "label" [attributes]
            parts = line.split('"')
            if len(parts) >= 2:
                node_id = parts[0].strip()
                node_label = parts[1].strip()
                nodes.append({
                    'id': int(node_id),
                    'label': node_label,
                })
        
        if in_edges and line:
            # Parse edge: source target weight
            parts = line.split()
            if len(parts) >= 2:
                source = int(parts[0])
                target = int(parts[1])
                weight = float(parts[2]) if len(parts) > 2 else 1.0
                edges.append({
                    'source': source,
                    'target': target,
                    'weight': weight,
                })
    
    nodes_df = pd.DataFrame(nodes)
    edges_df = pd.DataFrame(edges)
    
    logger.info(f"Loaded {len(nodes_df)} nodes and {len(edges_df)} edges")
    
    return nodes_df, edges_df


def load_vosviewer_map(map_path: str) -> pd.DataFrame:
    """
    Load VOSviewer map file (.map format).
    
    Map file contains node positions and cluster assignments.
    Format: tab-delimited with columns like:
    id, label, x, y, cluster, ...
    
    Args:
        map_path: Path to .map file
        
    Returns:
        DataFrame with node positions and attributes
    """
    logger.info(f"Loading VOSviewer map from {map_path}")
    
    map_file = Path(map_path)
    if not map_file.exists():
        raise FileNotFoundError(f"Map file not found: {map_path}")
    
    # Try to read as tab-delimited
    try:
        map_df = pd.read_csv(map_file, sep='\t', encoding='utf-8')
    except:
        # Try comma-delimited
        map_df = pd.read_csv(map_file, encoding='utf-8')
    
    logger.info(f"Loaded map with {len(map_df)} nodes")
    
    return map_df
