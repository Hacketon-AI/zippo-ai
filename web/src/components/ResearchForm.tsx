import { useState } from "react";
import type { ResearchRequest } from "../api/intelligenceApi";

interface Props {
  onRun: (req: ResearchRequest) => void;
  loading: boolean;
}

const TRACKS = ["GTM", "Finance", "Security", "General"] as const;
const MAX_SOURCES_OPTIONS = [3, 5, 10];

function ResearchForm({ onRun, loading }: Props) {
  const [query, setQuery] = useState("");
  const [track, setTrack] = useState<ResearchRequest["track"]>("General");
  const [company, setCompany] = useState("");
  const [competitors, setCompetitors] = useState("");
  const [maxSources, setMaxSources] = useState(5);
  const [useBrightdata, setUseBrightdata] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || loading) return;
    onRun({
      query: query.trim(),
      track,
      company: company.trim() || undefined,
      competitors: competitors.trim() || undefined,
      max_sources: maxSources,
      use_brightdata: useBrightdata,
    });
  };

  return (
    <form className="research-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="query">Query / Topic</label>
        <textarea
          id="query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your research query..."
          rows={4}
          disabled={loading}
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="track">Track</label>
          <select
            id="track"
            value={track}
            onChange={(e) => setTrack(e.target.value as ResearchRequest["track"])}
            disabled={loading}
          >
            {TRACKS.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="max-sources">Max Sources</label>
          <select
            id="max-sources"
            value={maxSources}
            onChange={(e) => setMaxSources(Number(e.target.value))}
            disabled={loading}
          >
            {MAX_SOURCES_OPTIONS.map((n) => (
              <option key={n} value={n}>{n}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="company">Company (optional)</label>
          <input
            id="company"
            type="text"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            placeholder="e.g. OpenAI"
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="competitors">Competitors (optional)</label>
          <input
            id="competitors"
            type="text"
            value={competitors}
            onChange={(e) => setCompetitors(e.target.value)}
            placeholder="e.g. Anthropic, Google"
            disabled={loading}
          />
        </div>
      </div>

      <div className="form-group toggle-group">
        <label className="toggle-label">
          <input
            type="checkbox"
            checked={useBrightdata}
            onChange={(e) => setUseBrightdata(e.target.checked)}
            disabled={loading}
          />
          <span>Use Bright Data live web</span>
        </label>
      </div>

      <button type="submit" className="btn-run" disabled={loading || !query.trim()}>
        {loading ? "Researching..." : "Run Live Research"}
      </button>
    </form>
  );
}

export default ResearchForm;
