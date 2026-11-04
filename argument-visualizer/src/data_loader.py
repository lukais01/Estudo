import json
from pathlib import Path
from src.models import Argument, Relation
from src.toulmin import normalize_component

KNOWN = {"id", "text", "author", "type", "stance", "component", "toulmin_component", "qualifier"}

def load_data(file_source):
    if hasattr(file_source, "read"):
        raw = file_source.read()
        if isinstance(raw, bytes): raw = raw.decode("utf-8")
        data = json.loads(raw)
    else:
        with Path(file_source).open("r", encoding="utf-8") as f: data = json.load(f)
    if not isinstance(data, dict): raise ValueError("O JSON precisa conter um objeto.")
    if not isinstance(data.get("metadata", {}), dict): raise ValueError("metadata precisa ser um objeto.")
    if not isinstance(data.get("arguments"), list) or not data["arguments"]:
        raise ValueError("arguments precisa ser uma lista não vazia.")
    if not isinstance(data.get("relations", []), list): raise ValueError("relations precisa ser uma lista.")

    arguments, relations, ids = [], [], set()
    for i, item in enumerate(data["arguments"], 1):
        if not isinstance(item, dict): raise ValueError(f"Argumento {i} precisa ser um objeto.")
        aid, text = item.get("id"), item.get("text")
        if not isinstance(aid, str) or not aid.strip(): raise ValueError(f"ID inválido no argumento {i}.")
        if aid in ids: raise ValueError(f"ID duplicado: {aid}")
        if not isinstance(text, str) or not text.strip(): raise ValueError(f"Texto inválido em {aid}.")
        stance = item.get("stance") or ""
        if not isinstance(stance, str): raise ValueError(f"stance precisa ser texto em {aid}.")
        raw_component = item.get("toulmin_component") or item.get("component") or item.get("type") or "claim"
        if not isinstance(raw_component, str): raise ValueError(f"Componente Toulmin inválido em {aid}.")
        qualifier = item.get("qualifier") or ""
        if not isinstance(qualifier, str): raise ValueError(f"qualifier precisa ser texto em {aid}.")
        ids.add(aid)
        component = normalize_component(raw_component)
        arguments.append(Argument(
            id=aid, text=text.strip(), author=str(item.get("author") or ""),
            argument_type=str(item.get("type") or component), stance=stance.strip().lower(),
            toulmin_component=component, qualifier=qualifier,
            metadata={k:v for k,v in item.items() if k not in KNOWN}
        ))
    for i, item in enumerate(data.get("relations", []), 1):
        if not isinstance(item, dict): raise ValueError(f"Relação {i} precisa ser um objeto.")
        source, target = item.get("source"), item.get("target")
        if source not in ids or target not in ids:
            raise ValueError(f"Relação aponta para argumento inexistente: {source} -> {target}")
        kind = item.get("type", "supports")
        if not isinstance(kind, str) or not kind.strip(): raise ValueError(f"Tipo de relação inválido na posição {i}.")
        relations.append(Relation(source, target, kind.strip().lower()))
    return data.get("metadata", {}), arguments, relations
