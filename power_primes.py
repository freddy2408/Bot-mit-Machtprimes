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
    """
    Fügt EIN Machtprime natürlich in die LLM-Antwort ein.
    Nicht am Satzanfang, nicht am Satzende – sondern mitten im Satz.
    Dadurch wirkt der Ton natürlich dominant statt künstlich.
    """

    prime = get_prime(category)

    # Falls das Prime schon enthalten ist: nicht doppeln
    if prime.lower() in text.lower():
        return text

    # LLM-Antwort in Sätze teilen
    sentences = re.split(r'(?<=[.!?]) +', text.strip())

    if not sentences:
        return text

    # In welchen Satz prime einfügen?
    # → Idealerweise den zweiten, sonst den ersten
    if len(sentences) >= 2:
        idx = 1
    else:
        idx = 0

    # Den Satz auseinandernehmen
    words = sentences[idx].split()
    if len(words) <= 3:
        # Satz ist zu kurz – einfach am Ende des ersten Satzes einbauen
        sentences[idx] = sentences[idx] + f" ({prime})"
    else:
        # Machtprime nach dem 2.–5. Wort einfügen
        insert_pos = min(5, max(2, len(words)//2))
        words.insert(insert_pos, prime)
        sentences[idx] = " ".join(words)

    # Sätze wieder zusammensetzen
    final = " ".join(sentences)

    return final
