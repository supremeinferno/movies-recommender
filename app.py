import requests
import streamlit as st
from typing import Optional
import inspect

# =============================
# CONFIG
# =============================
API_BASE = "https://movie-rec-466x.onrender.com" or "http://127.0.0.1:8000"
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="CineVerse", page_icon="🎬", layout="wide")

# =============================
# COMPAT: st.image width param
# Streamlit renamed use_column_width -> use_container_width across
# versions. Detect which one this install actually supports so the
# app never breaks (or shows deprecation warnings) on either side.
# =============================
_IMAGE_WIDTH_KW = (
    "use_container_width"
    if "use_container_width" in inspect.signature(st.image).parameters
    else "use_column_width"
)


def show_image(src, **kwargs):
    kwargs[_IMAGE_WIDTH_KW] = True
    st.image(src, **kwargs)


_BUTTON_WIDTH_KW = (
    "use_container_width"
    if "use_container_width" in inspect.signature(st.button).parameters
    else None
)


def full_width_button(label, **kwargs):
    if _BUTTON_WIDTH_KW:
        kwargs[_BUTTON_WIDTH_KW] = True
    return st.button(label, **kwargs)

# =============================
# STYLES — Apple TV+ inspired
# =============================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

:root{
    --bg:#000000;
    --bg-soft:#0a0a0c;
    --card:#141416;
    --card-hover:#1c1c1f;
    --text:#f5f5f7;
    --muted:#86868b;
    --accent:#fa2d48;
    --accent-soft:rgba(250,45,72,.14);
    --border:rgba(255,255,255,.08);
}

html,body,[class*="css"]{
    font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;
}

.stApp{
    background:var(--bg);
    color:var(--text);
}

.block-container{
    max-width:1600px;
    padding-top:1rem;
    padding-bottom:3rem;
}

#MainMenu, footer, header{
    visibility:hidden;
}

::-webkit-scrollbar{ width:8px; }
::-webkit-scrollbar-track{ background:var(--bg); }
::-webkit-scrollbar-thumb{ background:#2c2c2e; border-radius:999px; }
::-webkit-scrollbar-thumb:hover{ background:#3a3a3c; }

section[data-testid="stSidebar"]{
    background:var(--bg-soft);
    border-right:1px solid var(--border);
}

section[data-testid="stSidebar"] *{
    color:var(--text);
}

section[data-testid="stSidebar"] .stButton button{
    background:var(--card);
    border:1px solid var(--border);
    border-radius:12px;
    font-weight:600;
    color:var(--text);
    transition:.2s ease;
}

section[data-testid="stSidebar"] .stButton button:hover{
    background:var(--accent);
    border-color:var(--accent);
    color:white;
    transform:translateY(-1px);
}

section[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div[role="slider"]{
    background:var(--accent) !important;
}

.hero{
    position:relative;
    min-height:460px;
    border-radius:24px;
    overflow:hidden;
    display:flex;
    flex-direction:column;
    justify-content:center;
    padding:72px;
    margin-bottom:48px;
    background:
        radial-gradient(ellipse 900px 500px at 20% 30%, var(--accent-soft), transparent 60%),
        linear-gradient(rgba(0,0,0,.35), rgba(0,0,0,.95)),
        url("https://images.unsplash.com/photo-1440404653325-ab127d49abc1");
    background-size:cover;
    background-position:center;
    border:1px solid var(--border);
    box-shadow:0 30px 90px rgba(0,0,0,.6);
}

.hero-title{
    font-size:80px;
    font-weight:800;
    letter-spacing:-3px;
    line-height:.98;
    color:var(--text);
}

.hero-subtitle{
    margin-top:18px;
    max-width:680px;
    font-size:19px;
    line-height:1.7;
    color:#c7c7cc;
    font-weight:400;
}

/* =========================
   PREMIUM SEARCH BAR
   ========================= */

.stTextInput {
    margin-top: 10px;
    margin-bottom: 25px;
    position: relative;
}

/* Fix the clipping: target ALL Streamlit wrapper layers */
.stTextInput > div,
.stTextInput div[data-baseweb="base-input"],
.stTextInput div[data-baseweb="input"] {
    background: transparent !important;
    border: none !important;
    border-radius: 22px !important;
    height: 72px !important;
    min-height: 72px !important;
    overflow: visible !important;
    display: flex !important;
    align-items: center !important;
    box-shadow: none !important;
}

.stTextInput input {
    background: rgba(15, 23, 42, 0.90) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 22px !important;
    height: 72px !important;
    line-height: 72px !important;
    color: #ffffff !important;
    font-size: 18px !important;
    font-weight: 500 !important;
    padding: 0 24px !important;
    box-sizing: border-box !important;
    box-shadow:
        0 8px 30px rgba(0, 0, 0, 0.30),
        inset 0 1px 0 rgba(255, 255, 255, 0.03);
    transition: all 0.3s ease !important;
    position: relative;
    z-index: 1;
}

/* Hover */
.stTextInput input:hover {
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    box-shadow:
        0 12px 35px rgba(0, 0, 0, 0.35),
        inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

/* Focus — soft glow, no red ring */
.stTextInput input:focus {
    border: 1px solid rgba(129, 140, 248, 0.55) !important;
    background: rgba(20, 24, 48, 0.92) !important;
    box-shadow:
        0 0 0 4px rgba(99, 102, 241, 0.14),
        0 0 24px rgba(129, 140, 248, 0.20),
        0 15px 40px rgba(0, 0, 0, 0.40) !important;
}

/* Animated rotating gradient glow behind the box on focus */
.stTextInput::before {
    content: "";
    position: absolute;
    top: 10px;
    left: 0;
    right: 0;
    height: 72px;
    border-radius: 24px;
    padding: 1.5px;
    background: conic-gradient(
        from var(--angle, 0deg),
        #6366f1, #8b5cf6, #fa2d48, #6366f1
    );
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    opacity: 0;
    transition: opacity 0.4s ease;
    animation: rotateGlow 4s linear infinite;
    pointer-events: none;
    z-index: 0;
}

.stTextInput:has(input:focus)::before {
    opacity: 1;
}

@keyframes rotateGlow {
    to { --angle: 360deg; }
}

@property --angle {
    syntax: '<angle>';
    initial-value: 0deg;
    inherits: false;
}

/* Placeholder */
.stTextInput input::placeholder {
    color: #94a3b8 !important;
    font-size: 16px !important;
    font-weight: 400 !important;
    letter-spacing: 0.2px;
}


             
.section-title{
    font-size:32px;
    font-weight:800;
    letter-spacing:-1px;
    margin-top:8px;
    margin-bottom:18px;
    color:var(--text);
}

.section-title.spaced{
    margin-top:44px;
}

/* Reduce Streamlit's default vertical gaps between stacked blocks */
div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"]{
    margin-bottom:0 !important;
}

.stTextInput{
    margin-bottom:8px;
}

.poster-card{ transition:.3s cubic-bezier(.2,.8,.2,1); }

.poster-card img{
    border-radius:16px !important;
    transition:.3s cubic-bezier(.2,.8,.2,1);
    box-shadow:0 8px 24px rgba(0,0,0,.35);
}

.poster-card:hover img{
    transform:translateY(-6px) scale(1.025);
    box-shadow:0 20px 40px rgba(0,0,0,.55);
}

.movie-name{
    margin-top:10px;
    font-size:15px;
    font-weight:600;
    color:var(--text);
}

.movie-rating{
    margin-top:4px;
    font-size:13px;
    color:var(--accent);
    font-weight:600;
}

.movie-year{
    color:var(--muted);
    font-size:12px;
    margin-top:2px;
}

.stButton > button{
    width:100%;
    border:1px solid var(--border);
    border-radius:12px;
    background:var(--card);
    color:var(--text);
    font-weight:600;
    padding:.5rem 1rem;
    transition:.2s ease;
}

.stButton > button:hover{
    background:var(--accent);
    border-color:var(--accent);
    color:white;
    transform:translateY(-1px);
}

.stButton > button:active{
    transform:translateY(0);
}

.movie-info-card{
    background:var(--card);
    border-radius:20px;
    padding:28px;
    border:1px solid var(--border);
}

[data-testid="metric-container"]{
    background:var(--card);
    border-radius:16px;
    padding:15px;
    border:1px solid var(--border);
}

img{ border-radius:16px; }

.stSelectbox div[data-baseweb="select"] > div{
    background:var(--card) !important;
    border-color:var(--border) !important;
    border-radius:12px !important;
}

@keyframes fadeUp{
    from{ opacity:0; transform:translateY(10px); }
    to{ opacity:1; transform:translateY(0); }
}

.hero, .movie-info-card{
    animation:fadeUp .5s ease;
}

</style>
""", unsafe_allow_html=True)

# =============================
# STATE + ROUTING (single-file pages)
# =============================
if "view" not in st.session_state:
    st.session_state.view = "home"  # home | details
if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None
if "_hydrated_from_url" not in st.session_state:
    st.session_state._hydrated_from_url = False

# Only read query params into session_state ONCE, on true first load.
# Re-reading them on every rerun causes a race: st.rerun() right after
# mutating st.query_params can run before the browser's address bar
# value is updated, snapping navigation back to the previous page.
if not st.session_state._hydrated_from_url:
    qp_view = st.query_params.get("view")
    qp_id = st.query_params.get("id")
    if qp_view in ("home", "details"):
        st.session_state.view = qp_view
    if qp_id:
        try:
            st.session_state.selected_tmdb_id = int(qp_id)
            st.session_state.view = "details"
        except Exception:
            pass
    st.session_state._hydrated_from_url = True


def goto_home():
    st.session_state.view = "home"
    st.query_params["view"] = "home"
    if "id" in st.query_params:
        del st.query_params["id"]
    st.rerun()


def goto_details(tmdb_id: int):
    st.session_state.view = "details"
    st.session_state.selected_tmdb_id = int(tmdb_id)
    st.query_params["view"] = "details"
    st.query_params["id"] = str(int(tmdb_id))
    st.rerun()


# =============================
# API HELPERS
# =============================

@st.cache_data(ttl=30)
def api_get_json(path: str, params: Optional[dict] = None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=25)
        if r.status_code >= 400:
            return None, f"HTTP {r.status_code}: {r.text[:300]}"
        return r.json(), None
    except Exception as e:
        return None, f"Request failed: {e}"


def poster_grid(cards, cols=6, key_prefix="grid"):
    if not cards:
        st.info("No movies to show.")
        return

    rows = (len(cards) + cols - 1) // cols
    idx = 0
    for r in range(rows):
        colset = st.columns(cols)
        for c in range(cols):
            if idx >= len(cards):
                break
            m = cards[idx]
            idx += 1

            tmdb_id = m.get("tmdb_id")
            title = m.get("title", "Untitled")
            poster = m.get("poster_url")

            with colset[c]:
                st.markdown("<div class='poster-card'>", unsafe_allow_html=True)
                if poster:
                    show_image(poster)
                else:
                    st.write("🖼️ No poster")

                if st.button("Open", key=f"{key_prefix}_{r}_{c}_{idx}_{tmdb_id}"):
                    if tmdb_id:
                        goto_details(tmdb_id)

                st.markdown(
                    f"<div class='movie-name'>{title}</div></div>",
                    unsafe_allow_html=True,
                )


def to_cards_from_tfidf_items(tfidf_items):
    cards = []
    for x in tfidf_items or []:
        tmdb = x.get("tmdb") or {}
        if tmdb.get("tmdb_id"):
            cards.append(
                {
                    "tmdb_id": tmdb["tmdb_id"],
                    "title": tmdb.get("title") or x.get("title") or "Untitled",
                    "poster_url": tmdb.get("poster_url"),
                }
            )
    return cards


def parse_tmdb_search_to_cards(data, keyword: str, limit: int = 24):
    """
    Returns:
      suggestions: list[(label, tmdb_id)]
      cards: list[{tmdb_id,title,poster_url}]
    """
    keyword_l = keyword.strip().lower()

    if isinstance(data, dict) and "results" in data:
        raw = data.get("results") or []
        raw_items = []
        for m in raw:
            title = (m.get("title") or "").strip()
            tmdb_id = m.get("id")
            poster_path = m.get("poster_path")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": f"{TMDB_IMG}{poster_path}" if poster_path else None,
                    "release_date": m.get("release_date", ""),
                }
            )

    elif isinstance(data, list):
        raw_items = []
        for m in data:
            tmdb_id = m.get("tmdb_id") or m.get("id")
            title = (m.get("title") or "").strip()
            poster_url = m.get("poster_url")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": poster_url,
                    "release_date": m.get("release_date", ""),
                }
            )
    else:
        return [], []

    matched = [x for x in raw_items if keyword_l in x["title"].lower()]
    final_list = matched if matched else raw_items

    suggestions = []
    for x in final_list[:10]:
        year = (x.get("release_date") or "")[:4]
        label = f"{x['title']} ({year})" if year else x["title"]
        suggestions.append((label, x["tmdb_id"]))

    cards = [
        {"tmdb_id": x["tmdb_id"], "title": x["title"], "poster_url": x["poster_url"]}
        for x in final_list[:limit]
    ]
    return suggestions, cards


# =============================
# SIDEBAR
# =============================

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:10px 0 25px 0;">
        <div style="font-size:44px; margin-bottom:5px;">🎬</div>
        <div style="font-size:28px; font-weight:800; letter-spacing:-1px; color:#f5f5f7;">
            CineVerse
        </div>
        <div style="color:#86868b; font-size:13px; margin-top:6px;">
            Discover • Explore • Watch
        </div>
    </div>
    """, unsafe_allow_html=True)

    if full_width_button("🏠 Home"):
        goto_home()

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div style="color:#636366; font-size:11px; font-weight:700; letter-spacing:2px; margin-bottom:12px;">
        DISPLAY
    </div>
    """, unsafe_allow_html=True)

    grid_cols = st.slider("Posters Per Row", min_value=4, max_value=7, value=5)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; color:#636366; font-size:12px;">
        Powered by TMDB
    </div>
    """, unsafe_allow_html=True)


# ==========================================================
# VIEW: HOME
# ==========================================================

def render_home():
    st.markdown("""
    <div class="hero">
        <div class="hero-title">CineVerse</div>
        <div class="hero-subtitle">
            Discover trending films, timeless classics,
            hidden gems and personalized recommendations.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">🔍 Discover Movies</div>', unsafe_allow_html=True)

    typed = st.text_input("", placeholder="Search movies, actors, genres...", label_visibility="collapsed")

    if typed.strip():
        if len(typed.strip()) < 2:
            st.warning("Type at least 2 characters.")
        else:
            data, err = api_get_json("/tmdb/search", params={"query": typed.strip()})

            if err or data is None:
                st.error(f"Search failed: {err}")
            else:
                suggestions, cards = parse_tmdb_search_to_cards(data, typed.strip(), limit=24)

                if suggestions:
                    labels = ["-- Select a Movie --"] + [s[0] for s in suggestions]
                    selected = st.selectbox("Suggestions", labels, index=0)

                    if selected != "-- Select a Movie --":
                        label_to_id = {s[0]: s[1] for s in suggestions}
                        goto_details(label_to_id[selected])

                st.markdown('<div class="section-title spaced">🎬 Search Results</div>', unsafe_allow_html=True)
                poster_grid(cards, cols=grid_cols, key_prefix="search_results")
        return

    st.markdown('<div class="section-title spaced">🔥 Trending</div>', unsafe_allow_html=True)
    trending, _ = api_get_json("/home", {"category": "trending", "limit": 18})
    if trending:
        poster_grid(trending, cols=grid_cols, key_prefix="trending")

    st.markdown('<div class="section-title spaced">⭐ Top Rated</div>', unsafe_allow_html=True)
    top_rated, _ = api_get_json("/home", {"category": "top_rated", "limit": 18})
    if top_rated:
        poster_grid(top_rated, cols=grid_cols, key_prefix="top_rated")

    st.markdown('<div class="section-title spaced">🎬 Upcoming</div>', unsafe_allow_html=True)
    upcoming, _ = api_get_json("/home", {"category": "upcoming", "limit": 18})
    if upcoming:
        poster_grid(upcoming, cols=grid_cols, key_prefix="upcoming")

    st.markdown('<div class="section-title spaced">🍿 Now Playing</div>', unsafe_allow_html=True)
    now_playing, _ = api_get_json("/home", {"category": "now_playing", "limit": 18})
    if now_playing:
        poster_grid(now_playing, cols=grid_cols, key_prefix="now_playing")


# ==========================================================
# VIEW: DETAILS
# ==========================================================

def render_details():
    tmdb_id = st.session_state.selected_tmdb_id

    if not tmdb_id:
        st.warning("No movie selected.")
        if st.button("← Back to Home"):
            goto_home()
        st.stop()

    data, err = api_get_json(f"/movie/id/{tmdb_id}")

    if err or not data:
        st.error(f"Could not load details: {err or 'Unknown error'}")
        st.stop()

    backdrop = data.get("backdrop_url")
    if backdrop:
        st.markdown(
            f"""
            <div class="hero" style="
                min-height:480px;
                background:
                    radial-gradient(ellipse 900px 500px at 20% 30%, rgba(250,45,72,.14), transparent 60%),
                    linear-gradient(rgba(0,0,0,.35), rgba(0,0,0,.94)),
                    url('{backdrop}');
                background-size:cover;
                background-position:center;
            ">
                <div class="hero-title">{data.get("title", "Movie")}</div>
                <div class="hero-subtitle">{(data.get("overview") or "No overview available.")[:300]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🏠 Home", key="details_home_btn"):
            goto_home()

    left, right = st.columns([1, 2.4], gap="large")

    with left:
        if data.get("poster_url"):
            show_image(data["poster_url"])

    with right:
        release = data.get("release_date", "-")
        genres = ", ".join([g["name"] for g in data.get("genres", [])])

        st.markdown(
            f"""
            <div class="movie-info-card">
                <h1 style="margin-top:0; margin-bottom:15px;">{data.get("title", "")}</h1>
                <div style="color:var(--accent); font-weight:600; margin-bottom:12px;">
                    📅 {release}
                </div>
                <div style="color:var(--muted); margin-bottom:20px;">
                    🎭 {genres}
                </div>
                <div style="color:var(--text); line-height:1.9;">
                    {data.get("overview") or "No overview available."}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="section-title spaced">🔎 Similar Movies</div>', unsafe_allow_html=True)

    title = (data.get("title") or "").strip()

    if title:
        bundle, err2 = api_get_json(
            "/movie/search",
            params={"query": title, "tfidf_top_n": 12, "genre_limit": 12},
        )

        if not err2 and bundle:
            poster_grid(
                to_cards_from_tfidf_items(bundle.get("tfidf_recommendations")),
                cols=grid_cols,
                key_prefix="details_tfidf",
            )

            st.markdown('<div class="section-title spaced">🎭 More Like This</div>', unsafe_allow_html=True)
            poster_grid(
                bundle.get("genre_recommendations", []),
                cols=grid_cols,
                key_prefix="details_genre",
            )
        else:
            genre_only, err3 = api_get_json(
                "/recommend/genre",
                params={"tmdb_id": tmdb_id, "limit": 18},
            )
            if not err3 and genre_only:
                poster_grid(genre_only, cols=grid_cols, key_prefix="genre_only")
            else:
                st.warning("No recommendations available.")


# ==========================================================
# ROUTER
# ==========================================================

if st.session_state.view == "home":
    render_home()
elif st.session_state.view == "details":
    render_details()


#python3 -m streamlit run app.py                                              