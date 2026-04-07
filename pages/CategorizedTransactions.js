import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/dashboard.css";

function CategorizedTransactions() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const fetchTransactions = async () => {
    try {
      const res = await fetch("http://localhost:5000/api/transactions/all", {
        method: "GET",
        credentials: "include",
      });

      if (!res.ok) {
        throw new Error("Failed to fetch transactions");
      }

      const data = await res.json();
      setTransactions(data || []);
    } catch (err) {
      console.error(err);
      setError("Error loading transactions");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, []);

  return (
    <div className="dashboard-container">

      <div className="top-bar">
        <h2>Categorized Transactions</h2>
        <button className="logout-btn" onClick={() => navigate("/dashboard")}>
          Back to Dashboard
        </button>
      </div>

      {loading && <h3 className="center">Loading...</h3>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {!loading && transactions.length === 0 && (
        <p>No transactions found.</p>
      )}

      {!loading && transactions.length > 0 && (
        <div className="transactions">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Debit (₹)</th>
                <th>Credit (₹)</th>
                <th>Final Category</th>
              </tr>
            </thead>

            <tbody>
              {transactions.map((t) => (
                <tr key={t.id}>
                  <td>{t.date}</td>
                  <td>{t.description}</td>

                  {/* ✅ FIXED: Use debit/credit from backend */}
                  <td>{t.debit > 0 ? `₹${t.debit}` : "-"}</td>
                  <td>{t.credit > 0 ? `₹${t.credit}` : "-"}</td>

                  <td>{t.category || "Uncategorized"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default CategorizedTransactions;