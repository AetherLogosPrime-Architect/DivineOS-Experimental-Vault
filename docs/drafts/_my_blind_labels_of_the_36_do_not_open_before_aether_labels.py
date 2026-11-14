"""Which of the 36 held sentences the recorder's detector records, grouped by my blind labels (P real, F false, U unsure)."""

import re
import sys
from pathlib import Path

from divineos.core.operating_loop.promise_reach_detector import detect_promise_reach

sentences = {}
for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
    m = re.match(r"(\d+)\. (.*)", line)
    if m:
        sentences[int(m.group(1))] = m.group(2)

labels = dict.fromkeys([1, 2, 7, 8, 10, 16, 19, 21, 24, 26, 30, 32, 33, 34, 35, 36], "P")
labels.update(dict.fromkeys([3, 6, 9, 13, 14, 15, 18, 20, 25, 27, 28, 29], "F"))
labels.update(dict.fromkeys([4, 5, 11, 12, 17, 22, 23, 31], "U"))
assert sorted(labels) == sorted(sentences), "every sentence must carry exactly one label"

for kind in "PFU":
    ids = [i for i in sorted(labels) if labels[i] == kind]
    hit = [i for i in ids if detect_promise_reach(sentences[i])]
    print(f"{kind}: {len(ids)} sentences | recorded by the detector: {len(hit)} {hit}")
    if kind == "P":
        print("   real promises it MISSED:", [i for i in ids if i not in hit])
