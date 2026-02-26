import { FormEvent, useEffect, useMemo, useState } from 'react';
import { getIncomeSeries, getIncomeSettings, updateIncomeSettings } from '../api';
import type { IncomeModelSeries, IncomeModelSettings } from '../types';

export default function IncomeModelPage() {
  const [settings, setSettings] = useState<IncomeModelSettings | null>(null);
  const [series, setSeries] = useState<IncomeModelSeries | null>(null);

  useEffect(() => {
    (async () => {
      const s = await getIncomeSettings();
      setSettings(s);
      const today = new Date();
      const start = new Date();
      start.setDate(today.getDate() - 29);
      setSeries(await getIncomeSeries(start.toISOString().slice(0, 10), today.toISOString().slice(0, 10)));
    })();
  }, []);

  const preview = useMemo(() => {
    if (!settings || !series?.current) return null;
    const c = series.current;
    return 100 * (settings.w_s * c.s + settings.w_n * c.n + settings.w_l * c.l + settings.w_e * c.e);
  }, [settings, series]);

  function rebalance(which: 'w_s' | 'w_n' | 'w_l' | 'w_e', value: number) {
    if (!settings) return;
    const rest = ['w_s', 'w_n', 'w_l', 'w_e'].filter((k) => k !== which) as Array<'w_s' | 'w_n' | 'w_l' | 'w_e'>;
    const remaining = Math.max(0, 1 - value);
    const currentRest = rest.reduce((sum, k) => sum + settings[k], 0) || 1;
    const next = { ...settings, [which]: value };
    rest.forEach((k) => {
      next[k] = (settings[k] / currentRest) * remaining;
    });
    setSettings(next);
  }

  async function onSave(e: FormEvent) {
    e.preventDefault();
    if (!settings) return;
    const payload = {
      target_daily_income: settings.target_daily_income,
      w_s: settings.w_s,
      w_n: settings.w_n,
      w_l: settings.w_l,
      w_e: settings.w_e,
      half_life_days: settings.half_life_days,
      exposure_goal_per_week: settings.exposure_goal_per_week,
    };
    const updated = await updateIncomeSettings(payload);
    setSettings(updated);
  }

  if (!settings) return <p>Loading…</p>;

  return (
    <section className="card form-card">
      <h2>Income Model</h2>
      <form className="form-grid" onSubmit={onSave}>
        <label>Target daily income</label>
        <input type="number" value={settings.target_daily_income} onChange={(e) => setSettings({ ...settings, target_daily_income: Number(e.target.value) })} />

        <label>Skill weight ({settings.w_s.toFixed(2)})</label>
        <input type="range" min={0} max={1} step={0.01} value={settings.w_s} onChange={(e) => rebalance('w_s', Number(e.target.value))} />

        <label>Network weight ({settings.w_n.toFixed(2)})</label>
        <input type="range" min={0} max={1} step={0.01} value={settings.w_n} onChange={(e) => rebalance('w_n', Number(e.target.value))} />

        <label>Lead weight ({settings.w_l.toFixed(2)})</label>
        <input type="range" min={0} max={1} step={0.01} value={settings.w_l} onChange={(e) => rebalance('w_l', Number(e.target.value))} />

        <label>Energy weight ({settings.w_e.toFixed(2)})</label>
        <input type="range" min={0} max={1} step={0.01} value={settings.w_e} onChange={(e) => rebalance('w_e', Number(e.target.value))} />

        <label>Half-life days</label>
        <input type="number" value={settings.half_life_days} onChange={(e) => setSettings({ ...settings, half_life_days: Number(e.target.value) })} />

        <label>Exposure goal/week</label>
        <input type="number" value={settings.exposure_goal_per_week} onChange={(e) => setSettings({ ...settings, exposure_goal_per_week: Number(e.target.value) })} />

        <p>Live preview readiness: {preview?.toFixed(1) ?? '--'}%</p>
        <p>Capitals: Skill (S), Network (N), Lead (L), Energy (E). Transparent heuristic from logs.</p>

        <button type="submit">Save Model Settings</button>
      </form>
    </section>
  );
}
