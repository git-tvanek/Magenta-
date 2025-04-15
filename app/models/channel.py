#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Channel model
"""


class Channel:
    """
    Represents a TV channel
    """
    def __init__(self, id, name, logo=None, group=None, has_archive=False, original_name=None):
        self.id = id
        self.name = name
        self.original_name = original_name or name
        self.logo = logo
        self.group = group or "Other"
        self.has_archive = has_archive
        
    def to_dict(self):
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "original_name": self.original_name,
            "logo": self.logo,
            "group": self.group,
            "has_archive": self.has_archive
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            original_name=data.get("original_name"),
            logo=data.get("logo"),
            group=data.get("group", "Other"),
            has_archive=data.get("has_archive", False)
        )