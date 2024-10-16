import networkx as nx
from pyvis.network import Network
from rdflib import Graph, URIRef


def generate_knowledge_graph(kg):
    G = nx.Graph()
    for s, p, o in kg.graph:
        G.add_edge(str(s), str(o), label=str(p))

    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
    net.from_nx(G)
    net.save_graph("app/static/knowledge_graph.html")


def generate_query_graph(kg, query_results):
    G = nx.Graph()

    for uri in query_results:
        # Add the node for the current URI
        G.add_node(str(uri), label=str(uri).split('/')[-1])

        # Get all triples where this URI is the subject
        for s, p, o in kg.graph.triples((URIRef(uri), None, None)):
            G.add_edge(str(s), str(o), label=str(p).split('/')[-1])

        # Get all triples where this URI is the object
        for s, p, o in kg.graph.triples((None, None, URIRef(uri))):
            G.add_edge(str(s), str(o), label=str(p).split('/')[-1])

    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
    net.from_nx(G)
    net.show_buttons(filter_=['physics'])
    net.save_graph("app/static/query_graph.html")
