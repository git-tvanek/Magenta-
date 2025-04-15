#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API routes for the MagentaTV backend
"""
from flask import (
    request, jsonify, Response, redirect, 
    current_app, url_for, send_file
)
import os
import json
import io
import requests
import time
import logging

from app.api import api_bp
from app.api.helpers import get_api, server_url_from_request
from app.cache import get_from_cache, clear_cache
from app.config import update_config

logger = logging.getLogger(__name__)


# Root endpoint
@api_bp.route('/')
def index():
    """Main page with API information"""
    base_url = server_url_from_request()
    return jsonify({
        "name": "MagentaTV Backend API",
        "version": "1.0.0",
        "endpoints": {
            "channels": f"{base_url}/api/channels",
            "stream": f"{base_url}/api/stream/<channel_id>",
            "epg": f"{base_url}/api/epg/<channel_id>",
            "catchup": f"{base_url}/api/catchup/<channel_id>/<start_time>-<end_time>",
            "devices": f"{base_url}/api/devices",
            "playlist": f"{base_url}/api/playlist.m3u",
            "status": f"{base_url}/api/status",
            "config": f"{base_url}/api/config"
        }
    })


# Configuration endpoint
@api_bp.route('/config', methods=['GET', 'POST'])
def config_endpoint():
    """Get and set configuration"""
    if request.method == 'POST':
        # Update configuration
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Invalid data format"}), 400
            
        # Update configuration
        config = update_config(data)
        
        # Reset API instance
        get_api.cache_clear()
        
        return jsonify({"success": True, "config": config})
    else:
        # Get configuration
        return jsonify({
            "success": True, 
            "config": {k.lower(): v for k, v in current_app.config.items() 
                      if k in current_app.config and k != 'PASSWORD'}
        })


# Status endpoint
@api_bp.route('/status')
def status():
    """Get API status"""
    api = get_api()
    if api is None:
        return jsonify({"success": False, "message": "API is not initialized"}), 500
    
    config = {k.lower(): v for k, v in current_app.config.items() 
              if k not in ('PASSWORD', 'SECRET_KEY')}
    
    return jsonify({
        "success": True,
        "status": "online",
        "language": api.language,
        "quality": api.quality,
        "refresh_token_valid": bool(api.refresh_token),
        "token_expires": int(api.token_expires - time.time()),
        "config": config
    })


# Channels endpoint
@api_bp.route('/channels')
def channels():
    """Get channels list"""
    api = get_api()
    if api is None:
        return jsonify({"success": False, "message": "API is not initialized"}), 500
        
    channels_data = get_from_cache("channels", api.get_channels)
    
    if not channels_data:
        return jsonify({"success": False, "message": "Failed to get channels list"}), 500
        
    return jsonify({
        "success": True,
        "channels": channels_data
    })


# Stream endpoint
@api_bp.route('/stream/<channel_id>')
def stream(channel_id):
    """
    Get stream URL for channel
    
    With redirect=1 parameter, redirects directly to stream
    """
    api = get_api()
    if api is None:
        return jsonify({"success": False, "message": "API is not initialized"}), 500
        
    # Get stream info
    stream_info = get_from_cache(f"stream_{channel_id}", api.get_stream_url, channel_id)
    
    if not stream_info:
        return jsonify({"success": False, "message": "Failed to get stream"}), 404
    
    # Redirect to stream or return info
    if request.args.get('redirect', '0') == '1':
        return redirect(stream_info["url"])
    else:
        return jsonify({
            "success": True,
            "stream": stream_info
        })


# EPG endpoint
@api_bp.route('/epg/<channel_id>')
def epg(channel_id):
    """Get EPG for channel"""
    api = get_api()
    if api is None:
        return jsonify({"success": False, "message": "API is not initialized"}), 500
    
    # Parameters
    days_back = int(request.args.get('days_back', 1))
    days_forward = int(request.args.get('days_forward', 1))
    
    # Get EPG
    epg_data = get_from_cache(
        f"epg_{channel_id}_{days_back}_{days_forward}", 
        api.get_epg, 
        channel_id, 
        days_back, 
        days_forward
    )
    
    if not epg_data:
        return jsonify({"success": False, "message": "Failed to get EPG"}), 404
        
    return jsonify({
        "success": True,
        "epg": epg_data
    })


# Catchup endpoint
@api_bp.route('/catchup/<channel_id>/<time_range>')
def catchup(channel_id, time_range):
    """
    Get catchup stream URL for channel and time range
    
    Time format: start_timestamp-end_timestamp (Unix timestamp)
    """
    api = get_api()
    if api is None:
        return jsonify({"success": False, "message": "API is not initialized"}), 500
    
    # Parse time range
    try:
        start_time, end_time = time_range.split("-")
        start_time = int(start_time)
        end_time = int(end_time)
    except (ValueError, TypeError) as e:
        return jsonify({"success": False, "message": f"Invalid time format: {e}"}), 400
    
    # Get catchup stream info
    stream_info = get_from_cache(
        f"catchup_{channel_id}_{start_time}_{end_time}", 
        api.get_catchup_by_time, 
        channel_id, 
        start_time, 
        end_time
    )
    
    if not stream_info:
        return jsonify({"success": False, "message": "Failed to get catchup stream"}), 404
    
    # Redirect to stream or return info
    if request.args.get('redirect', '0') == '1':
        return redirect(stream_info["url"])
    else:
        return jsonify({
            "success": True,
            "stream": stream_info
        })


# Devices endpoint
@api_bp.route('/devices')
def devices():
    """Get devices list"""
    api = get_api()
    if api is None:
        return jsonify({"success": False, "message": "API is not initialized"}), 500
    
    # Get devices list
    devices_data = get_from_cache("devices", api.get_devices)
    
    if devices_data is None:
        return jsonify({"success": False, "message": "Failed to get devices list"}), 500
        
    return jsonify({
        "success": True,
        "devices": devices_data
    })


# Delete device endpoint
@api_bp.route('/devices/delete/<device_id>')
def delete_device(device_id):
    """Delete device by ID"""
    api = get_api()
    if api is None:
        return jsonify({"success": False, "message": "API is not initialized"}), 500
    
    # Delete device
    success = api.delete_device(device_id)
    
    # Clear cache
    clear_cache("devices")
    
    return jsonify({
        "success": success,
        "message": "Device deleted" if success else "Failed to delete device"
    })


# Playlist endpoint
@api_bp.route('/playlist.m3u')
def playlist():
    """Get M3U playlist"""
    api = get_api()
    if api is None:
        return jsonify({"success": False, "message": "API is not initialized"}), 500
    
    # Generate playlist
    server_url = ""
    if request.args.get('proxy', '1') == '1':
        server_url = server_url_from_request()
        
    playlist_content = get_from_cache(f"playlist_{server_url}", api.generate_m3u_playlist, server_url)
    
    if not playlist_content:
        return jsonify({"success": False, "message": "Failed to generate playlist"}), 500
    
    # Return playlist as file
    response = Response(playlist_content, mimetype='application/x-mpegURL')
    response.headers["Content-Disposition"] = "attachment; filename=magenta_tv.m3u"
    return response


# Clear cache endpoint
@api_bp.route('/cache/clear')
def clear_cache_endpoint():
    """Clear cache"""
    key = request.args.get('key', None)
    clear_cache(key)
    
    return jsonify({
        "success": True,
        "message": f"Cache {'key ' + key if key else 'all'} cleared"
    })


# Proxy endpoint
@api_bp.route('/proxy/<path:url>')
def proxy(url):
    """Proxy for redirecting requests"""
    if not url.startswith('http'):
        url = 'https://' + url
    
    # Get parameters from request
    headers = {}
    for key, value in request.headers.items():
        if key.lower() not in ['host', 'content-length', 'connection']:
            headers[key] = value
    
    # Create request
    try:
        response = requests.get(url, headers=headers, stream=True)
        
        # Create response
        flask_response = Response(
            response=response.iter_content(chunk_size=1024),
            status=response.status_code,
            headers=dict(response.headers)
        )
        
        return flask_response
    except Exception as e:
        logger.error(f"Error in proxy request: {e}")
        return jsonify({"success": False, "message": f"Error in proxy request: {str(e)}"}), 500