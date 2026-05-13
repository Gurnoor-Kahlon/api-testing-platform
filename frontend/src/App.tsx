import { useEffect, useMemo, useState } from 'react';
import './App.css';

type Summary = {
  total_projects: number;
  total_test_cases: number;
  total_test_suites: number;
  total_test_runs: number;
  total_passed_runs: number;
  total_failed_runs: number;
  overall_pass_rate: number;
  average_response_time_ms: number | null;
  most_recently_updated_project: string | null;
  trend: { date: string; passed: number; failed: number }[];
  latest_test_runs: { id: number; project_name: string; status: string; actual_response_time_ms: number | null; created_at: string }[];
  latest_failed_tests: { id: number; project_name: string; failure_reason: string | null; created_at: string }[];
};

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

function App() {
  const [token, setToken] = useState('');
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [authLoading, setAuthLoading] = useState(false);
  const [isSignupMode, setIsSignupMode] = useState(false);

  const [email, setEmail] = useState('owner@example.com');
  const [password, setPassword] = useState('Password123');
  const [fullName, setFullName] = useState('Owner User');

  const isAuthed = Boolean(token);

  const fetchSummary = async (authToken: string) => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_URL}/dashboard/summary`, { headers: { Authorization: `Bearer ${authToken}` } });
      if (!response.ok) throw new Error('Could not load dashboard data.');
      setSummary(await response.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (emailValue: string, passwordValue: string) => {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: emailValue, password: passwordValue }),
    });
    if (!response.ok) {
      throw new Error('Invalid credentials.');
    }
    const data = await response.json();
    setToken(data.access_token);
  };

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setAuthLoading(true);

    try {
      if (isSignupMode) {
        const registerResponse = await fetch(`${API_URL}/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password, full_name: fullName }),
        });

        if (!registerResponse.ok) {
          const payload = await registerResponse.json().catch(() => null);
          throw new Error(payload?.detail ?? 'Could not create account.');
        }
      }

      await handleLogin(email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown authentication error.');
    } finally {
      setAuthLoading(false);
    }
  };

  useEffect(() => {
    if (token) fetchSummary(token);
  }, [token]);

  const chartBars = useMemo(() => summary?.trend ?? [], [summary]);

  if (!isAuthed) {
    return <main className='auth'><form onSubmit={handleAuthSubmit} className='card'><h1>API Testing Platform</h1><p>{isSignupMode ? 'Create an account to start running API tests.' : 'Sign in to view your engineering dashboard.'}</p>{isSignupMode && <input value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder='Full name' />}<input value={email} onChange={(e) => setEmail(e.target.value)} placeholder='Email' /><input value={password} onChange={(e) => setPassword(e.target.value)} type='password' placeholder='Password' /><button type='submit' disabled={authLoading}>{authLoading ? 'Please wait...' : isSignupMode ? 'Create account' : 'Login'}</button><button type='button' onClick={() => { setIsSignupMode(!isSignupMode); setError(''); }} className='secondary'>{isSignupMode ? 'Already have an account? Login' : 'New user? Create account'}</button>{error && <p className='error'>{error}</p>}</form></main>;
  }

  return <main className='layout'>
    <aside className='sidebar'><h2>QA Ops</h2><nav><a>Dashboard</a><a>Projects</a><a>Test Cases</a><a>Test Suites</a><a>Run History</a></nav></aside>
    <section className='content'>
      <header><h1>Dashboard Overview</h1><button onClick={() => fetchSummary(token)}>Refresh</button></header>
      {loading && <p className='state'>Loading dashboard data...</p>}
      {error && <p className='error'>{error}</p>}
      {!loading && !error && summary && <>
        <div className='grid'>
          <article className='card'><h3>Projects</h3><strong>{summary.total_projects}</strong></article>
          <article className='card'><h3>Test Cases</h3><strong>{summary.total_test_cases}</strong></article>
          <article className='card'><h3>Test Suites</h3><strong>{summary.total_test_suites}</strong></article>
          <article className='card'><h3>Pass Rate</h3><strong>{summary.overall_pass_rate}%</strong></article>
          <article className='card'><h3>Avg Response</h3><strong>{summary.average_response_time_ms ?? 0}ms</strong></article>
          <article className='card'><h3>Recent Project</h3><strong>{summary.most_recently_updated_project ?? 'None'}</strong></article>
        </div>
        <section className='panel'><h3>Run Trend (7 days)</h3><div className='bars'>{chartBars.map((item) => <div key={item.date} className='bar-group'><span className='bar pass' style={{ height: `${item.passed * 12 + 6}px` }} /><span className='bar fail' style={{ height: `${item.failed * 12 + 6}px` }} /><small>{item.date.slice(5)}</small></div>)}</div></section>
        <section className='two-col'>
          <article className='panel'><h3>Latest Test Runs</h3>{summary.latest_test_runs.length === 0 ? <p className='state'>No test runs yet.</p> : <table><thead><tr><th>Project</th><th>Status</th><th>Response</th></tr></thead><tbody>{summary.latest_test_runs.map((run) => <tr key={run.id}><td>{run.project_name}</td><td><span className={`badge ${run.status}`}>{run.status}</span></td><td>{run.actual_response_time_ms ?? '-'} ms</td></tr>)}</tbody></table>}</article>
          <article className='panel'><h3>Recent Failures</h3>{summary.latest_failed_tests.length === 0 ? <p className='state'>No recent failures 🎉</p> : <ul>{summary.latest_failed_tests.map((f) => <li key={f.id}><strong>{f.project_name}</strong><p>{f.failure_reason ?? 'Unknown error'}</p></li>)}</ul>}</article>
        </section>
      </>}
    </section>
  </main>;
}

export default App;
