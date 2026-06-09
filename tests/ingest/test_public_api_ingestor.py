from unittest.mock import MagicMock, patch

import pytest
import requests

from semantica.ingest import (
    APIData,
    PublicAPIDetection,
    PublicAPIExamples,
    PublicAPIIngestor,
    ingest,
    ingest_public_api,
    list_available_methods,
)
from semantica.utils.exceptions import ValidationError


def _mock_response(
    status_code=200,
    json_payload=None,
    text="",
    headers=None,
):
    response = MagicMock()
    response.status_code = status_code
    response.headers = headers or {}
    response.text = text
    if json_payload is not None:
        response.json.return_value = json_payload
    else:
        response.json.side_effect = ValueError("not json")

    if status_code >= 400:
        response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            f"{status_code} error"
        )
    else:
        response.raise_for_status.return_value = None
    return response


def test_public_api_examples_catalog_lists_endpoints_and_samples() -> None:
    names = PublicAPIExamples.names()
    endpoints = PublicAPIExamples.endpoints()
    testing_examples = PublicAPIExamples.list_examples(tag="testing")
    sample = PublicAPIExamples.sample_response("jsonplaceholder_posts")

    assert "jsonplaceholder_posts" in names
    assert endpoints["jsonplaceholder_posts"].startswith("https://")
    assert {example.name for example in testing_examples} >= {
        "jsonplaceholder_posts",
        "jsonplaceholder_users",
        "jsonplaceholder_todos",
    }
    assert sample[0]["title"] == "sample post"


def test_public_api_ingestor_ingests_json_records() -> None:
    payload = [{"id": 1, "title": "hello"}]

    with patch("requests.Session") as mock_session_class:
        mock_session = mock_session_class.return_value
        mock_session.headers = {}
        mock_session.request.return_value = _mock_response(
            json_payload=payload,
            text='[{"id": 1, "title": "hello"}]',
            headers={"Content-Type": "application/json"},
        )

        result = PublicAPIIngestor(rate_limit_delay=0).ingest_public_api(
            "https://jsonplaceholder.typicode.com/posts"
        )

    assert isinstance(result, APIData)
    assert result.data == payload
    assert result.metadata["public_api"] is True
    assert result.metadata["authentication"] == "none"
    assert result.metadata["response_format"] == "json"
    assert result.metadata["record_count"] == 1


def test_public_api_ingestor_extracts_nested_record_path() -> None:
    payload = {
        "success": True,
        "result": {
            "count": 1,
            "results": [{"id": "dataset-1", "title": "Dataset"}],
        },
    }

    with patch("requests.Session") as mock_session_class:
        mock_session = mock_session_class.return_value
        mock_session.headers = {}
        mock_session.request.return_value = _mock_response(
            json_payload=payload,
            text='{"success": true}',
            headers={"Content-Type": "application/json"},
        )

        result = PublicAPIIngestor(rate_limit_delay=0).ingest_public_api(
            "https://catalog.data.gov/api/3/action/package_search",
            record_path="result.results",
        )

    assert result.data == [{"id": "dataset-1", "title": "Dataset"}]
    assert result.metadata["record_path"] == "result.results"


def test_public_api_ingestor_parses_csv_records() -> None:
    csv_text = "id,name\n1,Ada\n2,Grace\n"

    with patch("requests.Session") as mock_session_class:
        mock_session = mock_session_class.return_value
        mock_session.headers = {}
        mock_session.request.return_value = _mock_response(
            text=csv_text,
            headers={"Content-Type": "text/csv"},
        )

        result = PublicAPIIngestor(rate_limit_delay=0).ingest_public_api(
            "https://example.com/data.csv"
        )

    assert result.data == [{"id": "1", "name": "Ada"}, {"id": "2", "name": "Grace"}]
    assert result.metadata["response_format"] == "csv"


def test_public_api_ingestor_parses_xml_records_with_record_path() -> None:
    xml_text = "<items><item id='1'>Ada</item><item id='2'>Grace</item></items>"

    with patch("requests.Session") as mock_session_class:
        mock_session = mock_session_class.return_value
        mock_session.headers = {}
        mock_session.request.return_value = _mock_response(
            text=xml_text,
            headers={"Content-Type": "application/xml"},
        )

        result = PublicAPIIngestor(rate_limit_delay=0).ingest_public_api(
            "https://example.com/data.xml",
            record_path="children",
        )

    assert result.metadata["response_format"] == "xml"
    assert result.data[0]["tag"] == "item"
    assert result.data[0]["attributes"] == {"id": "1"}
    assert result.data[0]["text"] == "Ada"


def test_public_api_detection_reports_public_endpoint() -> None:
    with patch("requests.Session") as mock_session_class:
        mock_session = mock_session_class.return_value
        mock_session.headers = {}
        mock_session.request.return_value = _mock_response(
            headers={"Content-Type": "application/json"}
        )

        detection = PublicAPIIngestor(rate_limit_delay=0).detect_public_api(
            "https://jsonplaceholder.typicode.com/posts"
        )

    assert isinstance(detection, PublicAPIDetection)
    assert detection.is_public is True
    assert detection.requires_auth is False
    assert detection.response_status == 200


def test_public_api_detection_reports_auth_required() -> None:
    with patch("requests.Session") as mock_session_class:
        mock_session = mock_session_class.return_value
        mock_session.headers = {}
        mock_session.request.return_value = _mock_response(
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"},
        )

        detection = PublicAPIIngestor(rate_limit_delay=0).detect_public_api(
            "https://api.example.com/private"
        )

    assert detection.is_public is False
    assert detection.requires_auth is True
    assert detection.response_status == 401


def test_public_api_ingestor_rejects_authentication_inputs() -> None:
    with patch("requests.Session") as mock_session_class:
        mock_session = mock_session_class.return_value
        mock_session.headers = {}
        ingestor = PublicAPIIngestor(rate_limit_delay=0)

        with pytest.raises(ValidationError, match="no-auth endpoints"):
            ingestor.ingest_public_api(
                "https://api.example.com/data",
                headers={"Authorization": "Bearer token"},
            )

        mock_session.request.assert_not_called()


def test_public_api_convenience_methods_and_registry_dispatch() -> None:
    payload = [{"id": 1}]

    with patch("requests.Session") as mock_session_class:
        mock_session = mock_session_class.return_value
        mock_session.headers = {}
        mock_session.request.return_value = _mock_response(
            json_payload=payload,
            text='[{"id": 1}]',
            headers={"Content-Type": "application/json"},
        )

        direct = ingest_public_api(
            "https://jsonplaceholder.typicode.com/posts",
            rate_limit_delay=0,
        )
        unified = ingest(
            "https://jsonplaceholder.typicode.com/posts",
            source_type="public_api",
            rate_limit_delay=0,
        )
        methods = list_available_methods("public_api")

    assert isinstance(direct, APIData)
    assert direct.data == payload
    assert unified["data"].data == payload
    assert "endpoint" in methods["public_api"]
    assert "detect" in methods["public_api"]
