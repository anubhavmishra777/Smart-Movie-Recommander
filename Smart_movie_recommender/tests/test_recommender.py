from base64 import b64decode

from src.recommender import MovieRecommender, get_recommendations


def test_recommender_returns_requested_count():
    recommender = MovieRecommender()
    matched, recommendations = recommender.get_recommendations("Inception", top_n=5)

    assert matched == "Inception"
    assert len(recommendations) == 5
    assert all(movie.title != "Inception" for movie in recommendations)


def test_recommender_handles_close_title_match():
    recommender = MovieRecommender()
    matched, recommendations = recommender.get_recommendations("Interstelar", top_n=3)

    assert matched == "Interstellar"
    assert len(recommendations) == 3


def test_guideline_helper_returns_titles():
    titles = get_recommendations("The Matrix", top_n=4)

    assert len(titles) == 4
    assert all(isinstance(title, str) for title in titles)


def test_unknown_movie_poster_fallback_is_valid_svg_data_url():
    poster_url = MovieRecommender.poster_url("Tenet")
    prefix = "data:image/svg+xml;base64,"

    assert poster_url.startswith(prefix)
    decoded_svg = b64decode(poster_url.removeprefix(prefix)).decode("utf-8")
    assert "<svg" in decoded_svg
    assert "SMART PICK" in decoded_svg
    assert "Tenet" in decoded_svg
