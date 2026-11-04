import networkx as nx

def build_graph(arguments, relations):
    """Cada argumento vira nó; cada relação vira aresta direcionada."""
    graph = nx.MultiDiGraph()
    for a in arguments:
        graph.add_node(a.id, text=a.text, author=a.author, argument_type=a.argument_type,
                       stance=a.stance, toulmin_component=a.toulmin_component,
                       qualifier=a.qualifier, metadata=a.metadata)
    for r in relations:
        graph.add_edge(r.source, r.target, relation_type=r.relation_type)
    return graph
