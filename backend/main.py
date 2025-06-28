from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse

load_dotenv()
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from anthropic import Anthropic
from typing import List, Dict, Any

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Neo4j connection
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "test12345")
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

class SearchQuery(BaseModel):
    query: str
    max_results: int = 5

@app.get("/health")
def health_check():
    try:
        with driver.session() as session:
            result = session.run("RETURN 1 AS result")
            return {"status": "ok", "db": result.single()["result"]}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/graph")
def get_graph():
    try:
        with driver.session() as session:
            # Get nodes
            nodes_result = session.run("""
                MATCH (n)
                RETURN id(n) as id, labels(n) as labels, n.name as name, n.title as title, n.industry as industry, n.topic as topic
            """)
            nodes = []
            for record in nodes_result:
                label = record["labels"][0] if record["labels"] else "Node"
                node = {
                    "id": record["id"],
                    "label": record["name"] or record["title"] or label,
                    "group": label,
                }
                nodes.append(node)
            # Get edges
            edges_result = session.run("""
                MATCH (a)-[r]->(b)
                RETURN id(a) as from, id(b) as to, type(r) as label
            """)
            edges = []
            for record in edges_result:
                edges.append({
                    "from": record["from"],
                    "to": record["to"],
                    "label": record["label"],
                })
            return JSONResponse({"nodes": nodes, "edges": edges})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

def get_node_embeddings():
    with driver.session() as session:
        result = session.run("""
            MATCH (n)
            RETURN id(n) as id, labels(n) as labels, 
                   n.name as name, n.title as title, 
                   n.industry as industry, n.topic as topic
        """)
        
        node_data = []
        for record in result:
            text_content = ""
            if record["name"]:
                text_content += f"Name: {record['name']} "
            if record["title"]:
                text_content += f"Title: {record['title']} "
            if record["industry"]:
                text_content += f"Industry: {record['industry']} "
            if record["topic"]:
                text_content += f"Topic: {record['topic']} "
            
            label = record["labels"][0] if record["labels"] else "Node"
            text_content += f"Type: {label}"
            
            node_data.append({
                "id": record["id"],
                "text": text_content.strip(),
                "labels": record["labels"],
                "name": record["name"],
                "title": record["title"],
                "industry": record["industry"],
                "topic": record["topic"]
            })
        
        if not node_data:
            return [], []
        
        texts = [node["text"] for node in node_data]
        embeddings = embedding_model.encode(texts)
        
        return node_data, embeddings

def semantic_search(query: str, max_results: int = 5):
    node_data, embeddings = get_node_embeddings()
    
    if not node_data:
        return []
    
    query_embedding = embedding_model.encode([query])
    similarities = cosine_similarity(query_embedding, embeddings)[0]
    
    top_indices = np.argsort(similarities)[::-1][:max_results]
    
    results = []
    for idx in top_indices:
        if similarities[idx] > 0.1:
            node = node_data[idx]
            results.append({
                "node": node,
                "similarity": float(similarities[idx])
            })
    
    return results

def get_node_context(node_id: int):
    with driver.session() as session:
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

def generate_answer(query: str, search_results: List[Dict[Any, Any]]):
    if not search_results:
        return "No relevant information found in the knowledge graph."
    
    context_text = "Knowledge Graph Information:\\n\\n"
    
    for i, result in enumerate(search_results, 1):
        node = result["node"]
        similarity = result["similarity"]
        
        context_text += f"{i}. {node['text']} (Relevance: {similarity:.2f})\\n"
        
        node_context = get_node_context(node["id"])
        if node_context["relationships"]:
            context_text += "   Relationships:\\n"
            for rel in node_context["relationships"]:
                rel_text = f"   - {rel['type']}: "
                connected = rel["connected_node"]
                if 'name' in connected:
                    rel_text += connected['name']
                elif 'title' in connected:
                    rel_text += connected['title']
                context_text += rel_text + "\\n"
        context_text += "\\n"
    
    try:
        response = anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            temperature=0.3,
            system="You are a helpful assistant that answers questions based on the provided knowledge graph information. Use only the information provided and be concise and accurate.",
            messages=[
                {
                    "role": "user",
                    "content": f"Based on the following knowledge graph information, please answer this question: {query}\\n\\n{context_text}"
                }
            ]
        )
        
        return response.content[0].text
    except Exception as e:
        return f"Error generating answer: {str(e)}"

@app.post("/search")
def search_knowledge_graph(search_query: SearchQuery):
    try:
        search_results = semantic_search(search_query.query, search_query.max_results)
        
        if not search_results:
            return JSONResponse({
                "query": search_query.query,
                "results": [],
                "answer": "No relevant information found in the knowledge graph."
            })
        
        answer = generate_answer(search_query.query, search_results)
        
        return JSONResponse({
            "query": search_query.query,
            "results": search_results,
            "answer": answer
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 