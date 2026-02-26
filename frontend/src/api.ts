import type { AnalyticsSummary, Domain, IncomeModelSeries, IncomeModelSettings } from './types';

const API_BASE = 'http://localhost:8000';

export interface ActionPayload {
  occurred_at: string;
  domain: Domain;
  title: string;
  notes?: string;
  h: number;
  r: number;
  d: number;
  e: number;
  tags?: string;
}

export interface ExposurePayload {
  occurred_at: string;
  type: string;
  notes?: string;
}

export async function getAnalytics(start: string, end: string): Promise<AnalyticsSummary> {
  const res = await fetch(`${API_BASE}/api/analytics/summary?start=${start}&end=${end}`);
  if (!res.ok) throw new Error('Failed to load analytics');
  return res.json();
}

export async function createAction(payload: ActionPayload): Promise<void> {
  const res = await fetch(`${API_BASE}/api/actions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to create action');
}

export async function createExposure(payload: ExposurePayload): Promise<void> {
  const res = await fetch(`${API_BASE}/api/exposures`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to create exposure');
}

export async function getIncomeSettings(): Promise<IncomeModelSettings> {
  const res = await fetch(`${API_BASE}/api/income-model/settings`);
  if (!res.ok) throw new Error('Failed to load settings');
  return res.json();
}

export async function updateIncomeSettings(payload: Omit<IncomeModelSettings, 'id' | 'updated_at'>): Promise<IncomeModelSettings> {
  const res = await fetch(`${API_BASE}/api/income-model/settings`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to update settings');
  return res.json();
}

export async function getIncomeSeries(start: string, end: string): Promise<IncomeModelSeries> {
  const res = await fetch(`${API_BASE}/api/income-model/series?start=${start}&end=${end}`);
  if (!res.ok) throw new Error('Failed to load income series');
  return res.json();
}

export async function seedData(): Promise<void> {
  const res = await fetch(`${API_BASE}/api/dev/seed`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to seed data');
}
