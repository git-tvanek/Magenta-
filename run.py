#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MagentaTV Backend Server

Server zajišťující komunikaci s API služby Magenta TV / Magio TV.
Poskytuje REST API endpointy pro získání seznamu kanálů, streamů a EPG.
"""
from app.services import create_app
import os

# Create the Flask application instance
app = create_app()

if __name__ == '__main__':
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )