// 📁 src/pages/Logs.jsx
import { useEffect, useState } from "react";
import axios from "axios";
import Papa from "papaparse";

export default function Logs() {
  const [csvData, setCsvData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get("http://localhost:5050/logs");
      const text = res.data;
      const parsed = Papa.parse(text, { header: true });
      setCsvData(parsed.data);
    } catch (err) {
      console.error("❌ 로그 불러오기 실패:", err);
      setError("로그 불러오기 실패");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  return (
    <div style={{ padding: "1rem" }}>
      <h2>Jetson 로그 미리보기</h2>
      <button
        onClick={fetchLogs}
        style={{ marginBottom: "1rem", padding: "0.5rem 1rem" }}
      >
        🔄 새로고침
      </button>

      {loading && <p>⏳ 불러오는 중...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {!loading && !error && csvData.length > 0 && (
        <table style={{ borderCollapse: "collapse", width: "100%" }}>
          <thead>
            <tr>
              {Object.keys(csvData[0]).map((header) => (
                <th
                  key={header}
                  style={{ border: "1px solid #ccc", padding: "8px", background: "#f9f9f9" }}
                >
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {csvData.map((row, i) => (
              <tr key={i}>
                {Object.values(row).map((cell, j) => (
                  <td key={j} style={{ border: "1px solid #ccc", padding: "8px" }}>{cell}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {!loading && !error && csvData.length === 0 && (
        <p>데이터 없음</p>
      )}
    </div>
  );
}
