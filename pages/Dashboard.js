import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Chatbot from "./chatbot";

function Dashboard() {

  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showTransactions, setShowTransactions] = useState(false);

  const [user, setUser] = useState({
    name: "",
    email: "",
    is_admin: false   // ✅ ADD THIS
  });

  const [stats, setStats] = useState({
    total_spent: 0,
    budget: 0,
    savings: 0
  });

  const navigate = useNavigate();

  // =========================
  // Fetch Dashboard Stats
  // =========================
  const fetchDashboard = async () => {
    try {
      const res = await fetch("http://localhost:5000/api/dashboard", {
        credentials: "include"
      });

      const data = await res.json();

      setUser({
        name: data.user.name,
        email: data.user.email,
        is_admin: data.user.is_admin   // ✅ IMPORTANT
      });

      setStats({
        total_spent: data.total_spent,
        budget: data.budget,
        savings: data.savings
      });

    } catch (error) {
      console.error(error);
      alert("Failed to load dashboard");
    }
  };

  // =========================
  // Fetch Transactions
  // =========================
  const fetchTransactions = async () => {
    try {
      const res = await fetch("http://localhost:5000/api/transactions/latest", {
        credentials: "include"
      });

      const data = await res.json();

      setTransactions(data);
      setShowTransactions(true);

    } catch (error) {
      console.error(error);
      alert("Failed to load transactions");
    }
  };

  useEffect(() => {
    const loadData = async () => {
      await fetchDashboard();
      setLoading(false);
    };

    loadData();
  }, []);

  if (loading) {
    return <h2 style={{ textAlign: "center" }}>Loading...</h2>;
  }

  const budgetUsed =
    stats.budget > 0
      ? ((stats.total_spent / stats.budget) * 100).toFixed(0)
      : 0;

  return (
    <>
      <div className="dashboard-container">

        {/* ================= TOP BAR ================= */}
        <div className="top-bar">

          <div>
            <h2>Welcome, {user.name || user.email}</h2>
            <p>{user.email}</p>
          </div>

          <div style={{ display: "flex", gap: "10px" }}>

            {/* 👤 PROFILE */}
            <button onClick={() => navigate("/profile")}>
              👤 Profile
            </button>

            {/* 🔥 ADMIN BUTTON (ONLY FOR ADMIN) */}
            {user.is_admin && (
              <button
                style={{ background: "#dc2626" }}
                onClick={() => navigate("/admin")}
              >
                ⚙️ Admin Panel
              </button>
            )}

            {/* 🚪 LOGOUT */}
            <button onClick={() => navigate("/")}>
              Logout
            </button>

          </div>

        </div>

        {/* ================= STATS ================= */}
        <div className="card-row">

          <div className="card">
            <h3>Total Spent</h3>
            <p>₹{stats.total_spent}</p>
          </div>

          <div className="card">
            <h3>Budget Used</h3>
            <p>{budgetUsed}%</p>
          </div>

          <div className="card">
            <h3>Savings</h3>
            <p>₹{stats.savings}</p>
          </div>

        </div>

        {/* ================= ACTION BUTTONS ================= */}
        <div className="button-row">

          <button onClick={() => navigate("/upload-statements")}>
            Upload Statements
          </button>

          <button onClick={fetchTransactions}>
            View Categorized Transactions
          </button>

          <button onClick={() => navigate("/visualization")}>
            View Spending Visualization
          </button>

          <button onClick={() => navigate("/budget-planner")}>
            Budget Planner
          </button>

        </div>

        {/* ================= TRANSACTIONS ================= */}
        {showTransactions && (
          <div className="transactions">

            <h3>Categorized Transactions</h3>

            {transactions.length === 0 ? (
              <p>No transactions found.</p>
            ) : (

              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Description</th>
                    <th>Amount</th>
                    <th>Category</th>
                    <th>Source</th>
                  </tr>
                </thead>

                <tbody>
                  {transactions.map((tx) => (
                    <tr key={tx.id}>
                      <td>{tx.date}</td>
                      <td>{tx.description}</td>
                      <td>₹{tx.amount}</td>
                      <td>{tx.category || "Uncategorized"}</td>
                      <td>{tx.source}</td>
                    </tr>
                  ))}
                </tbody>

              </table>
            )}

          </div>
        )}

      </div>

      {/* ================= CHATBOT ================= */}
      <Chatbot />
    </>
  );
}

export default Dashboard;