"""Mutation tester custom (lane B, dispatch A) — mutmut nu ruleaza nativ pe Windows.
AST: flip comparatii (> <, >= <=, == !=), binop (+ -, * /), boolop (and/or), constante numerice (n->n+1).
Per mutant: scrie sursa mutata, ruleaza un subset de teste cu timeout, restaureaza. Mutant care TRECE = SUPRAVIETUITOR
(gol de test). Usage: python _mutate.py <fisier.py> <test_args...>"""
import ast
import os
import subprocess
import sys
import time

TARGET = sys.argv[1]
TEST_ARGS = sys.argv[2:] or ["tests/test_property_engine.py"]
PY = sys.executable

_CMP = {ast.Gt: ast.Lt, ast.Lt: ast.Gt, ast.GtE: ast.LtE, ast.LtE: ast.GtE,
        ast.Eq: ast.NotEq, ast.NotEq: ast.Eq}
_BIN = {ast.Add: ast.Sub, ast.Sub: ast.Add, ast.Mult: ast.Div, ast.Div: ast.Mult}
_BOOL = {ast.And: ast.Or, ast.Or: ast.And}

src = open(TARGET, encoding="utf-8").read()


def iter_points(tree):
    """Genereaza punctele de mutatie in ordine fixa de walk (kind, node, op_index)."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for i, op in enumerate(node.ops):
                if type(op) in _CMP:
                    yield ("cmp", node, i)
        elif isinstance(node, ast.BinOp) and type(node.op) in _BIN:
            yield ("bin", node, 0)
        elif isinstance(node, ast.BoolOp) and type(node.op) in _BOOL:
            yield ("bool", node, 0)
        elif (isinstance(node, ast.Constant) and isinstance(node.value, (int, float))
              and not isinstance(node.value, bool)):
            yield ("const", node, 0)


def describe(kind, node, opi):
    if kind == "cmp":
        return node.lineno, f"{type(node.ops[opi]).__name__}->{_CMP[type(node.ops[opi])].__name__}"
    if kind == "bin":
        return node.lineno, f"{type(node.op).__name__}->{_BIN[type(node.op)].__name__}"
    if kind == "bool":
        return node.lineno, f"{type(node.op).__name__}->{_BOOL[type(node.op)].__name__}"
    return node.lineno, f"const {node.value!r}->{node.value + 1!r}"


POINTS = [describe(k, n, o) for (k, n, o) in iter_points(ast.parse(src))]
print(f"# {TARGET}: {len(POINTS)} puncte | teste: {' '.join(TEST_ARGS)}", flush=True)


def mutate(i):
    t = ast.parse(src)
    for j, (kind, node, opi) in enumerate(iter_points(t)):
        if j != i:
            continue
        if kind == "cmp":
            node.ops[opi] = _CMP[type(node.ops[opi])]()
        elif kind == "bin":
            node.op = _BIN[type(node.op)]()
        elif kind == "bool":
            node.op = _BOOL[type(node.op)]()
        elif kind == "const":
            node.value = node.value + 1
        return ast.unparse(ast.fix_missing_locations(t))
    return None


survivors, killed = [], 0
t0 = time.time()
for i, (lineno, desc) in enumerate(POINTS):
    open(TARGET, "w", encoding="utf-8").write(mutate(i))
    try:
        r = subprocess.run(
            [PY, "-m", "pytest", *TEST_ARGS, "-q", "-x", "--no-header", "-p", "no:cacheprovider"],
            capture_output=True, timeout=120, env={**os.environ, "PYTHONPATH": "src"})
        if r.returncode == 0:
            survivors.append((lineno, desc))
            print(f"  SUPRAVIETUITOR L{lineno}: {desc}", flush=True)
        else:
            killed += 1
    except subprocess.TimeoutExpired:
        killed += 1
    finally:
        open(TARGET, "w", encoding="utf-8").write(src)

total = len(POINTS)
scor = (killed / total * 100) if total else 0
print(f"\n# SCOR {TARGET}: {killed}/{total} omorati = {scor:.0f}% | "
      f"{len(survivors)} supravietuitori | {time.time() - t0:.0f}s", flush=True)
