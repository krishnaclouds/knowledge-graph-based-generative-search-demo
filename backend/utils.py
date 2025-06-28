import logging
import sys
from typing import Dict, Any

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

def format_graph_data(nodes: list, edges: list) -> Dict[str, Any]:
    """Format graph data for frontend consumption"""
    formatted_nodes = []
    for node in nodes:
        label = node["labels"][0] if node["labels"] else "Node"
        formatted_node = {
            "id": node["id"],
            "label": node["name"] or node["title"] or label,
            "group": label,
        }
        formatted_nodes.append(formatted_node)
    
    return {"nodes": formatted_nodes, "edges": edges}