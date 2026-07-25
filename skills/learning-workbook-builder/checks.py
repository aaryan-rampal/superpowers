"""Tiny autograder for learning-workbook notebooks (opt-in feature).

Import at the top of a notebook:  from checks import *

Every check prints ✅ / ❌ / ⬜ and never raises, so one failing or
unimplemented cell does not halt the notebook. The headline tool is `check_fn`,
a PROPERTY TEST: it verifies the learner's formula against a reference on many
inputs without revealing the closed form, so the answer stays hidden while
correctness is still checked.
"""


def check(name, got, want, tol=1e-9):
    """Exact (or tolerant-numeric) equality."""
    try:
        ok = abs(got - want) <= tol
    except TypeError:
        ok = got == want
    print(f"{'✅' if ok else '❌'} {name}" + ("" if ok else f"  got={got!r} want={want!r}"))
    return ok


def approx(name, got, want, rel=0.05):
    """Relative-tolerance compare."""
    ok = abs(got - want) <= rel * abs(want) if want else abs(got) <= rel
    print(f"{'✅' if ok else '❌'} {name}" + ("" if ok else f"  got={got!r} want≈{want!r} (rel={rel})"))
    return ok


def check_true(name, cond, hint=""):
    """A boolean must hold."""
    ok = bool(cond)
    print(f"{'✅' if ok else '❌'} {name}" + ("" if ok else (f"  {hint}" if hint else "")))
    return ok


def check_fn(name, your_fn, ref_fn, cases, tol=1e-6):
    """Property test: your_fn must match ref_fn on every case.

    `cases` is a list of argument tuples (or bare values for one-arg fns).
    Reveals nothing about the formula — only pass/fail and the first mismatch.
    Returns None (⬜) if the stub is unimplemented.
    """
    if your_fn is None:
        print(f"⬜ {name} — not implemented yet")
        return None
    bad = []
    for c in cases:
        args = c if isinstance(c, tuple) else (c,)
        try:
            g = your_fn(*args)
        except NotImplementedError:
            print(f"⬜ {name} — not implemented yet")
            return None
        except Exception as e:  # noqa: BLE001 - report, don't crash the notebook
            print(f"❌ {name} — raised {type(e).__name__} on {args}: {e}")
            return False
        w = ref_fn(*args)
        if g is None or abs(g - w) > tol * (1 + abs(w)):
            bad.append((args, g, w))
    if bad:
        a, g, w = bad[0]
        print(f"❌ {name} — {len(bad)}/{len(cases)} wrong; e.g. f{a} = {g!r}, expected {w!r}")
        return False
    print(f"✅ {name} — matches reference on {len(cases)} cases")
    return True


if __name__ == "__main__":  # self-test
    assert check("eq", 2 + 2, 4)
    assert approx("rel", 0.99, 1.0, rel=0.05)
    assert check_true("bool", 1 < 2)
    assert check_fn("identity", lambda x: x * 2, lambda x: x + x, [1, 2, 3.5, -4])
    assert check_fn("wrong", lambda x: x + 1, lambda x: x, [1, 2]) is False
    assert check_fn("stub", None, lambda x: x, [1]) is None
    print("checks.py self-test passed")
