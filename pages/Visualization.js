import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  BarChart,
  Bar
} from "recharts";

function Visualization() {

  const navigate = useNavigate();

  const [data, setData] = useState({
    category_data: [],
    daily_data: [],
    monthly_data: []
  });

  const [filteredCategory, setFilteredCategory] = useState("All");

  // 🎨 Generate colors
  const generateColors = (data) => {
    const colors = {};
    const total = data.length;

    data.forEach((item, index) => {
      const hue = Math.floor((360 / total) * index);
      colors[item.category] = `hsl(${hue}, 70%, 60%)`;
    });

    colors["Others"] = "#999"; // color for grouped
    return colors;
  };

  // 📅 Format date
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short"
    });
  };

  useEffect(() => {
    fetch("http://localhost:5000/api/visualization-data", {
      credentials: "include"
    })
      .then(res => res.json())
      .then(data => setData(data));
  }, []);

  const totalSpending = data.category_data.reduce(
    (sum, item) => sum + item.amount,
    0
  );

  const filteredPieData =
    filteredCategory === "All"
      ? data.category_data
      : data.category_data.filter(
          item => item.category === filteredCategory
        );

  const categories = [
    "All",
    ...new Set(data.category_data.map(item => item.category))
  ];

  const dynamicColors = generateColors(data.category_data);

  // ✅ CLEAN PIE DATA (GROUP SMALL VALUES)
  const getCleanPieData = () => {
    const threshold = 2000;

    let major = [];
    let others = 0;

    filteredPieData.forEach(item => {
      if (item.amount < threshold) {
        others += item.amount;
      } else {
        major.push(item);
      }
    });

    if (others > 0) {
      major.push({ category: "Others", amount: others });
    }

    return major;
  };

  return (

    <div style={{ padding: 40 }}>

      <h2>Spending Visualization Dashboard</h2>

      {/* TOTAL */}
      <div
        style={{
          background: "#f4f6f9",
          padding: "20px",
          width: "250px",
          borderRadius: "10px",
          marginBottom: "30px",
          boxShadow: "0 2px 5px rgba(0,0,0,0.1)"
        }}
      >
        <h3>Total Spending</h3>
        <h2>₹{totalSpending.toFixed(2)}</h2>
      </div>

      {/* FILTER */}
      <div style={{ marginBottom: 30 }}>
        <label><b>Filter by Category:</b> </label>

        <select
          value={filteredCategory}
          onChange={(e) => setFilteredCategory(e.target.value)}
          style={{ padding: 5, marginLeft: 10 }}
        >
          {categories.map((cat, index) => (
            <option key={index}>{cat}</option>
          ))}
        </select>
      </div>

      {/* PIE CHART */}
      <h3>Spending by Category</h3>

      <PieChart width={400} height={300}>
        <Pie
          data={getCleanPieData()}
          dataKey="amount"
          nameKey="category"
          cx="50%"
          cy="50%"
          outerRadius={100}
          label={false} // ❌ REMOVE LABELS
        >
          {getCleanPieData().map((entry, index) => (
            <Cell
              key={index}
              fill={dynamicColors[entry.category]}
            />
          ))}
        </Pie>

        {/* ✅ CLEAN TOOLTIP */}
        <Tooltip
          formatter={(value, name) => [`₹${value}`, name]}
        />

        {/* ✅ CLEAN LEGEND */}
        <Legend
          layout="horizontal"
          verticalAlign="bottom"
          align="center"
          wrapperStyle={{ fontSize: "12px" }}
        />
      </PieChart>

      {/* LINE CHART */}
      <h3>Spending Over Time</h3>

      <LineChart width={650} height={300} data={data.daily_data}>
        <CartesianGrid strokeDasharray="3 3" />

        <XAxis dataKey="date" tickFormatter={formatDate} />

        <YAxis />

        <Tooltip />

        <Line
          type="monotone"
          dataKey="amount"
          stroke="#4D96FF"
          strokeWidth={3}
          dot={{ r: 4 }}
        />
      </LineChart>

      {/* BAR CHART */}
      <h3>Monthly Spending Comparison</h3>

      <BarChart width={650} height={300} data={data.monthly_data}>
        <CartesianGrid strokeDasharray="3 3" />

        <XAxis dataKey="month" />
        <YAxis />

        <Tooltip />
        <Legend />

        <Bar dataKey="amount" fill="#6BCB77" />
      </BarChart>

      {/* BUTTON */}
      <div style={{ marginTop: 40, textAlign: "center" }}>
        <button
          onClick={() => navigate("/dashboard")}
          style={{
            padding: "12px 30px",
            fontSize: "16px",
            backgroundColor: "#4CAF50",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer"
          }}
        >
          Continue
        </button>
      </div>

    </div>
  );
}

export default Visualization;