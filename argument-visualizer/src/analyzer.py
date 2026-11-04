from collections import Counter
import networkx as nx

def analyze_graph(graph):
    # Densidade sobre pares direcionados distintos; evita >1 em MultiDiGraph com arestas paralelas.
    simple = nx.DiGraph()
    simple.add_nodes_from(graph.nodes())
    simple.add_edges_from((u, v) for u, v in graph.edges())
    isolated = list(nx.isolates(graph))
    components = Counter(a.get("toulmin_component", "unclassified") for _, a in graph.nodes(data=True))
    centrality = nx.degree_centrality(simple) if graph.number_of_nodes() > 1 else {n: 0.0 for n in graph}
    return {
        "arguments": graph.number_of_nodes(), "relations": graph.number_of_edges(),
        "isolated_arguments": isolated, "isolated_count": len(isolated),
        "density": nx.density(simple), "in_degree": dict(graph.in_degree()),
        "out_degree": dict(graph.out_degree()), "degree_centrality": centrality,
        "component_counts": dict(components), "components_used": len(components),
    }
