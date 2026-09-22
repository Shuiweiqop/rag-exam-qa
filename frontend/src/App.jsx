import { useState } from "react";

// 后端地址(你的 FastAPI 跑在 8000 端口)
const API = "http://localhost:8000";

export default function App() {
  // ---- 提问相关的状态 ----
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);   // 存后端返回的答案
  const [loading, setLoading] = useState(false);

  // ---- 上传相关的状态 ----
  const [uploadText, setUploadText] = useState("");
  const [uploadMsg, setUploadMsg] = useState("");

  // ---- 调 /ask 接口 ----
  async function handleAsk() {
    if (!question.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch(`${API}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),   // 把问题发过去
      });
      const data = await res.json();
      setResult(data);                        // 存下返回的答案
    } catch (err) {
      setResult({ answer: "出错了:" + err.message, source: "" });
    }
    setLoading(false);
  }

  // ---- 调 /upload 接口 ----
  async function handleUpload() {
    if (!uploadText.trim()) return;
    setUploadMsg("上传中...");
    try {
      const res = await fetch(`${API}/upload`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: uploadText }),
      });
      const data = await res.json();
      setUploadMsg("已存入:" + data.text.slice(0, 30) + "...");
      setUploadText("");
    } catch (err) {
      setUploadMsg("出错了:" + err.message);
    }
  }

  return (
    <div style={{ maxWidth: 700, margin: "40px auto", fontFamily: "system-ui", padding: 20 }}>
      <h1>RAG Exam Q&A</h1>

      {/* ===== 提问区 ===== */}
      <section style={{ marginBottom: 40 }}>
        <h2>Ask a question</h2>
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. Which layer does CRC operate at?"
          style={{ width: "100%", padding: 10, fontSize: 16, boxSizing: "border-box" }}
          onKeyDown={(e) => e.key === "Enter" && handleAsk()}
        />
        <button onClick={handleAsk} disabled={loading} style={{ marginTop: 10, padding: "10px 20px", fontSize: 16 }}>
          {loading ? "Thinking..." : "Ask"}
        </button>

        {/* 显示答案 */}
        {result && (
          <div style={{ marginTop: 20, padding: 16, background: "#f5f5f5", borderRadius: 8 }}>
            <p style={{ fontSize: 18, fontWeight: "bold" }}>{result.answer}</p>
            {result.source && (
              <details style={{ marginTop: 12 }}>
                <summary style={{ cursor: "pointer", color: "#2E5A88" }}>
                  View source (distance: {result.distance?.toFixed(3)})
                </summary>
                <p style={{ marginTop: 8, color: "#555", fontSize: 14 }}>{result.source}</p>
              </details>
            )}
          </div>
        )}
      </section>

      {/* ===== 上传区 ===== */}
      <section>
        <h2>Add to knowledge base</h2>
        <textarea
          value={uploadText}
          onChange={(e) => setUploadText(e.target.value)}
          placeholder="Paste a piece of text to add..."
          rows={3}
          style={{ width: "100%", padding: 10, fontSize: 14, boxSizing: "border-box" }}
        />
        <button onClick={handleUpload} style={{ marginTop: 10, padding: "10px 20px", fontSize: 16 }}>
          Upload
        </button>
        {uploadMsg && <p style={{ color: "#2E8B57" }}>{uploadMsg}</p>}
      </section>
    </div>
  );
}