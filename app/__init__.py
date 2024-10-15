from flask import Flask
from app.ontology_loader import load_ontology, demonstrate_reasoning
from app.knowledge_graph import KnowledgeGraph
from app.query_engine import QueryEngine
import logging
from app.graph_generator import generate_knowledge_graph

app = Flask(__name__)

ontology = load_ontology('ontology/ifixit_ontology.owl')
if ontology is None:
    logging.error("Failed to load ontology. Exiting.")
    exit(1)

kg = KnowledgeGraph()
kg.load_data('data/Mac.json')

reasoned_ontology, reasoning_results = demonstrate_reasoning(ontology, kg)

kg.graph.serialize(destination='knowledge_graph.rdf', format='xml')
kg.graph.serialize(destination='knowledge_graph.ttl', format='turtle')

query_engine = QueryEngine(kg.graph)

app.config['REASONING_RESULTS'] = reasoning_results


generate_knowledge_graph(kg)

from app import routes
