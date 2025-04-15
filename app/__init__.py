#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Services module initialization

This module provides service classes that handle the core business logic of the application.
"""
from flask import Flask, current_app
import logging
import os

logger = logging.getLogger(__name__)

# Lazy load the MagentaTV service
def get_magenta_tv_service():
    """
    Get an instance of the MagentaTV service
    
    Returns:
        MagentaTV: An instance of the MagentaTV service
    """
    from app.services.magenta_tv import MagentaTV
    
    try:
        return MagentaTV(
            username=current_app.config["USERNAME"],
            password=current_app.config["PASSWORD"],
            language=current_app.config["LANGUAGE"],
            quality=current_app.config["QUALITY"]
        )
    except Exception as e:
        logger.error(f"Failed to initialize MagentaTV service: {e}")
        return None

def create_app(config_file=None):
    """
    Factory function that creates the Flask application
    
    Args:
        config_file (str, optional): Path to configuration file
        
    Returns:
        Flask: Configured Flask application instance
    """
    # Create app instance
    app = Flask(__name__)
    
    # Load default configuration
    from app.config import load_config
    app_config = load_config(config_file)
    app.config.update(app_config)
    
    # Ensure data directory exists
    os.makedirs(app.config["DATA_DIR"], exist_ok=True)
    
    # Initialize logging
    logging.basicConfig(
        level=logging.DEBUG if app.config["DEBUG"] else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize cache
    from app.cache import init_cache
    with app.app_context():
        init_cache()
    
    # Register blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp)
    
    logger.info(f"Application initialized with configuration: {app.config['LANGUAGE']}")
    return app