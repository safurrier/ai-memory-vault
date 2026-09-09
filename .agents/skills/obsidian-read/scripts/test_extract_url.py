import unittest
from unittest import mock

import extract_url as extractor


class ExtractUrlTests(unittest.TestCase):
    def response_with_body(self, body: bytes):
        response = mock.MagicMock()
        response.__enter__.return_value.read.return_value = body
        return response

    def test_normalize_url_preserves_unverified_redirect_path(self):
        original = "https://open.substack.com/pub/example/p/post?utm_source=share"

        normalized = extractor.normalize_url(original)

        self.assertEqual(normalized, "https://open.substack.com/pub/example/p/post")

    def test_non_json_jina_response_returns_failure(self):
        response = self.response_with_body(b"<html>temporary upstream error</html>")

        with mock.patch.object(extractor.urllib.request, "urlopen", return_value=response):
            result = extractor.extract_jina_reader("https://example.com")

        self.assertFalse(result.success)
        self.assertIn("Invalid JSON from Jina Reader", result.error)

    def test_invalid_jina_data_shape_returns_failure(self):
        response = self.response_with_body(b'{"data": []}')

        with mock.patch.object(extractor.urllib.request, "urlopen", return_value=response):
            result = extractor.extract_jina_reader("https://example.com")

        self.assertFalse(result.success)
        self.assertIn("expected a data object", result.error)

    def test_failed_jina_result_advances_to_wayback(self):
        failed = extractor.ExtractionResult(
            url="https://example.com",
            method="jina_reader",
            error="Invalid JSON from Jina Reader",
        )
        recovered = extractor.ExtractionResult(
            url="https://example.com",
            source_url="https://web.archive.org/example",
            method="wayback",
            content="Recovered content",
        )

        with mock.patch.object(extractor, "extract_jina_reader", return_value=failed), mock.patch.object(
            extractor, "extract_wayback", return_value=recovered
        ):
            result = extractor.extract_with_fallback("https://example.com")

        self.assertIs(result, recovered)


if __name__ == "__main__":
    unittest.main()
