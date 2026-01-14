"""Wordclouds panel figure (fig06)"""

import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def plot_wordclouds_panel(
    df: pd.DataFrame,
    output_path: str,
    figsize: tuple = (16, 8),
    dpi: int = 300,
    max_words: int = 100
) -> None:
    """
    Plot panel of wordclouds (title, abstract, keywords).
    
    Args:
        df: Canonical DataFrame with text fields
        output_path: Output file path
        figsize: Figure size in inches
        dpi: DPI for PNG output
        max_words: Maximum number of words in wordcloud
    """
    logger.info("Generating wordclouds panel")
    
    # Combine text from different fields
    title_text = ' '.join(df['title_raw'].dropna().astype(str))
    abstract_text = ' '.join(df['abstract_raw'].dropna().astype(str))
    keywords_text = ' '.join(df['keywords_raw'].dropna().astype(str))
    
    # Create figure with subplots
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    
    # Title wordcloud
    if title_text:
        wc_title = WordCloud(width=800, height=400, max_words=max_words, background_color='white').generate(title_text)
        axes[0].imshow(wc_title, interpolation='bilinear')
        axes[0].axis('off')
        axes[0].set_title('Titles', fontsize=14, fontweight='bold')
    
    # Abstract wordcloud
    if abstract_text:
        wc_abstract = WordCloud(width=800, height=400, max_words=max_words, background_color='white').generate(abstract_text)
        axes[1].imshow(wc_abstract, interpolation='bilinear')
        axes[1].axis('off')
        axes[1].set_title('Abstracts', fontsize=14, fontweight='bold')
    
    # Keywords wordcloud
    if keywords_text:
        wc_keywords = WordCloud(width=800, height=400, max_words=max_words, background_color='white').generate(keywords_text)
        axes[2].imshow(wc_keywords, interpolation='bilinear')
        axes[2].axis('off')
        axes[2].set_title('Keywords', fontsize=14, fontweight='bold')
    
    plt.suptitle('Word Clouds: Titles, Abstracts, and Keywords', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # Save
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    if output_path.endswith('.png'):
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    else:
        plt.savefig(output_path, bbox_inches='tight')
    
    plt.close()
    
    logger.info(f"Saved wordclouds panel: {output_path}")
