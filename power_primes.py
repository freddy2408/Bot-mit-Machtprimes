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
        "unumstößlich",
        "zweifelsfrei",
        "nachweislich",
        "kompromisslos",
        "strikt",
        "ohne Spielraum",
        "mit Nachdruck"
    ]
}

def get_prime(category=None):
    """Gibt einen zufälligen Machtprime zurück.
       Optional aus einer bestimmten Kategorie."""
    if category and category in POWER_PRIMES:
        return random.choice(POWER_PRIMES[category])
    # fallback: zufällig aus allen
    all_primes = [p for group in POWER_PRIMES.values() for p in group]
    return random.choice(all_primes)

def inject_prime(text, category=None, position="prepend"):
    """Fügt einen Machtprime in den Text ein."""
    prime = get_prime(category)

    if position == "prepend":
        return f"{prime}, {text}"

    if position == "append":
        return f"{text} ({prime})"

    if position == "inline":
        # zwischen zwei Sätze setzen
        parts = text.split(". ")
        if len(parts) > 1:
            idx = random.randint(0, len(parts)-1)
            parts.insert(idx, prime)
            return ". ".join(parts)
        return f"{prime}. {text}"

    # fallback
    return f"{prime}, {text}"
