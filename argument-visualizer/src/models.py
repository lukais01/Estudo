from dataclasses import dataclass, field

@dataclass
class Argument:
    id: str
    text: str
    author: str = ""
    argument_type: str = "claim"
    stance: str = ""
    toulmin_component: str = "claim"
    qualifier: str = ""
    metadata: dict = field(default_factory=dict)

@dataclass
class Relation:
    source: str
    target: str
    relation_type: str = "supports"
