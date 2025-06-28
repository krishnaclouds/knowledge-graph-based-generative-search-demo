import logging
from neo4j import GraphDatabase, Driver
from typing import Optional, List, Dict, Any
from config import get_settings

logger = logging.getLogger(__name__)

class Neo4jDatabase:
    def __init__(self):
        self.settings = get_settings()
        self.driver: Optional[Driver] = None
        self._connect()
    
    def _connect(self):
        """Initialize Neo4j connection"""
        try:
            self.driver = GraphDatabase.driver(
                self.settings.neo4j_uri,
                auth=(self.settings.neo4j_user, self.settings.neo4j_password)
            )
            logger.info(f"Connected to Neo4j at {self.settings.neo4j_uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 AS result")
                return {"status": "ok", "db": result.single()["result"]}
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "detail": str(e)}
    
    def get_all_nodes(self) -> List[Dict[str, Any]]:
        """Get all nodes from the database"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n)
                    RETURN id(n) as id, labels(n) as labels, 
                           n.name as name, n.title as title, 
                           n.industry as industry, n.topic as topic
                """)
                
                nodes = []
                for record in result:
                    nodes.append({
                        "id": record["id"],
                        "labels": record["labels"],
                        "name": record["name"],
                        "title": record["title"],
                        "industry": record["industry"],
                        "topic": record["topic"]
                    })
                return nodes
        except Exception as e:
            logger.error(f"Failed to get nodes: {e}")
            raise
    
    def get_all_edges(self) -> List[Dict[str, Any]]:
        """Get all relationships from the database"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (a)-[r]->(b)
                    RETURN id(a) as from, id(b) as to, type(r) as label
                """)
                
                edges = []
                for record in result:
                    edges.append({
                        "from": record["from"],
                        "to": record["to"],
                        "label": record["label"]
                    })
                return edges
        except Exception as e:
            logger.error(f"Failed to get edges: {e}")
            raise
    
    def get_node_context(self, node_id: int) -> Dict[str, Any]:
        """Get node with its relationships"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n)
                    WHERE id(n) = $node_id
                    OPTIONAL MATCH (n)-[r]-(connected)
                    RETURN n, type(r) as relationship, connected
                """, node_id=node_id)
                
                context = {"node": None, "relationships": []}
                
                for record in result:
                    if not context["node"]:
                        node = record["n"]
                        context["node"] = dict(node)
                    
                    if record["relationship"] and record["connected"]:
                        connected_node = dict(record["connected"])
                        context["relationships"].append({
                            "type": record["relationship"],
                            "connected_node": connected_node
                        })
                
                return context
        except Exception as e:
            logger.error(f"Failed to get node context for node {node_id}: {e}")
            raise

# Global database instance
db = Neo4jDatabase()