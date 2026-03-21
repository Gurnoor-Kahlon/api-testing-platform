import { useEffect, useMemo, useState } from "react";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
} from "chart.js";
import { Pie, Bar } from "react-chartjs-2";

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
);

type TestRun = {
  id: number;
  test_name: string;
  test_type: string;
  status: string;
  result: string | null;
  execution_time: number | null;
  created_at: string;
};

type TestSession = {
  id: string;
  status: string;
  started_at: string | null;
  finished_at: string | null;
  return_code: number | null;
  stdout: string | null;
  stderr: string | null;
};

function App() {
  const BACKEND_URL = "http://localhost:8000";

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const [token, setToken] = useState("");
  const [testRuns, setTestRuns] = useState<TestRun[]>([]);
  const [sessions, setSessions] = useState<TestSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [dashboardError, setDashboardError] = useState("");

  const [statusFilter, setStatusFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [sortOption, setSortOption] = useState("");

  const [runStatus, setRunStatus] = useState("");
  const [currentSessionId, setCurrentSessionId] = useState("");
  const [runOutput, setRunOutput] = useState("");
  const [isRunningTests, setIsRunningTests] = useState(false);

  const handleLogin = () => {
    if (username === "admin" && password === "password123") {
      setMessage("Login successful");
    } else {
      setMessage("Invalid username or password");
    }
  };

  const fetchLatestTestRuns = async (authToken: string) => {
    const params = new URLSearchParams();
    if (statusFilter) params.append("status", statusFilter);
    if (typeFilter) params.append("test_type", typeFilter);
    if (sortOption) params.append("sort", sortOption);

    const url = `${BACKEND_URL}/test-runs${
      params.toString() ? `?${params.toString()}` : ""
    }`;

    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to fetch test runs");
    }

    const data = await response.json();
    setTestRuns(Array.isArray(data) ? data : []);
  };

  const fetchSessions = async (authToken: string) => {
    const response = await fetch(`${BACKEND_URL}/test-sessions`, {
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to fetch sessions");
    }

    const data = await response.json();
    setSessions(Array.isArray(data) ? data : []);
  };

  const runAllTests = async () => {
    if (!token) return;

    try {
      setIsRunningTests(true);
      setRunStatus("Starting test session...");
      setRunOutput("");

      const response = await fetch(`${BACKEND_URL}/test-sessions/run-all`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to start test session");
      }

      const data = await response.json();
      const sessionId = data.session_id;
      setCurrentSessionId(sessionId);

      const interval = setInterval(async () => {
        try {
          const statusResponse = await fetch(
            `${BACKEND_URL}/test-sessions/${sessionId}`,
            {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }
          );

          if (!statusResponse.ok) {
            throw new Error("Failed to fetch test session status");
          }

          const sessionData = await statusResponse.json();
          setRunStatus(sessionData.status);
          setRunOutput(sessionData.stdout || sessionData.stderr || "");

          if (
            sessionData.status === "completed" ||
            sessionData.status === "failed"
          ) {
            clearInterval(interval);
            setIsRunningTests(false);
            await fetchLatestTestRuns(token);
            await fetchSessions(token);
          }
        } catch (error) {
          clearInterval(interval);
          setIsRunningTests(false);
          setRunStatus("failed");
          setRunOutput("Could not fetch test session status");
        }
      }, 2000);
    } catch (error) {
      setIsRunningTests(false);
      setRunStatus("failed");
      setRunOutput("Could not start test session");
    }
  };

  const clearAllTestRuns = async () => {
    if (!token) return;

    const confirmed = window.confirm(
      "Are you sure you want to delete all saved test runs?"
    );

    if (!confirmed) return;

    try {
      const response = await fetch(`${BACKEND_URL}/test-runs`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to clear test runs");
      }

      setTestRuns([]);
      setRunStatus("");
      setCurrentSessionId("");
      setRunOutput("");
    } catch (error) {
      console.error("Clear test runs failed:", error);
      alert("Could not clear test runs");
    }
  };

  useEffect(() => {
    const autoLogin = async () => {
      try {
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
          throw new Error("No access token returned");
        }

        setToken(accessToken);
        await fetchSessions(accessToken);
      } catch (error) {
        console.error("Auto-login failed:", error);
        setDashboardError("Could not authenticate with backend");
        setLoading(false);
      }
    };

    autoLogin();
  }, []);

  useEffect(() => {
    const fetchTestRuns = async () => {
      if (!token) return;

      try {
        setLoading(true);
        setDashboardError("");

        const params = new URLSearchParams();
        if (statusFilter) params.append("status", statusFilter);
        if (typeFilter) params.append("test_type", typeFilter);
        if (sortOption) params.append("sort", sortOption);

        const url = `${BACKEND_URL}/test-runs${
          params.toString() ? `?${params.toString()}` : ""
        }`;

        const response = await fetch(url, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch test runs");
        }

        const data = await response.json();
        setTestRuns(Array.isArray(data) ? data : []);
      } catch (error) {
        console.error("Fetch test runs failed:", error);
        setDashboardError("Could not load dashboard data");
      } finally {
        setLoading(false);
      }
    };

    fetchTestRuns();
  }, [token, statusFilter, typeFilter, sortOption]);

  const stats = useMemo(() => {
    const total = testRuns.length;
    const passed = testRuns.filter((t) => t.status === "passed").length;
    const failed = testRuns.filter((t) => t.status === "failed").length;
    const api = testRuns.filter((t) => t.test_type === "api").length;
    const ui = testRuns.filter((t) => t.test_type === "ui").length;

    return { total, passed, failed, api, ui };
  }, [testRuns]);

  const pieData = {
    labels: ["Passed", "Failed"],
    datasets: [
      {
        data: [stats.passed, stats.failed],
        backgroundColor: ["#22c55e", "#ef4444"],
        borderColor: ["#16a34a", "#dc2626"],
        borderWidth: 2,
      },
    ],
  };

  const barData = {
    labels: ["API", "UI"],
    datasets: [
      {
        label: "Test Count",
        data: [stats.api, stats.ui],
        backgroundColor: ["#3b82f6", "#a855f7"],
        borderColor: ["#2563eb", "#9333ea"],
        borderWidth: 2,
      },
    ],
  };

  const pieOptions = {
    plugins: {
      legend: {
        labels: {
          color: "white",
        },
      },
    },
  };

  const barOptions = {
    plugins: {
      legend: {
        labels: {
          color: "white",
        },
      },
    },
    scales: {
      x: {
        ticks: {
          color: "white",
        },
        grid: {
          color: "#374151",
        },
      },
      y: {
        ticks: {
          color: "white",
          stepSize: 1,
        },
        grid: {
          color: "#374151",
        },
      },
    },
  };

  const getStatusColor = (status: string) => {
    if (status === "passed") return "limegreen";
    if (status === "failed") return "red";
    return "white";
  };

  const getSessionStatusColor = (status: string) => {
    if (status === "completed") return "limegreen";
    if (status === "failed") return "red";
    if (status === "running") return "orange";
    return "white";
  };

  return (
    <div
      style={{
        padding: "40px",
        maxWidth: "1200px",
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
          style={{ padding: "8px", width: "260px" }}
        />
      </div>

      <div style={{ marginTop: "10px" }}>
        <input
          id="password"
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ padding: "8px", width: "260px" }}
        />
      </div>

      <button
        id="login-button"
        onClick={handleLogin}
        style={{ marginTop: "10px", padding: "10px 18px" }}
      >
        Login
      </button>

      {message && <p id="message">{message}</p>}

      <hr style={{ margin: "40px 0" }} />

      <h2>Test Runs Dashboard</h2>

      <div
        style={{
          marginBottom: "20px",
          display: "flex",
          gap: "20px",
          flexWrap: "wrap",
          fontSize: "18px",
        }}
      >
        <div>📊 Total: {stats.total}</div>
        <div style={{ color: "limegreen" }}>✅ Passed: {stats.passed}</div>
        <div style={{ color: "red" }}>❌ Failed: {stats.failed}</div>
        <div>🧪 API: {stats.api}</div>
        <div>🖥️ UI: {stats.ui}</div>
      </div>

      <div
        style={{
          marginBottom: "25px",
          display: "flex",
          gap: "10px",
          flexWrap: "wrap",
        }}
      >
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

        <select
          value={sortOption}
          onChange={(e) => setSortOption(e.target.value)}
          style={{ padding: "8px" }}
        >
          <option value="">No Sort</option>
          <option value="execution_time">Execution Time (Low to High)</option>
          <option value="-execution_time">Execution Time (High to Low)</option>
          <option value="newest">Newest First</option>
          <option value="oldest">Oldest First</option>
        </select>
      </div>

      <div style={{ marginBottom: "20px", display: "flex", gap: "10px" }}>
        <button
          onClick={runAllTests}
          disabled={isRunningTests || !token}
          style={{
            padding: "10px 18px",
            fontWeight: "bold",
            cursor: isRunningTests ? "not-allowed" : "pointer",
          }}
        >
          {isRunningTests ? "Running Tests..." : "Run All Tests"}
        </button>

        <button
          onClick={clearAllTestRuns}
          disabled={isRunningTests || !token}
          style={{
            padding: "10px 18px",
            fontWeight: "bold",
            cursor: isRunningTests ? "not-allowed" : "pointer",
          }}
        >
          Clear Results
        </button>
      </div>

      {runStatus && (
        <div
          style={{
            marginBottom: "20px",
            padding: "12px",
            backgroundColor: "#111827",
            borderRadius: "8px",
          }}
        >
          <p><strong>Session Status:</strong> {runStatus}</p>
          {currentSessionId && (
            <p><strong>Session ID:</strong> {currentSessionId}</p>
          )}
          {runOutput && (
            <pre
              style={{
                whiteSpace: "pre-wrap",
                overflowX: "auto",
                marginTop: "10px",
                fontSize: "13px",
              }}
            >
              {runOutput}
            </pre>
          )}
        </div>
      )}

      {loading && <p>Loading test runs...</p>}
      {!loading && dashboardError && <p>{dashboardError}</p>}

      {!loading && !dashboardError && (
        <>
          <div
            style={{
              backgroundColor: "#111827",
              padding: "20px",
              borderRadius: "12px",
              marginBottom: "30px",
            }}
          >
            <h3 style={{ marginBottom: "15px" }}>Recent Test Sessions</h3>

            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th style={{ border: "1px solid gray", padding: "8px" }}>ID</th>
                  <th style={{ border: "1px solid gray", padding: "8px" }}>Status</th>
                  <th style={{ border: "1px solid gray", padding: "8px" }}>Started At</th>
                </tr>
              </thead>
              <tbody>
                {sessions.map((session) => (
                  <tr key={session.id}>
                    <td style={{ border: "1px solid gray", padding: "8px" }}>
                      {session.id.slice(0, 8)}
                    </td>
                    <td
                      style={{
                        border: "1px solid gray",
                        padding: "8px",
                        color: getSessionStatusColor(session.status),
                        fontWeight: "bold",
                      }}
                    >
                      {session.status}
                    </td>
                    <td style={{ border: "1px solid gray", padding: "8px" }}>
                      {session.started_at
                        ? new Date(session.started_at).toLocaleString()
                        : "N/A"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "30px",
              marginBottom: "30px",
              alignItems: "start",
            }}
          >
            <div
              style={{
                backgroundColor: "#111827",
                padding: "20px",
                borderRadius: "12px",
              }}
            >
              <h3 style={{ marginBottom: "15px" }}>Pass vs Fail</h3>
              <div style={{ maxWidth: "320px", margin: "0 auto" }}>
                <Pie data={pieData} options={pieOptions} />
              </div>
            </div>

            <div
              style={{
                backgroundColor: "#111827",
                padding: "20px",
                borderRadius: "12px",
              }}
            >
              <h3 style={{ marginBottom: "15px" }}>API vs UI Tests</h3>
              <Bar data={barData} options={barOptions} />
            </div>
          </div>

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
              {testRuns.map((testRun) => (
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
        </>
      )}
    </div>
  );
}

export default App;