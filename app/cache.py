#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cache implementation for the MagentaTV backend
"""
import time
import threading
import logging

logger = logging.getLogger(__name__)

# Global cache variables
cache = {}
cache_expiry = {}
cache_lock = threading.Lock()


def init_cache():
    """
    Initialize the cache
    """
    global cache, cache_expiry
    
    with cache_lock:
        cache = {
            "channels": {},
            "streams": {},
            "epg": {},
            "devices": {}
        }
        cache_expiry = {}
    
    logger.debug("Cache initialized")


def get_from_cache(cache_key, fetch_function, *args, **kwargs):
    """
    Get data from cache or using the provided function
    
    Args:
        cache_key (str): Cache key
        fetch_function (callable): Function to fetch data if not in cache
        *args, **kwargs: Arguments to pass to the fetch function
        
    Returns:
        any: Data from cache or function
    """
    with cache_lock:
        # Check cache
        if cache_key in cache and time.time() < cache_expiry.get(cache_key, 0):
            logger.debug(f"Data retrieved from cache: {cache_key}")
            return cache[cache_key]
    
    # Fetch data
    data = fetch_function(*args, **kwargs)
    
    # Store in cache
    if data is not None:
        with cache_lock:
            from flask import current_app
            cache[cache_key] = data
            cache_expiry[cache_key] = time.time() + current_app.config["CACHE_TIMEOUT"]
            logger.debug(f"Data stored in cache: {cache_key}")
    
    return data


def clear_cache(cache_key=None):
    """
    Clear cache entries
    
    Args:
        cache_key (str, optional): Specific cache key to clear, or None to clear all
        
    Returns:
        bool: True if cache was cleared
    """
    with cache_lock:
        if cache_key is None:
            # Clear all cache
            global cache, cache_expiry
            cache = {
                "channels": {},
                "streams": {},
                "epg": {},
                "devices": {}
            }
            cache_expiry = {}
            logger.debug("All cache entries cleared")
        elif cache_key in cache:
            # Clear specific entry
            del cache[cache_key]
            if cache_key in cache_expiry:
                del cache_expiry[cache_key]
            logger.debug(f"Cache entry cleared: {cache_key}")
            
    return True


def get_cache_info():
    """
    Get information about current cache state
    
    Returns:
        dict: Cache information
    """
    with cache_lock:
        current_time = time.time()
        info = {
            "entries": len(cache),
            "keys": list(cache.keys()),
            "expires_in": {k: int(v - current_time) for k, v in cache_expiry.items()}
        }
        
    return info