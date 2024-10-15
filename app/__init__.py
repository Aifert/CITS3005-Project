from flask import Flask
from app.ontology_loader import load_ontology, demonstrate_reasoning
from app.knowledge_graph import KnowledgeGraph
from app.query_engine import QueryEngine
import logging

app = Flask(__name__)

ontology = load_ontology('ontology/ifixit_ontology.owl')
if ontology is None:
    logging.error("Failed to load ontology. Exiting.")
    exit(1)

kg = KnowledgeGraph()
kg.load_data('data/Mac.json')

reasoned_ontology, reasoning_results = demonstrate_reasoning(ontology, kg)

# Print reasoning results
print("\n--- Reasoning Results ---")
print(f"Total Procedures: {len(reasoning_results.get('AllProcedures', []))}")
print(f"Caution Procedures: {len(reasoning_results.get('CautionProcedures', []))}")
print("Caution Procedures List:")
for proc in reasoning_results.get('CautionProcedures', []):
    print(f"  - {proc}")
print("\nSteps with Caution:")
for step_name, step_text in reasoning_results.get('StepsWithCaution', []):
    print(f"  - {step_name}: {step_text}")

kg.graph.serialize(destination='knowledge_graph.rdf', format='xml')
kg.graph.serialize(destination='knowledge_graph.ttl', format='turtle')

query_engine = QueryEngine(kg.graph)

app.config['REASONING_RESULTS'] = reasoning_results

from app import routes
