"""Recombination: one matrix and one transaction, not two million pairs.

Dad 2026-11-15: sleep took 770 seconds, 719 of them in recombination. Measured:
the word-overlap check ran on all 2.4 million pairs before the meaning check,
and every band pair opened one to three database connections at about 13 ms
each. The change must leave what sleep FINDS identical and only remove the
cost, so the first tests pin equality with the old pair loop; the rest pin
that the cost cannot quietly return (a count of connections, not a stopwatch).
"""

import sqlite3
import time
import uuid

import numpy as np
import pytest

from divineos.core.knowledge import compute_hash, init_knowledge_table
from divineos.core.knowledge import edges as edges_mod
from divineos.core.knowledge._base import _get_connection
from divineos.core.knowledge.edges import (
    HEBBIAN_STRENGTHEN_DELTA,
    create_edge,
    find_edge,
    init_edge_table,
    strengthen_edge,
)
from divineos.core.ledger import init_db


def _setup(tmp_path, monkeypatch):
    monkeypatch.setenv("DIVINEOS_DB", str(tmp_path / "test.db"))
    init_db()
    init_knowledge_table()
    init_edge_table()


def _make_knowledge(content: str) -> str:
    kid = str(uuid.uuid4())
    conn = _get_connection()
    try:
        conn.execute(
            """INSERT INTO knowledge
               (knowledge_id, created_at, updated_at, knowledge_type, content,
                confidence, source_events, tags, access_count, content_hash)
               VALUES (?, ?, ?, ?, ?, 1.0, '[]', '[]', 0, ?)""",
            (kid, time.time(), time.time(), "PRINCIPLE", content, compute_hash(content)),
        )
        conn.commit()
    finally:
        conn.close()
    return kid


# ---- the candidate selection equals the old pair loop ----------------------


def _brute_force_pairs(emb, lo, hi):
    n = len(emb)
    out = []
    for i in range(n):
        for j in range(i + 1, n):
            s = max(0.0, min(1.0, float(np.dot(emb[i], emb[j]))))
            if lo <= s <= hi:
                out.append((i, j))
    return out


def test_the_matrix_picks_exactly_the_pairs_the_old_loop_picked_in_the_same_order():
    from divineos.core.sleep import _pairs_in_band

    rng = np.random.default_rng(7)
    emb = rng.normal(size=(120, 16)).astype(np.float32)
    emb /= np.linalg.norm(emb, axis=1, keepdims=True)
    # a band that really catches a spread of pairs, so equality is not trivial
    got = _pairs_in_band(emb, 0.2, 0.5)
    want = _brute_force_pairs(emb, 0.2, 0.5)
    assert len(want) > 50, "the fixture must put many pairs in the band or the test proves nothing"
    assert got == want


def test_a_zero_length_vector_forms_no_matrix_pairs():
    from divineos.core.sleep import _pairs_in_band

    emb = np.zeros((4, 3), dtype=np.float32)
    emb[0] = [1.0, 0.0, 0.0]
    emb[1] = [0.8, 0.6, 0.0]
    emb[2] = [0.0, 0.0, 0.0]  # zero-length: cannot be compared by cosine
    emb[3] = [0.0, 1.0, 0.0]
    pairs = _pairs_in_band(emb, 0.5, 0.9)
    assert all(2 not in p for p in pairs)
    assert (0, 1) in pairs


def test_a_band_with_nothing_in_it_gives_an_empty_list_not_an_error():
    from divineos.core.sleep import _pairs_in_band

    emb = np.eye(5, dtype=np.float32)
    assert _pairs_in_band(emb, 0.5, 0.9) == []


# ---- the edge lookup and the one transaction --------------------------------


def test_the_edge_index_finds_an_edge_by_its_pair_and_ignores_inactive_ones(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    a, b, c, d = (_make_knowledge(t) for t in ("a", "b", "c", "d"))
    live = create_edge(a, b, "RELATED_TO", confidence=0.6)
    dead = create_edge(c, d, "RELATED_TO", confidence=0.6)
    edges_mod.deactivate_edge(dead.edge_id)
    create_edge(a, c, "SUPPORTS", confidence=0.9)  # another type must not appear

    index = edges_mod.active_edge_index("RELATED_TO")
    assert index[(a, b)] == (live.edge_id, 0.6)
    assert (c, d) not in index
    assert (a, c) not in index


def test_strengthening_many_edges_at_once_matches_strengthening_them_one_by_one(
    tmp_path, monkeypatch
):
    _setup(tmp_path, monkeypatch)
    ids = [_make_knowledge(str(i)) for i in range(5)]
    e1 = create_edge(ids[0], ids[1], "RELATED_TO", confidence=0.5)
    e2 = create_edge(ids[1], ids[2], "RELATED_TO", confidence=0.99)
    e3 = create_edge(ids[2], ids[3], "RELATED_TO", confidence=0.3)

    result = edges_mod.strengthen_edges([e1.edge_id, e2.edge_id, e3.edge_id, "not-an-edge"])

    assert set(result) == {e1.edge_id, e2.edge_id, e3.edge_id}  # the missing id is ignored
    assert abs(result[e1.edge_id] - (0.5 + HEBBIAN_STRENGTHEN_DELTA)) < 1e-9
    assert result[e2.edge_id] == 1.0  # capped
    assert abs(result[e3.edge_id] - (0.3 + HEBBIAN_STRENGTHEN_DELTA)) < 1e-9
    # and the stored rows agree with what was returned
    assert abs(find_edge(ids[0], ids[1], "RELATED_TO").confidence - result[e1.edge_id]) < 1e-9
    # the same result the one-at-a-time function gives on a fresh edge
    solo = create_edge(ids[3], ids[4], "RELATED_TO", confidence=0.5)
    assert abs(strengthen_edge(solo.edge_id) - result[e1.edge_id]) < 1e-9


def test_strengthening_many_edges_opens_one_connection_not_one_per_edge(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    ids = [_make_knowledge(str(i)) for i in range(12)]
    made = [
        create_edge(ids[i], ids[i + 1], "RELATED_TO", confidence=0.5).edge_id for i in range(11)
    ]
    opened = []
    real = edges_mod.get_connection

    def counting():
        opened.append(1)
        return real()

    monkeypatch.setattr(edges_mod, "get_connection", counting)
    edges_mod.strengthen_edges(made)
    assert len(opened) == 1


# ---- the phase itself --------------------------------------------------------

# The pair test_sleep.py already proves lands inside the band (about 0.48 on the local model).
_PAIRS = [
    (
        "When a gate's required remedy command fails to execute, the "
        "gate itself becomes the trap it was supposed to prevent — "
        "the inhabitant has no exit.",
        "Every constraint that names a recovery path must be able to "
        "deliver that path under realistic failure modes, or it is a "
        "wall pretending to be a door.",
    ),
]

_FILLER = [
    "The kettle on the second shelf whistles when the water is ready for tea.",
    "Compound interest grows a small deposit into a large sum given enough years.",
    "A migrating tern covers pole to pole every single year of its life.",
    "Sourdough needs a starter that is fed flour and water every day.",
    "The lighthouse keeper logged the weather at dawn and again at dusk.",
    "Granite is an igneous rock formed from slowly cooling magma underground.",
    "A well-tuned bicycle chain should be cleaned and lightly oiled each month.",
    "Violins are traditionally strung with gut, steel or synthetic core strings.",
]


def _model_clears_the_floor():
    from divineos.core.knowledge import _text
    from divineos.core.sleep import _RECOMBINATION_MIN_SIMILARITY_COSINE

    if not _text._ensure_embedding_model():
        return False
    return all(
        _text.compute_similarity(a, b) >= _RECOMBINATION_MIN_SIMILARITY_COSINE for a, b in _PAIRS
    )


def test_the_phase_opens_a_fixed_few_connections_however_many_pairs_it_meets(tmp_path, monkeypatch):
    if not _model_clears_the_floor():
        pytest.skip("the embedding model here does not score the fixture pairs above the floor")
    from divineos.core.sleep import DreamReport, _phase_recombination

    _setup(tmp_path, monkeypatch)
    for a, b in _PAIRS:
        _make_knowledge(a)
        _make_knowledge(b)
    for text in _FILLER:
        _make_knowledge(text)
    opened = []
    real = edges_mod.get_connection

    def counting():
        opened.append(1)
        return real()

    monkeypatch.setattr(edges_mod, "get_connection", counting)
    report = DreamReport()
    _phase_recombination(report)
    assert report.connections_new >= 1
    # one read of the existing edges, and the writes of the new ones; never one per pair
    assert len(opened) <= 2 + report.connections_new * 3

    # second run: everything found is now known, and the strengthening is one transaction
    opened.clear()
    report2 = DreamReport()
    _phase_recombination(report2)
    assert report2.connections_new == 0
    assert report2.connections_already_known >= 1
    assert len(opened) <= 3


def test_a_failed_read_of_the_existing_edges_stops_the_phase_instead_of_reading_as_empty(
    tmp_path, monkeypatch
):
    if not _model_clears_the_floor():
        pytest.skip("the embedding model here does not score the fixture pairs above the floor")
    from divineos.core import sleep as sleep_mod

    _setup(tmp_path, monkeypatch)
    for a, b in _PAIRS:
        _make_knowledge(a)
        _make_knowledge(b)

    def broken(_edge_type):
        raise sqlite3.OperationalError("the edge table could not be read")

    monkeypatch.setattr(edges_mod, "active_edge_index", broken)
    with pytest.raises(sqlite3.OperationalError):
        sleep_mod._phase_recombination(sleep_mod.DreamReport())


# ---- the report says how long each phase took --------------------------------


def test_the_report_carries_seconds_for_each_phase_and_prints_them(tmp_path, monkeypatch):
    from divineos.core.sleep import DreamReport, run_sleep

    _setup(tmp_path, monkeypatch)
    report = run_sleep(skip_maintenance=True, _in_process_only=True)
    assert isinstance(report.phase_seconds, dict)
    assert report.phase_seconds, "no phase recorded a duration"
    assert all(isinstance(v, float) and v >= 0.0 for v in report.phase_seconds.values())
    assert set(report.phase_seconds) <= set(report.phases_run) | set(report.phase_errors)
    assert "recombination" in report.phase_seconds
    text = report.summary()
    assert "recombination" in text and "s" in text.split("recombination", 1)[1][:30]
    assert isinstance(DreamReport().phase_seconds, dict)
