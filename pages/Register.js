import { useState } from "react";
import { useNavigate } from "react-router-dom";

function Register() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showRules, setShowRules] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Password rules checks
  const rules = {
    length: password.length >= 8,
    digit: /[0-9]/.test(password),
    upper: /[A-Z]/.test(password),
    lower: /[a-z]/.test(password),
    special: /[^A-Za-z0-9]/.test(password),
  };

  const allValid =
    rules.length &&
    rules.digit &&
    rules.upper &&
    rules.lower &&
    rules.special;

  // Strength calculation
  const getStrength = () => {
    if (password.length === 0)
      return { width: "0%", text: "", color: "" };

    if (!allValid)
      return { width: "50%", text: "Medium", color: "orange" };

    return { width: "100%", text: "Strong", color: "green" };
  };

  const strength = getStrength();

  const handleRegister = async () => {
    if (!name || !email || !password || !confirmPassword) {
      setError("All fields are required");
      return;
    }

    if (!allValid) {
      setError("Password does not meet requirements");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);
    setError("");

    const res = await fetch("http://localhost:5000/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password }),
    });

    const data = await res.json();
    setLoading(false);

    if (res.ok) {
      alert("Registration successful");
      navigate("/login");
    } else {
      setError(data.message);
    }
  };

  return (
    <div className="page-center">
      <div className="card">
        <h2>Create Account</h2>

        {error && <div className="error">{error}</div>}

        <input
          type="text"
          placeholder="Full Name"
          onChange={(e) => setName(e.target.value)}
        />

        <input
          type="email"
          placeholder="Email"
          onChange={(e) => setEmail(e.target.value)}
        />

        {/* Password with rules */}
        <div className="password-wrapper">
          <input
            type="password"
            placeholder="Password"
            onFocus={() => setShowRules(true)}
            onBlur={() => setShowRules(false)}
            onChange={(e) => setPassword(e.target.value)}
          />

          {showRules && (
            <div className="password-rules">
              <p className={rules.length ? "rule-ok" : "rule-bad"}>
                • Minimum 8 characters
              </p>
              <p className={rules.digit ? "rule-ok" : "rule-bad"}>
                • At least 1 digit
              </p>
              <p className={rules.upper ? "rule-ok" : "rule-bad"}>
                • At least 1 uppercase letter
              </p>
              <p className={rules.lower ? "rule-ok" : "rule-bad"}>
                • At least 1 lowercase letter
              </p>
              <p className={rules.special ? "rule-ok" : "rule-bad"}>
                • At least 1 special character
              </p>
            </div>
          )}
        </div>

        {/* Strength meter */}
        <div className="strength-bar">
          <div
            className="strength-fill"
            style={{
              width: strength.width,
              background: strength.color,
            }}
          ></div>
        </div>
        <div className="strength-text" style={{ color: strength.color }}>
          {strength.text}
        </div>

        <input
          type="password"
          placeholder="Confirm Password"
          onChange={(e) => setConfirmPassword(e.target.value)}
        />

        <button onClick={handleRegister}>
          {loading ? <div className="loader"></div> : "Register"}
        </button>

        <p style={{ marginTop: "15px", fontSize: "14px" }}>
          Already have an account?{" "}
          <span
            style={{ color: "#0b3c6d", cursor: "pointer" }}
            onClick={() => navigate("/login")}
          >
            Login
          </span>
        </p>
      </div>
    </div>
  );
}

export default Register;
