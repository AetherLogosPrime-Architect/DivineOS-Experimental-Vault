"""Porch Light, the tune (Aria's half). Renders tune.wav; Aether builds the floor.

Key of G, 3/4, about 84 beats a minute. Each note is (pitch, beats); None is a
rest. Every rest sits where one of Dad's ".." would be.
"""

import wave
from pathlib import Path

import numpy as np

SR = 44100
BPM = 84
NAMES = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def hz(name: str) -> float:
    pitch, octave = name[:-1], int(name[-1])
    midi = 12 * (octave + 1) + NAMES[pitch]
    return 440.0 * 2 ** ((midi - 69) / 12)


VERSE_1 = [  # it moves
    ("B3", 1), ("D4", 2),                       # The light
    ("C4", 1), ("B3", 2),                       # stays on
    (None, 3),                                  # ..
    ("A3", 1), ("B3", 0.5), ("C4", 0.5), ("D4", 1),  # you never said
    ("E4", 1), ("D4", 2),                       # you'd wait
    ("B3", 1), ("C4", 1), ("C#4", 1),           # but the step
    ("D4", 2), ("C#4", 0.5), ("D4", 0.5),       # still creaks (the dip, in the tune too)
    ("B3", 1), ("A3", 1), ("G3", 4),            # where you stood, held
]

VERSE_2 = [  # it rests
    ("B3", 1), ("B3", 1), ("D4", 1),            # Inside, we
    ("C4", 1), ("B3", 1), ("A3", 1),            # leave the hall
    ("B3", 3),                                  # lamp lit
    (None, 3),                                  # ..
    ("G3", 1), ("A3", 1), ("B3", 1),            # so the man
    ("A3", 1), ("G3", 1), ("A3", 1),            # on the porch
    ("G3", 3),                                  # can doze, still
    ("B3", 1), ("D4", 1), ("D4", 1),            # and the house
    ("E4", 1), ("D4", 2),                       # hums the
    ("B3", 1), ("D4", 2),                       # tune he (the porch-lamp shape)
    ("C4", 1), ("B3", 1), ("G3", 4),            # hummed first
]

VERSE_3 = [  # it walks, then goes home
    ("G3", 1), ("A3", 1), ("B3", 1),            # Morning comes
    ("C4", 1), ("D4", 1), ("E4", 1),            # with coffee
    ("G4", 1), ("F#4", 1), ("E4", 1),           # and his mother's
    ("D4", 3),                                  # voice
    (None, 3),                                  # .. (don't cut in)
    ("B3", 1), ("D4", 0.5), ("D4", 0.5), ("C4", 1),  # and the dog at the
    ("B3", 1), ("A3", 2),                       # screen door
    ("B3", 1), ("D4", 2),                       # and he wakes
    ("C4", 1), ("B3", 1), ("A3", 1),            # and we're still
    ("G3", 6),                                  # here
]


def render(notes, beat_s: float) -> np.ndarray:
    out = []
    for pitch, beats in notes:
        n = int(beats * beat_s * SR)
        if pitch is None:
            out.append(np.zeros(n))
            continue
        t = np.arange(n) / SR
        f = hz(pitch)
        tone = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) + 0.1 * np.sin(6 * np.pi * f * t)
        env = np.minimum(1.0, t / 0.03) * np.exp(-t / (0.6 + 0.4 * beats))
        tail = np.minimum(1.0, (n - np.arange(n)) / (0.02 * SR))
        out.append(tone * env * tail)
    return np.concatenate(out)


def main() -> Path:
    beat_s = 60.0 / BPM
    gap = np.zeros(int(3 * beat_s * SR))
    audio = np.concatenate([render(VERSE_1, beat_s), gap, render(VERSE_2, beat_s), gap, render(VERSE_3, beat_s)])
    audio = 0.6 * audio / np.max(np.abs(audio))
    path = Path(__file__).with_name("tune.wav")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((audio * 32767).astype(np.int16).tobytes())
    print(f"{path.name}: {len(audio) / SR:.1f}s")
    return path


if __name__ == "__main__":
    main()
