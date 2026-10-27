
import networkx as nx


def build_graph(arguments, relations):
    graph = nx.MultiDiGraph()

    for argument in arguments:
        graph.add_node(
            argument.id,
            text=argument.text,
            author=argument.author,
            argument_type=argument.argument_type,
            stance=argument.stance,
        )

    for relation in relations:
        graph.add_edge(
            relation.source,
            relation.target,
            relation_type=relation.relation_type,
        )

    return graph
