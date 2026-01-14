"""Configuration loader for pipeline parameters"""

import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = "docs/PARAMETERS.yml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to PARAMETERS.yml file
        
    Returns:
        Dictionary containing configuration parameters
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML parsing fails
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Validate required sections
    required_sections = ['seeds', 'deduplication', 'paths', 'figures', 'tables']
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    return config


def get_path(config: Dict[str, Any], *keys: str) -> Path:
    """
    Get a path from configuration, resolving relative to repository root.
    
    Args:
        config: Configuration dictionary
        *keys: Nested keys to traverse (e.g., 'paths', 'raw_data', 'scopus')
        
    Returns:
        Path object (relative to repository root)
    """
    value = config
    for key in keys:
        value = value[key]
    
    return Path(value)


def get_seed(config: Dict[str, Any], seed_type: str = 'figure_generation') -> int:
    """
    Get a random seed from configuration.
    
    Args:
        config: Configuration dictionary
        seed_type: Type of seed ('figure_generation', 'sampling', 'clustering', 'network_layout')
        
    Returns:
        Seed value (integer)
    """
    return config['seeds'].get(seed_type, 42)
