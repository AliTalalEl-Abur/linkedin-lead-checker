import { useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://linkedin-lead-checker-api.onrender.com';

export default function DebugAuth() {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState('');
  const [responseText, setResponseText] = useState('');
  const [errorText, setErrorText] = useState('');
  const [loading, setLoading] = useState(false);

  const handleTest = async (e) => {
    e.preventDefault();
    setStatus('');
    setResponseText('');
    setErrorText('');
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });

      setStatus(`HTTP ${res.status}`);
      const text = await res.text();
      setResponseText(text);
    } catch (err) {
      setErrorText(err?.message || String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ maxWidth: 720, margin: '40px auto', fontFamily: 'system-ui' }}>
      <h1>Debug Auth</h1>
      <p><strong>API_URL:</strong> {API_URL}</p>
      <form onSubmit={handleTest}>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ display: 'block', width: '100%', padding: 8, marginTop: 6, marginBottom: 12 }}
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? 'Testing...' : 'Test /auth/login'}
        </button>
      </form>

      {status && (
        <p><strong>Status:</strong> {status}</p>
      )}
      {responseText && (
        <pre style={{ background: '#111', color: '#0f0', padding: 12, overflow: 'auto' }}>{responseText}</pre>
      )}
      {errorText && (
        <pre style={{ background: '#111', color: '#f66', padding: 12, overflow: 'auto' }}>{errorText}</pre>
      )}
    </main>
  );
}
