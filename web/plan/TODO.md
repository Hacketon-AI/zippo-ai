Tugas anda sebagai senior frontend developer akan mengerjakan webapp dengan tech stack React 18.3.1.silahkan analisa project frontend di dalam folder web,apakah ada salah setup atau sudah minimalize dari segi package ?. b

ketentuan :
Header: ZippoAI Live Intelligence Agent
Tabs: [Chat] [Live Research]
Live Research Form:

- Query / topic textarea
- Track dropdown: GTM, Finance, Security, General
- Company input optional
- Competitors input optional
- Max sources select: 3, 5, 10
- Toggle: Use Bright Data live web
- Button: Run Live Research
  Result:
- Executive Summary
- Key Signals
- Recommendations
- Sources
- Metadata

Loading message :
I’m gathering live data from the web first — give me a moment while I verify the latest information from reliable public sources.

Results display requirements:

1. Executive summary appears in a prominent card.
2. Each signal shows title, category, confidence, description, and source URLs.
3. Recommendations appear as actionable bullets.
4. Sources must be clickable and visible for judges.
5. Metadata must show used_brightdata, saved_to_memory, source_count, and track.
6. Errors must be human-readable, especially missing Bright Data API key and rate limits.

adapun lingkupan tugas anda sebagai berikut :

1. membuat components ResearchPanel.tsx (tujuan: Main Live Research page/tab)
2. membuat components ResearchForm.tsx (tujuan: Input query, track, company, competitors, max sources, use live web)
3. membuat components ResearchResult.tsx (tujuan: Display summary, signals, recommendations, metadata)
4. membuat components SignalCard.tsx (tujuan: One card per intelligence signa)
5. membuat components SourceList.tsx (tujuan: Clickable source links and snippets)
6. membuat components intelligenceApi.ts (tujuan: Client function for POST /api/v1/intelligence/research)
