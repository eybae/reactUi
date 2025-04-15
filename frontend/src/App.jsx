// src/App.jsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Sidebar from './components/Sidebar';
import WebSocketProvider from './contexts/WebSocketContext';
import ModeSelector from "./components/ModeSelector";

export default function App() {
  return (
    <div className="p-4">
      <ModeSelector />
        <WebSocketProvider>
          <Router>
            <div className="flex h-screen">
              <Sidebar />
              <div className="flex-1 overflow-auto p-4">
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                </Routes>
              </div>
            </div>
          </Router>
        </WebSocketProvider>
      </div>
  );
}