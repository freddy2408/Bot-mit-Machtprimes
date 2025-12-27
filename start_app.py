import sqlite3, uuid, random
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Studie Start", page_icon="▶️", layout="centered")

BOT_A_URL = "https://verhandlung.streamlit.app"
BOT_B_URL = "https://verhandlung123.streamlit.app"
DB_PATH = "assignments.sqlite3"

AUTO_REDIRECT = True   # <- optional: auf False setzen, wenn du keinen Auto-Redirect willst
REDIRECT_SECONDS = 3   # <- Countdown-Dauer


# ----------------------------
# DB helpers
# ----------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            pid TEXT PRIMARY KEY,
            order_code TEXT,
            created_ts TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_or_create_assignment(pid: str):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT order_code FROM assignments WHERE pid = ?", (pid,))
    row = c.fetchone()

    if row:
        order_code = row[0]
    else:
        order_code = random.choice(["AB", "BA"])
        c.execute(
            "INSERT INTO assignments (pid, order_code, created_ts) VALUES (?, ?, ?)",
            (pid, order_code, datetime.utcnow().isoformat())
        )
        conn.commit()

    conn.close()
    return order_code


# ----------------------------
# 1) pid aus URL oder neu generieren
# ----------------------------
pid = st.query_params.get("pid", None)
if not pid:
    pid = f"p-{uuid.uuid4().hex[:10]}"
    st.query_params["pid"] = pid

# 2) Reihenfolge fixieren (persistiert)
order_code = get_or_create_assignment(pid)
st.query_params["order"] = order_code


# ----------------------------
# 3) Ziel-URL bestimmen (nur 1 Button)
# ----------------------------
if order_code == "AB":
    next_url = f"{BOT_A_URL}?pid={pid}&order=AB&step=1"
else:
    next_url = f"{BOT_B_URL}?pid={pid}&order=BA&step=1"

next_label = "Weiter zu Teil 1"


# ----------------------------
# 4) UI / Layout
# ----------------------------
st.markdown(
    """
    <style>
      .subtitle { color: rgba(49, 51, 63, 0.7); margin-top: 0.2rem; }
      .badge {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        border: 1px solid rgba(49, 51, 63, 0.18);
        font-size: 0.85rem;
        color: rgba(49, 51, 63, 0.8);
        background: rgba(255,255,255,0.55);
      }
      .card {
        border: 1px solid rgba(49, 51, 63, 0.15);
        border-radius: 16px;
        padding: 18px 18px;
        background: rgba(255,255,255,0.6);
      }
      .meta {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
        font-size: 0.9rem;
        color: rgba(49, 51, 63, 0.75);
        margin-top: 8px;
      }
      div.stLinkButton > a {
        padding: 0.9rem 1.0rem !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
      }
      .tiny { color: rgba(49, 51, 63, 0.65); font-size: 0.9rem; margin-top: 6px; }
    </style>
    """,
    unsafe_allow_html=True
)

# Kopfzeile: links Titel + Infos, rechts Info-Icon
left, right = st.columns([0.88, 0.12], vertical_alignment="top")
with left:
    st.title("Start der Studie")
    st.markdown('<div class="subtitle">Du startest jetzt Teil 1. Danach wirst du zu Teil 2 weitergeleitet.</div>', unsafe_allow_html=True)
    st.markdown('<span class="badge">Teil 1 von 2</span> &nbsp; <span class="badge">Dauer: ca. 5–8 Min.</span>', unsafe_allow_html=True)

with right:
    with st.popover("ℹ️", help="Info / Disclaimer"):
        st.markdown(
            """
**Disclaimer**

- Die Verhandlung ist **fiktiv** – du kannst das iPad **nicht wirklich kaufen**.  
- Es werden **nur anonyme, nicht zuweisbare Daten** gespeichert – ausschließlich zu Zwecken unseres **Bachelorprojekts**.
            """
        )

st.write("")

# Card mit CTA
st.markdown('<div class="card">', unsafe_allow_html=True)

st.markdown("**Bitte lies kurz:**")
st.markdown("- Verhandle so, als wäre es eine echte Situation.\n- Bitte schließe Teil 1 vollständig ab, bevor du den Tab schließt.")

# dezente Meta-Infos (optional)
st.markdown(f'<div class="meta">Teilnehmer-ID: {pid} · Reihenfolge: {order_code}</div>', unsafe_allow_html=True)

st.write("")
st.link_button(next_label, next_url, use_container_width=True)

# Optional: Auto-Redirect mit Countdown (Button bleibt Fallback)
if AUTO_REDIRECT:
    st.write("")
    placeholder = st.empty()
    for i in range(REDIRECT_SECONDS, 0, -1):
        placeholder.markdown(f'<div class="tiny">Automatische Weiterleitung in <b>{i}</b> Sekunden …</div>', unsafe_allow_html=True)
        st.sleep(1)
    # Redirect
    st.markdown(f"<meta http-equiv='refresh' content='0; url={next_url}'>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

st.caption("Hinweis: Bitte lasse das Browserfenster geöffnet, bis du beide Teile abgeschlossen hast.")
