import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

from app.schemas.intelligence import IntelligenceRequest, IntelligenceResponse, IntelligenceSignal
from app.services.intelligence_service import IntelligenceService
from app.services.brightdata_service import BrightDataService
from app.services.brightdata_mcp_service import BrightDataMCPService
from app.services.ollama_service import OllamaService
from app.services.memory_service import MemoryService


@pytest.fixture
def mock_brightdata():
    mock = MagicMock(spec=BrightDataService)
    mock._enabled = True
    mock.search_web = AsyncMock()
    return mock


@pytest.fixture
def mock_brightdata_mcp():
    mock = MagicMock(spec=BrightDataMCPService)
    mock.search_web = AsyncMock()
    return mock


@pytest.fixture
def mock_ollama():
    mock = MagicMock(spec=OllamaService)
    mock.generate = AsyncMock()
    return mock


@pytest.fixture
def mock_memory():
    mock = MagicMock(spec=MemoryService)
    mock.remember = AsyncMock()
    return mock


@pytest.mark.asyncio
async def test_intelligence_service_synthesis_parsing(
    mock_brightdata, mock_brightdata_mcp, mock_ollama, mock_memory
):
    # Setup mock search result
    from app.schemas.intelligence import BrightDataSearchResponse, BrightDataSearchResult
    
    mock_search_res = BrightDataSearchResponse(
        used_brightdata=True,
        result_count=1,
        results=[
            BrightDataSearchResult(
                title="Google",
                url="https://google.com",
                snippet="Search engine",
                source="brightdata",
            )
        ]
    )
    mock_brightdata.search_web.return_value = mock_search_res

    # Setup mock Ollama response with structured JSON matching the new format
    mock_ollama.generate.return_value = {
        "model": "qwen3:4b",
        "answer": """
        {
            "executive_summary": "This is a great test synthesis.",
            "signals": [
                {
                    "title": "SQL Rise",
                    "category": "GTM",
                    "confidence": "high",
                    "description": "SQL is rising.",
                    "source_urls": ["https://google.com"]
                }
            ],
            "recommendations": ["Learn SQL"]
        }
        """
    }

    # Initialize Service
    service = IntelligenceService(
        brightdata=mock_brightdata,
        brightdata_mcp=mock_brightdata_mcp,
        ollama=mock_ollama,
        memory=mock_memory,
    )
    service._provider = "serp_api"

    # Run research
    response = await service.research(
        query="sql query validation",
        track="GTM",
        company="Zippo",
        competitors="None",
        use_brightdata=True,
    )

    # Assertions
    assert isinstance(response, IntelligenceResponse)
    assert response.executive_summary == "This is a great test synthesis."
    assert response.summary == "This is a great test synthesis."
    assert len(response.signals) == 1
    
    signal = response.signals[0]
    assert isinstance(signal, IntelligenceSignal)
    assert signal.title == "SQL Rise"
    assert signal.category == "GTM"
    assert signal.confidence == "high"
    assert signal.description == "SQL is rising."
    assert signal.source_urls == ["https://google.com"]
    
    assert response.recommendations == ["Learn SQL"]
    assert response.metadata.used_brightdata is True
    assert response.metadata.saved_to_memory is True
    assert response.metadata.source_count == 1
    assert response.metadata.track == "GTM"

    # Verify memory remember was called
    mock_memory.remember.assert_called_once()
    remember_args = mock_memory.remember.call_args[1]
    assert "Research Query: sql query validation" in remember_args["text"]
    assert "SQL Rise: SQL is rising." in remember_args["text"]
    assert remember_args["payload_extra"]["type"] == "research"


@pytest.mark.asyncio
async def test_intelligence_service_robust_parsing_fallback(
    mock_brightdata, mock_brightdata_mcp, mock_ollama, mock_memory
):
    from app.schemas.intelligence import BrightDataSearchResponse, BrightDataSearchResult
    
    mock_brightdata.search_web.return_value = BrightDataSearchResponse(
        used_brightdata=True,
        result_count=1,
        results=[
            BrightDataSearchResult(
                title="Google",
                url="https://google.com",
                snippet="Search engine",
                source="brightdata",
            )
        ]
    )

    # Ollama returns old format (array of strings instead of array of objects)
    mock_ollama.generate.return_value = {
        "model": "qwen3:4b",
        "answer": """
        {
            "summary": "Old summary fallback format.",
            "signals": [
                "This is a string signal instead of an object."
            ],
            "recommendations": ["Learn string formats"]
        }
        """
    }

    # Initialize Service
    service = IntelligenceService(
        brightdata=mock_brightdata,
        brightdata_mcp=mock_brightdata_mcp,
        ollama=mock_ollama,
        memory=mock_memory,
    )
    service._provider = "serp_api"

    # Run research
    response = await service.research(
        query="fallback testing",
        track="Finance",
        use_brightdata=True,
    )

    # Assertions: Should parse "summary" into "executive_summary",
    # and robustly heal/convert string signal to structured IntelligenceSignal!
    assert response.executive_summary == "Old summary fallback format."
    assert len(response.signals) == 1
    
    signal = response.signals[0]
    assert isinstance(signal, IntelligenceSignal)
    assert signal.title == "This is a string signal instead of an object."[:50]
    assert signal.category == "Finance"
    assert signal.confidence == "medium"
    assert signal.description == "This is a string signal instead of an object."
    assert signal.source_urls == []
    
    assert response.recommendations == ["Learn string formats"]
    assert response.metadata.saved_to_memory is True
