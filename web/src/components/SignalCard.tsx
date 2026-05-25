import type { Signal } from "../api/intelligenceApi";

interface Props {
  signal: Signal;
}

const CONFIDENCE_COLORS: Record<string, string> = {
  high: "#4caf50",
  medium: "#ff9800",
  low: "#e94560",
};

function SignalCard({ signal }: Props) {
  return (
    <div className="signal-card">
      <div className="signal-header">
        <h4 className="signal-title">{signal.title}</h4>
        <span className="signal-category">{signal.category}</span>
      </div>
      <div className="signal-body">
        <span
          className="signal-confidence"
          style={{ color: CONFIDENCE_COLORS[signal.confidence ?? ""] ?? "#888" }}
        >
          {(signal.confidence ?? "unknown").toUpperCase()}
        </span>
        <p className="signal-description">{signal.description}</p>
      </div>
      {(signal.source_urls ?? []).length > 0 && (
        <div className="signal-sources">
          {signal.source_urls.map((url, i) => (
            <a
              key={i}
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="signal-source-link"
            >
              Source {i + 1}
            </a>
          ))}
        </div>
      )}
    </div>
  );
}

export default SignalCard;
