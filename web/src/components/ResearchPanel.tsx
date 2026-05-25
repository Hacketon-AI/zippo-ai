import { useState } from "react";
import type { ResearchRequest, ResearchResponse } from "../api/intelligenceApi";
import { runResearch, ResearchError } from "../api/intelligenceApi";
import ResearchForm from "./ResearchForm";
import ResearchResult from "./ResearchResult";

const LOADING_MSG =
  "I'm gathering live data from the web first — give me a moment while I verify the latest information from reliable public sources.";

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
            "Bright Data API key is missing or invalid. Please configure it in the server settings."
          );
        } else if (err.status === 429) {
          setError(
            "Rate limit reached. Please wait a moment before submitting another request."
          );
        } else {
          setError(err.message);
        }
      } else {
        setError(err instanceof Error ? err.message : "An unexpected error occurred");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="research-panel">
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
    </div>
  );
}

export default ResearchPanel;
