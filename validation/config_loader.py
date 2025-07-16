"""
Configuration Loader for API Validation

This module handles loading and parsing of validation configuration files.
"""

import json
import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigLoader:
    """Loads and manages validation configuration."""
    
    DEFAULT_CONFIG = {
        'file_types': {
            'extensions': ['.py', '.yaml', '.yml', '.json'],
            'ignore_patterns': [
                '__pycache__',
                '.git',
                'node_modules',
                '.pytest_cache',
                'venv',
                '.venv',
                'target',
                'build',
                'dist'
            ]
        },
        'output': {
            'format': 'text',  # 'text' or 'json'
            'verbose': False
        },
        'pcf_rules': {
            # PCF-specific validation rules will be added here
            'enabled': True
        },
        'shp_ikp_rules': {
            # SHP/IKP-specific validation rules will be added here
            'enabled': True
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize config loader with optional config file path."""
        self.config_path = config_path or self._find_config_file()
        self.config = None
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or return default config."""
        if self.config is not None:
            return self.config
        
        if self.config_path and os.path.exists(self.config_path):
            try:
                self.config = self._load_config_file(self.config_path)
                # Merge with defaults to ensure all keys exist
                self.config = self._merge_configs(self.DEFAULT_CONFIG, self.config)
            except Exception as e:
                print(f"Warning: Could not load config from {self.config_path}: {e}")
                print("Using default configuration")
                self.config = self.DEFAULT_CONFIG.copy()
        else:
            self.config = self.DEFAULT_CONFIG.copy()
        
        return self.config
    
    def _find_config_file(self) -> Optional[str]:
        """Find configuration file in current directory or parent directories."""
        config_names = [
            'api_validation.yaml',
            'api_validation.yml',
            'api_validation.json',
            '.api_validation.yaml',
            '.api_validation.yml',
            '.api_validation.json'
        ]
        
        current_dir = Path.cwd()
        
        # Search in current directory and parent directories
        for parent in [current_dir] + list(current_dir.parents):
            for config_name in config_names:
                config_path = parent / config_name
                if config_path.exists():
                    return str(config_path)
        
        return None
    
    def _load_config_file(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML or JSON file."""
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.endswith(('.yaml', '.yml')):
                return yaml.safe_load(f) or {}
            elif config_path.endswith('.json'):
                return json.load(f) or {}
            else:
                raise ValueError(f"Unsupported config file format: {config_path}")
    
    def _merge_configs(self, default: Dict[str, Any], custom: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge custom config with default config."""
        result = default.copy()
        
        for key, value in custom.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def save_default_config(self, output_path: str = 'api_validation.yaml'):
        """Save the default configuration to a file for reference."""
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.DEFAULT_CONFIG, f, default_flow_style=False, indent=2)
        print(f"Default configuration saved to {output_path}") 