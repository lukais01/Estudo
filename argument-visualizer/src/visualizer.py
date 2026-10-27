
import matplotlib.pyplot as plt
import networkx as nx


def draw_graph(graph, selected_node=None):
    if graph.number_of_nodes() == 0:
        raise ValueError("Não há argumentos para visualizar.")

    positions = nx.spring_layout(graph, seed=42)

    node_colors = []

    for node, attributes in graph.nodes(data=True):
        if node == selected_node:
            node_colors.append("gold")
        elif attributes.get("stance") == "pro":
            node_colors.append("lightgreen")
        elif attributes.get("stance") == "con":
            node_colors.append("lightcoral")
        else:
            node_colors.append("lightblue")

    edge_colors = []

    for _, _, attributes in graph.edges(data=True):
        relation_type = attributes.get("relation_type", "")

        if relation_type in ("attacks", "rebuts"):
            edge_colors.append("red")
        else:
            edge_colors.append("green")

    fig, ax = plt.subplots(figsize=(14, 9))

    nx.draw_networkx_nodes(
        graph,
        positions,
        node_color=node_colors,
        node_size=2400,
        edgecolors="black",
        ax=ax,
    )

    labels = {
        node: f"{node}\n{attributes.get('text', '')[:55]}"
        for node, attributes in graph.nodes(data=True)
    }

    nx.draw_networkx_labels(
        graph,
        positions,
        labels=labels,
        font_size=8,
        ax=ax,
    )

    nx.draw_networkx_edges(
        graph,
        positions,
        edge_color=edge_colors,
        arrows=True,
        arrowsize=20,
        width=2,
        ax=ax,
    )

    edge_labels = {
        (source, target): attributes.get("relation_type", "")
        for source, target, attributes in graph.edges(data=True)
    }

    nx.draw_networkx_edge_labels(
        graph,
        positions,
        edge_labels=edge_labels,
        font_size=8,
        ax=ax,
    )

    ax.set_title("Rede de argumentos")
    ax.axis("off")
    fig.tight_layout()

    return fig
