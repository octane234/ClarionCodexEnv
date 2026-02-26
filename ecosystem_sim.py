"""Decentralized AI research ecosystem simulator.

This module models an ecosystem of research agents as a dynamical system with
state variables:
    c: coupling strength between agents
    H: idea-prior entropy
    D: dominant basin depth
    R: re-entry cost for abandoned basins

Features
--------
- Discrete-time integration of coupled differential rules.
- Adaptive coupling behavior when entropy declines.
- Random shock events applied during simulation.
- Parameter sweeps for regime mapping.
- Trajectory and phase diagram plotting.
- Attractor stability classification.
- Resilience metric Omega = f(H, 1/D, 1/R).
- CLI with optional interactive tuning.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np


@dataclass
class SimulationParams:
    """Model parameters and solver controls."""

    alpha_noise: float = 0.4
    beta: float = 0.25
    gamma: float = 0.3
    delta: float = 0.2
    epsilon: float = 0.22
    zeta: float = 0.12
    eta: float = 0.2
    theta: float = 0.14
    institutional_pressure: float = 0.7
    decay: float = 0.6
    exploration: float = 0.5
    fragmentation: float = 0.4
    dt: float = 0.05
    steps: int = 800
    adaptive_rate: float = 0.35
    entropy_floor: float = 0.95
    shock_prob: float = 0.03
    shock_scale: float = 0.25
    seed: int = 42


@dataclass
class SimulationState:
    """Dynamic state variables."""

    c: float = 0.85
    H: float = 1.4
    D: float = 0.75
    R: float = 0.55


@dataclass
class SimulationResult:
    """Collected simulation outputs."""

    t: np.ndarray
    c: np.ndarray
    H: np.ndarray
    D: np.ndarray
    R: np.ndarray
    omega: np.ndarray
    shocks: np.ndarray
    classification: str


def compute_omega(H: np.ndarray, D: np.ndarray, R: np.ndarray) -> np.ndarray:
    """Resilience metric Omega = H * (1 / (1 + D)) * (1 / (1 + R))."""

    return H / ((1.0 + D) * (1.0 + R))


def classify_attractor(result: SimulationResult) -> str:
    """Classify terminal behavior into the requested attractor categories."""

    tail = slice(int(0.8 * len(result.H)), None)
    H_tail = result.H[tail]
    D_tail = result.D[tail]
    R_tail = result.R[tail]

    H_mean = float(np.mean(H_tail))
    D_mean = float(np.mean(D_tail))
    R_mean = float(np.mean(R_tail))

    tail_std = float(np.std(np.column_stack([H_tail, D_tail, R_tail])))

    if H_mean < 0.35 and D_mean > 2.0:
        return "monoculture collapse"
    if H_mean > 1.0 and D_mean < 1.2 and R_mean < 1.2:
        return "resilient diversity regime"
    if D_mean > 1.6 and R_mean > 1.4:
        return "lock-in attractor"
    if tail_std < 0.04:
        return "stable mixed attractor"
    return "oscillatory / transitional"


def step_dynamics(
    state: SimulationState,
    p: SimulationParams,
    rng: np.random.Generator,
    prev_H: float,
) -> Tuple[SimulationState, bool]:
    """Advance one discrete timestep with adaptive coupling and stochastic shocks."""

    adaptive_adjust = p.adaptive_rate * max(0.0, p.entropy_floor - state.H)

    dHdt = p.alpha_noise - p.beta * state.c * state.D
    dDdt = p.gamma * state.c * state.H - p.delta * p.decay
    dRdt = p.epsilon * state.D - p.zeta * p.exploration
    dcdt = p.eta * p.institutional_pressure - p.theta * p.fragmentation + adaptive_adjust

    shock = rng.random() < p.shock_prob
    if shock:
        dHdt += rng.normal(0.0, p.shock_scale)
        dDdt += rng.normal(0.0, p.shock_scale * 0.6)
        dRdt += abs(rng.normal(0.0, p.shock_scale * 0.5))
        dcdt += rng.normal(0.0, p.shock_scale * 0.4)

    new_state = SimulationState(
        c=max(0.0, state.c + p.dt * dcdt),
        H=max(0.0, state.H + p.dt * dHdt),
        D=max(0.0, state.D + p.dt * dDdt),
        R=max(0.0, state.R + p.dt * dRdt),
    )

    if new_state.H < prev_H:
        # additional adaptive correction if entropy is actively declining
        new_state.c += p.dt * p.adaptive_rate * 0.5

    return new_state, shock


def run_simulation(params: SimulationParams, initial: SimulationState) -> SimulationResult:
    """Run the ecosystem simulation using Euler integration."""

    rng = np.random.default_rng(params.seed)

    t = np.arange(params.steps + 1) * params.dt
    c = np.zeros(params.steps + 1)
    H = np.zeros(params.steps + 1)
    D = np.zeros(params.steps + 1)
    R = np.zeros(params.steps + 1)
    shocks = np.zeros(params.steps + 1, dtype=bool)

    state = initial
    c[0], H[0], D[0], R[0] = state.c, state.H, state.D, state.R

    for i in range(1, params.steps + 1):
        prev_H = state.H
        state, shock = step_dynamics(state, params, rng, prev_H)
        c[i], H[i], D[i], R[i] = state.c, state.H, state.D, state.R
        shocks[i] = shock

    omega = compute_omega(H, D, R)
    provisional = SimulationResult(t, c, H, D, R, omega, shocks, "")
    classification = classify_attractor(provisional)

    return SimulationResult(t, c, H, D, R, omega, shocks, classification)


def plot_trajectories(result: SimulationResult, out_path: Path) -> None:
    """Plot state variable trajectories and resilience metric."""

    fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    axs[0].plot(result.t, result.H, label="H: entropy", lw=2)
    axs[0].plot(result.t, result.D, label="D: basin depth", lw=2)
    axs[0].plot(result.t, result.R, label="R: re-entry cost", lw=2)
    axs[0].plot(result.t, result.c, label="c: coupling", lw=2)
    shock_t = result.t[result.shocks]
    if len(shock_t):
        axs[0].vlines(shock_t, ymin=0, ymax=max(np.max(result.H), np.max(result.D), np.max(result.R), np.max(result.c)),
                      colors="gray", alpha=0.2, linewidth=0.8, label="shock")
    axs[0].set_ylabel("State value")
    axs[0].set_title(f"Ecosystem trajectories ({result.classification})")
    axs[0].legend(loc="upper right")

    axs[1].plot(result.t, result.omega, color="purple", lw=2)
    axs[1].set_xlabel("Time")
    axs[1].set_ylabel(r"$\Omega$")
    axs[1].set_title("Resilience metric")

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def parameter_sweep(
    base: SimulationParams,
    initial: SimulationState,
    c_values: np.ndarray,
    noise_values: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """Sweep initial coupling and alpha_noise to build phase diagrams."""

    omega_grid = np.zeros((len(noise_values), len(c_values)))
    class_grid = np.zeros((len(noise_values), len(c_values)))

    labels = {
        "monoculture collapse": 0,
        "resilient diversity regime": 1,
        "lock-in attractor": 2,
        "stable mixed attractor": 3,
        "oscillatory / transitional": 4,
    }

    for i, noise in enumerate(noise_values):
        for j, c0 in enumerate(c_values):
            p = replace(base, alpha_noise=float(noise), seed=base.seed + i * 1000 + j)
            init = replace(initial, c=float(c0))
            res = run_simulation(p, init)
            omega_grid[i, j] = np.mean(res.omega[-100:])
            class_grid[i, j] = labels[res.classification]

    return omega_grid, class_grid


def plot_phase_diagrams(
    c_values: np.ndarray,
    noise_values: np.ndarray,
    omega_grid: np.ndarray,
    class_grid: np.ndarray,
    out_prefix: Path,
) -> None:
    """Plot Omega and attractor classification phase diagrams."""

    fig, ax = plt.subplots(figsize=(9, 6))
    im = ax.imshow(
        omega_grid,
        origin="lower",
        aspect="auto",
        extent=[c_values.min(), c_values.max(), noise_values.min(), noise_values.max()],
        cmap="viridis",
    )
    fig.colorbar(im, ax=ax, label=r"mean $\Omega$ (tail)")
    ax.set_xlabel("initial coupling c0")
    ax.set_ylabel("alpha_noise")
    ax.set_title("Phase diagram: resilience")
    fig.tight_layout()
    fig.savefig(out_prefix.with_name(out_prefix.name + "_omega.png"), dpi=150)
    plt.close(fig)

    fig2, ax2 = plt.subplots(figsize=(9, 6))
    im2 = ax2.imshow(
        class_grid,
        origin="lower",
        aspect="auto",
        extent=[c_values.min(), c_values.max(), noise_values.min(), noise_values.max()],
        cmap="tab10",
    )
    cbar = fig2.colorbar(im2, ax=ax2)
    cbar.set_ticks([0, 1, 2, 3, 4])
    cbar.set_ticklabels(
        ["collapse", "resilient", "lock-in", "mixed", "osc/trans"]
    )
    ax2.set_xlabel("initial coupling c0")
    ax2.set_ylabel("alpha_noise")
    ax2.set_title("Phase diagram: attractor class")
    fig2.tight_layout()
    fig2.savefig(out_prefix.with_name(out_prefix.name + "_class.png"), dpi=150)
    plt.close(fig2)


def interactive_tune(params: SimulationParams, state: SimulationState) -> Tuple[SimulationParams, SimulationState]:
    """Prompt user for parameter overrides in interactive mode."""

    print("Interactive tuning: press Enter to keep defaults.")

    def ask_float(prompt: str, current: float) -> float:
        raw = input(f"{prompt} [{current}]: ").strip()
        return current if not raw else float(raw)

    params = replace(
        params,
        alpha_noise=ask_float("alpha_noise", params.alpha_noise),
        beta=ask_float("beta", params.beta),
        gamma=ask_float("gamma", params.gamma),
        dt=ask_float("dt", params.dt),
        shock_prob=ask_float("shock_prob", params.shock_prob),
        adaptive_rate=ask_float("adaptive_rate", params.adaptive_rate),
    )
    state = replace(
        state,
        c=ask_float("initial c", state.c),
        H=ask_float("initial H", state.H),
        D=ask_float("initial D", state.D),
        R=ask_float("initial R", state.R),
    )

    return params, state


def parse_args() -> argparse.Namespace:
    """CLI argument parser."""

    parser = argparse.ArgumentParser(description="Decentralized AI ecosystem simulation")
    parser.add_argument("--steps", type=int, default=800, help="integration steps")
    parser.add_argument("--dt", type=float, default=0.05, help="timestep")
    parser.add_argument("--seed", type=int, default=42, help="random seed")
    parser.add_argument("--interactive", action="store_true", help="interactive tuning mode")
    parser.add_argument("--run-sweep", action="store_true", help="run parameter sweep and phase diagrams")
    parser.add_argument("--outdir", type=Path, default=Path("outputs"), help="output directory")
    parser.add_argument("--config", type=Path, help="optional JSON file overriding params and initial state")
    return parser.parse_args()


def load_config(path: Path, params: SimulationParams, state: SimulationState) -> Tuple[SimulationParams, SimulationState]:
    """Load parameter overrides from JSON config."""

    data = json.loads(path.read_text())
    if "params" in data:
        for key, val in data["params"].items():
            if hasattr(params, key):
                setattr(params, key, val)
    if "state" in data:
        for key, val in data["state"].items():
            if hasattr(state, key):
                setattr(state, key, val)
    return params, state


def main() -> None:
    """CLI entry point."""

    args = parse_args()

    params = SimulationParams(steps=args.steps, dt=args.dt, seed=args.seed)
    state = SimulationState()

    if args.config:
        params, state = load_config(args.config, params, state)

    if args.interactive:
        params, state = interactive_tune(params, state)

    args.outdir.mkdir(parents=True, exist_ok=True)

    result = run_simulation(params, state)
    trajectory_path = args.outdir / "trajectory.png"
    plot_trajectories(result, trajectory_path)

    print(f"Stability classification: {result.classification}")
    print(f"Final Omega: {result.omega[-1]:.4f}")
    print(f"Mean tail Omega: {np.mean(result.omega[-100:]):.4f}")
    print(f"Saved trajectory plot: {trajectory_path}")

    if args.run_sweep:
        c_vals = np.linspace(0.1, 2.0, 45)
        noise_vals = np.linspace(0.05, 1.4, 45)
        omega_grid, class_grid = parameter_sweep(params, state, c_vals, noise_vals)
        prefix = args.outdir / "phase"
        plot_phase_diagrams(c_vals, noise_vals, omega_grid, class_grid, prefix)
        print(f"Saved phase diagrams: {prefix}_omega.png and {prefix}_class.png")


if __name__ == "__main__":
    main()
