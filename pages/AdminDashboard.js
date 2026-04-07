import { useEffect, useState } from "react";

function AdminDashboard() {

  const [users, setUsers] = useState([]);
  const [logs, setLogs] = useState([]);
  const [report, setReport] = useState(null);

  const [error, setError] = useState("");

  // ================= USERS =================
  const fetchUsers = async () => {
    try {
      const res = await fetch("http://localhost:5000/admin/users", {
        credentials: "include"
      });

      if (!res.ok) {
        throw new Error("Failed to fetch users");
      }

      const data = await res.json();
      setUsers(data);

    } catch (err) {
      console.error(err);
      setError("❌ Unable to load users (Check admin access)");
    }
  };

  // ================= LOGS =================
  const fetchLogs = async () => {
    try {
      const res = await fetch("http://localhost:5000/admin/logs", {
        credentials: "include"
      });

      if (!res.ok) {
        throw new Error("Failed to fetch logs");
      }

      const data = await res.json();
      setLogs(data);

    } catch (err) {
      console.error(err);
    }
  };

  // ================= REPORT =================
  const fetchReport = async () => {
    try {
      const res = await fetch("http://localhost:5000/admin/report", {
        credentials: "include"
      });

      if (!res.ok) {
        throw new Error("Failed to fetch report");
      }

      const data = await res.json();
      setReport(data);

    } catch (err) {
      console.error(err);
    }
  };

  // ================= DELETE USER =================
  const deleteUser = async (id) => {
    if (!window.confirm("Are you sure to delete this user?")) return;

    try {
      await fetch(`http://localhost:5000/admin/delete-user/${id}`, {
        method: "DELETE",
        credentials: "include"
      });

      fetchUsers();

    } catch (err) {
      console.error(err);
    }
  };

  // ================= RESET USER =================
  const resetUser = async (id) => {
    try {
      await fetch(`http://localhost:5000/admin/reset-user/${id}`, {
        method: "POST",
        credentials: "include"
      });

      alert("User data reset");

    } catch (err) {
      console.error(err);
    }
  };

  // ================= LOAD DATA =================
  useEffect(() => {
    fetchUsers();
    fetchLogs();
    fetchReport();
  }, []);

  return (
    <div className="dashboard-container">

      <h2>⚙️ Admin Panel</h2>

      {/* ERROR */}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {/* ================= PDF DOWNLOAD ================= */}
      <button
        onClick={() => window.open("http://localhost:5000/admin/report/pdf")}
        style={{
          marginBottom: "20px",
          background: "#0b3c6d",
          color: "#fff",
          padding: "10px",
          borderRadius: "8px"
        }}
      >
        📄 Download PDF Report
      </button>

      {/* ================= REPORT CARDS ================= */}
      {report && (
        <div style={{ display: "flex", gap: "20px", marginBottom: "30px" }}>

          <div className="card">
            <h4>Total Users</h4>
            <p>{report.total_users}</p>
          </div>

          <div className="card">
            <h4>Total Transactions</h4>
            <p>{report.total_transactions}</p>
          </div>

          <div className="card">
            <h4>Total Spent</h4>
            <p>₹{report.total_spent}</p>
          </div>

          <div className="card">
            <h4>This Month</h4>
            <p>₹{report.monthly_spent}</p>
          </div>

        </div>
      )}

      {/* ================= USERS ================= */}
      <h3>👥 Users</h3>

      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Actions</th>
          </tr>
        </thead>

        <tbody>
          {users.length === 0 ? (
            <tr>
              <td colSpan="3">No users found</td>
            </tr>
          ) : (
            users.map(u => (
              <tr key={u.id}>
                <td>{u.name}</td>
                <td>{u.email}</td>
                <td>
                  <button onClick={() => deleteUser(u.id)}>
                    Delete
                  </button>

                  <button onClick={() => resetUser(u.id)}>
                    Reset
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>

      {/* ================= LOGS ================= */}
      <h3 style={{ marginTop: "30px" }}>📜 Logs</h3>

      <table>
        <thead>
          <tr>
            <th>User ID</th>
            <th>Action</th>
            <th>Time</th>
          </tr>
        </thead>

        <tbody>
          {logs.length === 0 ? (
            <tr>
              <td colSpan="3">No logs available</td>
            </tr>
          ) : (
            logs.map((l, i) => (
              <tr key={i}>
                <td>{l.user_id}</td>
                <td>{l.action}</td>
                <td>{l.time}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>

    </div>
  );
}

export default AdminDashboard;