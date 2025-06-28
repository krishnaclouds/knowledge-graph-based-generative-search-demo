from dotenv import load_dotenv
load_dotenv()

from database import db
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_database():
    """Clear all existing data"""
    try:
        with db.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        logger.info("Database cleared successfully")
    except Exception as e:
        logger.error(f"Failed to clear database: {e}")
        raise

def create_sample_data():
    """Create comprehensive sample data for testing"""
    try:
        with db.driver.session() as session:
            # Create companies
            companies_data = [
                {"name": "Google", "industry": "Technology", "founded": 1998},
                {"name": "Apple", "industry": "Technology", "founded": 1976},
                {"name": "Microsoft", "industry": "Technology", "founded": 1975},
                {"name": "Tesla", "industry": "Automotive", "founded": 2003},
                {"name": "OpenAI", "industry": "Artificial Intelligence", "founded": 2015},
                {"name": "Meta", "industry": "Technology", "founded": 2004},
                {"name": "Amazon", "industry": "E-commerce", "founded": 1994},
                {"name": "Netflix", "industry": "Entertainment", "founded": 1997}
            ]
            
            for company in companies_data:
                session.run(
                    "CREATE (:Company {name: $name, industry: $industry, founded: $founded})",
                    **company
                )
            
            # Create people
            people_data = [
                {"name": "Sundar Pichai", "role": "CEO", "company": "Google"},
                {"name": "Tim Cook", "role": "CEO", "company": "Apple"},
                {"name": "Satya Nadella", "role": "CEO", "company": "Microsoft"},
                {"name": "Elon Musk", "role": "CEO", "company": "Tesla"},
                {"name": "Sam Altman", "role": "CEO", "company": "OpenAI"},
                {"name": "Mark Zuckerberg", "role": "CEO", "company": "Meta"},
                {"name": "Andy Jassy", "role": "CEO", "company": "Amazon"},
                {"name": "Reed Hastings", "role": "Co-CEO", "company": "Netflix"}
            ]
            
            for person in people_data:
                # Create person
                session.run(
                    "CREATE (:Person {name: $name, role: $role})",
                    name=person["name"], role=person["role"]
                )
                # Create relationship with company
                session.run(
                    """
                    MATCH (p:Person {name: $person_name}), (c:Company {name: $company_name})
                    CREATE (p)-[:WORKS_AT]->(c)
                    """,
                    person_name=person["name"], company_name=person["company"]
                )
            
            # Create topics and discussions
            topics_data = [
                {"name": "Artificial Intelligence", "description": "AI research and development"},
                {"name": "Machine Learning", "description": "ML algorithms and applications"},
                {"name": "Cloud Computing", "description": "Cloud infrastructure and services"},
                {"name": "Electric Vehicles", "description": "EV technology and market"},
                {"name": "Social Media", "description": "Social networking platforms"},
                {"name": "Streaming Technology", "description": "Video streaming and content delivery"},
                {"name": "E-commerce", "description": "Online retail and marketplace"},
                {"name": "Mobile Technology", "description": "Smartphones and mobile apps"}
            ]
            
            for topic in topics_data:
                session.run(
                    "CREATE (:Topic {name: $name, description: $description})",
                    **topic
                )
            
            # Create relationships between companies and topics
            company_topic_relations = [
                ("Google", "Artificial Intelligence", "RESEARCHES"),
                ("Google", "Cloud Computing", "PROVIDES"),
                ("Apple", "Mobile Technology", "DEVELOPS"),
                ("Microsoft", "Cloud Computing", "PROVIDES"),
                ("Microsoft", "Artificial Intelligence", "RESEARCHES"),
                ("Tesla", "Electric Vehicles", "MANUFACTURES"),
                ("OpenAI", "Artificial Intelligence", "RESEARCHES"),
                ("OpenAI", "Machine Learning", "DEVELOPS"),
                ("Meta", "Social Media", "OPERATES"),
                ("Meta", "Artificial Intelligence", "RESEARCHES"),
                ("Amazon", "E-commerce", "OPERATES"),
                ("Amazon", "Cloud Computing", "PROVIDES"),
                ("Netflix", "Streaming Technology", "PROVIDES")
            ]
            
            for company, topic, relation in company_topic_relations:
                session.run(
                    f"""
                    MATCH (c:Company {{name: $company}}), (t:Topic {{name: $topic}})
                    CREATE (c)-[:{relation}]->(t)
                    """,
                    company=company, topic=topic
                )
            
            # Create some collaboration relationships
            collaborations = [
                ("Google", "OpenAI", "COLLABORATES_WITH"),
                ("Microsoft", "OpenAI", "PARTNERS_WITH"),
                ("Apple", "Google", "COMPETES_WITH"),
                ("Tesla", "Google", "COLLABORATES_WITH"),
                ("Meta", "Microsoft", "COMPETES_WITH")
            ]
            
            for company1, company2, relation in collaborations:
                session.run(
                    f"""
                    MATCH (c1:Company {{name: $company1}}), (c2:Company {{name: $company2}})
                    CREATE (c1)-[:{relation}]->(c2)
                    """,
                    company1=company1, company2=company2
                )
            
        logger.info("Sample data created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create sample data: {e}")
        raise

def verify_data():
    """Verify that data was loaded correctly"""
    try:
        with db.driver.session() as session:
            # Count nodes
            result = session.run("MATCH (n) RETURN labels(n) as label, count(n) as count")
            logger.info("Data verification:")
            for record in result:
                logger.info(f"  {record['label'][0] if record['label'] else 'Unknown'}: {record['count']} nodes")
            
            # Count relationships
            result = session.run("MATCH ()-[r]->() RETURN type(r) as rel_type, count(r) as count")
            logger.info("Relationships:")
            for record in result:
                logger.info(f"  {record['rel_type']}: {record['count']} relationships")
                
    except Exception as e:
        logger.error(f"Failed to verify data: {e}")
        raise

def load_sample_data():
    """Main function to load sample data"""
    logger.info("Starting sample data loading...")
    
    try:
        # Test database connection
        health = db.health_check()
        if health["status"] != "ok":
            raise Exception(f"Database health check failed: {health}")
        
        # Clear and load data
        clear_database()
        create_sample_data()
        verify_data()
        
        logger.info("Sample data loading completed successfully!")
        
    except Exception as e:
        logger.error(f"Sample data loading failed: {e}")
        raise
    finally:
        # Close database connection
        db.close()

if __name__ == "__main__":
    load_sample_data()