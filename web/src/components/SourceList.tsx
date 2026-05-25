import type { Source } from "../api/intelligenceApi";

interface Props {
  sources: Source[];
}

function SourceList({ sources }: Props) {
  if (!sources.length) return null;

  return (
    <div className="source-list">
      <h3 className="section-title">Sources</h3>
      <div className="source-items">
        {sources.map((s, i) => (
          <div key={i} className="source-item">
            <a
              href={s.url}
              target="_blank"
              rel="noopener noreferrer"
              className="source-link"
            >
              {s.title || s.url}
            </a>
            {s.snippet && <p className="source-snippet">{s.snippet}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}

export default SourceList;
