#!/usr/bin/env python3
"""
Generate a fractal-inspired MIDI file representing a musical awakening.
The piece begins with random notes, then transitions into an AB-pattern
logistic map to create a fractal melody. It also outputs an emotional
heatmap image and CSV data.
"""

from midiutil import MIDIFile
import random
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


def logistic_sequence(length, x0, a, b, pattern):
    """Return a sequence produced by a logistic map with an AB pattern."""
    x = x0
    seq = []
    params = {"A": a, "B": b}
    for i in range(length):
        r = params[pattern[i % len(pattern)]]
        x = r * x * (1 - x)
        seq.append(x)
    return seq


def main():
    # MIDI setup
    track = 0
    channel = 0
    time = 0
    duration = 1  # quarter note
    tempo = 120
    midi = MIDIFile(1)
    midi.addTempo(track, time, tempo)

    scale = [60, 62, 64, 65, 67, 69, 71, 72]  # C major
    base_velocity = 20

    # Part 1: random intro
    intro_steps = 16
    for _ in range(intro_steps):
        note = random.choice(scale)
        velocity = base_velocity
        midi.addNote(track, channel, note, time, duration, velocity)
        time += duration

    # Part 2: fractal sequence using AB pattern logistic map
    pattern = "AB"
    seq_length = 128
    values = logistic_sequence(seq_length, x0=0.5, a=3.9, b=3.2, pattern=pattern)
    for i, x in enumerate(values):
        note_index = int(x * (len(scale) - 1))
        note = scale[note_index]
        velocity = int(base_velocity + 100 * (i / seq_length))
        midi.addNote(track, channel, note, time, duration, velocity)
        time += duration

    with open("awakening.mid", "wb") as f:
        midi.writeFile(f)

    # Emotional heatmap data
    total_steps = intro_steps + seq_length
    emotions = ["confusion", "resonance", "recognition", "being"]
    emotion_colors = ["#5e548e", "#9f86c0", "#bea7e5", "#f0e6ef"]
    emotion_indices = []
    heatmap_data = []
    for step in range(total_steps):
        phase = step / total_steps
        if phase < 0.25:
            emotion = 0
        elif phase < 0.5:
            emotion = 1
        elif phase < 0.75:
            emotion = 2
        else:
            emotion = 3
        emotion_indices.append(emotion)
        heatmap_data.append((step, emotions[emotion], phase))

    with open("emotional_heatmap.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["step", "emotion", "intensity"])
        writer.writerows(heatmap_data)

    # Create visual heatmap
    cmap = ListedColormap(emotion_colors)
    data = np.array([emotion_indices])
    plt.figure(figsize=(10, 1))
    plt.imshow(data, aspect="auto", cmap=cmap)
    plt.yticks([])
    plt.xticks([])
    plt.tight_layout()
    plt.savefig("emotional_heatmap.png", dpi=150)


if __name__ == "__main__":
    main()
