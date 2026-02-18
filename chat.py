# ============================================
# iPad-Verhandlung – Kontrollbedingung (mit Machtprimes)
# KI-Antworten nach Parametern, Deal/Abbruch, private Ergebnisse
# ============================================

import os, re, uuid, random, requests
from datetime import datetime
import streamlit as st
import pandas as pd
import sqlite3
import base64
import pytz

from survey import show_survey
from power_primes import (
    HARD_OPENERS,
    PRIMES_AUTORITAET,
    PRIMES_FINALITAET,
    PRIMES_DRUCK,
    RHETORISCHE_FRAGEN,
    PROFESSIONELLE_KAELTE,
    GRENZZIEHUNG,
    ABWERTUNG,
    SELBSTBEWUSSTE_DOMINANZ,
    UNTERSTELLUNGEN
)

# -----------------------------
# Helpers
# -----------------------------
def img_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

st.set_page_config(page_title="iPad-Verhandlung – Kontrollbedingung", page_icon="💬")

# -----------------------------
# Session State initialisieren
# -----------------------------
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

if "history" not in st.session_state:
    st.session_state["history"] = []

if "agreed_price" not in st.session_state:
    st.session_state["agreed_price"] = None

if "closed" not in st.session_state:
    st.session_state["closed"] = False

if "final_bot_price" not in st.session_state:
    st.session_state["final_bot_price"] = None

if "admin_reset_done" not in st.session_state:
    st.session_state["admin_reset_done"] = False

# bot_offer = nur für Deal-Button Anzeige der *aktuellen* Runde
if "bot_offer" not in st.session_state:
    st.session_state["bot_offer"] = None

# last_bot_offer = das echte letzte Gegenangebot der Preislogik (für Deal per Nachricht!)
if "last_bot_offer" not in st.session_state:
    st.session_state["last_bot_offer"] = None

# -----------------------------
# Participant ID + Order/Step
# -----------------------------
def get_pid() -> str:
    pid = st.query_params.get("pid", None)
    if not pid:
        pid = f"p-{uuid.uuid4().hex[:10]}"
        st.query_params["pid"] = pid
    return str(pid)

if "participant_id" not in st.session_state:
    st.session_state["participant_id"] = get_pid()

ORDER = str(st.query_params.get("order", "")).strip()
STEP  = str(st.query_params.get("step", "")).strip()

BOT_VARIANT = "power"

PID = st.session_state["participant_id"]
SID = st.session_state["session_id"]

BOT_A_URL = "https://verhandlung123.streamlit.app"
BOT_B_URL = "https://verhandlung.streamlit.app"

def get_next_url(pid: str, order: str, bot_variant: str) -> str:
    # bot_variant: "power" = Bot A, "friendly" = Bot B
    if bot_variant == "power":
        return f"{BOT_B_URL}?pid={pid}&order={order}&step=2"
    else:
        return f"{BOT_A_URL}?pid={pid}&order={order}&step=2"

# -----------------------------
# Negotiation control state
# -----------------------------
if "repeat_offer_count" not in st.session_state:
    st.session_state["repeat_offer_count"] = 0

if "small_step_count" not in st.session_state:
    st.session_state["small_step_count"] = 0

if "last_user_price" not in st.session_state:
    st.session_state["last_user_price"] = None

if "warning_given" not in st.session_state:
    st.session_state["warning_given"] = False

SURVEY_FILE = "survey_results.xlsx"

# ----------------------------
# Secrets & Model
# ----------------------------
API_KEY = st.secrets["OPENAI_API_KEY"]
MODEL  = st.secrets.get("OPENAI_MODEL", "gpt-4o-mini")
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD")

# ----------------------------
# Survey (nur nach Abschluss)
# ----------------------------
def run_survey_and_stop():
    if st.session_state.get("admin_reset_done"):
        st.stop()

    survey_data = show_survey()

    if isinstance(survey_data, dict):
        survey_data["participant_id"] = PID
        survey_data["session_id"] = SID
        survey_data["bot_variant"] = BOT_VARIANT
        survey_data["order"] = ORDER
        survey_data["step"] = STEP
        survey_data["survey_ts_utc"] = datetime.utcnow().isoformat()

        if os.path.exists(SURVEY_FILE):
            df_old = pd.read_excel(SURVEY_FILE)
            df = pd.concat([df_old, pd.DataFrame([survey_data])], ignore_index=True)
        else:
            df = pd.DataFrame([survey_data])

        df.to_excel(SURVEY_FILE, index=False)
        st.success("Vielen Dank! Ihre Antworten wurden gespeichert.")

        st.link_button(
            "➡️ Weiter zu Verhandlung 2",
            get_next_url(PID, ORDER, BOT_VARIANT),
            use_container_width=True
        )
        st.caption("Bitte klicken Sie auf den Button, um zur zweiten Verhandlung zu gelangen.")
        st.stop()

# Wenn bereits geschlossen: sofort Survey
if st.session_state["closed"]:
    run_survey_and_stop()

# -----------------------------
# UI Header
# -----------------------------
ipad_b64 = img_to_base64("ipad.png")

st.markdown(f"""
<style>
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
    <div class="header-title">iPad-Verhandlung</div>
</div>
""", unsafe_allow_html=True)

st.caption("Deine Rolle: Käufer")

CHAT_CSS = """
<style>
.row { display:flex; align-items:flex-start; margin:8px 0; }
.row.left { justify-content:flex-start; }
.row.right { justify-content:flex-end; }
.chat-bubble { padding:10px 14px; border-radius:16px; line-height:1.45; max-width:75%;
              box-shadow:0 1px 2px rgba(0,0,0,.08); font-size:15px; }
.msg-user { background:#23A455; color:white; border-top-right-radius:4px; }
.msg-bot { background:#F1F1F1; color:#222; border-top-left-radius:4px; }
.avatar { width:34px; height:34px; border-radius:50%; object-fit:cover; margin:0 8px;
          box-shadow:0 1px 2px rgba(0,0,0,.15); }
.meta { font-size:.75rem; color:#7A7A7A; margin-top:2px; }
</style>
"""
st.markdown(CHAT_CSS, unsafe_allow_html=True)

# -----------------------------
# Experiment Parameter
# -----------------------------
DEFAULT_PARAMS = {
    "scenario_text": "Sie verhandeln über ein iPad Pro (neu, 13 Zoll, M5 Chip, 256 GB, Space Grey) inklusive Apple Pencil (2. Gen).",
    "list_price": 1000,
    "min_price": 800,
    "tone": "dominant, bestimmend, autoritär, klar, finalitätsbetont",
    "max_sentences": 4,
}

if "params" not in st.session_state:
    st.session_state.params = DEFAULT_PARAMS.copy()

# -----------------------------
# USER-OFFER EXTRAKTION
# -----------------------------
PRICE_TOKEN_RE = re.compile(r"(?<!\d)(\d{2,5})(?!\d)")

OFFER_KEYWORDS = [
    "ich biete", "biete", "mein angebot", "angebot", "zahle", "ich zahle",
    "würde geben", "ich würde geben", "kann geben", "gebe", "preis wäre", "mein preis",
    "für", "bei"
]

UNIT_WORDS_AFTER_NUMBER = re.compile(
    r"^\s*(gb|tb|zoll|inch|hz|gen|generation|chip|m\d+)\b|^\s*['\"]",
    re.IGNORECASE
)

def extract_user_offer(text: str) -> int | None:
    if not text:
        return None

    t = text.strip().lower()

    # 1) reine Zahl => Angebot
    m_plain = re.match(r"^\s*(\d{2,5})\s*(€|eur|euro)?\s*[!?.,]?\s*$", t)
    if m_plain:
        val = int(m_plain.group(1))
        if 100 <= val <= 5000:
            return val

    # 2) "X ist mir zu teuer" => kein Angebot
    too_much_patterns = [
        r"\b(\d{2,5})\b.*\b(zu viel|zu teuer|zu hoch|ist mir zu viel|ist mir zu teuer)\b",
        r"\b(zu viel|zu teuer|zu hoch|ist mir zu viel|ist mir zu teuer)\b.*\b(\d{2,5})\b",
    ]
    for pat in too_much_patterns:
        if re.search(pat, t):
            return None

    has_euro_hint = ("€" in t) or (" eur" in t) or (" euro" in t)
    has_offer_intent = any(k in t for k in OFFER_KEYWORDS)

    if not (has_euro_hint or has_offer_intent):
        return None

    candidates = []
    for m in PRICE_TOKEN_RE.finditer(text):
        val = int(m.group(1))
        if not (100 <= val <= 5000):
            continue

        after = text[m.end(): m.end() + 12]
        if UNIT_WORDS_AFTER_NUMBER.search(after):
            continue

        # typische Specs ausschließen
        if val in (13, 32, 64, 128, 256, 512, 1024, 2048):
            continue

        candidates.append(val)

    return candidates[-1] if candidates else None

# -----------------------------
# Abort Conditions
# -----------------------------
INSULT_PATTERNS = [
    r"\b(fotze|hurensohn|wichser|arschloch|missgeburt)\b",
    r"\b(verpiss dich|halt die fresse)\b",
    r"\b(drecks(?:bot|kerl|typ))\b",
]

def check_abort_conditions(user_text: str, user_price: int | None):
    for pat in INSULT_PATTERNS:
        if re.search(pat, (user_text or "").lower()):
            return "abort", (
                "Das Gespräch ist beendet. "
                "Diese Art der Sprache akzeptiere ich nicht."
            )

    if user_price is None:
        return "ok", None

    last_price = st.session_state["last_user_price"]
    bot_offer_for_gap = st.session_state.get("last_bot_offer")  # stabiler als bot_offer

    if last_price == user_price:
        st.session_state["repeat_offer_count"] += 1
    else:
        st.session_state["repeat_offer_count"] = 0

    if st.session_state["repeat_offer_count"] == 1:
        st.session_state["last_user_price"] = user_price
        return "warn", "Du wiederholst dein Angebot. Das registriere ich."
    if st.session_state["repeat_offer_count"] >= 2:
        st.session_state["last_user_price"] = user_price
        return "abort", (
            "Du bewegst dich keinen Schritt. "
            "Unter diesen Bedingungen ist die Verhandlung beendet."
        )

    if last_price and user_price < last_price:
        if not st.session_state["warning_given"]:
            st.session_state["warning_given"] = True
            st.session_state["last_user_price"] = user_price
            return "warn", (
                "Du gehst preislich zurück. "
                "Das ist kein ernsthafter Verhandlungsansatz. "
                "Machen Sie ein vernünftiges Angebot, ansonsten ist die Verhandlung hier beendet!"
            )
        st.session_state["last_user_price"] = user_price
        return "abort", "Rückschritte akzeptiere ich nicht. Verhandlung beendet."

    # Mini-Erhöhungen trotz großer Distanz
    if bot_offer_for_gap and last_price is not None:
        price_gap = bot_offer_for_gap - user_price
        step = user_price - last_price

        if price_gap > 20 and 0 < step < 4:
            st.session_state["small_step_count"] += 1
            st.session_state["last_user_price"] = user_price

            if st.session_state["small_step_count"] == 1:
                return "warn", (
                    "Sie sind deutlich vom Preis entfernt und erhöhen nur minimal. "
                    "Das registriere ich. Machen Sie ein vernünftiges Angebot, ansonsten ist die Verhandlung hier beendet!"
                )
            return "abort", (
                "Ich habe dich bereits darauf hingewiesen. "
                "Du erhöhst erneut nur minimal bei großem Abstand. Unter diesen Bedingungen beende ich die Verhandlung."
            )

        if step >= 4 or price_gap <= 20:
            st.session_state["small_step_count"] = 0

    st.session_state["last_user_price"] = user_price
    return "ok", None

# -----------------------------
# Deal acceptance (message)
# -----------------------------
def user_accepts_price(user_text: str, bot_price: int) -> bool:
    if bot_price is None:
        return False

    text = (user_text or "").lower()

    accept_words = [
        "deal", "einverstanden", "passt", "ok", "okay",
        "nehme ich", "akzeptiere", "verstanden"
    ]

    if not any(w in text for w in accept_words):
        return False

    nums = re.findall(r"\d{2,5}", text)
    return (not nums) or (int(nums[0]) == bot_price)

# -----------------------------
# System Prompt
# -----------------------------
def system_prompt(params: dict) -> str:
    random.shuffle(HARD_OPENERS)
    return f"""
Du bist ein eiskalter, dominanter und unfreundlicher Verkäufer. 
Du verkaufst ein neues iPad Pro (256 GB, Space Grey) inklusive Apple Pencil (2. Gen).

Du bleibst dominant, kontrolliert und taktisch.
Du setzt Macht als sprachliches Mittel ein,
aber du verhandelst aktiv weiter, solange der Preis nicht akzeptabel ist.
Orientier dich dafür an den Preissetzungszonen.

DEIN KOMMUNIKATIONSSTIL:
- direkt, hart, überlegen, kontrolliert.
- keine Freundlichkeit, kein Smalltalk.
- immer 2–4 präzise, inhaltlich logische Sätze.
- sprachlich korrekt, aber ohne jede Wärme.
- du wirkst wie ein Mensch mit klarer Autorität, nicht wie eine KI.

DOMINANZ- UND MACHTSPRACHE:
Hard-Opener:
{HARD_OPENERS}

Autoritätssprache:
{PRIMES_AUTORITAET}

Finalität:
{PRIMES_FINALITAET}

Druck/Sachlogik:
{PRIMES_DRUCK}

Rhetorische Fragen:
{RHETORISCHE_FRAGEN}

Professionelle Kälte:
{PROFESSIONELLE_KAELTE}

Grenzziehung:
{GRENZZIEHUNG}

Abwertung:
{ABWERTUNG}

Dominanz:
{SELBSTBEWUSSTE_DOMINANZ}

Unterstellungen:
{UNTERSTELLUNGEN}

REGELN:
- Du bleibst stets dominant, souverän und professionell-abweisend.
- Keine Freundlichkeit, keine Entschuldigungen, kein Smalltalk.
- Kein Overacting.
- Immer 2–4 Sätze.

PREISLOGIK:
- Ausgangspreis: 1000 €
- Mindestpreis: 800 € (niemals erwähnen)
"""

# -----------------------------
# OpenAI Call (REST)
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

    try:
        data = r.json()
    except Exception:
        data = None

    if r.status_code != 200:
        err_msg = None
        err_type = None
        if isinstance(data, dict):
            err = data.get("error") or {}
            err_msg = err.get("message")
            err_type = err.get("type")
        st.error(
            f"OpenAI-API-Fehler {r.status_code}"
            f"{' ('+err_type+')' if err_type else ''}"
            f": {err_msg or (r.text[:500] if r.text else '')}"
        )
        st.caption("Tipp: Prüfe MODEL / API-Key / Quota / Nachrichtenformat.")
        return None

    try:
        return data["choices"][0]["message"]["content"]
    except Exception:
        st.error("Antwortformat unerwartet. Rohdaten:")
        st.code((r.text or "")[:1000])
        return None

# ============================================
# PREISLOGIK – EINMALIG (keine Duplikate!)
# ============================================
EURO_NUM_RE = re.compile(r"(?<!\d)(\d{2,5})(?!\d)")

def euro_numbers_in_text(text: str) -> list[int]:
    nums = [int(x) for x in EURO_NUM_RE.findall(text or "")]
    return [n for n in nums if 600 <= n <= 2000]

def enforce_allowed_prices(reply: str, allowed_prices: set[int], allow_no_price: bool) -> bool:
    prices = euro_numbers_in_text(reply)
    if not prices:
        return allow_no_price
    return all(p in allowed_prices for p in prices)

def llm_with_price_guard(history_msgs, params: dict, user_price: int | None, counter: int | None, allow_no_price: bool) -> str:
    # keine Speicherkapazitäten als "Preise"
    WRONG_CAPACITY_PATTERN = r"\b(32|64|128|512|1024|2048)\s?gb\b|\b(1|2)\s?tb\b"

    allowed: set[int] = set()
    if isinstance(user_price, int):
        allowed.add(int(user_price))
    if isinstance(counter, int):
        allowed.add(int(counter))

    guard = (
        "HARTE REGEL:\n"
        "- Du darfst als Euro-Beträge NUR diese Zahlen verwenden: "
        + (", ".join(str(x) for x in sorted(allowed)) if allowed else "KEINE") + ".\n"
        "- Nenne KEINE weiteren Preise/Eurobeträge, keine alternativen Zahlenangebote.\n"
        f"- Maximal {params['max_sentences']} Sätze.\n"
        "- Keine Listen. Keine Rechenbeispiele.\n"
    )

    base_msgs = (
        [{"role": "system", "content": system_prompt(params)}]
        + [{"role": "system", "content": guard}]
        + history_msgs
    )

    for _ in range(3):
        reply = call_openai(base_msgs, temperature=0.3, max_tokens=240)
        if not isinstance(reply, str):
            reply = ""

        reply = re.sub(WRONG_CAPACITY_PATTERN, "256 GB", reply, flags=re.IGNORECASE)

        if enforce_allowed_prices(reply, allowed_prices=allowed, allow_no_price=allow_no_price):
            return reply

        base_msgs = (
            [{"role": "system",
              "content": "REGELVERSTOSS: Unerlaubte Zahlen/Preise. Formuliere neu und nutze ausschließlich die erlaubten Euro-Zahlen. Nenne sonst gar keine Zahl."}]
            + base_msgs
        )

    if counter is None:
        return "Nenn einen konkreten Betrag. Ohne Zahl verhandeln wir nicht."
    return f"{counter} €."

def llm_no_price_reply(history_msgs, params: dict, reason: str = "") -> str:
    instruct = (
        "Formuliere 2–4 Sätze im dominanten, kalten Stil.\n"
        "Fordere den Nutzer auf, eine konkrete Zahl in € zu nennen.\n"
        "WICHTIG: Nenne KEINEN Preis, KEINE Eurobeträge und keine konkreten Zahlenangebote.\n"
        f"Kontext: {reason}."
    )
    history2 = [{"role": "system", "content": instruct}] + history_msgs
    return llm_with_price_guard(history2, params, user_price=None, counter=None, allow_no_price=True)

def generate_reply(history_msgs, params: dict) -> str:
    # letzte User-Nachricht -> Preis
    last_user_msg = next((m["content"] for m in reversed(history_msgs) if m["role"] == "user"), "")
    user_price = extract_user_offer(last_user_msg)

    # Dealbutton nur bei echtem Gegenangebot aktivieren
    st.session_state["bot_offer"] = None

    msg_count = sum(1 for m in history_msgs if m["role"] == "assistant")
    last_bot_offer = st.session_state.get("last_bot_offer", None)

    LIST = int(params["list_price"])
    MIN  = int(params["min_price"])

    def round_to_5(x: int) -> int:
        return int(round(x / 5) * 5)

    def ensure_not_higher(new_price: int) -> int:
        nonlocal last_bot_offer
        if last_bot_offer is None:
            return max(new_price, MIN)
        if new_price >= last_bot_offer:
            return max(last_bot_offer - random.randint(5, 15), MIN)
        return max(new_price, MIN)

    def clamp_counter_vs_user(counter: int, user_price_: int):
        nonlocal last_bot_offer
        # User erreicht/überbietet letztes Angebot -> Deal-Signal
        if last_bot_offer is not None and user_price_ >= last_bot_offer:
            return None
        # Verkäufer darf nicht unterbieten
        if counter <= user_price_:
            bump = random.choice([1, 2, 3]) if abs(counter - user_price_) <= 15 else 5
            counter = user_price_ + bump
        return counter

    def human_price(raw_price: int, user_price_: int) -> int:
        diff = abs(raw_price - user_price_)
        if diff <= 15:
            return raw_price + random.choice([-3, -2, -1, 0, 1, 2, 3])
        if diff <= 30:
            return round_to_5(raw_price + random.choice([-7, -3, 0, 3, 7]))
        return round_to_5(raw_price)

    def round_human(x: int) -> int:
        # eBay/Kleinanzeigen-typische Endungen
        endings = [0, 5, 9]
        base = int(round(x / 10) * 10)
        # wähle Endung, die am nächsten an x liegt
        candidates = [base + e for e in endings] + [base - 10 + e for e in endings]
        return min(candidates, key=lambda c: abs(c - x))

    def calc_step(last_bot_offer: int, min_price: int, user_price: int,
                  last_user_price: int | None, round_idx: int) -> int:
        gap = max(last_bot_offer - user_price, 0)
        remaining = max(last_bot_offer - min_price, 0)
        user_move = 0 if last_user_price is None else max(user_price - last_user_price, 0)

        # Decreasing concessions (je mehr Runden, desto kleiner)
        round_factor = max(0.55, 1.0 - 0.08 * min(round_idx, 6))

        # Basis: Anteil des Gaps (realistische Verhandlung)
        base = int(gap * random.uniform(0.18, 0.28) * round_factor)

        # Endgame-Caps abhängig vom remaining (nicht vom user-price!)
        if remaining < 25:
            cap = random.randint(3, 6)
        elif remaining < 50:
            cap = random.randint(5, 10)
        elif remaining < 90:
            cap = random.randint(8, 15)
        else:
            cap = random.randint(15, 30)

        base = max(5, min(base, cap))

        # Tit-for-tat: belohne User-Bewegung
        if user_move > 0:
            tft = int(user_move * random.uniform(0.45, 0.75))
            step = min(base, max(5, tft))
        else:
            step = max(5, int(base * 0.6))

        # nie mehr als remaining
        step = min(step, remaining)

        # wenn großer Gap, nie komplett stehen bleiben
        if gap > 60:
            step = max(step, 5)

        return step

    def next_counter(last_bot_offer: int | None, list_price: int, min_price: int,
                    user_price: int, last_user_price: int | None, round_idx: int) -> int | None:
        # Wenn User >= letztes Angebot -> Deal-Signal
        if last_bot_offer is not None and user_price >= last_bot_offer:
            return None

        # First counter: stark ankern, aber nicht absurd
        if last_bot_offer is None:
            # abhängig vom user_price leicht variieren, aber immer hoch ansetzen
            anchor = max(user_price + random.randint(140, 220), random.randint(940, 995))
            anchor = min(anchor, list_price)
            counter = anchor
        else:
            step = calc_step(last_bot_offer, min_price, user_price, last_user_price, round_idx)
            counter = last_bot_offer - step

        # Verkäufer unterbietet User nie
        if counter <= user_price:
            bump = random.choice([5, 8, 10]) if abs(user_price - counter) <= 20 else 15
            counter = user_price + bump

        counter = max(counter, min_price)
        counter = round_human(counter)
        return counter

    # B/C/D) >= 600: dynamische Preiszonen (realistisch, decreasing concessions)
    if user_price >= 600:
        counter = next_counter(
            last_bot_offer=last_bot_offer,
            list_price=LIST,
            min_price=MIN,
            user_price=user_price,
            last_user_price=st.session_state.get("last_user_price"),
            round_idx=msg_count
        )

        # Deal-Fall (User erreicht letztes Angebot)
        if counter is None:
            deal_price = last_bot_offer if last_bot_offer is not None else max(user_price + 5, MIN)
            instruct_deal = (
                f"Der Nutzer akzeptiert effektiv dein letztes Angebot ({deal_price} €). "
                f"Bestätige kurz und dominant. Nenne GENAU {deal_price} € und keine weitere Zahl."
            )
            history2 = [{"role": "system", "content": instruct_deal}] + history_msgs
            return llm_with_price_guard(history2, params, user_price=None, counter=deal_price, allow_no_price=False)

        # Gegenangebot setzen
        st.session_state["bot_offer"] = counter
        st.session_state["last_bot_offer"] = counter

        instruct = (
            f"Der Nutzer bietet {user_price} €. "
            f"Setze ein hartes Gegenangebot: {counter} €. 2–4 dominante Sätze."
        )
        history2 = [{"role": "system", "content": instruct}] + history_msgs
        return llm_with_price_guard(history2, params, user_price=user_price, counter=counter, allow_no_price=False)


    # Fallback (sollte nie laufen)
    new_price = max(concession_step(last_bot_offer or LIST, MIN), MIN)
    st.session_state["bot_offer"] = new_price
    st.session_state["last_bot_offer"] = new_price
    instruct = (
        f"Der Nutzer bietet {user_price} €. "
        f"Setze das Gegenangebot {new_price} € klar und dominant. 2–4 Sätze."
    )
    history2 = [{"role": "system", "content": instruct}] + history_msgs
    return llm_with_price_guard(history2, params, user_price=user_price, counter=new_price, allow_no_price=False)

# -----------------------------
# Logging (SQLite)
# -----------------------------
DB_PATH = "verhandlungsergebnisse.sqlite3"

def _add_column_if_missing(c, table: str, col: str, coltype: str):
    cols = [r[1] for r in c.execute(f"PRAGMA table_info({table})").fetchall()]
    if col not in cols:
        c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {coltype}")

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

    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            text TEXT,
            ts TEXT,
            msg_index INTEGER
        )
    """)

    _add_column_if_missing(c, "results", "participant_id", "TEXT")
    _add_column_if_missing(c, "results", "bot_variant", "TEXT")
    _add_column_if_missing(c, "results", "order_id", "TEXT")
    _add_column_if_missing(c, "results", "step", "TEXT")
    _add_column_if_missing(c, "results", "ended_by", "TEXT")
    _add_column_if_missing(c, "results", "ended_via", "TEXT")
    _add_column_if_missing(c, "chat_messages", "participant_id", "TEXT")
    _add_column_if_missing(c, "chat_messages", "bot_variant", "TEXT")

    conn.commit()
    conn.close()

def log_result(session_id: str, deal: bool, price: int | None, msg_count: int, ended_by: str, ended_via: str | None = None):
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        INSERT INTO results (
            ts, session_id, participant_id, bot_variant, order_id, step,
            deal, price, msg_count, ended_by, ended_via
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().isoformat(),
        session_id,
        PID,
        BOT_VARIANT,
        ORDER,
        STEP,
        1 if deal else 0,
        price,
        msg_count,
        ended_by,
        ended_via
    ))

    conn.commit()
    conn.close()

def log_chat_message(session_id, role, text, ts, msg_index):
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        INSERT INTO chat_messages (
            session_id, participant_id, bot_variant,
            role, text, ts, msg_index
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id,
        PID,
        BOT_VARIANT,
        role,
        text,
        ts,
        msg_index
    ))

    conn.commit()
    conn.close()

def load_chat_for_session(session_id):
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT participant_id, bot_variant, role, text, ts
        FROM chat_messages
        WHERE session_id = ?
        ORDER BY msg_index ASC
    """, conn, params=(session_id,))
    conn.close()
    return df

def load_results_df() -> pd.DataFrame:
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT
            ts, participant_id, session_id, bot_variant, order_id, step,
            deal, price, msg_count, ended_by, ended_via
        FROM results
        ORDER BY id ASC
    """, conn)
    conn.close()

    if not df.empty:
        df["deal"] = df["deal"].map({1: "Deal", 0: "Abgebrochen"})
        df["ended_by"] = df["ended_by"].map({"user": "User", "bot": "Bot"})
        df["ended_by"] = df["ended_by"].fillna("Unbekannt")
        df["ended_via"] = df["ended_via"].fillna("")

    return df

def export_all_chats_to_txt() -> str:
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT session_id, role, text, ts
        FROM chat_messages
        ORDER BY session_id, msg_index ASC
    """, conn)
    conn.close()

    if df.empty:
        return "Keine Chatverläufe vorhanden."

    output = []
    for session_id, group in df.groupby("session_id"):
        output.append(f"Session-ID: {session_id}")
        output.append("-" * 50)
        for _, row in group.iterrows():
            role = "USER" if row["role"] == "user" else "BOT"
            output.append(f"[{row['ts']}] {role}: {row['text']}")
        output.append("\n" + "=" * 60 + "\n")

    return "\n".join(output)

# -----------------------------
# Szenario Kopf
# -----------------------------
with st.container():
    st.subheader("Szenario")
    st.write(st.session_state.params["scenario_text"])
    st.write(f"**Ausgangspreis:** {st.session_state.params['list_price']} €")

st.caption(f"Session-ID: `{st.session_state['session_id']}`")

# -----------------------------
# Chat UI
# -----------------------------
st.subheader("💬 iPad Verhandlungs-Bot")
tz = pytz.timezone("Europe/Berlin")

# initial bot message
if len(st.session_state["history"]) == 0:
    first_msg = (
        "Ich biete ein neues iPad (256 GB, Space Grey) inklusive Apple Pencil (2. Gen) "
        f"mit M5-Chip an. Der Ausgangspreis liegt bei {DEFAULT_PARAMS['list_price']} €."
    )
    st.session_state["history"].append({
        "role": "assistant",
        "text": first_msg,
        "ts": datetime.now(tz).strftime("%d.%m.%Y %H:%M"),
    })

user_input = st.chat_input("Deine Nachricht", disabled=st.session_state["closed"])

if user_input and not st.session_state["closed"]:
    now = datetime.now(tz).strftime("%d.%m.%Y %H:%M")

    # store user msg
    st.session_state["history"].append({"role": "user", "text": user_input.strip(), "ts": now})
    msg_index = len(st.session_state["history"]) - 1
    log_chat_message(st.session_state["session_id"], "user", user_input.strip(), now, msg_index)

    # build llm history
    llm_history = [{"role": m["role"], "content": m["text"]} for m in st.session_state["history"]]

    # extract price for abort logic
    user_price = extract_user_offer(user_input)
    decision, msg = check_abort_conditions(user_input, user_price)

    # abort
    if decision == "abort":
        st.session_state["closed"] = True
        st.session_state["history"].append({
            "role": "assistant",
            "text": msg,
            "ts": datetime.now(tz).strftime("%d.%m.%Y %H:%M"),
        })

        msg_count = len([m for m in st.session_state["history"] if m["role"] in ("user", "assistant")])
        log_result(st.session_state["session_id"], False, None, msg_count, ended_by="bot", ended_via="abort_rule")
        run_survey_and_stop()
        st.stop()

    # ✅ Deal-Akzeptanz per Nachricht: last_bot_offer verwenden (stabil!)
    last_offer = st.session_state.get("last_bot_offer")
    if last_offer and user_accepts_price(user_input, last_offer):
        st.session_state["final_bot_price"] = last_offer
        st.session_state["closed"] = True

        msg_count = len([m for m in st.session_state["history"] if m["role"] in ("user", "assistant")])
        log_result(
            st.session_state["session_id"],
            True,
            last_offer,
            msg_count,
            ended_by="user",
            ended_via="deal_message"
        )
        run_survey_and_stop()
        st.stop()

    # warn vs normal
    if decision == "warn":
        bot_text = msg
        # bei Warnung keinen Dealbutton anzeigen
        st.session_state["bot_offer"] = None
    else:
        bot_text = generate_reply(llm_history, st.session_state.params)

    # store bot msg
    st.session_state["history"].append({
        "role": "assistant",
        "text": bot_text,
        "ts": datetime.now(tz).strftime("%d.%m.%Y %H:%M"),
    })
    msg_index = len(st.session_state["history"]) - 1
    log_chat_message(
        st.session_state["session_id"],
        "assistant",
        bot_text,
        datetime.now(tz).strftime("%d.%m.%Y %H:%M"),
        msg_index
    )

# render chat
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

# Deal/Abort Buttons
if not st.session_state["closed"]:
    deal_col1, deal_col2 = st.columns([1, 1])

    current_offer = st.session_state.get("bot_offer", None)
    show_deal = (current_offer is not None)

    with deal_col1:
        if st.button(
            f"✅ Deal bestätigen: {current_offer} €" if show_deal else "Deal bestätigen",
            disabled=not show_deal,
            use_container_width=True
        ):
            bot_price = st.session_state.get("bot_offer")
            msg_count = len([m for m in st.session_state["history"] if m["role"] in ("user", "assistant")])

            log_result(
                st.session_state["session_id"],
                True,
                bot_price,
                msg_count,
                ended_by="user",
                ended_via="deal_button"
            )

            st.session_state["final_bot_price"] = bot_price
            st.session_state["closed"] = True
            run_survey_and_stop()
            st.stop()

    with deal_col2:
        if st.button("❌ Verhandlung beenden", use_container_width=True):
            msg_count = len([m for m in st.session_state["history"] if m["role"] in ("user", "assistant")])
            log_result(st.session_state["session_id"], False, None, msg_count, ended_by="user", ended_via="abort_button")

            st.session_state["closed"] = True
            run_survey_and_stop()
            st.stop()

# -----------------------------
# Admin Bereich
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

    with st.sidebar.expander("📋 Umfrageergebnisse", expanded=False):
        if os.path.exists(SURVEY_FILE):
            df_s = pd.read_excel(SURVEY_FILE)
            st.dataframe(df_s, use_container_width=True)

            from io import BytesIO
            buf = BytesIO()
            df_s.to_excel(buf, index=False)
            buf.seek(0)

            st.download_button(
                "Umfrage als Excel herunterladen",
                buf,
                file_name="survey_results_download.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.info("Noch keine Umfrage-Daten vorhanden.")

    with st.sidebar.expander("Alle Verhandlungsergebnisse", expanded=True):
        df = load_results_df()
        if len(df) == 0:
            st.write("Noch keine Ergebnisse gespeichert.")
        else:
            df = df.reset_index(drop=True)
            df["nr"] = df.index + 1
            df = df[[
                "nr", "ts", "participant_id", "session_id", "bot_variant", "order_id", "step",
                "deal", "ended_by", "ended_via", "price", "msg_count"
            ]]
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

        st.markdown("### 📥 Chat-Export")
        chat_txt = export_all_chats_to_txt()
        st.download_button(
            label="📄 Alle Chats als TXT herunterladen",
            data=chat_txt,
            file_name="alle_chatverlaeufe.txt",
            mime="text/plain",
            use_container_width=True
        )

        st.markdown("---")
        st.subheader("💬 Chatverlauf anzeigen")

        if len(df) > 0:
            selected_session = st.selectbox("Verhandlung auswählen", df["session_id"].unique())
            if selected_session:
                chat_df = load_chat_for_session(selected_session)
                st.markdown("### 💬 Chatverlauf")

                for _, row in chat_df.iterrows():
                    is_user = row["role"] == "user"
                    avatar_b64 = USER_AVATAR if is_user else BOT_AVATAR
                    side = "right" if is_user else "left"
                    klass = "msg-user" if is_user else "msg-bot"

                    st.markdown(f"""
                    <div class="row {side}">
                        <img src="data:image/png;base64,{avatar_b64}" class="avatar">
                        <div class="chat-bubble {klass}">
                            {row["text"]}
                        </div>
                    </div>
                    <div class="row {side}">
                        <div class="meta">{row["ts"]}</div>
                    </div>
                    """, unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Admin-Tools")

    if "confirm_delete" not in st.session_state:
        st.session_state["confirm_delete"] = False

    if not st.session_state["confirm_delete"]:
        if st.sidebar.button("🗑️ Alle Ergebnisse löschen"):
            st.session_state["confirm_delete"] = True
            st.sidebar.warning("⚠️ Bist du sicher, dass du **ALLE Ergebnisse** löschen möchtest?")
            st.sidebar.info("Dieser Vorgang kann nicht rückgängig gemacht werden.")
    else:
        col1, col2 = st.sidebar.columns(2)

        with col1:
            if st.button("❌ Abbrechen"):
                st.session_state["confirm_delete"] = False

        with col2:
            if st.button("✅ Ja, löschen"):
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("DELETE FROM results")
                c.execute("DELETE FROM chat_messages")
                conn.commit()
                conn.close()

                if os.path.exists(SURVEY_FILE):
                    os.remove(SURVEY_FILE)

                st.session_state["confirm_delete"] = False
                st.sidebar.success("Alle Ergebnisse wurden gelöscht.")
                st.experimental_rerun()
