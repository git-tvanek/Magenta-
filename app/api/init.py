#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API module initialization
"""
from flask import Blueprint

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import routes
from app.api import routes