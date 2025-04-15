// src/components/ModeToggle.jsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function ModeSelector() {
  const [mode, setMode] = useState("auto"); // 초기값: 자동제어
  const navigate = useNavigate();

  const handleModeChange = (newMode) => {
    setMode(newMode);

    if (newMode === "group") {
      navigate("/group-control");
    } else if (newMode === "single") {
      navigate("/individual-control");
    }
  };

  const baseStyle = "px-4 py-2 rounded font-semibold";
  const activeStyle = "bg-blue-600 text-white";
  const inactiveStyle = "bg-gray-200 text-gray-600";

  return (
    <div className="flex gap-3 mb-4">
      <button
        className={`${baseStyle} ${mode === "auto" ? activeStyle : inactiveStyle}`}
        onClick={() => handleModeChange("auto")}
      >
        자동제어
      </button>
      <button
        className={`${baseStyle} ${mode === "group" ? activeStyle : inactiveStyle}`}
        onClick={() => handleModeChange("group")}
      >
        일괄제어
      </button>
      <button
        className={`${baseStyle} ${mode === "single" ? activeStyle : inactiveStyle}`}
        onClick={() => handleModeChange("single")}
      >
        개별제어
      </button>
    </div>
  );
}

