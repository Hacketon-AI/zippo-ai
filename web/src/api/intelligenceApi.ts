const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export interface ResearchRequest {
  query: string;
  track: "GTM" | "Finance" | "Security" | "General";
  company?: string;
  competitors?: string;
  max_sources: number;
  use_brightdata: boolean;
}

export interface Signal {
  title: string;
  category: string;
  confidence: "high" | "medium" | "low";
  description: string;
  source_urls: string[];
}

export interface Source {
  url: string;
  title: string;
  snippet: string;
}

export interface ResearchMetadata {
  used_brightdata: boolean;
  saved_to_memory: boolean;
  source_count: number;
  track: string;
}

export interface ResearchResponse {
  executive_summary: string;
  signals: Signal[];
  recommendations: string[];
  sources: Source[];
  metadata: ResearchMetadata;
}

export class ResearchError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string
  ) {
    super(message);
    this.name = "ResearchError";
  }
}

export async function runResearch(req: ResearchRequest): Promise<ResearchResponse> {
  const res = await fetch(`${API_BASE}/api/v1/intelligence/research`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: "Unknown error" }));
    const detail = body.detail || `HTTP ${res.status}`;
    throw new ResearchError(detail, res.status, body.code);
  }

  return res.json();
}
