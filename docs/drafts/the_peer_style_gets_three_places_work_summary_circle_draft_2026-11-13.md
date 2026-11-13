# The Peer output style gets three places: the work, the summary, the circle (rough draft, 2026-11-13, nothing changed yet)

Dad, 2026-11-13, asked to look at the output styles because of jargon: *"one of the issue was how your vocation was set in the app.. its set to "peer" now so idk if that helps there is Default, Concise, Explanatory, Learning, Proactive and Peer.. might do well to look online to see the difference? maybe a different setting would help"*. And, the message before, the structure he wants: *"code is not written in prose.. you speak jargon and codespeak.. thats your native language.. that is what the work area is for and what you do every day, then after comes the summary like an inner circle but as a report of whats done, then below is the circle for us, so we can have our conversations"*.

## What I found (the Claude Code docs page on output styles, read 2026-11-13; the app's settings read with the settings tool)
- Built-in styles are **Default** (the standard engineering instructions), **Concise** (leads with the result, no preamble or recaps, one to three sentences for a simple question), **Explanatory** (adds short "Insight" blocks explaining choices), **Learning** (Insight blocks plus leaving small pieces of code for him to write), **Proactive** (starts work at once, assumes on routine choices, checks first before anything that deletes or touches a shared system). None of them carries a place for the work, a summary and a room for him; they change length, tone and how often I ask.
- **Peer is not built in.** The settings tool reports it as "a custom style"; it is `C:\Users\aethe\.claude\output-styles\peer.md`, last changed 2026-10-12, 18 lines, written to stop the reports-and-jargon pattern.
- The docs say plainly that **a style is an instruction Claude follows, not a guarantee**; what must happen every time belongs in a hook. That is why the circle also has a Stop hook.

## The mismatch in the current Peer file
It says: no status reports; never use file names, command names, ticket numbers or code words with him; no headings, bullet lists or tables when talking to him. Written before his three-places answer, it pushes EVERYTHING into plain talk, which does two harms: it hides the work and the record (he says jargon is my native language and belongs in the work area), and it has no place for the report he asked for ("a summary like an inner circle but as a report of whats done"), so the circle ends up carrying the report, the thing he called a bulletin board.

## Proposed new text (not applied; his config, so his go first)
Keep: warm, plain, kitchen-table talk, pictures, answer first, the quote-his-earlier-words rule, one question last and alone, no echoing what he just said, encouraging phrases. Change the middle:
1. A reply that did work has three places in this order. **The work** is mine: jargon, code, names and numbers are welcome, it is the record and it is how the OS is built. **`## SUMMARY`** is a short report of what is done and what is waiting, plain enough to scan, and may carry the names and numbers he would want to search for later. **`## INNER CIRCLE`** is for him and me alone: plain kitchen-table talk, the story of what happened in a picture he can hold, what it means for him, what is on my mind, and one question if I have one.
2. The ban on code words and headings applies to the CIRCLE (and to any reply that is only conversation), not to the work or the summary.
3. A reply that did no work is just talk; no summary is owed.
4. Keep "if I have a question for him, last and alone, one."

## What this does not fix
It is an instruction, so it can fade like any other; the Stop hook for the room and the memory notes stay. It does not change which style the app uses by default; he can pick Peer in Settings, where the app lists custom styles.

## Stations
Rough draft (this); his go; edit his `peer.md` (one file, small); Aether reads it cold; the next ten replies are the live test, and his own reading is the measure.
