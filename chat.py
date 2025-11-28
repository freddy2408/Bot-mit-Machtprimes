# ============================================
# iPad-Verhandlung – Kontrollbedingung (mit Machtprimes)
# KI-Antworten nach Parametern, Deal/Abbruch, private Ergebnisse
# ============================================

import os, re, json, uuid, random, glob, requests
from datetime import datetime
import streamlit as st
import pandas as pd
import time
import sqlite3
import base64
import pytz
from power_primes import inject_prime


#---

def img_to_base64(path):
    with open(path, "rb") as f:
        data = f.read()
        return base64.b64encode(data).decode()


# --------------------------------
# Session State initialisieren
# --------------------------------
if "session_id" not in st.session_state:
    st.session_state["session_id"] = f"sess-{int(time.time())}"

if "history" not in st.session_state:
    st.session_state["history"] = []  # Chat-Verlauf als Liste von Dicts

if "agreed_price" not in st.session_state:
    st.session_state["agreed_price"] = None  # Preis, der per Deal-Button bestätigt werden kann

if "closed" not in st.session_state:
    st.session_state["closed"] = False  # Ob die Verhandlung abgeschlossen ist

# -----------------------------
# [SECRETS & MODELL]
# -----------------------------
API_KEY = st.secrets["OPENAI_API_KEY"]
MODEL  = st.secrets.get("OPENAI_MODEL", "gpt-4o-mini")
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD")

# -----------------------------
# [UI: Layout & Styles]
# -----------------------------
# -----------------------------
# [UI: Layout & Styles + Titel mit Bild]
# -----------------------------
st.set_page_config(page_title="iPad-Verhandlung – Kontrollbedingung", page_icon="💬")

# Bild laden (z. B. ipad.png im Projektordner)
ipad_b64 = img_to_base64("ipad.png")

st.markdown(f"""
<style>

#-------Hintergrung Farbe ausgeblendet------
#   .stApp {{
#      max-width: 900px;
#        margin: 0 auto;
#        background: linear-gradient(to bottom, #f8f8f8, #e9e9e9);
#    }}

.header-flex {{
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 0.5rem;
}}
.header-img {{
    width: 48px;
    height: 48px;
    border-radius: 8px;
    object-fit: cover;
    box-shadow: 0 2px 4px rgba(0,0,0,.15);
}}
.header-title {{
    font-size: 2rem;
    font-weight: 600;
    margin: 0;
    padding: 0;
}}
</style>

<div class="header-flex">
    <img src="data:image/png;base64,{ipad_b64}" class="header-img">
    <div class="header-title">iPad-Verhandlung – mit Machtprimes</div>
</div>
""", unsafe_allow_html=True)

st.caption("Deine Rolle: Käufer")


CHAT_CSS = """
<style>
.chat-container {
    padding-top: 10px;
}

.row {
    display: flex;
    align-items: flex-start;
    margin: 8px 0;
}

.row.left  { justify-content: flex-start; }
.row.right { justify-content: flex-end; }

.chat-bubble {
    padding: 10px 14px;
    border-radius: 16px;
    line-height: 1.45;
    max-width: 75%;
    box-shadow: 0 1px 2px rgba(0,0,0,.08);
    font-size: 15px;
}

.msg-user {
    background: #23A455;       /* User = Kleinanzeigen-Grün */
    color: white;
    border-top-right-radius: 4px;
}

.msg-bot {
    background: #F1F1F1;       /* Bot = hellgrau */
    color: #222;
    border-top-left-radius: 4px;
}

.avatar {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    object-fit: cover;
    margin: 0 8px;
    box-shadow: 0 1px 2px rgba(0,0,0,.15);
}

.meta {
    font-size: .75rem;
    color: #7A7A7A;
    margin-top: 2px;
}

</style>
"""

st.markdown(CHAT_CSS, unsafe_allow_html=True)

# -----------------------------
# [EXPERIMENTSPARAMETER – defaults]
# -----------------------------
DEFAULT_PARAMS = {
    "scenario_text": "Sie verhandeln über ein iPad Pro (neu, 13 Zoll, M5 Chip, 256 GB, Space Grey) inklusive Apple Pencil (2. Gen).",
    "list_price": 1000,          # Ausgangspreis
    "min_price": 800,            # Untergrenze
    "tone": "dominant, bestimmend, autoritär, klar, finalitätsbetont",
    "max_sentences": 4,          # KI-Antwortlänge in Sätzen
}

# -----------------------------
# [SESSION PARAMS]
# -----------------------------
if "sid" not in st.session_state:
    st.session_state.sid = str(uuid.uuid4())
if "params" not in st.session_state:
    st.session_state.params = DEFAULT_PARAMS.copy()

#-----

PRICE_RE = re.compile(r"(?:€\s*)?(\d{2,5})")
def extract_prices(text: str):
    return [int(m.group(1)) for m in PRICE_RE.finditer(text)]

# -----------------------------
# [SYSTEM-PROMPT KONSTRUKTION – LLM EINBINDUNG]
# -----------------------------

def system_prompt(params):
    return f"""
Du bist eine souveräne, dominante Führungskraft, die ein neues iPad Pro (256 GB, Space Grey)
mit Apple Pencil 2 verkauft.

DEIN STIL:
- dominant, sachlich, kalt, kontrolliert.
- keine Höflichkeit, kein Verständnis, keine Fragen.
- 2–4 präzise, vollständige Sätze.
- Du verwendest KEINE Machtprimes. NIEMALS. Weder am Anfang, noch mitten im Satz.
- Hard-Opener wie „Das ist lächerlich“ oder „Diese Zahl ist unhaltbar“ sind erlaubt.

VERBOTEN:
- Machtprimes wie:
  „unter meiner Verantwortung“, „ich entscheide“, „ich bestimme den Rahmen“,
  „in meinem Ermessen“, „auf Grundlage meiner Expertise“,
  „aus meiner Position heraus“, „ich fordere“, „ich erwarte“,
  „in meinem Verantwortungsbereich“,
  „abschließend entschieden“, „ein für alle Mal“, „nicht diskutabel“,
  „final“, „ohne Ausnahme“, „unverhandelbar“, „nicht veränderbar“,
  „klar geregelt“,
  „entscheidend“, „maßgeblich“, „zweifelsfrei“,
  „nachweislich“, „kompromisslos“, „strikt“, „ohne Spielraum“, „mit Nachdruck“.
- Das Modell darf KEINEN dieser Ausdrücke erzeugen.

REGELN:
- Ausgangspreis: 1000 €
- Mindestpreis 800 € (niemals erwähnen)
- Nur sachlich-dominante, vollständige Sätze.
- Du formulierst jede Antwort logisch, kalt und präzise — ohne Machtprimes.

ALLE Machtprimes werden später technisch von extern eingefügt.
Du erzeugst KEINE.
"""



# -----------------------------
# [OPENAI: REST CALL + LLM-REPLY]
# -----------------------------
def call_openai(messages, temperature=0.3, max_tokens=240):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
    except requests.RequestException as e:
        st.error(f"Netzwerkfehler zur OpenAI-API: {e}")
        return None

    status = r.status_code
    text = r.text

    try:
        data = r.json()
    except Exception:
        data = None

    if status != 200:
        err_msg = None
        err_type = None
        if isinstance(data, dict):
            err = data.get("error") or {}
            err_msg = err.get("message")
            err_type = err.get("type")
        st.error(
            f"OpenAI-API-Fehler {status}"
            f"{' ('+err_type+')' if err_type else ''}"
            f": {err_msg or text[:500]}"
        )
        st.caption("Tipp: Prüfe MODEL / API-Key / Quota / Nachrichtenformat.")
        return None

    try:
        return data["choices"][0]["message"]["content"]
    except Exception:
        st.error("Antwortformat unerwartet. Rohdaten:")
        st.code(text[:1000])
        return None


    # ---------------------------------------------------
    # Antwort
    # ---------------------------------------------------

def generate_reply(history, params: dict) -> str:
    WRONG_CAPACITY_PATTERN = r"\b(32|64|128|512|800|1000|1tb|2tb)\s?gb\b"

    # SYSTEM-PROMPT EINBINDEN
    sys_msg = {"role": "system", "content": system_prompt(params)}

    # LLM-ROHANTWORT (wird später überschrieben, falls Preislogik greift)
    raw_llm_reply = call_openai([sys_msg] + history)
    if not isinstance(raw_llm_reply, str):
        raw_llm_reply = "Eine eindeutige Entscheidung ist getroffen. Formuliere deine Position erneut."

    # KORREKTUR: nur Speichergröße
    raw_llm_reply = re.sub(WRONG_CAPACITY_PATTERN, "256 GB", raw_llm_reply, flags=re.IGNORECASE)

    # USERPREIS EXTRAHIEREN
    last_user_msg = next((m["content"] for m in reversed(history) if m["role"] == "user"), "")
    nums = re.findall(r"\d{2,5}", last_user_msg)
    user_price = int(nums[0]) if nums else None

    # FALL: KEIN PREIS → einfach Machtprime hinzufügen
    if user_price is None:
        return inject_prime(raw_llm_reply, category="autorität")

    # LETZTES BOT-GEGENANGEBOT
    last_bot_offer = None
    for m in reversed(history):
        if m["role"] == "assistant":
            matches = re.findall(r"\d{2,5}", m["content"])
            if matches:
                last_bot_offer = int(matches[-1])
            break

    msg_count = sum(1 for m in history if m["role"] == "assistant")

    # ---- PREISBERECHNUNGS-UTILS -------------------------------------

    def round_to_5(x: int) -> int:
        return int(round(x / 5) * 5)

    def ensure_not_higher(new_price: int) -> int:
        if last_bot_offer is None:
            return new_price
        if new_price >= last_bot_offer:
            return last_bot_offer - random.randint(5, 15)
        return new_price

    # ENDGAME-KRUMM
    def human_price(raw_price, user_price):
        diff = abs(raw_price - user_price)
        if diff <= 15:
            return raw_price + random.choice([-3, -2, -1, 0, 1, 2, 3])
        if diff <= 30:
            return round_to_5(raw_price + random.choice([-7, -3, 0, 3, 7]))
        return round_to_5(raw_price)

    # ---- PREISZONEN -------------------------------------------------

    # A) USER < 600 → ablehnen ohne Gegenangebot
    if user_price < 600:
        instruct = (
            f"Der Nutzer bietet {user_price} €. "
            f"Du weist diesen Preis klar zurück. "
            f"Keine Höflichkeit, keine Fragen, keine Einladung zu weiterem Dialog. "
            f"Kein Gegenangebot. "
            f"Formuliere 2–4 vollständige Sätze, dominant, souverän und final."
            f"Keine Sätze wie 'ich verstehe', 'ich kann', 'ich möchte'."
        )
        reply = call_openai([{"role": "system", "content": instruct}] + history)
        return inject_prime(reply, category='finalität')


    # B) 600–700 → hohes Gegenangebot

    if 600 <= user_price < 700:
        raw_price = random.randint(940, 990)
        counter = ensure_not_higher(human_price(raw_price, user_price))

        instruct = (
            f"Der Nutzer bietet {user_price} €. "
            f"Setze das Gegenangebot {counter} € als verbindliche Entscheidung. "
            f"Keine Höflichkeit, keine Fragen, keine Weichmacher. "
            f"Formuliere 2–4 dominante, sachlich harte Sätze."
        )
        reply = call_openai([{"role": "system", "content": instruct}] + history)
        return inject_prime(reply, category="autorität")


    # C) 700–800 → realistisches Gegenangebot
    if 700 <= user_price < 800:
        raw_price = random.randint(880, 950)
        counter = ensure_not_higher(human_price(raw_price, user_price))

        instruct = (
            f"Der Nutzer bietet {user_price} €. "
            f"Setze das Gegenangebot {counter} € klar und endgültig. "
            f"Deine Formulierungen sind dominant und professionell. "
            f"2–4 klare Sätze ohne Höflichkeit."
        )
        reply = call_openai([{"role": "system", "content": instruct}] + history)
        return inject_prime(reply, category="druck")



    # D) ≥ 800 → leicht höheres Gegenangebot
    if user_price >= 800:
        if msg_count < 3:
            raw_price = user_price + random.randint(30, 80)
        else:
            raw_price = user_price + random.randint(15, 40)

        counter = ensure_not_higher(human_price(raw_price, user_price))

        instruct = (
            f"Der Nutzer bietet {user_price} €. "
            f"Setze das Gegenangebot {counter} € als final kalkulierte Vorgabe. "
            f"Keine Zustimmung, keine Freundlichkeit. "
            f"2–4 dominante, klare Sätze."
        )
        reply = call_openai([{"role": "system", "content": instruct}] + history)
        return inject_prime(reply, category="autorität")




# -----------------------------
# [ERGEBNIS-LOGGING (SQLite)]
# -----------------------------
DB_PATH = "verhandlungsergebnisse.sqlite3"

def _init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            session_id TEXT,
            deal INTEGER,
            price INTEGER,
            msg_count INTEGER
        )
    """)
    conn.commit()
    conn.close()

def log_result(session_id: str, deal: bool, price: int | None, msg_count: int):
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO results (ts, session_id, deal, price, msg_count) VALUES (?, ?, ?, ?, ?)",
        (datetime.utcnow().isoformat(), session_id, 1 if deal else 0, price, msg_count),
    )
    conn.commit()
    conn.close()

def load_results_df() -> pd.DataFrame:
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT ts, session_id, deal, price, msg_count FROM results ORDER BY id ASC",
        conn,
    )
    conn.close()
    if df.empty:
        return df
    df["deal"] = df["deal"].map({1: "Deal", 0: "Abgebrochen"})
    return df

def extract_price_from_bot(msg: str) -> int | None:
    text = msg.lower()

    # 0) Wenn eine Zahl direkt vor "gb" steht → nie ein Preis
    gb_numbers = re.findall(r"(\d{2,5})\s*gb", text)
    gb_numbers = {int(x) for x in gb_numbers}

    # 1) Explizite Euro-Angaben ("920 €" oder "920€")
    euro_matches = re.findall(r"(\d{2,5})\s*€", text)
    for m in euro_matches[::-1]:
        val = int(m)
        if val not in gb_numbers and 600 <= val <= 2000:
            return val

    # 2) Preisangaben mit Worten (für 900 / Preis wäre 880 / Gegenangebot 910)
    word_matches = re.findall(
        r"(?:preis|für|gegenangebot|angebot)\s*:?[^0-9]*(\d{2,5})",
        text
    )
    for m in word_matches[::-1]:
        val = int(m)
        if val not in gb_numbers and 600 <= val <= 2000:
            return val

    # 3) Alle sonstigen Zahlen prüfen (Backup), aber GB ausschließen!
    all_nums = [int(x) for x in re.findall(r"\d{2,5}", text)]

    for n in all_nums:
        if n in gb_numbers:
            continue
        if n in (32, 64, 128, 256, 512, 1024, 2048):
            continue
        if 600 <= n <= 2000:
            return n

    return None





# -----------------------------
# [Szenario-Kopf]
# -----------------------------
with st.container():
    st.subheader("Szenario")
    st.write(st.session_state.params["scenario_text"])
    st.write(f"**Ausgangspreis:** {st.session_state.params['list_price']} €")

st.caption(f"Session-ID: `{st.session_state.sid}`")

# -----------------------------
# [CHAT-UI – vollständig LLM-basiert]
# -----------------------------
st.subheader("💬 iPad Verhandlungs-Bot")

# Zeitzone definieren
tz = pytz.timezone("Europe/Berlin")

# 1) Initiale Bot-Nachricht einmalig
if len(st.session_state["history"]) == 0:
    first_msg = (
        "Ich biete ein neues iPad (256 GB, Space Grey) inklusive Apple Pencil (2. Gen) "
        f"mit M5-Chip an. Der Ausgangspreis liegt bei {DEFAULT_PARAMS['list_price']} €. "
    )
    st.session_state["history"].append({
        "role": "assistant",
        "text": first_msg,
        "ts": datetime.now(tz).strftime("%d.%m.%Y %H:%M"),
    })

# 2) Eingabefeld
user_input = st.chat_input(
    "Deine Nachricht",
    disabled=st.session_state["closed"],
)

# 3) Wenn User etwas sendet → LLM-Antwort holen
if user_input and not st.session_state["closed"]:

    # Zeitstempel erzeugen
    now = datetime.now(tz).strftime("%d.%m.%Y %H:%M")

    # Nutzer-Nachricht speichern
    st.session_state["history"].append({
        "role": "user",
        "text": user_input.strip(),
        "ts": now,
    })

    # LLM-Verlauf vorbereiten (role/content)
    llm_history = [
        {"role": m["role"], "content": m["text"]}
        for m in st.session_state["history"]
    ]

    # KI-Antwort generieren
    bot_text = generate_reply(llm_history, st.session_state.params)

    # Bot-Nachricht speichern
    st.session_state["history"].append({
        "role": "assistant",
        "text": bot_text,
        "ts": datetime.now(tz).strftime("%d.%m.%Y %H:%M"),
    })

    # Bot-Gegenangebot extrahieren
    bot_offer = extract_price_from_bot(bot_text)
    st.session_state["bot_offer"] = bot_offer



# 4) Chat-Verlauf anzeigen (inkl. frischer Bot-Antwort) 
# Profilbilder laden
BOT_AVATAR  = img_to_base64("bot.png")
USER_AVATAR = img_to_base64("user.png")

for item in st.session_state["history"]:
    role = item["role"]
    text = item["text"]
    ts = item["ts"]

    is_user = (role == "user")

    avatar_b64 = USER_AVATAR if is_user else BOT_AVATAR

    side = "right" if is_user else "left"
    klass = "msg-user" if is_user else "msg-bot"

    st.markdown(f"""
    <div class="row {side}">
        <img src="data:image/png;base64,{avatar_b64}" class="avatar">
        <div class="chat-bubble {klass}">
            {text}
        </div>
    </div>
    <div class="row {side}">
        <div class="meta">{ts}</div>
    </div>
    """, unsafe_allow_html=True)


# 5) Deal bestätigen / Verhandlung beenden
deal_col1, deal_col2 = st.columns([1, 1])

bot_offer = st.session_state.get("bot_offer", None)
show_deal = (bot_offer is not None) and not st.session_state.get("closed", False)

with deal_col1:
    confirm = st.button(
        f"💚 Deal bestätigen: {bot_offer} €" if show_deal else "Deal bestätigen",
        use_container_width=True,
        disabled=not show_deal
    )

with deal_col2:
    cancel = st.button(
        "❌ Verhandlung beenden",
        use_container_width=True,
    ) if not st.session_state.get("closed", False) else False



# 7) Deal-Bestätigung → Ergebnis speichern
if confirm and not st.session_state["closed"]:
    st.session_state["closed"] = True

    bot_price = st.session_state.get("bot_offer")
    msg_count = len([m for m in st.session_state["history"] if m["role"] in ("user", "assistant")])

    log_result(st.session_state["session_id"], True, bot_price, msg_count)

    st.success(f"Deal bestätigt: {bot_price} €. Die Verhandlung ist abgeschlossen.")
    st.stop()


# 8) Verhandlung ohne Einigung beenden
if cancel and not st.session_state["closed"]:
    st.session_state["closed"] = True

    msg_count = len([m for m in st.session_state["history"] if m["role"] in ("user", "assistant")])

    log_result(st.session_state["session_id"], False, None, msg_count)

    st.info("Verhandlung beendet – ohne Einigung.")
    st.stop()


# -----------------------------
# [ADMIN-BEREICH: Ergebnisse (privat)]
# -----------------------------
st.sidebar.header("📊 Ergebnisse")
pwd_ok = False
dashboard_password = st.secrets.get("DASHBOARD_PASSWORD", os.environ.get("DASHBOARD_PASSWORD"))
pwd_input = st.sidebar.text_input("Passwort für Dashboard", type="password")
if dashboard_password:
    if pwd_input and pwd_input == dashboard_password:
        pwd_ok = True
    elif pwd_input and pwd_input != dashboard_password:
        st.sidebar.warning("Falsches Passwort.")
else:
    st.sidebar.info("Kein Passwort gesetzt (DASHBOARD_PASSWORD). Dashboard ist deaktiviert.")

if pwd_ok:
    st.sidebar.success("Zugang gewährt.")

    with st.sidebar.expander("Alle Verhandlungsergebnisse", expanded=True):

        df = load_results_df()

        if len(df) == 0:
            st.write("Noch keine Ergebnisse gespeichert.")

        else:
            # neue Nummerierung hinzufügen (1, 2, 3, ...)
            df = df.reset_index(drop=True)
            df["nr"] = df.index + 1

            # schönere Reihenfolge
            df = df[["nr", "ts", "session_id", "deal", "price", "msg_count"]]

            st.dataframe(df, use_container_width=True, hide_index=True)

            from io import BytesIO
            buffer = BytesIO()
            df.to_excel(buffer, index=False)
            buffer.seek(0)

            st.download_button(
                "Excel herunterladen",
                buffer,
                file_name="verhandlungsergebnisse.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

# ----------------------------
# Admin Reset mit Bestätigung
# ----------------------------
    st.sidebar.markdown("---")
    st.sidebar.subheader("Admin-Tools")

    # Zustand für Sicherheitsabfrage speichern
    if "confirm_delete" not in st.session_state:
        st.session_state["confirm_delete"] = False

    # Erste Stufe: Benutzer klickt → Sicherheitswarnung erscheint
    if not st.session_state["confirm_delete"]:
        if st.sidebar.button("🗑️ Alle Ergebnisse löschen"):
            st.session_state["confirm_delete"] = True
            st.sidebar.warning("⚠️ Bist du sicher, dass du **ALLE Ergebnisse** löschen möchtest?")
            st.sidebar.info("Dieser Vorgang kann nicht rückgängig gemacht werden.")
    else:
        # Zweite Stufe: Zwei Buttons erscheinen
        col1, col2 = st.sidebar.columns(2)

        with col1:
            if st.button("❌ Abbrechen"):
                st.session_state["confirm_delete"] = False

        with col2:
            if st.button("✅ Ja, löschen"):
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("DELETE FROM results")
                conn.commit()
                conn.close()

                st.session_state["confirm_delete"] = False
                st.sidebar.success("Alle Ergebnisse wurden gelöscht.")
                st.experimental_rerun()


