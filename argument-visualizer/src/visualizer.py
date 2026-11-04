"""Exportação estática opcional do grafo com Matplotlib."""
import matplotlib.pyplot as plt
import networkx as nx
from src.toulmin import component_color

def draw_graph(graph, selected_node=None):
    if graph.number_of_nodes() == 0: raise ValueError("Não há argumentos para visualizar.")
    layout_graph = nx.DiGraph(graph)
    pos = nx.spring_layout(layout_graph, seed=42, k=1.2)
    fig, ax = plt.subplots(figsize=(15, 9))
    colors = ["#FFD166" if n == selected_node else component_color(a.get("toulmin_component", ""))
              for n, a in graph.nodes(data=True)]
    nx.draw_networkx_nodes(graph, pos, node_color=colors, node_size=1800,
                           edgecolors="#344054", linewidths=1.2, ax=ax)
    labels = {n: f"{n}\n{a.get('text', '')[:45]}" for n, a in graph.nodes(data=True)}
    nx.draw_networkx_labels(graph, pos, labels=labels, font_size=8, ax=ax)
    nx.draw_networkx_edges(graph, pos, arrows=True, arrowsize=18, width=1.8,
                           connectionstyle="arc3,rad=0.08", ax=ax)
    ax.set_title("Mapa de argumentos — modelo de Toulmin")
    ax.axis("off")
    fig.tight_layout()
    return fig
