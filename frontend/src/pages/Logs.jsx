// 📁 src/pages/Logs.jsx
import { useEffect, useState } from "react";
import axios from "axios";
import Papa from "papaparse";

export default function Logs() {
  const [fileList, setFileList] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [csvData, setCsvData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchFileList = async () => {
    try {
      const res = await axios.get("http://localhost:5050/api/logs/list");
      setFileList(res.data);
      if (res.data.length > 0) setSelectedFile(res.data[0].relative_path);
    } catch (err) {
      console.error("❌ 파일 목록 불러오기 실패:", err);
    }
  };

  const fetchFilePreview = async (filePath) => {
    setLoading(true);
    setError(null);
    setCsvData([]);
    try {
      const res = await axios.get("http://localhost:5050/api/logs/file", {
        params: { path: filePath },
      });
      if (filePath.endsWith(".csv")) {
        const parsed = Papa.parse(res.data, { header: true });
        setCsvData(parsed.data);
      }
    } catch (err) {
      console.error("❌ 파일 미리보기 실패:", err);
      setError("파일 미리보기 실패");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFileList();
  }, []);

  useEffect(() => {
    if (selectedFile) fetchFilePreview(selectedFile);
  }, [selectedFile]);

  const downloadLink = selectedFile
    ? `http://localhost:5050/api/logs/download?path=${encodeURIComponent(selectedFile)}`
    : "#";

  return (
    <div style={{ padding: "1rem" }}>
      <h2>Jetson 파일 브라우저</h2>

      <div style={{ marginBottom: "1rem" }}>
        <label>📂 파일 선택: </label>
        <select
          value={selectedFile || ""}
          onChange={(e) => setSelectedFile(e.target.value)}
        >
          {fileList.map((file) => (
            <option key={file.relative_path} value={file.relative_path}>
              {file.name}
            </option>
          ))}
        </select>

        {selectedFile && (
          <a
            href={downloadLink}
            style={{ marginLeft: "1rem" }}
            download
          >
            ⬇️ 다운로드
          </a>
        )}
      </div>

      {loading && <p>⏳ 불러오는 중...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {!loading && !error && selectedFile && selectedFile.endsWith(".csv") && csvData.length > 0 && (
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

      {!loading && !error && selectedFile && !selectedFile.endsWith(".csv") && (
        <p>📁 미리보기 지원되지 않음: {selectedFile.split("/").pop()}</p>
      )}
    </div>
  );
}
