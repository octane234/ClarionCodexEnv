import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createExposure } from '../api';

const exposureTypes = ['application', 'outreach', 'post', 'proposal', 'interview', 'portfolio_update'];

export default function LogExposurePage() {
  const navigate = useNavigate();
  const [type, setType] = useState(exposureTypes[0]);
  const [occurredAt, setOccurredAt] = useState(new Date().toISOString().slice(0, 16));
  const [notes, setNotes] = useState('');

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    await createExposure({
      type,
      occurred_at: new Date(occurredAt).toISOString(),
      notes,
    });
    navigate('/dashboard');
  }

  return (
    <section className="card form-card">
      <h2>Log Exposure</h2>
      <form onSubmit={onSubmit} className="form-grid">
        <label>Type</label>
        <select value={type} onChange={(e) => setType(e.target.value)}>
          {exposureTypes.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>

        <label>Occurred At</label>
        <input type="datetime-local" value={occurredAt} onChange={(e) => setOccurredAt(e.target.value)} required />

        <label>Notes</label>
        <textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={4} />

        <button type="submit">Save Exposure</button>
      </form>
    </section>
  );
}
