from neo4j import GraphDatabase
import os

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "test12345")
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

companies = [
    {"name": "OpenAI", "industry": "AI"},
    {"name": "Google", "industry": "Tech"},
    {"name": "Tesla", "industry": "Automotive"},
]

news = [
    {"title": "OpenAI launches new model", "topic": "AI", "companies": ["OpenAI"]},
    {"title": "Google invests in AI", "topic": "AI", "companies": ["Google", "OpenAI"]},
    {"title": "Tesla unveils new car", "topic": "Automotive", "companies": ["Tesla"]},
]

def load_data():
    with driver.session() as session:
        # Clear existing data
        session.run("MATCH (n) DETACH DELETE n")
        # Create companies
        for c in companies:
            session.run(
                "CREATE (:Company {name: $name, industry: $industry})",
                name=c["name"], industry=c["industry"]
            )
        # Create news and relationships
        for n in news:
            session.run(
                "CREATE (news:News {title: $title, topic: $topic})",
                title=n["title"], topic=n["topic"]
            )
            for company in n["companies"]:
                session.run(
                    "MATCH (c:Company {name: $company}), (news:News {title: $title}) "
                    "CREATE (c)-[:MENTIONED_IN]->(news)",
                    company=company, title=n["title"]
                )
    print("Sample data loaded.")

if __name__ == "__main__":
    load_data() 