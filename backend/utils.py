import logging
import sys
import json
from datetime import datetime, date
from typing import Dict, Any
from neo4j.time import DateTime, Date, Time

def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration"""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # Reduce noise from other libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("neo4j").setLevel(logging.WARNING)

def serialize_for_json(obj):
    """Custom JSON serializer for Neo4j and other non-serializable objects"""
    if isinstance(obj, (DateTime, Date, Time)):
        return obj.isoformat()
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):
        # Handle custom objects by converting to dict
        return {k: serialize_for_json(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize_for_json(item) for item in obj]
    else:
        return obj

def safe_json_serialize(data):
    """Safely serialize data to JSON, handling Neo4j types"""
    return json.loads(json.dumps(data, default=serialize_for_json))

