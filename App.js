import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useEffect } from "react";

import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import Dashboard from "./pages/Dashboard";
import StatementUpload from "./pages/StatementUpload";
import CategorizedTransactions from "./pages/CategorizedTransactions";
import Visualization from "./pages/Visualization";
import BudgetPlanner from "./pages/BudgetPlanner";
import SavingsSuggestions from "./pages/SavingsSuggestions";
import Profile from "./pages/Profile";
import AdminDashboard from "./pages/AdminDashboard";

function App() {

  useEffect(() => {
    // ✅ 1. Apply theme from localStorage FIRST (fast load)
    const savedTheme = localStorage.getItem("theme") || "light";

    document.body.classList.remove("light", "dark");
    document.body.classList.add(savedTheme);

    // ✅ 2. Sync with backend (optional but recommended)
    fetch("http://localhost:5000/api/profile", {
      credentials: "include"
    })
      .then(res => res.ok ? res.json() : null)
      .then(data => {
        if (data?.theme) {
          document.body.classList.remove("light", "dark");
          document.body.classList.add(data.theme);

          localStorage.setItem("theme", data.theme);
        }
      })
      .catch(() => {
        // silent fail (no crash if backend not available)
      });

  }, []);

  return (
    <BrowserRouter>
      <Routes>

        {/* Public Routes */}
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password/:token" element={<ResetPassword />} />

        {/* Protected Pages */}
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/upload-statements" element={<StatementUpload />} />
        <Route path="/categorized-transactions" element={<CategorizedTransactions />} />
        <Route path="/visualization" element={<Visualization />} />
        <Route path="/budget-planner" element={<BudgetPlanner />} />
        <Route path="/savings-suggestions" element={<SavingsSuggestions />} />

        {/* Profile */}
        <Route path="/profile" element={<Profile />} />
        <Route path="/admin" element={<AdminDashboard/>}/>

      </Routes>
    </BrowserRouter>
  );
}

export default App;