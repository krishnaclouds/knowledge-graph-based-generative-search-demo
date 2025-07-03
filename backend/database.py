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
    
    
    

# Global database instance
db = Neo4jDatabase()