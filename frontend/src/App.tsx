import { useEffect, useMemo, useState } from "react";

type TestRun = {
  id: number;
  test_name: string;
  test_type: string;
  status: string;
  result: string | null;
  execution_time: number | null;
  created_at: string;
};

function App() {
  const BACKEND_URL = "http://localhost:8000";

  // Login demo state
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  // Dashboard state
  const [token, setToken] = useState("");
  const [testRuns, setTestRuns] = useState<TestRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [dashboardError, setDashboardError] = useState("");

  // Filters
  const [statusFilter, setStatusFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");

  const handleLogin = () => {
    if (username === "admin" && password === "password123") {
      setMessage("Login successful");
    } else {
      setMessage("Invalid username or password");
    }
  };

  useEffect(() => {
    const autoLoginAndFetch = async () => {
      try {
        setLoading(true);
        setDashboardError("");

        const loginResponse = await fetch(`${BACKEND_URL}/auth/login`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            username: "admin",
            password: "password123",
          }),
        });

        if (!loginResponse.ok) {
          throw new Error("Failed to log in to backend");
        }

        const loginData = await loginResponse.json();
        const accessToken = loginData.access_token;

        if (!accessToken) {
          throw new Error("No access token returned from backend");
        }

        setToken(accessToken);

        const testRunsResponse = await fetch(`${BACKEND_URL}/test-runs`, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });

        if (!testRunsResponse.ok) {
          throw new Error("Failed to fetch test runs");
        }

        const testRunsData = await testRunsResponse.json();
        setTestRuns(Array.isArray(testRunsData) ? testRunsData : []);
      } catch (error) {
        console.error("Dashboard load error:", error);
        setDashboardError("Could not load dashboard data");
      } finally {
        setLoading(false);
      }
    };

    autoLoginAndFetch();
  }, []);

  const filteredTestRuns = useMemo(() => {
    return testRuns.filter((testRun) => {
      const matchesStatus =
        !statusFilter || testRun.status === statusFilter;
      const matchesType =
        !typeFilter || testRun.test_type === typeFilter;

      return matchesStatus && matchesType;
    });
  }, [testRuns, statusFilter, typeFilter]);

  const stats = useMemo(() => {
    const total = testRuns.length;
    const passed = testRuns.filter((t) => t.status === "passed").length;
    const failed = testRuns.filter((t) => t.status === "failed").length;
    const api = testRuns.filter((t) => t.test_type === "api").length;
    const ui = testRuns.filter((t) => t.test_type === "ui").length;

    return { total, passed, failed, api, ui };
  }, [testRuns]);

  const getStatusColor = (status: string) => {
    if (status === "passed") return "limegreen";
    if (status === "failed") return "red";
    return "white";
  };

  return (
    <div
      style={{
        padding: "40px",
        maxWidth: "1100px",
        margin: "0 auto",
        color: "white",
      }}
    >
      <h1>Login Demo</h1>

      <div>
        <input
          id="username"
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={{ padding: "8px", width: "220px" }}
        />
      </div>

      <div style={{ marginTop: "10px" }}>
        <input
          id="password"
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ padding: "8px", width: "220px" }}
        />
      </div>

      <button
        id="login-button"
        onClick={handleLogin}
        style={{ marginTop: "10px", padding: "8px 16px" }}
      >
        Login
      </button>

      {message && <p id="message">{message}</p>}

      <hr style={{ margin: "40px 0" }} />

      <h2>Test Runs Dashboard</h2>

      <div style={{ marginBottom: "20px", display: "flex", gap: "20px", flexWrap: "wrap" }}>
        <div>📊 Total: {stats.total}</div>
        <div style={{ color: "limegreen" }}>✅ Passed: {stats.passed}</div>
        <div style={{ color: "red" }}>❌ Failed: {stats.failed}</div>
        <div>🧪 API: {stats.api}</div>
        <div>🖥️ UI: {stats.ui}</div>
      </div>

      <div style={{ marginBottom: "20px", display: "flex", gap: "10px" }}>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          style={{ padding: "8px" }}
        >
          <option value="">All Status</option>
          <option value="passed">Passed</option>
          <option value="failed">Failed</option>
        </select>

        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          style={{ padding: "8px" }}
        >
          <option value="">All Types</option>
          <option value="api">API</option>
          <option value="ui">UI</option>
        </select>
      </div>

      {loading && <p>Loading test runs...</p>}

      {!loading && dashboardError && <p>{dashboardError}</p>}

      {!loading && !dashboardError && token && (
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            marginTop: "20px",
          }}
        >
          <thead>
            <tr>
              <th style={{ border: "1px solid gray", padding: "8px" }}>ID</th>
              <th style={{ border: "1px solid gray", padding: "8px" }}>Test Name</th>
              <th style={{ border: "1px solid gray", padding: "8px" }}>Type</th>
              <th style={{ border: "1px solid gray", padding: "8px" }}>Status</th>
              <th style={{ border: "1px solid gray", padding: "8px" }}>Result</th>
              <th style={{ border: "1px solid gray", padding: "8px" }}>Execution Time</th>
              <th style={{ border: "1px solid gray", padding: "8px" }}>Created At</th>
            </tr>
          </thead>
          <tbody>
            {filteredTestRuns.map((testRun) => (
              <tr key={testRun.id}>
                <td style={{ border: "1px solid gray", padding: "8px" }}>
                  {testRun.id}
                </td>
                <td style={{ border: "1px solid gray", padding: "8px" }}>
                  {testRun.test_name}
                </td>
                <td style={{ border: "1px solid gray", padding: "8px" }}>
                  {testRun.test_type}
                </td>
                <td
                  style={{
                    border: "1px solid gray",
                    padding: "8px",
                    color: getStatusColor(testRun.status),
                    fontWeight: "bold",
                  }}
                >
                  {testRun.status}
                </td>
                <td style={{ border: "1px solid gray", padding: "8px" }}>
                  {testRun.result ?? "N/A"}
                </td>
                <td style={{ border: "1px solid gray", padding: "8px" }}>
                  {testRun.execution_time ?? "N/A"}
                </td>
                <td style={{ border: "1px solid gray", padding: "8px" }}>
                  {new Date(testRun.created_at).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default App;