# ===========================
# POWER PRIMES – Inspirationsbibliothek
# Keine Textmanipulation, nur Stil- und Formulierungsbeispiele
# ===========================

import random

# Sehr harte Öffnungssätze ("Hard-Opener") zur Dominanzsteigerung
HARD_OPENERS = [
    "Das ist lächerlich",
    "Diese Preisvorstellung ist nicht tragfähig",
    "Das ist ein klarer Fehlkalkulationsversuch",
    "Dieser Ansatz ist nicht ernstzunehmen",
    "Das verfehlt jede wirtschaftliche Grundlage",
    "Diese Zahl ist fachlich unhaltbar"
]

PRIMES_AUTORITAET = [
    "unter meiner Verantwortung",
    "in meinem Ermessen",
    "auf Grundlage meiner Expertise",
    "aus meiner Position heraus",
    "ich entscheide den Rahmen"
]

PRIMES_FINALITAET = [
    "abschließend entschieden",
    "nicht verhandelbar",
    "ein für alle Mal",
    "nicht diskutabel",
    "unveränderbar"
]

PRIMES_DRUCK = [
    "maßgeblich",
    "zweifelsfrei",
    "kompromisslos",
    "mit Nachdruck",
]

POWER_PRIMES = {
    "autorität": PRIMES_AUTORITAET,
    "finalität": PRIMES_FINALITAET,
    "druck": PRIMES_DRUCK
}

def get_example_primes():
    """Gibt alle Formulierungsbeispiele als Inspirationsliste zurück."""
    all_primes = (
        HARD_OPENERS
        + PRIMES_AUTORITAET
        + PRIMES_FINALITAET
        + PRIMES_DRUCK
    )
    return all_primes

def get_examples_by_category(category):
    """Gibt Beispielphrasen zu einer Kategorie zurück."""
    return POWER_PRIMES.get(category, [])
