import { useState } from "react";

function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleLogin = () => {
    if (username === "admin" && password === "password123") {
      setMessage("Login successful");
    } else {
      setMessage("Invalid username or password");
    }
  };

  return (
    <div style={{ padding: "40px" }}>
      <h1>Login Demo</h1>

      <div>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
      </div>

      <div style={{ marginTop: "10px" }}>
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </div>

      <button onClick={handleLogin} style={{ marginTop: "10px" }}>
        Login
      </button>

      {message && <p id="message">{message}</p>}
    </div>
  );
}

export default App;