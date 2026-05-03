from __future__ import annotations

from html import escape

import streamlit as st

from src.recommender import MovieRecommender


st.set_page_config(
    page_title="Smart Movie Recommender",
    page_icon="movie",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 15% 10%, rgba(214, 64, 69, 0.20), transparent 28%),
            radial-gradient(circle at 80% 0%, rgba(34, 163, 159, 0.18), transparent 26%),
            linear-gradient(135deg, #101820 0%, #17212b 45%, #211a25 100%);
        color: #f7f4ec;
    }
    [data-testid="stHeader"] {
        background: transparent;
    }
    .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    .hero {
        padding: 2rem 0 1.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.14);
        margin-bottom: 1.25rem;
    }
    .hero h1 {
        font-size: clamp(2.2rem, 5vw, 5.5rem);
        line-height: 0.95;
        margin: 0;
        color: #fff8ec;
        letter-spacing: 0;
    }
    .hero p {
        max-width: 720px;
        color: rgba(255, 248, 236, 0.72);
        font-size: 1.05rem;
        line-height: 1.7;
        margin-top: 1rem;
    }
    .badge {
        display: inline-flex;
        margin-bottom: 1rem;
        padding: 0.5rem 0.7rem;
        border-radius: 999px;
        background: linear-gradient(135deg, #ff4d5a, #f59e0b);
        color: white;
        font-size: 0.78rem;
        font-weight: 900;
    }
    .poster-wall {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.8rem;
        margin-top: 1rem;
    }
    .poster-tile {
        position: relative;
        display: block;
        aspect-ratio: 2 / 3;
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.14);
        box-shadow: 0 18px 38px rgba(0, 0, 0, 0.25);
    }
    .poster-tile img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }
    .poster-tile span {
        position: absolute;
        inset: auto 0 0 0;
        padding: 2.2rem 0.65rem 0.65rem;
        color: white;
        font-weight: 800;
        font-size: 0.84rem;
        background: linear-gradient(to top, rgba(0, 0, 0, 0.82), transparent);
    }
    .result-card {
        display: grid;
        grid-template-columns: 116px 1fr;
        gap: 1rem;
        padding: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.08);
        box-shadow: 0 20px 44px rgba(0, 0, 0, 0.25);
        margin-bottom: 1rem;
    }
    .poster {
        width: 116px;
        aspect-ratio: 2 / 3;
        object-fit: cover;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    .result-card h3 {
        color: #fff8ec;
        margin: 0 0 0.45rem;
        font-size: 1.3rem;
    }
    .result-card p {
        color: rgba(255, 248, 236, 0.70);
        margin: 0.4rem 0 0.7rem;
        line-height: 1.55;
    }
    .chips {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
    }
    .chip {
        padding: 0.32rem 0.55rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.13);
        color: rgba(255, 248, 236, 0.88);
        font-size: 0.86rem;
    }
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 0.65rem;
        border: 1px solid rgba(255, 255, 255, 0.12);
    }
    @media (max-width: 640px) {
        .result-card {
            grid-template-columns: 86px 1fr;
            gap: 0.8rem;
        }
        .poster {
            width: 86px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_recommender() -> MovieRecommender:
    return MovieRecommender()


recommender = load_recommender()
fallback_poster = recommender.poster_url("Smart Movie")


def poster_img(src: str, title: str) -> str:
    safe_title = escape(title)
    return (
        f'<img src="{src}" alt="{safe_title} poster" '
        f'onerror="this.onerror=null;this.src=\'{fallback_poster}\';">'
    )


def poster_tile(title: str) -> str:
    return (
        '<a class="poster-tile">'
        f'{poster_img(recommender.poster_url(title), title)}'
        f"<span>{escape(title)}</span>"
        "</a>"
    )


def result_card(rank: int, movie) -> str:
    return (
        '<article class="result-card">'
        f'{poster_img(movie.poster_url, movie.title).replace("<img ", "<img class=\"poster\" ", 1)}'
        "<div>"
        f'<h3>{rank}. {escape(movie.title)} '
        f'<span style="color: rgba(255,248,236,0.55); font-weight: 400;">'
        f"({movie.release_year})</span></h3>"
        f"<p>{escape(movie.overview)}</p>"
        '<div class="chips">'
        f'<span class="chip">Similarity {movie.similarity_score:.2f}</span>'
        f'<span class="chip">Rating {movie.vote_average:.1f}/10</span>'
        f'<span class="chip">{escape(movie.genres)}</span>'
        "</div>"
        "</div>"
        "</article>"
    )

st.markdown(
    """
    <section class="hero">
        <div class="badge">NEW CINEMA MODE</div>
        <h1>Cinema AI Search</h1>
        <p>Search a movie you already love and get a poster-rich recommendation wall powered by NLP, TF-IDF, and cosine similarity.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1, 2])

with left:
    st.subheader("Search")
    movie_title = st.selectbox(
        "Choose from dataset",
        options=recommender.titles,
        index=0,
        help="Start typing to search the available movie dataset.",
    )

    custom_title = st.text_input(
        "Or enter a movie title",
        placeholder="Example: Interstellar",
    )

    top_n = st.slider("Number of recommendations", min_value=5, max_value=15, value=10)
    run_button = st.button("Recommend Movies", type="primary", use_container_width=True)

    st.divider()
    st.write("Try these")
    suggestion_cols = st.columns(2)
    suggestions = ["Inception", "Interstellar", "Iron Man", "Coco"]
    for index, title in enumerate(suggestions):
        suggestion_cols[index % 2].caption(title)

query = custom_title.strip() or movie_title

with right:
    st.subheader("Movie Matches")

    if run_button:
        matched_title, recommendations = recommender.get_recommendations(query, top_n=top_n)

        if matched_title is None:
            st.error("Movie not found in the dataset. Try another title from the list.")
        else:
            st.success(f"Showing movies similar to: {matched_title}")

            for rank, movie in enumerate(recommendations, start=1):
                st.markdown(result_card(rank, movie), unsafe_allow_html=True)
    else:
        featured_titles = [
            "Inception",
            "Interstellar",
            "The Dark Knight",
            "The Matrix",
            "Iron Man",
            "Coco",
            "Parasite",
            "Whiplash",
        ]
        st.info("Select a movie and click Recommend Movies, or try one of these poster-wall examples.")
        tiles = "".join(poster_tile(title) for title in featured_titles)
        st.markdown(f'<div class="poster-wall">{tiles}</div>', unsafe_allow_html=True)

st.divider()
st.write(
    "This app demonstrates an end-to-end AI/ML workflow: data cleaning, text preprocessing, "
    "TF-IDF feature extraction, cosine similarity, and local web deployment."
)
