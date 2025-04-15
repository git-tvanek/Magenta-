#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration management for the MagentaTV backend
"""
import os
import json


# Default configuration
DEFAULT_CONFIG = {
    "USERNAME": "",                # Přihlašovací jméno
    "PASSWORD": "",                # Heslo
    "LANGUAGE": "cz",              # Jazyk ("cz" nebo "sk")
    "QUALITY": "p5",               # Kvalita streamu (p1-p5, kde p5 je nejvyšší)
    "APP_VERSION": "4.0.25-hf.0",             
    "HOST": "0.0.0.0",             # Adresa, na které bude server poslouchat
    "PORT": 5000,                  # Port serveru
    "CACHE_TIMEOUT": 3600,         # Platnost cache v sekundách (1 hodina)
    "DATA_DIR": "data",            # Složka pro ukládání dat
    "DEBUG": False                  # Debug mód
}


def load_config(config_file=None):
    """
    Load configuration from file

    Args:
        config_file (str, optional): Path to the configuration file.
                                    If None, tries to load from default location.

    Returns:
        dict: Configuration dictionary
    """
    config = DEFAULT_CONFIG.copy()
    
    # Determine config file path
    if config_file is None:
        config_file = os.path.join(config["DATA_DIR"], "config.json")
    
    # Load config from file if exists
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                # Update config with loaded values
                for key, value in loaded_config.items():
                    if key.upper() in config:
                        config[key.upper()] = value
        except Exception as e:
            print(f"Error loading config: {e}")
    
    return config


def save_config(config, config_file=None):
    """
    Save configuration to file

    Args:
        config (dict): Configuration dictionary
        config_file (str, optional): Path to save the configuration

    Returns:
        bool: True if saved successfully, False otherwise
    """
    if config_file is None:
        config_file = os.path.join(config["DATA_DIR"], "config.json")
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        # Convert keys to lowercase for storage
        save_config = {k.lower(): v for k, v in config.items()}
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(save_config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def update_config(new_config, config_file=None):
    """
    Update configuration with new values and save to file

    Args:
        new_config (dict): New configuration values
        config_file (str, optional): Path to the configuration file

    Returns:
        dict: Updated configuration
    """
    # Load current config
    config = load_config(config_file)
    
    # Update config
    for key, value in new_config.items():
        key_upper = key.upper()
        if key_upper in config:
            config[key_upper] = value
    
    # Save updated config
    save_config(config, config_file)
    
    return config