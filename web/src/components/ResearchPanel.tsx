import { useState } from "react";
import type { ResearchRequest, ResearchResponse } from "../api/intelligenceApi";
import { runResearch, ResearchError } from "../api/intelligenceApi";
import ResearchForm from "./ResearchForm";
import ResearchResult from "./ResearchResult";

const LOADING_MSG =
  "Sedang mengumpulkan data langsung dari web — tunggu sebentar sementara aku memverifikasi informasi terbaru dari sumber publik yang terpercaya.";

function ResearchPanel() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ResearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRun = async (req: ResearchRequest) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await runResearch(req);
      setResult(data);
    } catch (err) {
      if (err instanceof ResearchError) {
        if (err.status === 401 || err.status === 403) {
          setError(
            "Bright Data API key tidak valid atau belum dikonfigurasi. Silakan periksa pengaturan server."
          );
        } else if (err.status === 429) {
          setError(
            "Rate limit tercapai. Tunggu sebentar sebelum mengirim permintaan berikutnya."
          );
        } else {
          setError(err.message);
        }
      } else {
        setError(err instanceof Error ? err.message : "Terjadi kesalahan tak terduga");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <ResearchForm onRun={handleRun} loading={loading} />

      {loading && (
        <div className="research-loading">
          <div className="loading-spinner" />
          <p>{LOADING_MSG}</p>
        </div>
      )}

      {error && (
        <div className="research-error">
          <p>{error}</p>
        </div>
      )}

      {result && !loading && <ResearchResult result={result} />}
    </>
  );
}

export default ResearchPanel;
