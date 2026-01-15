"""Network analysis for co-authorship and keyword co-occurrence.

Builds network graphs and computes centrality metrics using networkx.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

# Check for networkx
NETWORKX_AVAILABLE = False
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    logger.warning("networkx not available. Network analysis will be skipped.")


def _parse_delimited(
    value: str,
    delimiters: List[str] = [';']
) -> List[str]:
    """Parse delimited string into list of cleaned items."""
    if pd.isna(value) or not str(value).strip():
        return []
    
    text = str(value)
    
    # Use first delimiter that exists
    for delim in delimiters:
        if delim in text:
            items = text.split(delim)
            break
    else:
        items = [text]
    
    # Clean items
    result = []
    for item in items:
        cleaned = item.strip()
        if cleaned and len(cleaned) > 1:
            result.append(cleaned)
    
    return result


def build_coauthorship_graph(
    df: pd.DataFrame,
    author_field: str = 'authors_raw',
    min_collaborations: int = 1,
    normalize_names: bool = True
) -> Optional[Any]:
    """
    Build co-authorship network graph.
    
    Creates edges between authors who have co-authored papers together.
    Edge weights represent number of collaborations.
    
    Args:
        df: DataFrame with author data
        author_field: Column containing author names (semicolon-separated)
        min_collaborations: Minimum collaborations to include edge
        normalize_names: Whether to normalize author names
        
    Returns:
        networkx.Graph or None if networkx unavailable
    """
    if not NETWORKX_AVAILABLE:
        logger.warning("networkx not available, skipping co-authorship network")
        return None
    
    logger.info("Building co-authorship network")
    
    if author_field not in df.columns:
        logger.warning(f"Author field '{author_field}' not found")
        return None
    
    # Count collaborations
    collab_counts: Dict[Tuple[str, str], int] = defaultdict(int)
    author_pubs: Dict[str, int] = defaultdict(int)
    
    for _, row in df.iterrows():
        authors = _parse_delimited(row.get(author_field, ''), [';', ','])
        
        if normalize_names:
            authors = [a.title() for a in authors]
        
        # Count publications per author
        for author in authors:
            author_pubs[author] += 1
        
        # Count collaborations (all pairs)
        for i, author1 in enumerate(authors):
            for author2 in authors[i+1:]:
                # Sort to ensure consistent edge keys
                edge = tuple(sorted([author1, author2]))
                collab_counts[edge] += 1
    
    # Build graph
    G = nx.Graph()
    
    # Add nodes with publication count attribute
    for author, pubs in author_pubs.items():
        G.add_node(author, publications=pubs)
    
    # Add edges
    for (author1, author2), weight in collab_counts.items():
        if weight >= min_collaborations:
            G.add_edge(author1, author2, weight=weight)
    
    logger.info(f"Built co-authorship network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


def build_keyword_cooccurrence_graph(
    df: pd.DataFrame,
    keyword_field: str = 'keywords_raw',
    min_cooccurrences: int = 2,
    normalize_keywords: bool = True
) -> Optional[Any]:
    """
    Build keyword co-occurrence network graph.
    
    Creates edges between keywords that appear together in documents.
    
    Args:
        df: DataFrame with keyword data
        keyword_field: Column containing keywords (semicolon-separated)
        min_cooccurrences: Minimum co-occurrences to include edge
        normalize_keywords: Whether to normalize keyword case
        
    Returns:
        networkx.Graph or None if networkx unavailable
    """
    if not NETWORKX_AVAILABLE:
        logger.warning("networkx not available, skipping keyword network")
        return None
    
    logger.info("Building keyword co-occurrence network")
    
    if keyword_field not in df.columns:
        logger.warning(f"Keyword field '{keyword_field}' not found")
        return None
    
    # Count co-occurrences
    cooccur_counts: Dict[Tuple[str, str], int] = defaultdict(int)
    keyword_counts: Dict[str, int] = defaultdict(int)
    
    for _, row in df.iterrows():
        keywords = _parse_delimited(row.get(keyword_field, ''), [';', ','])
        
        if normalize_keywords:
            keywords = [k.lower().strip() for k in keywords]
            keywords = list(set(keywords))  # Remove duplicates within document
        
        # Count keyword occurrences
        for kw in keywords:
            keyword_counts[kw] += 1
        
        # Count co-occurrences
        for i, kw1 in enumerate(keywords):
            for kw2 in keywords[i+1:]:
                edge = tuple(sorted([kw1, kw2]))
                cooccur_counts[edge] += 1
    
    # Build graph
    G = nx.Graph()
    
    # Add nodes with count attribute
    for keyword, count in keyword_counts.items():
        G.add_node(keyword, count=count)
    
    # Add edges
    for (kw1, kw2), weight in cooccur_counts.items():
        if weight >= min_cooccurrences:
            G.add_edge(kw1, kw2, weight=weight)
    
    logger.info(f"Built keyword network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


def compute_centrality_metrics(
    G: Any,
    top_n: int = 50
) -> pd.DataFrame:
    """
    Compute centrality metrics for network nodes.
    
    Args:
        G: networkx Graph
        top_n: Number of top nodes to return
        
    Returns:
        DataFrame with node, degree, betweenness, closeness, eigenvector
    """
    if not NETWORKX_AVAILABLE or G is None:
        return pd.DataFrame()
    
    logger.info("Computing centrality metrics")
    
    if G.number_of_nodes() == 0:
        return pd.DataFrame()
    
    # Compute centralities
    degree_cent = nx.degree_centrality(G)
    
    # Betweenness can be slow for large graphs
    if G.number_of_nodes() < 5000:
        betweenness_cent = nx.betweenness_centrality(G)
    else:
        betweenness_cent = {n: 0 for n in G.nodes()}
        logger.warning("Graph too large, skipping betweenness centrality")
    
    # Closeness
    closeness_cent = nx.closeness_centrality(G)
    
    # Eigenvector (may fail for disconnected graphs)
    try:
        eigenvector_cent = nx.eigenvector_centrality(G, max_iter=1000)
    except:
        eigenvector_cent = {n: 0 for n in G.nodes()}
    
    # Build DataFrame
    records = []
    for node in G.nodes():
        records.append({
            'node': node,
            'degree': G.degree(node),
            'degree_centrality': round(degree_cent.get(node, 0), 4),
            'betweenness_centrality': round(betweenness_cent.get(node, 0), 4),
            'closeness_centrality': round(closeness_cent.get(node, 0), 4),
            'eigenvector_centrality': round(eigenvector_cent.get(node, 0), 4),
        })
    
    df = pd.DataFrame(records)
    df = df.sort_values('degree', ascending=False).head(top_n).reset_index(drop=True)
    
    return df


def export_network_edges(
    G: Any,
    output_path: str
) -> None:
    """
    Export network edges to CSV.
    
    Args:
        G: networkx Graph
        output_path: Output file path
    """
    if not NETWORKX_AVAILABLE or G is None:
        return
    
    edges = []
    for u, v, data in G.edges(data=True):
        edges.append({
            'source': u,
            'target': v,
            'weight': data.get('weight', 1)
        })
    
    df = pd.DataFrame(edges)
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    logger.info(f"Exported {len(edges)} edges to {output_path}")


def export_network_nodes(
    G: Any,
    output_path: str
) -> None:
    """
    Export network nodes to CSV.
    
    Args:
        G: networkx Graph
        output_path: Output file path
    """
    if not NETWORKX_AVAILABLE or G is None:
        return
    
    nodes = []
    for node, data in G.nodes(data=True):
        record = {'node': node}
        record.update(data)
        record['degree'] = G.degree(node)
        nodes.append(record)
    
    df = pd.DataFrame(nodes)
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    logger.info(f"Exported {len(nodes)} nodes to {output_path}")


def get_largest_component(G: Any) -> Any:
    """
    Get the largest connected component of a graph.
    
    Args:
        G: networkx Graph
        
    Returns:
        Subgraph of largest connected component
    """
    if not NETWORKX_AVAILABLE or G is None:
        return None
    
    if G.number_of_nodes() == 0:
        return G
    
    components = list(nx.connected_components(G))
    if not components:
        return G
    
    largest = max(components, key=len)
    return G.subgraph(largest).copy()


def filter_graph_by_degree(G: Any, min_degree: int = 2) -> Any:
    """
    Filter graph to only include nodes with minimum degree.
    
    Args:
        G: networkx Graph
        min_degree: Minimum node degree to keep
        
    Returns:
        Filtered graph
    """
    if not NETWORKX_AVAILABLE or G is None:
        return None
    
    nodes_to_keep = [n for n, d in G.degree() if d >= min_degree]
    return G.subgraph(nodes_to_keep).copy()
