import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";

function SavingsSuggestions() {

  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);

  const navigate = useNavigate();
  const location = useLocation();

  // Get month from URL query parameter
  const params = new URLSearchParams(location.search);
  const month = params.get("month");

  useEffect(() => {

    if (!month) {
      alert("Month not selected");
      setLoading(false);
      return;
    }

    console.log("Selected month:", month);

    fetch(`http://localhost:5000/api/savings-suggestions?month=${month}`, {
      credentials: "include"
    })
      .then(res => res.json())
      .then(data => {

        console.log("API Response:", data);

        if (Array.isArray(data)) {
          setSuggestions(data);
        } else {
          setSuggestions([]);
        }

        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching suggestions:", err);
        setSuggestions([]);
        setLoading(false);
      });

  }, [month]);

  return (

    <div style={{ padding: "30px" }}>

      <h2>AI Savings Suggestions</h2>

      {loading ? (

        <p>Loading suggestions...</p>

      ) : (

        <table border="1" cellPadding="10" style={{ width: "80%", marginTop: "20px" }}>

          <thead>
            <tr>
              <th>Category</th>
              <th>Spent</th>
              <th>Suggestion</th>
            </tr>
          </thead>

          <tbody>

            {suggestions.length > 0 ? (

              suggestions.map((s, index) => (
                <tr key={index}>
                  <td>{s.category}</td>
                  <td>₹{s.spent}</td>
                  <td>{s.suggestion}</td>
                </tr>
              ))

            ) : (

              <tr>
                <td colSpan="3" style={{ textAlign: "center" }}>
                  No suggestions available for this month
                </td>
              </tr>

            )}

          </tbody>

        </table>

      )}

      <br />

      <button
        onClick={() => navigate("/dashboard")}
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

export default SavingsSuggestions;