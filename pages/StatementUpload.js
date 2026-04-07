import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

function StatementUpload() {
  const [files, setFiles] = useState([]);
  const [password, setPassword] = useState("");
  const [transactions, setTransactions] = useState([]);
  const [batchId, setBatchId] = useState(null);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  // ✅ YOUR ORIGINAL CATEGORY LIST (UNCHANGED)
  const categories = [
    "Uncategorized",
    "Food & Dining",
    "Groceries",
    "Shopping",
    "Clothing",
    "Travel",
    "Fuel",
    "Transportation",
    "Bills & Utilities",
    "Electricity",
    "Water Bill",
    "Internet",
    "Mobile Recharge",
    "Rent",
    "EMI",
    "Insurance",
    "Medical",
    "Pharmacy",
    "Education",
    "Salary",
    "Freelance Income",
    "Investment",
    "Mutual Fund",
    "Stock Market",
    "Entertainment",
    "Subscription",
    "Gym",
    "Gift",
    "Charity",
    "Transfer",
    "ATM Withdrawal"
  ];

  // ================= UPLOAD =================
  const handleUpload = async () => {
    if (files.length === 0) {
      alert("Please select file(s)");
      return;
    }

    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));
    if (password) formData.append("password", password);

    try {
      setLoading(true);

      const response = await fetch(
        "http://localhost:5000/api/upload-statement",
        {
          method: "POST",
          credentials: "include",
          body: formData,
        }
      );

      const data = await response.json();

      if (response.ok) {
        setBatchId(data.batch_id);
        fetchBatchTransactions(data.batch_id);
      } else {
        alert(data.message);
      }
    } catch {
      alert("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  // ================= FETCH =================
  const fetchBatchTransactions = async (batchId) => {
    const response = await fetch(
      `http://localhost:5000/api/transactions/batch/${batchId}`,
      { credentials: "include" }
    );

    const data = await response.json();
    setTransactions(data);
  };

  // ================= ADD MANUAL =================
  const handleManualAdd = () => {
    const today = new Date().toISOString().split("T")[0];

    const newRow = {
      id: "manual-" + Date.now(),
      date: today,
      description: "",
      debit: "",
      credit: "",
      category: "Uncategorized",
      is_locked: false,
      isNew: true,
    };

    setTransactions([...transactions, newRow]);
  };

  // ================= HANDLE CHANGE =================
  const handleChange = (index, field, value) => {
    const updated = [...transactions];
    updated[index][field] = value;
    setTransactions(updated);
  };

  // ================= DELETE =================
  const handleDelete = async (tx) => {
    if (tx.isNew) {
      setTransactions(transactions.filter((t) => t !== tx));
      return;
    }

    await fetch(
      `http://localhost:5000/api/transactions/${tx.id}`,
      {
        method: "DELETE",
        credentials: "include",
      }
    );

    setTransactions(transactions.filter((t) => t.id !== tx.id));
  };

  // ================= SAVE ALL =================
  const handleSaveAll = async () => {
    try {
      setLoading(true);

      for (let tx of transactions) {
        if (tx.isNew) {
          const amount =
            tx.debit && tx.debit > 0
              ? -Math.abs(tx.debit)
              : tx.credit && tx.credit > 0
              ? Math.abs(tx.credit)
              : 0;

          await fetch(
            "http://localhost:5000/api/transactions/manual",
            {
              method: "POST",
              credentials: "include",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                date: tx.date,
                description: tx.description,
                amount: amount,
                batch_id: batchId,
              }),
            }
          );
        } else {
          await fetch(
            `http://localhost:5000/api/transactions/${tx.id}`,
            {
              method: "PUT",
              credentials: "include",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                category: tx.category,
              }),
            }
          );
        }
      }

      alert("Saved successfully!");
      navigate("/dashboard");
    } catch {
      alert("Save failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 40 }}>
      <h2>Upload Bank Statement</h2>

      <input
        type="file"
        multiple
        accept=".pdf,.xlsx,.xls"
        onChange={(e) => setFiles(Array.from(e.target.files))}
      />

      <br /><br />

      <input
        type="password"
        placeholder="PDF Password (if any)"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <br /><br />

      <button onClick={handleUpload}>
        {loading ? "Uploading..." : "Upload"}
      </button>

      {transactions.length > 0 && (
        <>
          <h3 style={{ marginTop: 30 }}>Transactions</h3>

          <button
            onClick={handleManualAdd}
            style={{
              marginBottom: 15,
              backgroundColor: "blue",
              color: "white",
              padding: "6px 12px",
              border: "none",
              cursor: "pointer"
            }}
          >
            ➕ Add Manual Transaction
          </button>

          <table border="1" width="100%" cellPadding="8">
            <thead>
              <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Debit (₹)</th>
                <th>Credit (₹)</th>
                <th>Category</th>
                <th>Delete</th>
              </tr>
            </thead>

            <tbody>
              {transactions.map((tx, index) => (
                <tr key={tx.id}>
                  <td>
                    <input
                      type="date"
                      value={tx.date}
                      disabled={tx.is_locked}
                      onChange={(e) =>
                        handleChange(index, "date", e.target.value)
                      }
                    />
                  </td>

                  <td>
                    <input
                      value={tx.description}
                      disabled={tx.is_locked}
                      onChange={(e) =>
                        handleChange(index, "description", e.target.value)
                      }
                    />
                  </td>

                  <td>
                    <input
                      type="number"
                      value={tx.debit || ""}
                      disabled={tx.is_locked}
                      onChange={(e) =>
                        handleChange(index, "debit", e.target.value)
                      }
                    />
                  </td>

                  <td>
                    <input
                      type="number"
                      value={tx.credit || ""}
                      disabled={tx.is_locked}
                      onChange={(e) =>
                        handleChange(index, "credit", e.target.value)
                      }
                    />
                  </td>

                  <td>
                    <select
                      value={tx.category}
                      onChange={(e) =>
                        handleChange(index, "category", e.target.value)
                      }
                    >
                      {categories.map((cat) => (
                        <option key={cat} value={cat}>
                          {cat}
                        </option>
                      ))}
                    </select>
                  </td>

                  <td>
                    <button
                      onClick={() => handleDelete(tx)}
                      style={{
                        backgroundColor: "red",
                        color: "white",
                        border: "none",
                        padding: "5px 10px",
                        cursor: "pointer"
                      }}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <br />

          <button
            onClick={handleSaveAll}
            style={{
              padding: "10px 20px",
              backgroundColor: "green",
              color: "white",
              fontWeight: "bold",
              border: "none",
              cursor: "pointer"
            }}
          >
            💾 Save All & Continue
          </button>
        </>
      )}
    </div>
  );
}

export default StatementUpload;