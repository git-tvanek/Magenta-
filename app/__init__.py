#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask application factory
"""
from flask import Flask
import os
import logging
from logging.handlers import RotatingFileHandler

from app.config import load_config
from app.cache import init_cache


def create_app(config_file=None):
    """
    Application factory function

    Args:
        config_file (str, optional): Path to the configuration file

    Returns:
        Flask: Flask application instance
    """
    # Initialize Flask app
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False
    
    # Load configuration
    config = load_config(config_file)
    app.config.update(config)
    
    # Setup logging
    setup_logging(app)
    
    # Initialize cache
    init_cache()
    
    # Register blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp)
    
    # Create data directory if it doesn't exist
    os.makedirs(app.config["DATA_DIR"], exist_ok=True)
    
    app.logger.info("Application initialized successfully")
    return app


def setup_logging(app):
    """
    Setup logging for the application

    Args:
        app (Flask): Flask application instance
    """
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(app.config["DATA_DIR"], "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # Configure logging
    log_level = logging.DEBUG if app.config["DEBUG"] else logging.INFO
    log_file = os.path.join(logs_dir, "magenta_tv.log")
    
    # Setup file handler
    file_handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    file_handler.setLevel(log_level)
    
    # Setup stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    stream_handler.setLevel(log_level)
    
    # Configure application logger
    app.logger.setLevel(log_level)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(stream_handler)
    
    # Remove default handler
    app.logger.handlers = [file_handler, stream_handler]
    
    # Mute Werkzeug logger in production
    if not app.config["DEBUG"]:
        logging.getLogger('werkzeug').setLevel(logging.ERROR)