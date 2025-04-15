#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program model
"""


class Program:
    """
    Represents a TV program
    """
    def __init__(self, schedule_id, title, start_time, end_time, 
                 description=None, duration=0, category=None, 
                 year=None, episode=None, images=None):
        self.schedule_id = schedule_id
        self.title = title
        self.start_time = start_time
        self.end_time = end_time
        self.description = description or ""
        self.duration = duration
        self.category = category or ""
        self.year = year
        self.episode = episode
        self.images = images or []
        
    def to_dict(self):
        """Convert to dictionary representation"""
        return {
            "schedule_id": self.schedule_id,
            "title": self.title,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "description": self.description,
            "duration": self.duration,
            "category": self.category,
            "year": self.year,
            "episode": self.episode,
            "images": self.images
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        return cls(
            schedule_id=data.get("schedule_id"),
            title=data.get("title", ""),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            description=data.get("description"),
            duration=data.get("duration", 0),
            category=data.get("category"),
            year=data.get("year"),
            episode=data.get("episode"),
            images=data.get("images", [])
        )