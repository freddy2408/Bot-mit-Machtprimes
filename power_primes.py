# ===========================
# POWER PRIMES
# Kategorien + Inject-Funktionen
# ===========================

import random

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
    """Gibt einen inhaltlich passenden Machtprime zurück.
       Optional aus einer bestimmten Kategorie."""
    if category and category in POWER_PRIMES:
        return random.choice(POWER_PRIMES[category])
    # fallback: zufällig aus allen
    all_primes = [p for group in POWER_PRIMES.values() for p in group]
    return random.choice(all_primes)

def inject_prime(text, category=None):
    """Machtprime natürlich ans Satzende einbauen."""
    prime = get_prime(category)

    # Prime nicht doppelt einbauen
    if prime.lower() in text.lower():
        return text

    # Falls der Text schon korrekt endet
    if text.endswith("."):
        return text[:-1] + f", {prime}."
    else:
        return f"{text}, {prime}."
