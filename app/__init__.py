from flask import Flask
from app.ontology_loader import load_ontology
from app.knowledge_graph import KnowledgeGraph
from app.query_engine import QueryEngine

app = Flask(__name__)

ontology = load_ontology('ontology/ifixit_ontology.owl')
kg = KnowledgeGraph()
kg.load_data('data/Mac.json')

kg.graph.serialize(destination='knowledge_graph.rdf', format='xml')

kg.graph.serialize(destination='knowledge_graph.ttl', format='turtle')
query_engine = QueryEngine(kg.graph)

from app import routes
