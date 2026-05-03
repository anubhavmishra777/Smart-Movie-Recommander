from __future__ import annotations

from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from src.recommender import MovieRecommender


HOST = "127.0.0.1"
PORT = 8000


class MovieRequestHandler(BaseHTTPRequestHandler):
    recommender = MovieRecommender()

    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)
        params = parse_qs(parsed_url.query)
        query = params.get("movie", [""])[0].strip()
        top_n = int(params.get("top_n", ["10"])[0])

        matched_title = None
        recommendations = []
        if query:
            matched_title, recommendations = self.recommender.get_recommendations(query, top_n=top_n)

        html = self.render_page(query, matched_title, recommendations, top_n)
        encoded = html.encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args) -> None:
        return

    def render_page(self, query, matched_title, recommendations, top_n) -> str:
        options = "\n".join(
            f'<option value="{escape(title)}">' for title in self.recommender.titles
        )

        hero_poster = self.recommender.poster_url(query or "cinema")
        fallback_poster = self.recommender.poster_url("Smart Movie")

        if query and matched_title is None:
            results_html = '<p class="alert">Movie not found. Try a title from the dataset.</p>'
        elif recommendations:
            cards = []
            for rank, movie in enumerate(recommendations, start=1):
                cards.append(
                    f"""
                    <article class="movie-card">
                        <img class="poster" src="{movie.poster_url}" alt="{escape(movie.title)} poster" onerror="this.onerror=null;this.src='{fallback_poster}';">
                        <div>
                            <div class="eyebrow">Match #{rank}</div>
                            <h2>{escape(movie.title)} <span>{movie.release_year}</span></h2>
                            <p>{escape(movie.overview)}</p>
                            <div class="meta">
                                <span>Similarity {movie.similarity_score:.2f}</span>
                                <span>Rating {movie.vote_average:.1f}/10</span>
                                <span>{escape(movie.genres)}</span>
                            </div>
                        </div>
                    </article>
                    """
                )
            results_html = (
                f'<p class="matched">Showing movies similar to <strong>{escape(matched_title)}</strong></p>'
                + "\n".join(cards)
            )
        else:
            results_html = self.render_home_wall(fallback_poster)

        return f"""
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Smart Movie Recommender</title>
            <style>
                :root {{
                    --ink: #fff8ee;
                    --muted: rgba(255, 248, 238, 0.68);
                    --deep: #0f1720;
                    --panel: rgba(255, 255, 255, 0.09);
                    --accent: #ff4d5a;
                    --cyan: #22d3c5;
                    --gold: #f5c451;
                    --line: rgba(255, 255, 255, 0.14);
                }}
                * {{ box-sizing: border-box; }}
                body {{
                    margin: 0;
                    font-family: Arial, Helvetica, sans-serif;
                    color: var(--ink);
                    background:
                        radial-gradient(circle at 12% 8%, rgba(255, 77, 90, 0.34), transparent 25%),
                        radial-gradient(circle at 86% 0%, rgba(34, 211, 197, 0.25), transparent 27%),
                        linear-gradient(135deg, #0f1720 0%, #172331 48%, #241723 100%);
                    min-height: 100vh;
                }}
                body::before {{
                    content: "";
                    position: fixed;
                    inset: 0;
                    pointer-events: none;
                    opacity: 0.12;
                    background-image:
                        linear-gradient(rgba(255,255,255,0.22) 1px, transparent 1px),
                        linear-gradient(90deg, rgba(255,255,255,0.22) 1px, transparent 1px);
                    background-size: 64px 64px;
                    mask-image: linear-gradient(to bottom, black, transparent 78%);
                }}
                main {{
                    width: min(1180px, calc(100% - 32px));
                    margin: 0 auto;
                    padding: 30px 0 48px;
                }}
                header {{
                    display: grid;
                    grid-template-columns: 1.1fr 320px;
                    gap: 28px;
                    align-items: center;
                    min-height: 330px;
                    border-bottom: 1px solid var(--line);
                    padding-bottom: 28px;
                }}
                h1 {{
                    font-size: clamp(2.6rem, 7vw, 6.8rem);
                    line-height: 0.9;
                    margin: 0 0 8px;
                    letter-spacing: 0;
                    max-width: 760px;
                }}
                .badge {{
                    display: inline-flex;
                    align-items: center;
                    margin-bottom: 18px;
                    padding: 9px 12px;
                    border-radius: 999px;
                    background: linear-gradient(135deg, var(--accent), #f59e0b);
                    color: white;
                    font-size: 0.78rem;
                    font-weight: 900;
                    letter-spacing: 0;
                    box-shadow: 0 18px 45px rgba(255, 77, 90, 0.28);
                }}
                .tagline {{
                    color: var(--muted);
                    margin: 0;
                    max-width: 640px;
                    line-height: 1.6;
                    font-size: 1.08rem;
                }}
                .hero-actions {{
                    display: flex;
                    gap: 10px;
                    flex-wrap: wrap;
                    margin-top: 22px;
                }}
                .pill {{
                    border: 1px solid var(--line);
                    border-radius: 999px;
                    padding: 9px 12px;
                    color: var(--ink);
                    background: rgba(255, 255, 255, 0.08);
                    text-decoration: none;
                    font-size: 0.92rem;
                }}
                .spotlight {{
                    position: relative;
                    width: min(100%, 300px);
                    margin-left: auto;
                    aspect-ratio: 2 / 3;
                    border-radius: 18px;
                    overflow: hidden;
                    border: 1px solid rgba(255, 255, 255, 0.22);
                    box-shadow: 0 32px 80px rgba(0, 0, 0, 0.42);
                    transform: rotate(2deg);
                }}
                .spotlight img {{
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    display: block;
                    filter: saturate(1.12) contrast(1.05);
                }}
                .spotlight::after {{
                    content: "AI PICKS";
                    position: absolute;
                    left: 14px;
                    bottom: 14px;
                    font-size: 0.78rem;
                    font-weight: 800;
                    letter-spacing: 0;
                    background: var(--accent);
                    color: white;
                    padding: 8px 10px;
                    border-radius: 999px;
                }}
                .layout {{
                    display: grid;
                    grid-template-columns: 360px 1fr;
                    gap: 24px;
                    margin-top: 28px;
                }}
                form, .movie-card {{
                    background: var(--panel);
                    border: 1px solid var(--line);
                    border-radius: 14px;
                    box-shadow: 0 22px 58px rgba(0, 0, 0, 0.25);
                    backdrop-filter: blur(18px);
                }}
                form {{
                    padding: 22px;
                    position: sticky;
                    top: 20px;
                }}
                form h2 {{
                    margin-top: 0;
                    font-size: 1.4rem;
                }}
                label {{
                    display: block;
                    font-weight: 700;
                    margin-bottom: 8px;
                }}
                input, select, button {{
                    width: 100%;
                    min-height: 48px;
                    border-radius: 10px;
                    border: 1px solid var(--line);
                    padding: 10px 12px;
                    font-size: 1rem;
                    margin-bottom: 16px;
                    color: var(--ink);
                    background: rgba(255, 255, 255, 0.10);
                    outline: none;
                }}
                input::placeholder {{
                    color: rgba(255, 248, 238, 0.42);
                }}
                option {{
                    color: #111827;
                }}
                button {{
                    border: 0;
                    background: linear-gradient(135deg, var(--accent), #f59e0b);
                    color: white;
                    font-weight: 700;
                    cursor: pointer;
                    box-shadow: 0 14px 28px rgba(255, 77, 90, 0.28);
                }}
                button:hover {{
                    transform: translateY(-1px);
                    filter: brightness(1.08);
                }}
                .matched, .empty, .alert {{
                    margin: 0 0 16px;
                    padding: 14px 16px;
                    border-radius: 12px;
                    background: rgba(255, 255, 255, 0.10);
                    border: 1px solid var(--line);
                }}
                .alert {{ color: #ffd6d9; }}
                .movie-card {{
                    display: grid;
                    grid-template-columns: 128px 1fr;
                    gap: 16px;
                    padding: 14px;
                    margin-bottom: 16px;
                    transition: transform 160ms ease, border-color 160ms ease, background 160ms ease;
                }}
                .movie-card:hover {{
                    transform: translateY(-3px);
                    border-color: rgba(255, 255, 255, 0.30);
                    background: rgba(255, 255, 255, 0.12);
                }}
                .poster {{
                    width: 128px;
                    aspect-ratio: 2 / 3;
                    object-fit: cover;
                    border-radius: 10px;
                    border: 1px solid rgba(255, 255, 255, 0.18);
                    box-shadow: 0 18px 35px rgba(0, 0, 0, 0.35);
                }}
                .eyebrow {{
                    display: inline-flex;
                    align-items: center;
                    color: var(--gold);
                    font-size: 0.78rem;
                    font-weight: 800;
                    margin-bottom: 8px;
                }}
                h2 {{
                    margin: 0 0 8px;
                    font-size: 1.35rem;
                }}
                h2 span {{
                    color: var(--muted);
                    font-size: 0.95rem;
                    font-weight: 400;
                }}
                .movie-card p {{
                    color: var(--muted);
                    line-height: 1.55;
                    margin: 0 0 12px;
                }}
                .meta {{
                    display: flex;
                    gap: 12px;
                    flex-wrap: wrap;
                    font-size: 0.92rem;
                }}
                .meta span {{
                    border: 1px solid var(--line);
                    border-radius: 999px;
                    padding: 7px 9px;
                    background: rgba(255, 255, 255, 0.08);
                }}
                .hint {{
                    color: var(--muted);
                    font-size: 0.92rem;
                    line-height: 1.5;
                    margin-top: 2px;
                }}
                .home-panel {{
                    display: grid;
                    gap: 18px;
                }}
                .poster-wall {{
                    display: grid;
                    grid-template-columns: repeat(4, minmax(0, 1fr));
                    gap: 12px;
                    margin-bottom: 18px;
                }}
                .poster-tile {{
                    position: relative;
                    display: block;
                    aspect-ratio: 2 / 3;
                    border-radius: 12px;
                    overflow: hidden;
                    border: 1px solid var(--line);
                    box-shadow: 0 18px 38px rgba(0, 0, 0, 0.26);
                    text-decoration: none;
                    background: rgba(255, 255, 255, 0.08);
                }}
                .poster-tile img {{
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    display: block;
                    transition: transform 180ms ease;
                }}
                .poster-tile:hover img {{
                    transform: scale(1.06);
                }}
                .poster-tile span {{
                    position: absolute;
                    inset: auto 0 0 0;
                    padding: 34px 10px 10px;
                    color: white;
                    font-weight: 800;
                    font-size: 0.88rem;
                    background: linear-gradient(to top, rgba(0, 0, 0, 0.82), transparent);
                }}
                .mood-grid {{
                    display: grid;
                    grid-template-columns: repeat(4, minmax(0, 1fr));
                    gap: 12px;
                }}
                .mood-card {{
                    min-height: 124px;
                    padding: 16px;
                    border-radius: 14px;
                    border: 1px solid var(--line);
                    background:
                        linear-gradient(145deg, rgba(255, 77, 90, 0.20), rgba(34, 211, 197, 0.10)),
                        rgba(255, 255, 255, 0.08);
                    color: var(--ink);
                    text-decoration: none;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                }}
                .mood-card strong {{
                    font-size: 1rem;
                }}
                .mood-card span {{
                    color: var(--muted);
                    line-height: 1.4;
                    font-size: 0.9rem;
                }}
                @media (max-width: 820px) {{
                    header, .layout {{ display: block; }}
                    header {{ min-height: auto; }}
                    .spotlight {{ margin: 26px 0 0; width: 220px; }}
                    form {{ position: static; margin-bottom: 20px; }}
                    .movie-card {{ grid-template-columns: 92px 1fr; }}
                    .poster {{ width: 92px; }}
                    .poster-wall, .mood-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
                }}
            </style>
        </head>
        <body>
            <main>
                <header>
                    <div>
                        <div class="badge">NEW CINEMA MODE</div>
                        <h1>Cinema AI Search</h1>
                        <p class="tagline">Type one movie you love. The app reads genres, keywords, and story text, then builds a poster-rich recommendation wall like a real streaming product.</p>
                        <div class="hero-actions">
                            <a class="pill" href="?movie=Inception&top_n=8">Inception vibe</a>
                            <a class="pill" href="?movie=Interstellar&top_n=8">Space mode</a>
                            <a class="pill" href="?movie=Iron%20Man&top_n=8">Superhero blast</a>
                            <a class="pill" href="?movie=Coco&top_n=8">Family night</a>
                        </div>
                    </div>
                    <div class="spotlight">
                        <img src="{hero_poster}" alt="Cinematic poster preview" onerror="this.onerror=null;this.src='{fallback_poster}';">
                    </div>
                </header>
                <section class="layout">
                    <form method="get">
                        <h2>Find your movie match</h2>
                        <label for="movie">Movie title</label>
                        <input id="movie" name="movie" list="movie-list" value="{escape(query)}" placeholder="Example: Inception">
                        <datalist id="movie-list">{options}</datalist>
                        <label for="top_n">Number of recommendations</label>
                        <select id="top_n" name="top_n">
                            {self.render_top_n_options(top_n)}
                        </select>
                        <button type="submit">Recommend Movies</button>
                        <p class="hint">Type a title from the dataset or use the quick vibe buttons above. Small spelling mistakes are handled automatically.</p>
                    </form>
                    <section>{results_html}</section>
                </section>
            </main>
        </body>
        </html>
        """

    def render_home_wall(self, fallback_poster: str) -> str:
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
        posters = []
        for title in featured_titles:
            url = self.recommender.poster_url(title)
            posters.append(
                f"""
                <a class="poster-tile" href="?movie={escape(title)}&top_n=8">
                    <img src="{url}" alt="{escape(title)} poster" onerror="this.onerror=null;this.src='{fallback_poster}';">
                    <span>{escape(title)}</span>
                </a>
                """
            )

        moods = [
            ("Mind Bending", "Inception", "Dreams, simulations, and twist-heavy stories"),
            ("Space Survival", "Interstellar", "Astronauts, science, planets, and rescue missions"),
            ("Hero Energy", "Iron Man", "Action, technology, superheroes, and big battles"),
            ("Emotional Night", "Coco", "Family, music, memory, and animated warmth"),
        ]
        mood_cards = []
        for mood, title, text in moods:
            mood_cards.append(
                f"""
                <a class="mood-card" href="?movie={escape(title)}&top_n=8">
                    <strong>{escape(mood)}</strong>
                    <span>{escape(text)}</span>
                </a>
                """
            )

        return f"""
        <section class="home-panel">
            <div>
                <p class="matched">Start by searching a movie, or click a poster below.</p>
                <div class="poster-wall">{"".join(posters)}</div>
            </div>
            <div class="mood-grid">{"".join(mood_cards)}</div>
        </section>
        """

    @staticmethod
    def render_top_n_options(selected: int) -> str:
        return "\n".join(
            f'<option value="{value}" {"selected" if value == selected else ""}>{value}</option>'
            for value in range(5, 16)
        )


def run() -> None:
    server = HTTPServer((HOST, PORT), MovieRequestHandler)
    print(f"Smart Movie Recommender running at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop the server.")
    server.serve_forever()


if __name__ == "__main__":
    run()
