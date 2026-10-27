
import json
from pathlib import Path

from src.models import Argument, Relation


def load_data(file_source):
    if hasattr(file_source, "read"):
        data = json.load(file_source)
    else:
        with Path(file_source).open("r", encoding="utf-8") as file:
            data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("O JSON precisa conter um objeto.")

    if not isinstance(data.get("arguments"), list):
        raise ValueError("Campo 'arguments' inválido.")

    if not isinstance(data.get("relations", []), list):
        raise ValueError("Campo 'relations' inválido.")

    arguments = []
    relations = []
    seen_ids = set()

    for item in data["arguments"]:
        argument_id = item["id"]

        if not isinstance(argument_id, str) or not argument_id:
            raise ValueError("ID de argumento inválido.")

        if argument_id in seen_ids:
            raise ValueError(f"ID duplicado: {argument_id}")

        if not isinstance(item.get("text"), str):
            raise ValueError(f"Texto inválido: {argument_id}")

        seen_ids.add(argument_id)

        known = {"id", "text", "author", "type", "stance"}

        arguments.append(
            Argument(
                id=argument_id,
                text=item["text"],
                author=item.get("author", ""),
                argument_type=item.get("type", "claim"),
                stance=item.get("stance", ""),
                metadata={
                    key: value
                    for key, value in item.items()
                    if key not in known
                },
            )
        )

    for item in data.get("relations", []):
        source = item.get("source")
        target = item.get("target")

        if source not in seen_ids or target not in seen_ids:
            raise ValueError(
                f"Relação com argumento inexistente: {source} -> {target}"
            )

        relations.append(
            Relation(
                source=source,
                target=target,
                relation_type=item.get("type", "supports"),
            )
        )

    return data.get("metadata", {}), arguments, relations
