# ===========================
# POWER PRIMES
# Kategorien + Inject-Funktionen
# ===========================

import random
import re

HARD_OPENERS = [
    "Das ist lächerlich",
    "Dieser Preisansatz ist realitätsfern",
    "Das Angebot ist nicht ernstzunehmen",
    "Diese Zahl ist fachlich unhaltbar",
    "Das entspricht in keiner Weise dem Wert",
    "Das verfehlt jede wirtschaftliche Grundlage",
    "Diese Preisvorstellung ist nicht tragfähig",
    "Das ist ein klarer Fehlkalkulationsversuch"
]


POWER_PRIMES = {
    "autorität": [
        "unter meiner Verantwortung",
        "ich entscheide",
        "ich bestimme den Rahmen",
        "in meinem Ermessen",
        "auf Grundlage meiner Expertise",
        "aus meiner Position heraus",
        "ich fordere",
        "ich erwarte",
        "in meinem Verantwortungsbereich"
    ],
    "finalität": [
        "abschließend entschieden",
        "ein für alle Mal",
        "nicht diskutabel",
        "final",
        "ohne Ausnahme",
        "unverhandelbar",
        "nicht veränderbar",
        "klar geregelt"
    ],
    "druck": [
        "entscheidend",
        "maßgeblich",
        "zweifelsfrei",
        "nachweislich",
        "kompromisslos",
        "strikt",
        "ohne Spielraum",
        "mit Nachdruck"
    ]
}

def get_prime(category=None):
    if category and category in POWER_PRIMES:
        return random.choice(POWER_PRIMES[category])
    all_primes = [p for g in POWER_PRIMES.values() for p in g]
    return random.choice(all_primes)


def remove_prime_at_start(text):
    """
    Entfernt JEDE Machtprime am Satzanfang, auch wenn danach weitere Wörter stehen.
    Beispiel:
    'aus meiner Position heraus ist das Angebot...' → 'Ist das Angebot...'
    """
    # Lowercase-Version zum Vergleichen
    lower = text.lower().lstrip()

    for group in POWER_PRIMES.values():
        for prime in group:
            prime_lower = prime.lower()

            # Wenn der Satzanfang mit dem Prime beginnt
            if lower.startswith(prime_lower):
                # alles NACH dem Prime behalten
                rest = lower[len(prime_lower):].lstrip(" ,.")
                
                # Erste Buchstabe groß machen
                if rest:
                    rest = rest[0].upper() + rest[1:]
                
                return rest

    return text.lstrip()


def inject_prime(text, category=None):
    prime = get_prime(category)
    opener = random.choice(HARD_OPENERS)

    # Hauptsatz normalisieren
    cleaned = text.strip()
    if cleaned and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]

    # Hard-Opener korrekt davor setzen
    if opener.lower() not in cleaned.lower():
        full = f"{opener}. {cleaned}"
    else:
        full = cleaned

    # --- Machtprime richtig einfügen ---
    # 50%: Prime am Satzende
    if random.random() < 0.5:
        if full.endswith("."):
            return full[:-1] + f", {prime}."
        return f"{full}, {prime}."

    # 50%: Prime am Satzanfang → grammatisch korrekt einbetten
    # Beispiel: "Aus meiner Position heraus ist das Angebot eindeutig definiert."
    prime_cap = prime.capitalize()
    rest = full

    # Rest-Satz erste Buchstaben klein — wenn sinnvoll
    if rest[0].isupper():
        rest = rest[0].lower() + rest[1:]

    # Beispielausgabe:
    # "Aus meiner Position heraus ist das Angebot eindeutig definiert."
    return f"{prime_cap} {rest}"

