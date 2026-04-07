import { useNavigate } from "react-router-dom";

function Home() {
  const navigate = useNavigate();

  return (
    <div className="page-center">
      <div className="card">
        <h2>Personal Finance Visualizer</h2>
        <p>Track, analyze and improve your financial life.</p>

        <button onClick={() => navigate("/login")}>Login</button>
        <button className="link-btn" onClick={() => navigate("/register")}>
          Register
        </button>
      </div>
    </div>
  );
}

export default Home;
