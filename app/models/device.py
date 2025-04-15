#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Device model
"""


class Device:
    """
    Represents a registered device
    """
    def __init__(self, id, name, type="other", is_this_device=False):
        self.id = id
        self.name = name
        self.type = type
        self.is_this_device = is_this_device
        
    def to_dict(self):
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "is_this_device": self.is_this_device
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            type=data.get("type", "other"),
            is_this_device=data.get("is_this_device", False)
        )