"""Vocabulário e convenções visuais dos elementos de Toulmin."""
TOULMIN_LABELS = {
    "claim": "Claim / Conclusão",
    "grounds": "Grounds / Dados",
    "warrant": "Warrant / Garantia",
    "backing": "Backing / Apoio à garantia",
    "qualifier": "Qualifier / Qualificador",
    "rebuttal": "Rebuttal / Refutação",
}
ALIASES = {
    "claim": "claim", "conclusion": "claim", "thesis": "claim",
    "grounds": "grounds", "ground": "grounds", "data": "grounds", "evidence": "grounds", "fact": "grounds",
    "warrant": "warrant", "guarantee": "warrant", "rule": "warrant",
    "backing": "backing", "supporting_theory": "backing",
    "qualifier": "qualifier", "qualification": "qualifier",
    "rebuttal": "rebuttal", "counterargument": "rebuttal", "reservation": "rebuttal",
}
COLORS = {
    "claim": "#F4C95D", "grounds": "#83C5BE", "warrant": "#90A8ED",
    "backing": "#B8A1D9", "qualifier": "#F2B880", "rebuttal": "#E58C9A",
}
SHAPES = {
    "claim": "star", "grounds": "dot", "warrant": "diamond",
    "backing": "hexagon", "qualifier": "triangle", "rebuttal": "square",
}

def normalize_component(value):
    key = str(value or "claim").strip().lower().replace("-", "_").replace(" ", "_")
    return ALIASES.get(key, key)

def component_color(component):
    return COLORS.get(component, "#AAB2BD")

def component_shape(component):
    return SHAPES.get(component, "dot")
