"""Topic modeling with LDA and thematic evolution analysis.

Implements Latent Dirichlet Allocation (LDA) for topic discovery
with fallback support for both gensim and scikit-learn.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import logging
import re
import pickle

logger = logging.getLogger(__name__)

# Check for optional dependencies
GENSIM_AVAILABLE = False
SKLEARN_LDA_AVAILABLE = False

try:
    import gensim
    from gensim import corpora
    from gensim.models import LdaModel
    GENSIM_AVAILABLE = True
except ImportError:
    pass

try:
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.decomposition import LatentDirichletAllocation
    SKLEARN_LDA_AVAILABLE = True
except ImportError:
    pass


# Topic name mapping based on top terms (will be populated during fitting)
TOPIC_NAMES = {
    0: "Digital Financial Services",
    1: "Microfinance & Credit",
    2: "Mobile Banking",
    3: "Financial Literacy",
    4: "Regulatory Framework",
    5: "Blockchain & Fintech",
    6: "Rural Development",
    7: "Payment Systems",
}


def preprocess_text(text: str, min_word_length: int = 3) -> List[str]:
    """
    Preprocess text for topic modeling.
    
    Args:
        text: Raw text string
        min_word_length: Minimum word length to keep
        
    Returns:
        List of preprocessed tokens
    """
    if pd.isna(text) or not str(text).strip():
        return []
    
    text = str(text).lower()
    
    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    # Tokenize
    tokens = text.split()
    
    # Filter by length and remove common stopwords
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them', 'their',
        'we', 'our', 'you', 'your', 'he', 'she', 'his', 'her', 'who', 'which',
        'what', 'where', 'when', 'why', 'how', 'all', 'each', 'every', 'both',
        'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
        'only', 'same', 'so', 'than', 'too', 'very', 'just', 'also', 'now',
        'study', 'paper', 'research', 'analysis', 'results', 'using', 'based',
        'new', 'article', 'review', 'approach', 'method', 'model', 'data',
    }
    
    tokens = [t for t in tokens if len(t) >= min_word_length and t not in stopwords]
    
    return tokens


def prepare_corpus(
    df: pd.DataFrame,
    text_fields: List[str] = ['title_raw', 'abstract_raw', 'keywords_raw']
) -> Tuple[List[List[str]], List[str]]:
    """
    Prepare text corpus from DataFrame.
    
    Args:
        df: DataFrame with text columns
        text_fields: List of column names to combine for text
        
    Returns:
        Tuple of (list of tokenized documents, list of combined raw texts)
    """
    documents = []
    raw_texts = []
    
    for _, row in df.iterrows():
        combined_text = ""
        for field in text_fields:
            if field in df.columns:
                value = row.get(field, '')
                if pd.notna(value):
                    combined_text += " " + str(value)
        
        raw_texts.append(combined_text.strip())
        tokens = preprocess_text(combined_text)
        documents.append(tokens)
    
    logger.info(f"Prepared corpus with {len(documents)} documents")
    return documents, raw_texts


def _infer_topic_name(top_words: List[str]) -> str:
    """Infer a descriptive topic name from top words."""
    # Keywords that suggest specific topics
    topic_indicators = {
        'Digital Financial Services': ['digital', 'technology', 'fintech', 'platform', 'online'],
        'Microfinance & Credit': ['microfinance', 'credit', 'loan', 'lending', 'borrowing', 'mfi'],
        'Mobile Banking': ['mobile', 'phone', 'sms', 'mpesa', 'banking', 'money'],
        'Financial Literacy': ['literacy', 'education', 'knowledge', 'training', 'awareness'],
        'Regulatory Framework': ['regulation', 'policy', 'government', 'law', 'compliance'],
        'Blockchain & Fintech': ['blockchain', 'cryptocurrency', 'bitcoin', 'decentralized'],
        'Rural Development': ['rural', 'agriculture', 'farmer', 'poverty', 'development'],
        'Payment Systems': ['payment', 'transaction', 'transfer', 'remittance', 'cash'],
        'Women & Gender': ['women', 'gender', 'female', 'empowerment'],
        'Insurance & Risk': ['insurance', 'risk', 'microinsurance', 'protection'],
    }
    
    words_set = set(top_words)
    best_match = "General Financial Inclusion"
    best_score = 0
    
    for topic_name, indicators in topic_indicators.items():
        score = len(set(indicators) & words_set)
        if score > best_score:
            best_score = score
            best_match = topic_name
    
    return best_match


def fit_lda_model_gensim(
    documents: List[List[str]],
    n_topics: int = 8,
    seed: int = 42,
    passes: int = 10,
    iterations: int = 100
) -> Tuple[Any, pd.DataFrame, np.ndarray, Dict]:
    """
    Fit LDA model using gensim.
    
    Args:
        documents: List of tokenized documents
        n_topics: Number of topics
        seed: Random seed
        passes: Number of passes through corpus
        iterations: Max iterations per pass
        
    Returns:
        Tuple of (model, topic_terms_df, doc_topic_matrix, dictionary)
    """
    if not GENSIM_AVAILABLE:
        raise ImportError("gensim is not available")
    
    logger.info(f"Fitting gensim LDA with {n_topics} topics (seed={seed})")
    
    # Create dictionary and corpus
    dictionary = corpora.Dictionary(documents)
    dictionary.filter_extremes(no_below=5, no_above=0.5)
    corpus = [dictionary.doc2bow(doc) for doc in documents]
    
    # Fit model
    np.random.seed(seed)
    model = LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=n_topics,
        random_state=seed,
        passes=passes,
        iterations=iterations,
        alpha='auto',
        eta='auto'
    )
    
    # Extract topic-term matrix
    topic_terms = []
    topic_names = {}
    for topic_id in range(n_topics):
        top_words = model.show_topic(topic_id, topn=20)
        words = [w for w, _ in top_words]
        probs = [p for _, p in top_words]
        
        topic_name = _infer_topic_name(words[:10])
        topic_names[topic_id] = topic_name
        
        for word, prob in top_words:
            topic_terms.append({
                'topic_id': topic_id,
                'topic_name': topic_name,
                'term': word,
                'weight': prob
            })
    
    topic_terms_df = pd.DataFrame(topic_terms)
    
    # Compute document-topic matrix
    doc_topic = np.zeros((len(corpus), n_topics))
    for i, doc_bow in enumerate(corpus):
        topic_dist = model.get_document_topics(doc_bow, minimum_probability=0)
        for topic_id, prob in topic_dist:
            doc_topic[i, topic_id] = prob
    
    logger.info("Gensim LDA fitting complete")
    return model, topic_terms_df, doc_topic, {'dictionary': dictionary, 'topic_names': topic_names}


def fit_lda_model_sklearn(
    raw_texts: List[str],
    n_topics: int = 8,
    seed: int = 42,
    max_iter: int = 100,
    max_features: int = 2000
) -> Tuple[Any, pd.DataFrame, np.ndarray, Dict]:
    """
    Fit LDA model using scikit-learn (fallback).
    
    Args:
        raw_texts: List of raw text documents
        n_topics: Number of topics
        seed: Random seed
        max_iter: Maximum iterations
        max_features: Maximum vocabulary size
        
    Returns:
        Tuple of (model, topic_terms_df, doc_topic_matrix, metadata)
    """
    if not SKLEARN_LDA_AVAILABLE:
        raise ImportError("scikit-learn is not available")
    
    logger.info(f"Fitting sklearn LDA with {n_topics} topics (seed={seed})")
    
    # Vectorize
    vectorizer = CountVectorizer(
        max_features=max_features,
        min_df=5,
        max_df=0.5,
        stop_words='english'
    )
    doc_term_matrix = vectorizer.fit_transform(raw_texts)
    feature_names = vectorizer.get_feature_names_out()
    
    # Fit LDA
    model = LatentDirichletAllocation(
        n_components=n_topics,
        random_state=seed,
        max_iter=max_iter,
        learning_method='batch'
    )
    doc_topic = model.fit_transform(doc_term_matrix)
    
    # Extract topic-term matrix
    topic_terms = []
    topic_names = {}
    for topic_id, topic in enumerate(model.components_):
        top_indices = topic.argsort()[:-21:-1]
        top_words = [feature_names[i] for i in top_indices]
        top_weights = [topic[i] for i in top_indices]
        
        # Normalize weights
        total = sum(top_weights)
        top_weights = [w / total for w in top_weights]
        
        topic_name = _infer_topic_name(top_words[:10])
        topic_names[topic_id] = topic_name
        
        for word, weight in zip(top_words, top_weights):
            topic_terms.append({
                'topic_id': topic_id,
                'topic_name': topic_name,
                'term': word,
                'weight': weight
            })
    
    topic_terms_df = pd.DataFrame(topic_terms)
    
    logger.info("Sklearn LDA fitting complete")
    return model, topic_terms_df, doc_topic, {'vectorizer': vectorizer, 'topic_names': topic_names}


def fit_lda_model(
    df: pd.DataFrame,
    n_topics: int = 8,
    seed: int = 42,
    text_fields: List[str] = ['title_raw', 'abstract_raw', 'keywords_raw'],
    **kwargs
) -> Tuple[Any, pd.DataFrame, np.ndarray, Dict]:
    """
    Fit LDA model with automatic fallback.
    
    Tries gensim first, falls back to scikit-learn if not available.
    
    Args:
        df: DataFrame with text columns
        n_topics: Number of topics to extract
        seed: Random seed for reproducibility
        text_fields: List of text column names
        **kwargs: Additional arguments passed to the LDA implementation
        
    Returns:
        Tuple of (model, topic_terms_df, doc_topic_matrix, metadata)
    """
    documents, raw_texts = prepare_corpus(df, text_fields)
    
    # Filter empty documents
    valid_indices = [i for i, doc in enumerate(documents) if len(doc) > 0]
    documents = [documents[i] for i in valid_indices]
    raw_texts = [raw_texts[i] for i in valid_indices]
    
    if len(documents) < n_topics:
        logger.warning(f"Only {len(documents)} documents with text, reducing topics to {len(documents)}")
        n_topics = max(2, len(documents) // 2)
    
    if GENSIM_AVAILABLE:
        try:
            return fit_lda_model_gensim(documents, n_topics, seed, **kwargs)
        except Exception as e:
            logger.warning(f"Gensim LDA failed: {e}. Falling back to sklearn.")
    
    if SKLEARN_LDA_AVAILABLE:
        return fit_lda_model_sklearn(raw_texts, n_topics, seed, **kwargs)
    
    raise ImportError("Neither gensim nor scikit-learn is available for LDA")


def topic_evolution_by_year(
    df: pd.DataFrame,
    doc_topic: np.ndarray,
    year_field: str = 'year_clean'
) -> pd.DataFrame:
    """
    Compute topic shares by year for thematic evolution analysis.
    
    Args:
        df: DataFrame with year column
        doc_topic: Document-topic probability matrix (n_docs x n_topics)
        year_field: Column name for publication year
        
    Returns:
        DataFrame with columns: year, topic_id, topic_name, share, count
    """
    logger.info("Computing topic evolution by year")
    
    if year_field not in df.columns:
        logger.warning(f"Year field '{year_field}' not found")
        return pd.DataFrame()
    
    # Get years for valid documents
    years = df[year_field].values[:len(doc_topic)]
    
    # Group by year
    evolution_records = []
    unique_years = sorted(set(y for y in years if pd.notna(y) and y > 1900))
    
    n_topics = doc_topic.shape[1]
    
    for year in unique_years:
        year_mask = years == year
        if not any(year_mask):
            continue
        
        year_topics = doc_topic[year_mask]
        topic_shares = year_topics.mean(axis=0)
        
        for topic_id in range(n_topics):
            evolution_records.append({
                'year': int(year),
                'topic_id': topic_id,
                'topic_name': TOPIC_NAMES.get(topic_id, f"Topic {topic_id}"),
                'share': topic_shares[topic_id],
                'count': year_mask.sum()
            })
    
    result = pd.DataFrame(evolution_records)
    logger.info(f"Computed evolution for {len(unique_years)} years")
    return result


def get_top_terms_per_topic(
    topic_terms_df: pd.DataFrame,
    n_terms: int = 10
) -> pd.DataFrame:
    """
    Get top N terms for each topic.
    
    Args:
        topic_terms_df: DataFrame from fit_lda_model
        n_terms: Number of top terms per topic
        
    Returns:
        DataFrame with top terms per topic
    """
    result = (
        topic_terms_df
        .sort_values(['topic_id', 'weight'], ascending=[True, False])
        .groupby('topic_id')
        .head(n_terms)
        .reset_index(drop=True)
    )
    return result


def save_topic_model(
    model: Any,
    metadata: Dict,
    output_dir: str,
    prefix: str = 'lda_model'
) -> None:
    """
    Save topic model and metadata to disk.
    
    Args:
        model: The fitted LDA model
        metadata: Dictionary with vocabulary/topic names
        output_dir: Output directory path
        prefix: Filename prefix
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save model
    model_path = output_path / f"{prefix}.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    # Save metadata
    meta_path = output_path / f"{prefix}_metadata.pkl"
    with open(meta_path, 'wb') as f:
        pickle.dump(metadata, f)
    
    logger.info(f"Saved topic model to {output_dir}")
