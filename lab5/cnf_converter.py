import json
import sys
from itertools import combinations


def to_internal(raw):
    vn = set(raw["VN"])
    vt = set(raw["VT"])
    s = raw["S"]
    p = {}
    for lhs, rhs_list in raw["P"].items():
        rules = set()
        for rhs in rhs_list:
            rules.add(tuple(rhs))
        if rules:
            p[lhs] = rules
    return {"VN": vn, "VT": vt, "S": s, "P": p}


def to_external(g):
    out_p = {}
    for lhs in sorted(g["P"]):
        rules = sorted(g["P"][lhs])
        out_p[lhs] = [list(rhs) for rhs in rules]
    return {
        "VN": sorted(g["VN"]),
        "VT": sorted(g["VT"]),
        "S": g["S"],
        "P": out_p,
    }


def clone_grammar(g):
    return {
        "VN": set(g["VN"]),
        "VT": set(g["VT"]),
        "S": g["S"],
        "P": {lhs: set(rules) for lhs, rules in g["P"].items()},
    }


def eliminate_epsilon(g):
    g = clone_grammar(g)
    vn = g["VN"]
    p = g["P"]

    nullable = set()
    changed = True
    while changed:
        changed = False
        for lhs, rules in p.items():
            if lhs in nullable:
                continue
            for rhs in rules:
                if len(rhs) == 0:
                    nullable.add(lhs)
                    changed = True
                    break
                ok = True
                for sym in rhs:
                    if sym not in vn or sym not in nullable:
                        ok = False
                        break
                if ok:
                    nullable.add(lhs)
                    changed = True
                    break

    new_p = {}
    for lhs, rules in p.items():
        built = set()
        for rhs in rules:
            if len(rhs) == 0:
                continue
            nullable_pos = [i for i, sym in enumerate(rhs) if sym in nullable]
            for r in range(len(nullable_pos) + 1):
                for combo in combinations(nullable_pos, r):
                    skip = set(combo)
                    cand = tuple(sym for i, sym in enumerate(rhs) if i not in skip)
                    if len(cand) > 0:
                        built.add(cand)
        if built:
            new_p[lhs] = built

    g["P"] = new_p
    return g


def eliminate_unit(g):
    g = clone_grammar(g)
    vn = g["VN"]
    p = g["P"]

    unit_graph = {a: set() for a in vn}
    for a in vn:
        for rhs in p.get(a, set()):
            if len(rhs) == 1 and rhs[0] in vn:
                unit_graph[a].add(rhs[0])

    closure = {}
    for a in vn:
        seen = {a}
        stack = [a]
        while stack:
            x = stack.pop()
            for y in unit_graph.get(x, set()):
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        closure[a] = seen

    new_p = {}
    for a in vn:
        rules = set()
        for b in closure[a]:
            for rhs in p.get(b, set()):
                if len(rhs) == 1 and rhs[0] in vn:
                    continue
                rules.add(rhs)
        if rules:
            new_p[a] = rules

    g["P"] = new_p
    return g


def eliminate_inaccessible(g):
    g = clone_grammar(g)
    vn = g["VN"]
    p = g["P"]
    start = g["S"]

    reachable = {start}
    changed = True
    while changed:
        changed = False
        for lhs in list(reachable):
            for rhs in p.get(lhs, set()):
                for sym in rhs:
                    if sym in vn and sym not in reachable:
                        reachable.add(sym)
                        changed = True

    new_p = {}
    for lhs in reachable:
        rules = p.get(lhs, set())
        if rules:
            new_p[lhs] = set(rules)

    g["VN"] = reachable
    g["P"] = new_p
    return g


def eliminate_nonproductive(g):
    g = clone_grammar(g)
    vn = g["VN"]
    vt = g["VT"]
    p = g["P"]

    productive = set()
    changed = True
    while changed:
        changed = False
        for lhs, rules in p.items():
            if lhs in productive:
                continue
            for rhs in rules:
                ok = True
                for sym in rhs:
                    if sym in vt:
                        continue
                    if sym in vn and sym in productive:
                        continue
                    ok = False
                    break
                if ok:
                    productive.add(lhs)
                    changed = True
                    break

    new_p = {}
    for lhs in productive:
        built = set()
        for rhs in p.get(lhs, set()):
            ok = True
            for sym in rhs:
                if sym in vt:
                    continue
                if sym in productive:
                    continue
                ok = False
                break
            if ok:
                built.add(rhs)
        if built:
            new_p[lhs] = built

    g["VN"] = productive
    g["P"] = new_p
    return g


def to_cnf(g):
    g = clone_grammar(g)
    vn = set(g["VN"])
    vt = g["VT"]
    p = g["P"]

    new_p = {}

    def add_rule(lhs, rhs):
        new_p.setdefault(lhs, set()).add(tuple(rhs))

    term_map = {}
    n_counter = 1

    def fresh_n():
        nonlocal n_counter
        while True:
            name = f"N{n_counter}"
            n_counter += 1
            if name not in vn and name not in vt and name not in term_map.values():
                vn.add(name)
                return name

    def term_nt(t):
        if t in term_map:
            return term_map[t]
        base = "T_" + "".join(ch if ch.isalnum() else "_" for ch in t)
        if base == "T_":
            base = "T"
        name = base
        i = 1
        while name in vn or name in vt:
            name = f"{base}_{i}"
            i += 1
        vn.add(name)
        term_map[t] = name
        add_rule(name, (t,))
        return name

    for lhs, rules in p.items():
        for rhs in rules:
            if len(rhs) == 1 and rhs[0] in vt:
                add_rule(lhs, rhs)
                continue

            if len(rhs) >= 2:
                tokens = list(rhs)
                for i, sym in enumerate(tokens):
                    if sym in vt:
                        tokens[i] = term_nt(sym)

                if len(tokens) == 2:
                    add_rule(lhs, tuple(tokens))
                else:
                    cur = lhs
                    for i in range(len(tokens) - 2):
                        nxt = fresh_n()
                        add_rule(cur, (tokens[i], nxt))
                        cur = nxt
                    add_rule(cur, (tokens[-2], tokens[-1]))

    g["VN"] = vn
    g["P"] = new_p
    return g


def main():
    path = "grammar.json"
    if len(sys.argv) > 1:
        path = sys.argv[1]

    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    g = to_internal(raw)
    g = eliminate_epsilon(g)
    g = eliminate_unit(g)
    g = eliminate_inaccessible(g)
    g = eliminate_nonproductive(g)
    g = to_cnf(g)

    print(json.dumps(to_external(g), indent=2))


if __name__ == "__main__":
    main()
