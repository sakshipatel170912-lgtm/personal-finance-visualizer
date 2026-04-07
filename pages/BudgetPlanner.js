import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

function BudgetPlanner() {

  const navigate = useNavigate();

  const [budgets, setBudgets] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [suggestions, setSuggestions] = useState([]);

  const [categories, setCategories] = useState([]);

  const [category, setCategory] = useState("");
  const [amount, setAmount] = useState("");
  const [month, setMonth] = useState("");



  // ================= LOAD CATEGORIES =================
  useEffect(() => {
    fetchCategories();
  }, []);


  const fetchCategories = async () => {

    try {

      const res = await fetch(
        "http://localhost:5000/api/categories",
        { credentials: "include" }
      );

      const data = await res.json();

      if (Array.isArray(data)) {
        setCategories(data);
      }

    } catch (error) {
      console.error("Error loading categories:", error);
    }

  };



  // ================= FETCH BUDGET =================
  const fetchBudget = async () => {

    if (!month) {
      alert("Please select month first");
      return;
    }

    const monthNumber = month.split("-")[1];
    const yearNumber = month.split("-")[0];

    try {

      const res = await fetch(
        `http://localhost:5000/api/budget-analysis?month=${monthNumber}&year=${yearNumber}`,
        {
          method: "GET",
          credentials: "include"
        }
      );

      const data = await res.json();

      if (res.ok) {

        const filteredBudgets = (data.budget_data || []).filter(
          (b) => b.budget > 0
        );

        setBudgets(filteredBudgets);
        setAlerts(data.alerts || []);

      } else {

        setBudgets([]);
        setAlerts([]);

      }

    } catch (error) {

      console.error("Error fetching budget:", error);
      alert("Server error");

    }

  };



  // ================= SAVE BUDGET =================
  const saveBudget = async () => {

    if (!category || !amount || !month) {
      alert("Please fill all fields");
      return;
    }

    const monthNumber = month.split("-")[1];
    const yearNumber = month.split("-")[0];

    try {

      const res = await fetch("http://localhost:5000/api/set-budget", {

        method: "POST",

        headers: {
          "Content-Type": "application/json"
        },

        credentials: "include",

        body: JSON.stringify({
          category: category,
          amount: Number(amount),
          month: Number(monthNumber),
          year: Number(yearNumber)
        })

      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "Failed to save budget");
      }

      alert("Budget saved successfully");

      fetchBudget();

      setCategory("");
      setAmount("");

    } catch (error) {

      console.error("Error saving budget:", error);
      alert(error.message);

    }

  };



  // ================= SAVING SUGGESTIONS =================
  const getSavingsSuggestions = async () => {

    if (!month) {
      alert("Please select month first");
      return;
    }

    try {

      const res = await fetch(
        `http://localhost:5000/api/savings-suggestions?month=${month}`,
        {
          method: "GET",
          credentials: "include"
        }
      );

      const data = await res.json();

      if (Array.isArray(data)) {
        setSuggestions(data);
      } else {
        setSuggestions([]);
      }

    } catch (error) {

      console.error("Error fetching suggestions:", error);
      alert("Failed to load saving suggestions");

    }

  };



  // ================= DASHBOARD =================
  const goToDashboard = () => {
    navigate("/dashboard");
  };



  return (

    <div style={{ padding: "30px" }}>

      <h2>Budget Planner</h2>


      {/* ALERTS */}
      {alerts.length > 0 && (

        <div style={{ marginBottom: "20px" }}>

          {alerts.map((a, i) => (
            <div
              key={i}
              style={{
                backgroundColor: "#ffe6e6",
                color: "red",
                padding: "8px",
                marginBottom: "5px"
              }}
            >
              ⚠ {a}
            </div>
          ))}

        </div>

      )}



      {/* INPUTS */}

      <div style={{ marginBottom: "15px" }}>


        {/* CATEGORY DROPDOWN */}

        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          style={{ marginRight: "10px", padding: "6px" }}
        >

          <option value="">Select Category</option>

          {categories.map((c, index) => (
            <option key={index} value={c}>
              {c}
            </option>
          ))}

        </select>



        <input
          type="number"
          placeholder="Budget Amount"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          style={{ marginRight: "10px", padding: "5px" }}
        />


        <input
          type="month"
          value={month}
          onChange={(e) => setMonth(e.target.value)}
          style={{ marginRight: "10px", padding: "5px" }}
        />

      </div>



      <button onClick={saveBudget}>
        Save Budget
      </button>

      <button onClick={fetchBudget} style={{ marginLeft: "10px" }}>
        View Budget
      </button>

      <button onClick={getSavingsSuggestions} style={{ marginLeft: "10px" }}>
        Show Saving Suggestions
      </button>



      <br /><br />


      {/* BUDGET TABLE */}

      <table border="1" cellPadding="10">

        <thead>
          <tr>
            <th>Category</th>
            <th>Budget</th>
            <th>Spent</th>
            <th>Remaining</th>
          </tr>
        </thead>

        <tbody>

          {budgets.length > 0 ? (

            budgets.map((b, i) => (

              <tr key={i}>

                <td>{b.category}</td>

                <td>₹{b.budget}</td>

                <td>₹{b.spent}</td>

                <td
                  style={{
                    color: b.remaining < 0 ? "red" : "green",
                    fontWeight: "bold"
                  }}
                >
                  ₹{b.remaining}
                </td>

              </tr>

            ))

          ) : (

            <tr>
              <td colSpan="4">No budget data found</td>
            </tr>

          )}

        </tbody>

      </table>



      {/* SAVING SUGGESTIONS */}

      {suggestions.length > 0 && (

        <div>

          <h3>Saving Suggestions</h3>

          <table border="1" cellPadding="10">

            <thead>
              <tr>
                <th>Category</th>
                <th>Spent</th>
                <th>Suggestion</th>
              </tr>
            </thead>

            <tbody>

              {suggestions.map((s, i) => (

                <tr key={i}>

                  <td>{s.category}</td>
                  <td>₹{s.spent}</td>
                  <td>{s.suggestion}</td>

                </tr>

              ))}

            </tbody>

          </table>

        </div>

      )}



      <br />

      <button
        onClick={goToDashboard}
        style={{
          padding: "10px 20px",
          backgroundColor: "#28a745",
          color: "white",
          border: "none",
          borderRadius: "5px",
          cursor: "pointer"
        }}
      >
        Continue to Dashboard
      </button>

    </div>

  );

}

export default BudgetPlanner;