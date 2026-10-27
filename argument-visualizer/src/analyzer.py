
import networkx as nx


def analyze_graph(graph):
    return {
        "arguments": graph.number_of_nodes(),
        "relations": graph.number_of_edges(),
        "isolated_arguments": list(nx.isolates(graph)),
        "density": nx.density(graph),
        "in_degree": dict(graph.in_degree()),
        "out_degree": dict(graph.out_degree()),
    }
