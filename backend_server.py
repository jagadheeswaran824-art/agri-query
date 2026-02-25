#!/usr/bin/env python3
"""
KrishiSahay Live AI Backend Server
Advanced Python backend with WebSocket support, real-time AI chat, and comprehensive features
"""

import os
import json
import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid
import hashlib
from dataclasses import dataclass, asdict
from collections import defaultdict
import threading
import queue

# Flask and WebSocket imports
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from werkzeug.middleware.proxy_fix import ProxyFix

# Additional imports for advanced features
import redis
from cachetools import TTLCache
import schedule
from concurrent.futures import ThreadPoolExecutor
import requests
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/backend.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='public', static_url_path='')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'krishisahay-secret-key-2024')
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Enable CORS
CORS(app, origins="*")

# Initialize SocketIO
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    logger=True,
    engineio_logger=True
)

# Global configuration
CONFIG = {
    'PORT': int(os.environ.get('PORT', 5000)),
    'DEBUG': os.environ.get('DEBUG', 'False').lower() == 'true',
    'REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379'),
    'WATSONX_API_KEY': os.environ.get('WATSONX_API_KEY', ''),
    'WATSONX_PROJECT_ID': os.environ.get('WATSONX_PROJECT_ID', ''),
    'WATSONX_REGION': os.environ.get('WATSONX_REGION', 'us-south'),
    'MAX_CONNECTIONS': int(os.environ.get('MAX_CONNECTIONS', 1000)),
    'RATE_LIMIT': int(os.environ.get('RATE_LIMIT', 100)),
    'CACHE_TTL': int(os.environ.get('CACHE_TTL', 1800))  # 30 minutes
}

# Data structures
@dataclass
class UserSession:
    session_id: str
    socket_id: str
    join_time: datetime
    last_activity: datetime
    query_count: int = 0
    user_agent: str = ""
    ip_address: str = ""

@dataclass
class ChatMessage:
    session_id: str
    message_id: str
    query: str
    response: str
    timestamp: datetime
    response_time: float
    confidence: float = 0.0
    category: str = "general"
    mode: str = "online"

@dataclass
class SystemAnalytics:
    total_queries: int = 0
    avg_response_time: float = 0.0
    active_users: int = 0
    error_rate: float = 0.0
    top_queries: List[Dict] = None
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.top_queries is None:
            self.top_queries = []
        if self.last_updated is None:
            self.last_updated = datetime.now()

# Global state management
class StateManager:
    def __init__(self):
        self.active_sessions: Dict[str, UserSession] = {}
        self.chat_history: Dict[str, List[ChatMessage]] = defaultdict(list)
        self.analytics = SystemAnalytics()
        self.response_cache = TTLCache(maxsize=1000, ttl=CONFIG['CACHE_TTL'])
        self.redis_client = None
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.message_queue = queue.Queue()
        
        # Initialize Redis if available
        self._init_redis()
        
    def _init_redis(self):
        try:
            self.redis_client = redis.from_url(CONFIG['REDIS_URL'], decode_responses=True)
            self.redis_client.ping()
            logger.info("✅ Connected to Redis")
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory storage: {e}")
            self.redis_client = None

state_manager = StateManager()

# Enhanced Agricultural Knowledge Base
AGRICULTURE_KNOWLEDGE = {
    'aphids': {
        'crops': ['mustard', 'wheat', 'cotton', 'cabbage', 'cauliflower'],
        'solution': 'Spray neem oil solution (5ml per liter) or use imidacloprid 17.8% SL @ 0.5ml/liter. Apply during early morning or evening.',
        'severity': 'medium',
        'category': 'pest',
        'symptoms': ['curled leaves', 'sticky honeydew', 'yellowing', 'stunted growth'],
        'prevention': ['regular monitoring', 'beneficial insects', 'proper spacing', 'yellow sticky traps'],
        'organic_solutions': ['neem oil', 'soap spray', 'ladybugs', 'lacewings'],
        'chemical_solutions': ['imidacloprid', 'thiamethoxam', 'acetamiprid'],
        'application_timing': ['early morning', 'evening', 'avoid flowering'],
        'dosage': '5ml neem oil per liter or 0.5ml imidacloprid per liter'
    },
    'leaf spot': {
        'crops': ['tomato', 'potato', 'brinjal', 'chili'],
        'solution': 'Remove infected leaves. Spray mancozeb 75% WP @ 2g/liter or copper oxychloride @ 3g/liter at 10-day intervals.',
        'severity': 'high',
        'category': 'disease',
        'symptoms': ['brown spots', 'leaf yellowing', 'defoliation', 'circular lesions'],
        'prevention': ['cr