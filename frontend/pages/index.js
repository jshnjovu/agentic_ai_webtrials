import { useState } from 'react';

export default function Home() {
  const [location, setLocation] = useState('');
  const [niche, setNiche] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);

  const runAgent = async () => {
    setLoading(true);
    // TODO: Call backend API to run agent and return results
    // Placeholder demo:
    setTimeout(() => {
      setResults([
        { business_name: 'Example Co', score_overall: 55 },
        { business_name: 'Sample Services', score_overall: 92 }
      ]);
      setLoading(false);
    }, 1500);
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'system-ui, sans-serif' }}>
      <h1>LeadGen Website Makeover Agent</h1>
      <p>Enter a location and niche, then run the agent.</p>

      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
        <input placeholder="Location" value={location} onChange={e => setLocation(e.target.value)} />
        <input placeholder="Niche" value={niche} onChange={e => setNiche(e.target.value)} />
        <button onClick={runAgent} disabled={loading || !location || !niche}>
          {loading ? 'Running…' : 'Run Agent'}
        </button>
      </div>

      <div>
        {results.length > 0 && results.map((r, i) => (
          <div key={i} style={{ padding: '0.5rem 0' }}>
            <strong>{r.business_name}</strong> — Score: {r.score_overall}
          </div>
        ))}
      </div>
    </div>
  );
}
