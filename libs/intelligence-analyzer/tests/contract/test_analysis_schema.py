"""
Contract tests for analyzer output schema

Verifies that the analyzer output conforms to the expected schema.
"""

import pytest
from pydantic import ValidationError


class TestAnalyzerOutputSchema:
    """Contract tests for AnalysisResult model output."""

    def test_analyzer_result_model_exists(self):
        """Test that the AnalysisResult model can be imported."""
        try:
            from intelligence_analyzer.models import AnalysisResult
            assert AnalysisResult is not None
        except ImportError:
            pytest.fail("AnalysisResult model should be importable from intelligence_analyzer.models")

    def test_analyzer_output_required_fields(self):
        """Test that AnalysisResult requires all mandatory fields."""
        from intelligence_analyzer.models import AnalysisResult

        valid_result = {
            "summary": "This article discusses NVIDIA's latest GPU architecture.",
            "entities": [
                {"text": "NVIDIA", "type": "company", "mentions": 5},
                {"text": "Jensen Huang", "type": "person", "mentions": 2},
            ],
            "classification": "product_launch",
            "sentimentScore": 8,
        }

        result = AnalysisResult(**valid_result)
        assert result.summary == "This article discusses NVIDIA's latest GPU architecture."
        assert len(result.entities) == 2
        assert result.classification == "product_launch"
        assert result.sentimentScore == 8

    def test_analyzer_output_missing_required_field(self):
        """Test that AnalysisResult raises error when required fields are missing."""
        from intelligence_analyzer.models import AnalysisResult

        # Missing required field 'classification'
        invalid_result = {
            "summary": "This article discusses NVIDIA's latest GPU architecture.",
            "entities": [],
            "sentimentScore": 8,
        }

        with pytest.raises(ValidationError) as exc_info:
            AnalysisResult(**invalid_result)

        assert "classification" in str(exc_info.value).lower()

    def test_analyzer_output_entities_structure(self):
        """Test that entities have the correct structure."""
        from intelligence_analyzer.models import AnalysisResult

        valid_result = {
            "summary": "Test summary",
            "entities": [
                {"text": "NVIDIA", "type": "company", "mentions": 5},
                {"text": "Jensen Huang", "type": "person", "mentions": 2},
                {"text": "H100", "type": "product", "mentions": 3},
            ],
            "classification": "product_launch",
            "sentimentScore": 7,
        }

        result = AnalysisResult(**valid_result)
        assert len(result.entities) == 3

        # Check first entity structure
        first_entity = result.entities[0]
        assert hasattr(first_entity, "text")
        assert hasattr(first_entity, "type")
        assert hasattr(first_entity, "mentions")
        assert first_entity.text == "NVIDIA"
        assert first_entity.type == "company"
        assert first_entity.mentions == 5

    def test_analyzer_output_entity_types_validation(self):
        """Test that entity types are validated."""
        from intelligence_analyzer.models import AnalysisResult

        # Invalid entity type
        invalid_result = {
            "summary": "Test summary",
            "entities": [
                {"text": "NVIDIA", "type": "invalid_type", "mentions": 5},
            ],
            "classification": "product_launch",
            "sentimentScore": 7,
        }

        with pytest.raises(ValidationError) as exc_info:
            AnalysisResult(**invalid_result)

        assert "type" in str(exc_info.value).lower()

    def test_analyzer_output_classification_validation(self):
        """Test that classification field has valid values."""
        from intelligence_analyzer.models import AnalysisResult

        valid_classifications = [
            "competitive_news",
            "personnel_change",
            "product_launch",
            "market_trend",
        ]

        for classification in valid_classifications:
            valid_result = {
                "summary": "Test summary",
                "entities": [],
                "classification": classification,
                "sentimentScore": 5,
            }
            result = AnalysisResult(**valid_result)
            assert result.classification == classification

        # Invalid classification
        invalid_result = {
            "summary": "Test summary",
            "entities": [],
            "classification": "invalid_classification",
            "sentimentScore": 5,
        }

        with pytest.raises(ValidationError) as exc_info:
            AnalysisResult(**invalid_result)

        assert "classification" in str(exc_info.value).lower()

    def test_analyzer_output_sentiment_range_validation(self):
        """Test that sentimentScore is within the valid range (1-10)."""
        from intelligence_analyzer.models import AnalysisResult

        # Valid sentiment scores
        for score in [1, 5, 10]:
            valid_result = {
                "summary": "Test summary",
                "entities": [],
                "classification": "product_launch",
                "sentimentScore": score,
            }
            result = AnalysisResult(**valid_result)
            assert result.sentimentScore == score

        # Invalid sentiment score (too low)
        invalid_result_low = {
            "summary": "Test summary",
            "entities": [],
            "classification": "product_launch",
            "sentimentScore": 0,
        }

        with pytest.raises(ValidationError):
            AnalysisResult(**invalid_result_low)

        # Invalid sentiment score (too high)
        invalid_result_high = {
            "summary": "Test summary",
            "entities": [],
            "classification": "product_launch",
            "sentimentScore": 11,
        }

        with pytest.raises(ValidationError):
            AnalysisResult(**invalid_result_high)

    def test_analyzer_output_entity_mentions_validation(self):
        """Test that entity mentions count is a positive integer."""
        from intelligence_analyzer.models import AnalysisResult

        # Invalid mentions count (zero)
        invalid_result = {
            "summary": "Test summary",
            "entities": [
                {"text": "NVIDIA", "type": "company", "mentions": 0},
            ],
            "classification": "product_launch",
            "sentimentScore": 7,
        }

        with pytest.raises(ValidationError) as exc_info:
            AnalysisResult(**invalid_result)

        assert "mentions" in str(exc_info.value).lower()

    def test_analyzer_output_empty_entities_allowed(self):
        """Test that AnalysisResult allows empty entities list."""
        from intelligence_analyzer.models import AnalysisResult

        valid_result = {
            "summary": "Test summary with no identified entities.",
            "entities": [],
            "classification": "market_trend",
            "sentimentScore": 5,
        }

        result = AnalysisResult(**valid_result)
        assert result.entities == []

    def test_analyzer_output_summary_min_length(self):
        """Test that summary has a minimum length requirement."""
        from intelligence_analyzer.models import AnalysisResult

        # Very short summary
        invalid_result = {
            "summary": "Short",
            "entities": [],
            "classification": "market_trend",
            "sentimentScore": 5,
        }

        with pytest.raises(ValidationError) as exc_info:
            AnalysisResult(**invalid_result)

        assert "summary" in str(exc_info.value).lower()

    def test_analyzer_output_json_serialization(self):
        """Test that AnalysisResult can be serialized to JSON."""
        from intelligence_analyzer.models import AnalysisResult

        valid_result = {
            "summary": "This article discusses NVIDIA's latest GPU architecture and market position.",
            "entities": [
                {"text": "NVIDIA", "type": "company", "mentions": 5},
            ],
            "classification": "product_launch",
            "sentimentScore": 8,
        }

        result = AnalysisResult(**valid_result)
        json_output = result.model_dump_json()

        assert isinstance(json_output, str)
        assert "NVIDIA" in json_output
        assert "product_launch" in json_output

    def test_analyzer_input_model_exists(self):
        """Test that the AnalysisInput model can be imported."""
        try:
            from intelligence_analyzer.models import AnalysisInput
            assert AnalysisInput is not None
        except ImportError:
            pytest.fail("AnalysisInput model should be importable from intelligence_analyzer.models")

    def test_analyzer_input_required_fields(self):
        """Test that AnalysisInput requires all mandatory fields."""
        from intelligence_analyzer.models import AnalysisInput

        valid_input = {
            "url": "https://example.com/article",
            "title": "Test Article",
            "content": "This is the article content for analysis.",
            "publishDate": "2024-01-15T10:00:00Z",
        }

        analysis_input = AnalysisInput(**valid_input)
        assert analysis_input.url == "https://example.com/article"
        assert analysis_input.title == "Test Article"
        assert analysis_input.content == "This is the article content for analysis."
