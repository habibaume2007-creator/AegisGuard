"""Static analysis: call graph, SQL-injection sink detection, reachability."""
import ast
import networkx as nx

ROUTE_NAMES = {"route", "get", "post", "put", "delete"}
EXEC_NAMES = {"execute", "executemany", "executescript"}


def _call_name(call):
    f = call.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


def _is_route(fn):
    for d in fn.decorator_list:
        if isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and d.func.attr in ROUTE_NAMES:
            return True
    return False


def _functions(tree):
    return [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]


def build_call_graph(source: str) -> nx.DiGraph:
    """Nodes are functions; an edge A -> B means A calls B."""
    tree = ast.parse(source)
    funcs = _functions(tree)
    names = {f.name for f in funcs}
    G = nx.DiGraph()
    for f in funcs:
        G.add_node(f.name, route=_is_route(f), line=f.lineno)
    for f in funcs:
        for node in ast.walk(f):
            if isinstance(node, ast.Call):
                called = _call_name(node)
                if called in names and called != f.name:
                    G.add_edge(f.name, called)
    return G


def _is_dynamic_sql(expr, tainted):
    if isinstance(expr, ast.JoinedStr):                                   # f-string
        return True
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, (ast.Add, ast.Mod)):  # "a" + x, "a %s" % x
        return True
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) and expr.func.attr == "format":
        return True
    if isinstance(expr, ast.Name) and expr.id in tainted:
        return True
    return False


def _calls_in(fn) -> set:
    return {_call_name(n) for n in ast.walk(fn) if isinstance(n, ast.Call)}


def _is_sql_injection(fn) -> bool:
    tainted = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Assign) and _is_dynamic_sql(node.value, set()):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    tainted.add(t.id)
    for node in ast.walk(fn):
        if (isinstance(node, ast.Call) and _call_name(node) in EXEC_NAMES
                and node.args and _is_dynamic_sql(node.args[0], tainted)):
            return True
    return False


SAFE_PATH_CALLS = {"realpath", "resolve", "commonpath", "is_relative_to", "secure_filename", "basename"}
ESCAPE_CALLS = {"escape", "escape_silent", "quote"}


def _is_path_build(expr) -> bool:
    if isinstance(expr, ast.Call) and _call_name(expr) == "join":
        return True
    if isinstance(expr, ast.JoinedStr):
        return True
    return isinstance(expr, ast.BinOp) and isinstance(expr.op, (ast.Add, ast.Div))


def _is_path_traversal(fn) -> bool:
    """open() on a path built from other values, with no check that it stays in a folder."""
    if _calls_in(fn) & SAFE_PATH_CALLS:
        return False
    tainted = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Assign) and _is_path_build(node.value):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    tainted.add(t.id)
    for node in ast.walk(fn):
        if isinstance(node, ast.Call) and _call_name(node) == "open" and node.args:
            a = node.args[0]
            if _is_path_build(a) or (isinstance(a, ast.Name) and a.id in tainted):
                return True
    return False


def _builds_html(expr) -> bool:
    consts = [n.value for n in ast.walk(expr) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    has_tag = any("<" in c for c in consts)
    if isinstance(expr, ast.JoinedStr):
        return has_tag and any(isinstance(v, ast.FormattedValue) for v in expr.values)
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, (ast.Add, ast.Mod)):
        return has_tag and any(isinstance(n, (ast.Name, ast.Call, ast.Attribute)) for n in ast.walk(expr))
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) and expr.func.attr == "format":
        return has_tag
    return False


def _is_xss(fn) -> bool:
    """Returns HTML built from other values without any escaping call."""
    if _calls_in(fn) & ESCAPE_CALLS:
        return False
    return any(isinstance(n, ast.Return) and n.value is not None and _builds_html(n.value)
               for n in ast.walk(fn))


def _is_unsafe_deserialization(fn) -> bool:
    """Detect obvious pickle loads and yaml.load calls without a safe loader."""
    for node in ast.walk(fn):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Attribute):
            owner = node.func.value.id if isinstance(node.func.value, ast.Name) else None
            if owner == "pickle" and node.func.attr in {"load", "loads"}:
                return True
            if owner == "yaml" and node.func.attr == "load":
                has_safe_loader = any(
                    kw.arg == "Loader" and (
                        (isinstance(kw.value, ast.Attribute) and kw.value.attr in {"SafeLoader", "CSafeLoader"})
                        or (isinstance(kw.value, ast.Name) and kw.value.id in {"SafeLoader", "CSafeLoader"})
                    )
                    for kw in node.keywords
                )
                if not has_safe_loader:
                    return True
    return False


RULES = [("sql_injection", _is_sql_injection), ("path_traversal", _is_path_traversal), ("xss", _is_xss),
         ("unsafe_deserialization", _is_unsafe_deserialization)]


def find_vulns(source: str) -> list:
    """Returns [(vulnerability_type, function_name)] for every suspicious function."""
    tree = ast.parse(source)
    found = []
    for fn in _functions(tree):
        for vuln_type, check in RULES:
            if check(fn):
                found.append((vuln_type, fn.name))
    return found


def find_sinks(source: str) -> list:
    """Function names only (kept for older code)."""
    return [fn for _, fn in find_vulns(source)]


def paths_to(G: nx.DiGraph, sink: str) -> list:
    """Paths from route handlers (public entry points) down to the sink."""
    result = []
    for n, data in G.nodes(data=True):
        if data.get("route") and nx.has_path(G, n, sink):
            result.append(nx.shortest_path(G, n, sink))
    return result


def to_dot(G: nx.DiGraph, path=None) -> str:
    """Graphviz DOT text for st.graphviz_chart. The vulnerable path is highlighted."""
    hl = set(path or [])
    lines = ["digraph G {", "rankdir=LR;",
             'node [shape=box, style="rounded,filled", fontname="Helvetica"];']
    for n, d in G.nodes(data=True):
        color = "#f6c28b" if n in hl else ("#cfe3ff" if d.get("route") else "#eaeff6")
        lines.append(f'"{n}" [fillcolor="{color}"];')
    for a, b in G.edges:
        style = ' [color="#c0392b", penwidth=2]' if a in hl and b in hl else ""
        lines.append(f'"{a}" -> "{b}"{style};')
    lines.append("}")
    return "\n".join(lines)