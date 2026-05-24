from __future__ import annotations

import csv
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import networkx as nx


BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "Lord of the mysteries.csv"
JSON_PATH = BASE_DIR / "character_graph_data.json"
SEED = 42


def load_rows() -> list[dict[str, str]]:
    expected_columns = ["name1", "name2", "relation"]
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != expected_columns:
            raise ValueError(f"Unexpected columns: {reader.fieldnames!r}")

        rows: list[dict[str, str]] = []
        for row in reader:
            name1 = row["name1"].strip()
            name2 = row["name2"].strip()
            relation = row["relation"].strip() or "未标注"
            if not name1 or not name2:
                continue
            rows.append({"name1": name1, "name2": name2, "relation": relation})
        return rows


def build_graph(rows: list[dict[str, str]]) -> nx.Graph:
    graph = nx.Graph()
    for row in rows:
        source = row["name1"]
        target = row["name2"]
        relation = row["relation"]
        if graph.has_edge(source, target):
            graph[source][target]["weight"] += 1
            graph[source][target]["relations"][relation] = graph[source][target]["relations"].get(relation, 0) + 1
        else:
            graph.add_edge(source, target, weight=1, relations={relation: 1})
    return graph


def normalize_layout(graph: nx.Graph) -> dict[str, tuple[float, float]]:
    layout = nx.spring_layout(graph, seed=SEED, weight="weight", k=1.45 / math.sqrt(max(graph.number_of_nodes(), 2)))
    xs = [point[0] for point in layout.values()]
    ys = [point[1] for point in layout.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    normalized: dict[str, tuple[float, float]] = {}
    for node, (x, y) in layout.items():
        norm_x = (x - min_x) / (max_x - min_x) if max_x > min_x else 0.5
        norm_y = (y - min_y) / (max_y - min_y) if max_y > min_y else 0.5
        normalized[node] = (round(0.08 + norm_x * 0.84, 6), round(0.1 + norm_y * 0.8, 6))
    return normalized


def build_core_scores(graph: nx.Graph) -> dict[str, float]:
    weighted_degrees = {node: sum(data["weight"] for _, _, data in graph.edges(node, data=True)) for node in graph.nodes}
    log_values = [math.log1p(value) for value in weighted_degrees.values()]
    low = min(log_values)
    high = max(log_values)

    scores: dict[str, float] = {}
    for node, value in weighted_degrees.items():
        current = math.log1p(value)
        normalized = 1.0 if high <= low else (current - low) / (high - low)
        curved = normalized**0.8
        scores[node] = round(18 + curved * 78, 2)
    return scores


def export_graph(graph: nx.Graph) -> dict[str, object]:
    layout = normalize_layout(graph)
    core_scores = build_core_scores(graph)
    weighted_degrees = {node: sum(data["weight"] for _, _, data in graph.edges(node, data=True)) for node in graph.nodes}

    nodes = [
        {
            "id": node,
            "label": node,
            "x": layout[node][0],
            "y": layout[node][1],
            "degree": graph.degree(node),
            "weighted_degree": weighted_degrees[node],
            "core_score": core_scores[node],
        }
        for node in graph.nodes
    ]

    edges = []
    for source, target, data in graph.edges(data=True):
        relation_counts = Counter(data["relations"])
        edges.append(
            {
                "source": source,
                "target": target,
                "weight": data["weight"],
                "relations": dict(sorted(relation_counts.items(), key=lambda item: (-item[1], item[0]))),
            }
        )

    return {
        "nodes": nodes,
        "edges": edges,
        "meta": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "layout_seed": SEED,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        },
    }


def main() -> None:
    rows = load_rows()
    graph = build_graph(rows)
    payload = export_graph(graph)
    JSON_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {JSON_PATH}")


if __name__ == "__main__":
    main()
