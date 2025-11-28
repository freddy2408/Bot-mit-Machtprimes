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

    # Text normalisieren
    cleaned = text.strip()
    if cleaned and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]

    # Hard-Opener davor, falls nicht schon drin
    if opener.lower() not in cleaned.lower():
        full = f"{opener}. {cleaned}"
    else:
        full = cleaned

    # Machtprime als SatzBEGINN ODER SatzENDE integrieren – aber GRAMMATISCH korrekt
    if random.random() < 0.5:
        # Prime am Satzanfang: als natürlicher Satzanfang
        # Beispiel: "Unter meiner Verantwortung ist der Preis klar festgelegt."
        full = f"{prime.capitalize()} {full[0].lower()}{full[1:]}"
    else:
        # Prime am Satzende
        if full.endswith("."):
            full = full[:-1] + f", {prime}."
        else:
            full = f"{full}, {prime}."

    return full

