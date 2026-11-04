from src.data_loader import load_data
from src.graph_builder import build_graph
from src.analyzer import analyze_graph

def test_sample_json():
    metadata, arguments, relations = load_data("data/exemplo_toulmin.json")
    graph = build_graph(arguments, relations)
    metrics = analyze_graph(graph)
    assert metadata["title"]
    assert graph.number_of_nodes() == 7
    assert graph.number_of_edges() == 6
    assert graph.nodes["D1"]["toulmin_component"] == "grounds"
    assert metrics["components_used"] == 6
