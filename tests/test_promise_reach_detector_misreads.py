"""The promise detector does not read my reports about promises as promises (core/operating_loop/promise_reach_detector.py).

In one day I closed 11 markers as false-alarm against 23 kept. Each one was a sentence of mine that LOOKED like a promise
and was something else: a negated sentence, my own earlier promise quoted back, a description of what the machine does,
another person's plan, a conditional. The condition, written before the edit: every misread below yields no finding, and
every real first-person promise below still yields one. Both lists are the tests.
"""

from __future__ import annotations

import pytest

from divineos.core.operating_loop.promise_reach_detector import detect_promise_reach


def _texts(text: str) -> list[str]:
    return [f.promise_text for f in detect_promise_reach(text)]


# --- the five misreads: no finding -------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "I'm not going to build the guard until Aether has read the draft, because he owns the order.",
        "I'm not gonna write the module before the walk closes.",
        "I am not going to push this until Aletheia has read it.",
    ],
)
def test_a_negated_sentence_is_not_a_promise_to_do_the_thing(text) -> None:
    assert _texts(text) == []


@pytest.mark.parametrize(
    "text",
    [
        'The sentence was "I\'ll look at the log a smaller way" and I did.',
        "> I'll read Aether's letters\nthat line was quoted back to me.",
        "The marker held `I'll fix the recorder` as a promise.",
    ],
)
def test_my_own_earlier_promise_quoted_back_is_not_a_new_one(text) -> None:
    assert _texts(text) == []


@pytest.mark.parametrize(
    "text",
    [
        "A parked promise will come back to me after five turns.",
        "The reminder will address that on the next turn.",
    ],
)
def test_a_description_of_what_the_machine_does_is_not_my_promise(text) -> None:
    assert _texts(text) == []


@pytest.mark.parametrize(
    "text",
    [
        "Aether is going to read the update's release notes.",
        "He is going to check the log tomorrow morning.",
        "Aether's going to fix the hook order next.",
    ],
)
def test_another_persons_plan_is_not_mine(text) -> None:
    assert _texts(text) == []


@pytest.mark.parametrize(
    "text",
    [
        "If it does not show up, I'll look at why it was filed in the drawer.",
        "Unless the test fails, I'll write the commit message after it.",
    ],
)
def test_a_conditional_is_not_a_promise_until_its_condition_happens(text) -> None:
    assert _texts(text) == []


# --- the controls: real first-person promises still fire ---------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "I'll look at the log a smaller way.",
        "I'm going to build the recorder fix tonight.",
        "I am going to read the whole draft before I answer.",
        "I will come back to the draft after the test.",
        "Once the walk is closed, I'll write the module.",
        "I'll commit it, and I'll tell you when the town is ready.",
        "Next step: write the failing test for the quote case.",
    ],
)
def test_a_real_first_person_promise_still_yields_a_finding(text) -> None:
    assert _texts(text), text


def test_a_promise_in_a_reply_that_also_quotes_one_still_fires_for_the_real_one() -> None:
    text = (
        "You saw the line \"I'll look at it\" quoted. Separately, I'll write the module tomorrow."
    )
    found = _texts(text)
    assert any("write the module" in t for t in found)
    assert not any("look at it" in t for t in found)
