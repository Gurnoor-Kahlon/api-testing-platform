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

function App() {
  const BACKEND_URL = "http://localhost:8000";

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const [token, setToken] = useState("");
  const [testRuns, setTestRuns] = useState<TestRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [dashboardError, setDashboardError] = useState("");

  const [statusFilter, setStatusFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [sortOption, setSortOption] = useState("");

  const handleLogin = () => {
    if (username === "admin" && password === "password123") {
      setMessage("Login successful");
    } else {
      setMessage("Invalid username or password");
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

        const url = `${BACKEND_URL}/test-runs${params.toString() ? `?${params.toString()}` : ""}`;

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
        borderWidth: 1,
      },
    ],
  };

  const barData = {
    labels: ["API", "UI"],
    datasets: [
      {
        label: "Test Count",
        data: [stats.api, stats.ui],
        borderWidth: 1,
      },
    ],
  };

  const getStatusColor = (status: string) => {
    if (status === "passed") return "limegreen";
    if (status === "failed") return "red";
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

      {loading && <p>Loading test runs...</p>}
      {!loading && dashboardError && <p>{dashboardError}</p>}

      {!loading && !dashboardError && (
        <>
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
                <Pie data={pieData} />
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
              <Bar data={barData} />
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