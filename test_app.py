from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def _mock_github(status_code, body=None):
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.is_error = status_code >= 400
    mock_response.json.return_value = body or []

    mock_async_client = AsyncMock()
    mock_async_client.get.return_value = mock_response

    mock_ctx = MagicMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_async_client)
    mock_ctx.__aexit__ = AsyncMock(return_value=False)
    return mock_ctx, mock_async_client


def test_returns_gists_for_valid_user():
    mock_gists = [
        {"id": "abc123", "description": "Hello World", "public": True},
        {"id": "def456", "description": "Another gist", "public": True},
    ]
    mock_ctx, _ = _mock_github(200, mock_gists)
    with patch("httpx.AsyncClient", return_value=mock_ctx):
        response = client.get("/octocat")

    assert response.status_code == 200
    assert response.json() == mock_gists


def test_returns_empty_list_when_user_has_no_gists():
    mock_ctx, _ = _mock_github(200, [])
    with patch("httpx.AsyncClient", return_value=mock_ctx):
        response = client.get("/octocat")

    assert response.status_code == 200
    assert response.json() == []


def test_returns_404_for_unknown_user():
    mock_ctx, _ = _mock_github(404)
    with patch("httpx.AsyncClient", return_value=mock_ctx):
        response = client.get("/this_user_does_not_exist_xyz")

    assert response.status_code == 404


def test_calls_correct_github_api_url():
    mock_ctx, mock_async_client = _mock_github(200)
    with patch("httpx.AsyncClient", return_value=mock_ctx):
        client.get("/octocat")

    mock_async_client.get.assert_called_once_with(
        "https://api.github.com/users/octocat/gists",
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )


def test_returns_502_on_github_api_error():
    mock_ctx, _ = _mock_github(500)
    with patch("httpx.AsyncClient", return_value=mock_ctx):
        response = client.get("/octocat")

    assert response.status_code == 502
