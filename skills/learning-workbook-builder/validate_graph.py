#!/usr/bin/env python3
"""Validate and topologically order a learning prerequisite graph.

The deterministic core of the learning-workbook-builder skill. The agent builds
the prerequisite graph (judgment); THIS script verifies and orders it (mechanics),
so the structural guarantees are *executed*, not performed by the model in its head.

Usage:
    python3 validate_graph.py graph.json

Input JSON:
{
  "nodes": [
    {"id": "estimators",
     "concept": "Bias, variance, MSE of an estimator",
     "weight": "high",            # core | high | medium
     "delta": "refresher",        # biggest-gap | new | new-ish | refresher
     "threshold": false,          # is this a threshold/gateway concept?
     "provenance": ["https://...", "artifact:cell_47"]}
  ],
  "edges": [
    {"prereq": "estimators", "concept": "cvar", "provenance": ["https://..."]}
  ]
}

Edge semantics: `prereq` must be taught BEFORE `concept`.

Exits 0 and prints the teaching order on success; exits 1 and prints every
problem on failure. The order is deterministic: ready nodes are emitted by
(weight rank, delta rank, id), so high-weight / high-gap concepts come first
and re-runs are byte-identical.
"""
import json
import sys
from collections import defaultdict

WEIGHT_RANK = {"core": 0, "high": 1, "medium": 2}
DELTA_RANK = {"biggest-gap": 0, "new": 1, "new-ish": 2, "refresher": 3}


def fail(errors):
    print("GRAPH INVALID — fix the graph, do not hand-edit the order:\n")
    for e in errors:
        print("  - " + e)
    sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("usage: python3 validate_graph.py graph.json", file=sys.stderr)
        sys.exit(2)

    with open(sys.argv[1]) as f:
        g = json.load(f)

    nodes = {n["id"]: n for n in g.get("nodes", [])}
    edges = g.get("edges", [])
    errors = []

    if not nodes:
        fail(["no nodes in graph"])

    # 1. every node carries provenance and valid weight/delta
    for nid, n in nodes.items():
        if not n.get("provenance"):
            errors.append(
                f"node '{nid}' has no provenance — every concept must cite a "
                f"fetched source or the artifact"
            )
        if n.get("weight") not in WEIGHT_RANK:
            errors.append(f"node '{nid}' invalid weight {n.get('weight')!r} (core/high/medium)")
        if n.get("delta") not in DELTA_RANK:
            errors.append(
                f"node '{nid}' invalid delta {n.get('delta')!r} "
                f"(biggest-gap/new/new-ish/refresher)"
            )

    # 2. every edge references real nodes and carries provenance
    for e in edges:
        for end in ("prereq", "concept"):
            if e.get(end) not in nodes:
                errors.append(
                    f"edge {e.get('prereq')!r}->{e.get('concept')!r} references "
                    f"unknown node {e.get(end)!r}"
                )
        if not e.get("provenance"):
            errors.append(f"edge {e.get('prereq')!r}->{e.get('concept')!r} has no provenance")

    if errors:
        fail(errors)

    # 3. cycle detection + deterministic topological order (Kahn's algorithm)
    indeg = {nid: 0 for nid in nodes}
    adj = defaultdict(list)
    for e in edges:
        adj[e["prereq"]].append(e["concept"])
        indeg[e["concept"]] += 1

    def sort_key(nid):
        n = nodes[nid]
        return (WEIGHT_RANK[n["weight"]], DELTA_RANK[n["delta"]], nid)

    ready = sorted([nid for nid, d in indeg.items() if d == 0], key=sort_key)
    order = []
    while ready:
        nid = ready.pop(0)
        order.append(nid)
        for m in adj[nid]:
            indeg[m] -= 1
            if indeg[m] == 0:
                ready.append(m)
        ready.sort(key=sort_key)

    if len(order) != len(nodes):
        stuck = [nid for nid, d in indeg.items() if d > 0]
        fail([f"cycle detected — these concepts are in a prerequisite loop: {', '.join(sorted(stuck))}"])

    # success
    print(f"GRAPH OK — {len(nodes)} concepts, {len(edges)} prerequisite edges.")
    thresh = [nid for nid in order if nodes[nid].get("threshold")]
    if thresh:
        print(f"threshold concepts (teach with most care): {', '.join(thresh)}")
    print("\nteaching order:")
    for i, nid in enumerate(order, 1):
        n = nodes[nid]
        flag = " *threshold*" if n.get("threshold") else ""
        print(f"  {i:>2}. {nid}  [{n['weight']}/{n['delta']}]{flag}  — {n['concept']}")


if __name__ == "__main__":
    main()
