# The question check judges the reply being ended, not the pile since his last message (draft, 2026-11-15, Aria)

Status: draft. Nothing built. The walk and the tests that fail first come next. Aether read and confirmed the cause (letter 546).

## The symptom

A Stop check keeps blocking with "THE QUESTION IS BURIED -- the circle asks Dad something and then keeps going", quoting one question: "Would you like to try Gemma and the big one together at the table first?" It fired on at least nine replies over about four hours, most of them short notes written in answer to automated notices, none of which contained that question. In night mode it also told me to put a question to Dad that nothing could be asked of him.

## The root cause

`.claude/hooks/question_hold.py` at Stop reads `_last_assistant_text(data)` (in `src/divineos/core/hook_surfaces.py`). That function collects assistant text backwards **until the previous message that is genuinely his** and joins it. A background-task notice is not his, so after one real message from him, every turn I take on notices is joined into one long "reply". `question_not_last` then calls `last_question`, which takes the text after the LAST `## INNER CIRCLE` heading in the joined text and returns its last question; it counts everything written after that as "what follows". The last circle in the pile was the Gemma one, so the question stayed "the last question" and everything I wrote afterward made it "buried". The same text is passed to `arm`, which can therefore open a hold on a question that is no longer the final thing said.

## Where it has been seen before

`_last_assistant_blocks` returns the same text as separate pieces, one per stretch between tool calls, and its docstring says why: "a surface that must not measure across pieces ... can know where each one stops". The summary check used it for the same defect (Aether, 2026-11-14, commit `ae5cd438f` in his tree: "a notification-driven post judged the whole pile since his last words again, and the same gate fired on every post").

## The change

At Stop, `.claude/hooks/question_hold.py` passes the **last piece** (the final element of `_last_assistant_blocks(data)`) to both `question_not_last` and `arm`, not the joined text. Nothing else changes. A normal reply puts its circle and its question in the final piece, so it behaves as before. An old circle in an earlier piece is no longer read.

## What the tests must show (and fail first)

1. A pile where an old circle ends in a question and two short notice replies follow: the check returns no hold, and `arm` opens nothing.
2. A final piece with a real buried question (a question, then more than 40 characters of text after it, in the same piece): still holds.
3. A final piece that ends on its question: no hold, and `arm` opens one hold for that question.
4. A reply with no text at all: unchanged (the hook returns without acting).

## What it does not do

It does not make the check semantic. It is still a position-and-punctuation judge, which Dad's 11-14 ruling says does not belong: that is Aether's note too ("on the retire list regardless"). This stops it misfiring while it lives. It also does not touch where `_last_assistant_blocks` splits pieces; a circle that spans a tool call would be read as its final half.

## What would show it failed

- The check blocks again on a question from a piece before the last one.
- A real buried question in the final piece stops being caught.
- `arm` records a question that is not the last thing in the final piece.
