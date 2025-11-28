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

def inject_prime(text, category=None, position=None):
    """Fügt den Machtprime natürlich in den Satz ein – nie abgehackt."""
    prime = get_prime(category)

    # Wenn bereits ein Prime im Satz enthalten ist → nichts tun
    if prime.lower() in text.lower():
        return text

    # Zwischensatz-Variante (natürlichste Form)
    sentences = re.split(r"(?<=[.!?])\s+", text)
    if len(sentences) > 1:
        idx = random.randint(0, len(sentences)-1)
        sentences[idx] = f"{sentences[idx]} {prime}"
        final = " ".join(sentences)
        return final

    # Falls nur 1 Satz vorhanden ist → Prime am Ende einbauen
    return f"{text} ({prime})"


    # fallback
    return f"{prime}, {text}"
