"""The gap count sorts every ask of Dad's into exactly one pile.

Draft: docs/drafts/the_gap_count_for_his_asks_draft_2026-11-09.md
Walk: walk-ef6b0ef7b8f7 (invariant: the piles sum to the number of asks).
"""

from divineos.core.ask_gap import Ask, Step, classify, summarize

HIS = [10.0, 20.0, 30.0, 40.0, 50.0]  # timestamps of his messages
FROM = 5.0  # oldest time the transcripts could be read


def _ask(i, ts, files=("a.py",), kind="do", withdrawn=False):
    return Ask(id=i, ts=ts, text=f"ask {i}", files=tuple(files), kind=kind, withdrawn=withdrawn)


def _step(ts, kind="change", files=("a.py",), size=5, desc="edit a.py"):
    return Step(ts=ts, kind=kind, files=tuple(files), size=size, desc=desc)


def test_a_change_to_the_named_file_is_a_step_and_the_gap_counts_his_messages():
    row = classify(_ask(1, 11.0), [_step(41.0)], HIS, FROM)
    assert row.pile == "step_found"
    assert row.gap == 3  # his messages at 20, 30, 40 went by
    assert row.step_label == "change"
    assert row.step_desc == "edit a.py"


def test_a_draft_is_counted_but_labelled_a_draft():
    row = classify(_ask(1, 11.0), [_step(21.0, kind="draft")], HIS, FROM)
    assert row.pile == "step_found"
    assert row.step_label == "draft"


def test_a_whitespace_only_change_is_not_a_step():
    row = classify(_ask(1, 11.0), [_step(21.0, size=0)], HIS, FROM)
    assert row.pile == "no_step_yet"


def test_a_change_to_a_file_the_ask_does_not_name_is_not_a_step():
    row = classify(_ask(1, 11.0), [_step(21.0, files=("other.py",))], HIS, FROM)
    assert row.pile == "no_step_yet"


def test_a_step_before_the_ask_does_not_count():
    row = classify(_ask(1, 25.0), [_step(21.0)], HIS, FROM)
    assert row.pile == "no_step_yet"


def test_a_letter_that_quotes_the_ask_is_an_acknowledgment_only():
    row = classify(_ask(1, 11.0), [_step(12.0, kind="ack_letter")], HIS, FROM)
    assert row.pile == "letter_only"


def test_a_real_step_wins_over_an_earlier_letter():
    steps = [_step(12.0, kind="ack_letter"), _step(31.0)]
    row = classify(_ask(1, 11.0), steps, HIS, FROM)
    assert row.pile == "step_found"
    assert row.gap == 2


def test_reads_and_searches_never_count():
    for kind in ("read", "grep", "reach_open", "goal", "learn", "reply_will"):
        row = classify(_ask(1, 11.0), [_step(12.0, kind=kind)], HIS, FROM)
        assert row.pile == "no_step_yet", kind


def test_an_ask_naming_no_file_is_its_own_pile_not_zero():
    row = classify(_ask(1, 11.0, files=()), [_step(12.0)], HIS, FROM)
    assert row.pile == "no_file_named"
    assert row.gap is None


def test_an_ask_older_than_the_oldest_readable_transcript_could_not_be_looked_at():
    row = classify(_ask(1, 2.0), [], HIS, FROM)
    assert row.pile == "could_not_look"
    assert row.gap is None


def test_a_withdrawn_ask_is_shown_as_withdrawn_never_as_neglect():
    row = classify(_ask(1, 11.0, withdrawn=True), [], HIS, FROM)
    assert row.pile == "withdrawn"


def test_a_question_is_answered_by_an_answering_reply_and_the_gap_counts_to_it():
    q = _ask(1, 11.0, files=(), kind="answer")
    row = classify(q, [_step(31.0, kind="answer_reply", files=(), desc="replied")], HIS, FROM)
    assert row.pile == "wanted_an_answer"
    assert row.gap == 2
    assert row.step_desc == "replied"


def test_a_question_with_no_answering_reply_is_no_step_yet():
    q = _ask(1, 11.0, files=(), kind="answer")
    assert classify(q, [], HIS, FROM).pile == "no_step_yet"


def test_the_piles_always_sum_to_the_number_of_asks():
    asks = [
        _ask(1, 11.0),
        _ask(2, 12.0, files=()),
        _ask(3, 2.0),
        _ask(4, 13.0, withdrawn=True),
        _ask(5, 14.0, files=(), kind="answer"),
        _ask(6, 15.0),
    ]
    steps = [_step(41.0), _step(42.0, kind="answer_reply", files=())]
    rows = [classify(a, steps, HIS, FROM) for a in asks]
    summary = summarize(rows)
    assert sum(summary.piles.values()) == len(asks)
    assert summary.total == len(asks)


def test_the_summary_leads_with_the_median_and_names_the_worst_asks():
    asks = [_ask(i, 11.0) for i in range(1, 5)]
    rows = [
        classify(asks[0], [_step(21.0)], HIS, FROM),
        classify(asks[1], [_step(31.0)], HIS, FROM),
        classify(asks[2], [_step(51.0)], HIS, FROM),
        classify(asks[3], [], HIS, FROM),
    ]
    summary = summarize(rows)
    assert summary.median_gap == 2
    assert [r.ask.id for r in summary.worst] == [3, 2, 1]
    assert summary.drafts + summary.changes == 3
