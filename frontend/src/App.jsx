// 📁 App.jsx
import { Outlet, Link, useLocation } from "react-router-dom";
import { LampProvider } from "./context/LampContext.jsx";
import { LampSettingsProvider } from "./context/LampSettingsContext.jsx";

export default function App() {
  const location = useLocation();

  const navStyle = {
    background: "#333",
    padding: "1rem",
    color: "white",
    display: "flex",
    gap: "1rem",
  };

  const linkStyle = (path) => ({
    color: location.pathname === path ? "#FFD700" : "white",
    textDecoration: "none",
    fontWeight: "bold",
  });

  return (
    <LampProvider>
      <LampSettingsProvider>
        <div>
          <header style={{ background: "#222", color: "white", padding: "1rem" }}>
            <h1>ESLS Dashboard</h1>
            <nav style={navStyle}>
              <Link to="/" style={linkStyle("/")}>대시보드</Link>
              <Link to="/group-control" style={linkStyle("/group-control")}>일괄제어</Link>
              <Link to="/auto-control" style={linkStyle("/auto-control")}>자동제어</Link>
              <Link to="/single-control" style={linkStyle("/single-control")}>개별제어</Link>
              <Link to="/camera" style={linkStyle("/camera")}>카메라 제어</Link>
              <Link to="/logs" style={linkStyle("/logs")}>로그 데이터</Link>
            </nav>
          </header>
          <main style={{ padding: "1rem" }}>
            <Outlet />
          </main>
        </div>
      </LampSettingsProvider>
    </LampProvider>
  );
}
