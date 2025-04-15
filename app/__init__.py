#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Services module initialization

This module provides service classes that handle the core business logic of the application.
"""
from flask import current_app
import logging

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