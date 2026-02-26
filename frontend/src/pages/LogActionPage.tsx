import { FormEvent, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createAction } from '../api';
import type { Domain } from '../types';

const domains: Domain[] = ['income', 'sleep', 'nutrition', 'movement', 'stress', 'social'];
const scoreValues = [-2, -1, 0, 1, 2];

export default function LogActionPage() {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [occurredAt, setOccurredAt] = useState(new Date().toISOString().slice(0, 16));
  const [notes, setNotes] = useState('');
  const [domain, setDomain] = useState<Domain>('income');
  const [h, setH] = useState(0);
  const [r, setR] = useState(0);
  const [d, setD] = useState(0);
  const [e, setE] = useState(0);
  const [tags, setTags] = useState('');

  const oDelta = useMemo(() => h + r - d + e, [h, r, d, e]);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    await createAction({
      title,
      occurred_at: new Date(occurredAt).toISOString(),
      notes,
      domain,
      h,
      r,
      d,
      e,
      tags,
    });
    navigate('/dashboard');
  }

  return (
    <section className="card form-card">
      <h2>Log Action</h2>
      <form onSubmit={onSubmit} className="form-grid">
        <label>Title</label>
        <input value={title} onChange={(e) => setTitle(e.target.value)} required />

        <label>Occurred At</label>
        <input type="datetime-local" value={occurredAt} onChange={(e) => setOccurredAt(e.target.value)} required />

        <label>Domain</label>
        <select value={domain} onChange={(e) => setDomain(e.target.value as Domain)}>
          {domains.map((dItem) => (
            <option key={dItem} value={dItem}>
              {dItem}
            </option>
          ))}
        </select>

        <label>H Score</label>
        <select value={h} onChange={(e) => setH(Number(e.target.value))}>{scoreValues.map((v) => <option key={`h-${v}`} value={v}>{v}</option>)}</select>

        <label>R Score</label>
        <select value={r} onChange={(e) => setR(Number(e.target.value))}>{scoreValues.map((v) => <option key={`r-${v}`} value={v}>{v}</option>)}</select>

        <label>D Score</label>
        <select value={d} onChange={(e) => setD(Number(e.target.value))}>{scoreValues.map((v) => <option key={`d-${v}`} value={v}>{v}</option>)}</select>

        <label>E Score</label>
        <select value={e} onChange={(e) => setE(Number(e.target.value))}>{scoreValues.map((v) => <option key={`e-${v}`} value={v}>{v}</option>)}</select>

        <label>Tags</label>
        <input value={tags} onChange={(e) => setTags(e.target.value)} placeholder="comma,separated" />

        <label>Notes</label>
        <textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={4} />

        <p className="o-delta">Computed O_delta: {oDelta}</p>

        <button type="submit">Save Action</button>
      </form>
    </section>
  );
}
