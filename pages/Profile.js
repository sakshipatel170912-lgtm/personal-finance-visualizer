import { useEffect, useState } from "react";

function Profile() {

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    currency: "INR",
    theme: "light",
    notifications: false,
    savings_goal: "",
    budget: ""
  });

  const [loading, setLoading] = useState(true);

  // ================= LOAD USER DATA =================
  useEffect(() => {
    fetch("http://localhost:5000/api/profile", {
      credentials: "include"
    })
      .then(res => res.json())
      .then(data => {
        setForm({
          name: data.name || "",
          email: data.email || "",
          password: "",
          currency: data.currency || "INR",
          theme: data.theme || "light",
          notifications: data.notifications || false,
          savings_goal: data.savings_goal || "",
          budget: data.budget || ""
        });

        // ✅ APPLY THEME ON LOAD (FIXED)
        const savedTheme = data.theme || "light";

        document.body.classList.remove("light", "dark");
        document.body.classList.add(savedTheme);

        localStorage.setItem("theme", savedTheme);

        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        alert("Failed to load profile");
        setLoading(false);
      });
  }, []);

  // ================= SAVE ALL =================
  const handleSaveAll = async () => {
    try {
      const res = await fetch("http://localhost:5000/api/profile/update-all", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        credentials: "include",
        body: JSON.stringify(form)
      });

      const data = await res.json();

      if (!res.ok) throw new Error(data.error);

      // 🔥 SAVE + APPLY THEME (FIXED)
      localStorage.setItem("theme", form.theme);

      document.body.classList.remove("light", "dark");
      document.body.classList.add(form.theme);

      alert("Profile Updated Successfully ✅");

      setTimeout(() => {
        window.location.href = "/dashboard";
      }, 800);

    } catch (err) {
      console.error(err);
      alert("Error: " + err.message);
    }
  };

  if (loading) {
    return <h2 style={{ textAlign: "center" }}>Loading Profile...</h2>;
  }

  return (
    <div className="profile-container">
      <h2>User Profile</h2>

      <input
        placeholder="Name"
        value={form.name}
        onChange={(e) => setForm({ ...form, name: e.target.value })}
      />

      <input
        placeholder="Email"
        value={form.email}
        onChange={(e) => setForm({ ...form, email: e.target.value })}
      />

      <h3>Change Password</h3>
      <input
        type="password"
        placeholder="New Password"
        value={form.password}
        onChange={(e) => setForm({ ...form, password: e.target.value })}
      />

      <h3>Preferences</h3>

      <select
        value={form.currency}
        onChange={(e) => setForm({ ...form, currency: e.target.value })}
      >
        <option value="INR">INR</option>
        <option value="USD">USD</option>
        <option value="EUR">EUR</option>
      </select>

      {/* 🔥 FIXED THEME SELECT */}
      <select
        value={form.theme}
        onChange={(e) => {
          const newTheme = e.target.value;

          setForm({ ...form, theme: newTheme });

          document.body.classList.remove("light", "dark");
          document.body.classList.add(newTheme);
        }}
      >
        <option value="light">Light</option>
        <option value="dark">Dark</option>
      </select>

      <label>
        <input
          type="checkbox"
          checked={form.notifications}
          onChange={(e) =>
            setForm({ ...form, notifications: e.target.checked })
          }
        />
        Enable Notifications
      </label>

      <h3>Financial Goals</h3>

      <input
        placeholder="Saving Goal"
        value={form.savings_goal}
        onChange={(e) =>
          setForm({ ...form, savings_goal: e.target.value })
        }
      />

      <input
        placeholder="Budget"
        value={form.budget}
        onChange={(e) =>
          setForm({ ...form, budget: e.target.value })
        }
      />

      <button onClick={handleSaveAll}>
        Save All Changes
      </button>
    </div>
  );
}

export default Profile;