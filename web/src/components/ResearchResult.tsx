import type { ResearchResponse } from "../api/intelligenceApi";
import SignalCard from "./SignalCard";
import SourceList from "./SourceList";

interface Props {
  result: ResearchResponse;
}

function ResearchResult({ result }: Props) {
  return (
    <div className="research-result">
      <div className="executive-summary">
        <h3>Executive Summary</h3>
        <p>{result.executive_summary}</p>
      </div>

      {result.signals.length > 0 && (
        <div className="signals-section">
          <h3 className="section-title">Key Signals</h3>
          <div className="signals-list">
            {result.signals.map((s, i) => (
              <SignalCard key={i} signal={s} />
            ))}
          </div>
        </div>
      )}

      {result.recommendations.length > 0 && (
        <div className="recommendations-section">
          <h3 className="section-title">Recommendations</h3>
          <ul className="recommendations-list">
            {result.recommendations.map((r, i) => (
              <li key={i} className="recommendation-item">
                {r}
              </li>
            ))}
          </ul>
        </div>
      )}

      <SourceList sources={result.sources} />

      <div className="metadata-section">
        <h3 className="section-title">Metadata</h3>
        <table className="metadata-table">
          <tbody>
            <tr>
              <td>Used Bright Data</td>
              <td>{result.metadata.used_brightdata ? "Yes" : "No"}</td>
            </tr>
            <tr>
              <td>Saved to Memory</td>
              <td>{result.metadata.saved_to_memory ? "Yes" : "No"}</td>
            </tr>
            <tr>
              <td>Source Count</td>
              <td>{result.metadata.source_count}</td>
            </tr>
            <tr>
              <td>Track</td>
              <td>{result.metadata.track}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ResearchResult;
