import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import App from "./App";
import Dashboard from "./pages/Dashboard";
import GroupControl from "./pages/GroupControl";
import "./index.css";
import AutoControl from "./pages/AutoControl";
import SingleControl from "./pages/SingleControl";
import Camera from "./pages/Camera";
import Logs from "./pages/Logs";

ReactDOM.createRoot(document.getElementById("root")).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<App />}>
        <Route index element={<Dashboard />} />
        <Route path="group-control" element={<GroupControl />} />
        <Route path="auto-control" element={<AutoControl />} />
        <Route path="single-control" element={<SingleControl />} />
        #<Route path="camera" element={<Camera />} />
        <Route path="logs" element={<Logs />} />
      </Route>
    </Routes>
  </BrowserRouter>
);
