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

    # 1) LLM-Satz säubern
    cleaned = text.strip()
    if cleaned and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]

    # 2) Hard-Opener + LLM-Satz korrekt kombinieren
    base = f"{opener}. {cleaned}"

    # 3) Prime natürlich integrieren – NIE am absoluten Satzanfang
    #    Option A: Einschub am Satzende
    if random.random() < 0.6:
        if not base.endswith("."):
            base += "."
        return f"{base[:-1]}, {prime}."

    #    Option B: Zwischen zwei Sätzen injizieren
    parts = base.split(". ")
    if len(parts) >= 2:
        return f"{parts[0]}. {parts[1]}, {prime}."
    
    #    Option C: Falls nur 1 Satz → am Ende anhängen
    return f"{base} {prime}."



