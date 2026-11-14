from unittest.mock import mock_open, patch

with patch("builtins.open", mock_open(read_data=b"test-certificate")):
    with patch("grpc.ssl_channel_credentials"), patch("grpc.secure_channel"):
        with patch("recommendations_pb2_grpc.RecommendationsStub"):
            import marketplace

from recommendations_pb2 import (
    BookCategory,
    BookRecommendation,
    RecommendationRequest,
    RecommendationResponse,
)


def render_with_recommendations(monkeypatch, books):
    class FakeClient:
        def Recommend(self, request):
            assert request == RecommendationRequest(
                user_id=1,
                category=BookCategory.MYSTERY,
                max_results=3,
            )
            return RecommendationResponse(recommendations=books)

    monkeypatch.setattr(marketplace, "recommendations_client", FakeClient())
    return marketplace.app.test_client().get("/")


def test_empty_recommendations(monkeypatch):
    response = render_with_recommendations(monkeypatch, [])

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "<title>Online Books For You</title>" in html
    assert "<h1>Mystery books you may like</h1>" in html
    assert "<li>" not in html


def test_three_recommendations(monkeypatch):
    books = [
        BookRecommendation(id=1, title="The Silent Patient"),
        BookRecommendation(id=2, title="Gone Girl"),
        BookRecommendation(id=3, title="The Guest List"),
    ]

    response = render_with_recommendations(monkeypatch, books)
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "<li>The Silent Patient</li>" in html
    assert "<li>Gone Girl</li>" in html
    assert "<li>The Guest List</li>" in html
    assert html.count("<li>") == 3


def test_repeated_titles_are_rendered(monkeypatch):
    books = [
        BookRecommendation(id=1, title="Duplicate"),
        BookRecommendation(id=2, title="Duplicate"),
    ]

    response = render_with_recommendations(monkeypatch, books)
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert html.count("<li>Duplicate</li>") == 2
