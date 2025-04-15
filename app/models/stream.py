#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stream model
"""


class Stream:
    """
    Represents a media stream
    """
    def __init__(self, url, headers=None, content_type=None, is_live=True):
        self.url = url
        self.headers = headers or {}
        self.content_type = content_type or "application/vnd.apple.mpegurl"
        self.is_live = is_live
        
    def to_dict(self):
        """Convert to dictionary representation"""
        return {
            "url": self.url,
            "headers": self.headers,
            "content_type": self.content_type,
            "is_live": self.is_live
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        return cls(
            url=data.get("url", ""),
            headers=data.get("headers", {}),
            content_type=data.get("content_type"),
            is_live=data.get("is_live", True)
        )