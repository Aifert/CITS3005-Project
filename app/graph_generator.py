import networkx as nx
from pyvis.network import Network
from rdflib import Graph


def generate_knowledge_graph(kg):
    G = nx.Graph()
    for s, p, o in kg.graph:
        G.add_edge(str(s), str(o), label=str(p))

    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
    net.from_nx(G)
    net.save_graph("app/static/knowledge_graph.html")
