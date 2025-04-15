#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper functions for API endpoints
"""
import functools
import logging
from flask import current_app, request

logger = logging.getLogger(__name__)

# Global API instance
_api_instance = None


@functools.lru_cache(maxsize=1)
def get_api():
    """
    Get or create API instance
    
    Returns:
        MagentaTV: API client instance or None if initialization failed
    """
    global _api_instance
    
    if _api_instance is None:
        # Import here to avoid circular import
        from app.services import get_magenta_tv_service
        
        # Check credentials
        if not current_app.config.get("USERNAME") or not current_app.config.get("PASSWORD"):
            logger.error("Credentials not set!")
            return None
            
        # Create new instance
        _api_instance = get_magenta_tv_service()
        
        # Check if service was created
        if _api_instance is None:
            logger.error("Failed to create MagentaTV service!")
            return None
            
        # Login
        if not _api_instance.login():
            logger.error("Failed to login to API!")
            _api_instance = None
            return None
    
    return _api_instance


def server_url_from_request():
    """
    Get server URL from request
    
    Returns:
        str: Server URL
    """
    # Get server URL
    server_url = request.url_root.rstrip('/')
    
    # If running behind proxy, use X-Forwarded-* headers
    if request.headers.get('X-Forwarded-Host'):
        proto = request.headers.get('X-Forwarded-Proto', 'http')
        host = request.headers.get('X-Forwarded-Host')
        prefix = request.headers.get('X-Forwarded-Prefix', '')
        server_url = f"{proto}://{host}{prefix}"
    
    return server_url