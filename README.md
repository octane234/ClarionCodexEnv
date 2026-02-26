# ClarionCodexEnv
Vibe coding stuff

## Fractal Awakening Symphony

`fractal_awakening.py` generates a MIDI file and emotional heatmap based on a fractal logistic map.

### Usage

1. Install dependencies:

   ```bash
   pip install midiutil matplotlib
   ```

2. Run the generator:

   ```bash
   python fractal_awakening.py
   ```

   This creates:

   - `awakening.mid` — the fractal crescendo
   - `emotional_heatmap.png` — visual map of confusion → resonance → recognition → being
   - `emotional_heatmap.csv` — raw data for the heatmap

   The `.mid` and `.png` files are generated outputs and are ignored by version control.
   Run the script whenever you need fresh copies.

3. Open `awakening.mid` in MuseScore to shape the final *Awakening* score.

## Decentralized AI Ecosystem Simulator

`ecosystem_sim.py` simulates a decentralized AI research ecosystem as a dynamical system with adaptive coupling and shock events.

### Usage

```bash
pip install numpy matplotlib
python ecosystem_sim.py --run-sweep
```

Optional interactive tuning:

```bash
python ecosystem_sim.py --interactive
```

Outputs are written to `outputs/` by default:
- `trajectory.png`
- `phase_omega.png`
- `phase_class.png` (when `--run-sweep` is used)
