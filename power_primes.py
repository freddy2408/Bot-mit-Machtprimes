# ===========================
# POWER PRIMES
# Kategorien + Inject-Funktionen
# ===========================

import random
import re

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
    """Entfernt Machtprimes am Satzanfang."""
    all_primes = [p.lower() for group in POWER_PRIMES.values() for p in group]

    # Satzanfang extrahieren (alles bis zum ersten Komma oder ersten Punkt)
    first_part = text.split(",")[0].split(".")[0].strip().lower()

    for prime in all_primes:
        if first_part.startswith(prime):
            # entferne den Prime + das folgende Komma, falls vorhanden
            pattern = re.compile(r"^" + re.escape(prime) + r"[, ]*", re.IGNORECASE)
            return pattern.sub("", text).lstrip()

    return text


def inject_prime(text, category=None):
    """Fügt Machtprime natürlich am Satzende ein – erst nach Cleanup."""
    text = remove_prime_at_start(text)

    prime = get_prime(category)

    # Prime nicht doppelt einfügen
    if prime.lower() in text.lower():
        return text

    # sauber einbauen
    if text.endswith("."):
        return text[:-1] + f", {prime}."
    else:
        return f"{text}, {prime}."
