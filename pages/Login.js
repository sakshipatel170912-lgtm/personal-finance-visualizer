import { useState } from "react";
import { useNavigate } from "react-router-dom";

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async () => {
    setLoading(true);
    setError("");

    try {
      const res = await fetch("http://localhost:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include", // 
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (res.ok) {
        alert("Login successful");
        navigate("/dashboard"); // go to dashboard
      } else {
        setError(data.message || "Login failed");
      }
    } catch (err) {
      setError("Cannot connect to backend. Make sure Flask is running.");
    }

    setLoading(false);
  };

  return (
    <div className="page-center">
      <div className="card">
        <h2>Login</h2>

        {error && <div className="error">{error}</div>}

        <input
          type="email"
          placeholder="Email"
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          onChange={(e) => setPassword(e.target.value)}
        />

        <p
          style={{ cursor: "pointer", color: "#0b3c6d" }}
          onClick={() => navigate("/forgot-password")}
        >
          Forgot password?
        </p>

        <button onClick={handleLogin} disabled={loading}>
          {loading ? "Loading..." : "Login"}
        </button>
      </div>
    </div>
  );
}

export default Login;
