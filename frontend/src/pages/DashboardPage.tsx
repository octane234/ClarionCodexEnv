import { ReactNode, useEffect, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { getAnalytics, getIncomeSeries, seedData } from '../api';
import type { AnalyticsSummary, IncomeModelSeries } from '../types';

function formatDateInput(d: Date): string {
  return d.toISOString().slice(0, 10);
}

export default function DashboardPage() {
  const today = new Date();
  const startDefault = new Date(today);
  startDefault.setDate(today.getDate() - 29);

  const [start, setStart] = useState<string>(formatDateInput(startDefault));
  const [end, setEnd] = useState<string>(formatDateInput(today));
  const [data, setData] = useState<AnalyticsSummary | null>(null);
  const [income, setIncome] = useState<IncomeModelSeries | null>(null);
  const [loading, setLoading] = useState(false);

  async function refresh() {
    setLoading(true);
    try {
      const [analytics, incomeSeries] = await Promise.all([getAnalytics(start, end), getIncomeSeries(start, end)]);
      setData(analytics);
      setIncome(incomeSeries);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <section>
      <div className="row">
        <label>Start</label>
        <input type="date" value={start} onChange={(e) => setStart(e.target.value)} />
        <label>End</label>
        <input type="date" value={end} onChange={(e) => setEnd(e.target.value)} />
        <button onClick={refresh}>Refresh</button>
        <button
          onClick={async () => {
            await seedData();
            await refresh();
          }}
        >
          Seed Demo Data
        </button>
      </div>

      {loading && <p>Loading…</p>}
      {data && (
        <>
          <div className="kpi-grid">
            <article className="card"><h3>Cumulative Optionality</h3><p>{data.totals.sum_o_delta}</p></article>
            <article className="card"><h3>Avg O_delta/day</h3><p>{data.totals.avg_o_delta}</p></article>
            <article className="card"><h3>Latest Constraint Debt (7d)</h3><p>{data.totals.constraint_debt_7d_last}</p></article>
            <article className="card"><h3>Exposures (period)</h3><p>{data.totals.exposure_count_period}</p></article>
            <article className="card"><h3>Target Readiness</h3><p>{data.totals.readiness_latest}%</p><small>confidence {Math.round(data.totals.confidence_latest * 100)}%</small></article>
          </div>

          <div className="card">
            <h3>Capital breakdown</h3>
            <p>S: {data.totals.capitals_latest.s.toFixed(2)} · N: {data.totals.capitals_latest.n.toFixed(2)} · L: {data.totals.capitals_latest.l.toFixed(2)} · E: {data.totals.capitals_latest.e.toFixed(2)}</p>
            <p>
              {data.totals.capitals_latest.l < 0.4
                ? 'Lead capital is low → aim to log exposures toward your weekly goal.'
                : 'Lead capital is in a healthy range.'}
            </p>
          </div>

          <div className="chart-grid">
            <ChartCard title="Cumulative Optionality">
              <ResponsiveContainer width="100%" height={240}><LineChart data={data.daily}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="date" /><YAxis /><Tooltip /><Line type="monotone" dataKey="cumulative" stroke="#3b82f6" dot={false} /></LineChart></ResponsiveContainer>
            </ChartCard>

            <ChartCard title="Constraint Debt (7d Rolling)">
              <ResponsiveContainer width="100%" height={240}><LineChart data={data.daily}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="date" /><YAxis /><Tooltip /><Line type="monotone" dataKey="constraint_debt_7d" stroke="#ef4444" dot={false} /></LineChart></ResponsiveContainer>
            </ChartCard>

            <ChartCard title="Irreversibility Proxy">
              <ResponsiveContainer width="100%" height={240}><LineChart data={data.daily}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="date" /><YAxis domain={[0, 4]} /><Tooltip /><Line type="monotone" dataKey="irreversibility_avg" stroke="#8b5cf6" dot={false} /></LineChart></ResponsiveContainer>
            </ChartCard>

            <ChartCard title="Exposures per Week">
              <ResponsiveContainer width="100%" height={240}><BarChart data={data.weekly_exposure}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="week_start" /><YAxis /><Tooltip /><Bar dataKey="count" fill="#10b981" /></BarChart></ResponsiveContainer>
            </ChartCard>

            <ChartCard title="Target Readiness Trend">
              <ResponsiveContainer width="100%" height={240}><LineChart data={income?.daily ?? []}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="date" /><YAxis domain={[0, 100]} /><Tooltip /><Line type="monotone" dataKey="readiness" stroke="#f59e0b" dot={false} /></LineChart></ResponsiveContainer>
            </ChartCard>
          </div>
        </>
      )}
    </section>
  );
}

function ChartCard({ title, children }: { title: string; children: ReactNode }) {
  return (
    <article className="card">
      <h3>{title}</h3>
      {children}
    </article>
  );
}
