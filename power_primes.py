# ===========================
# POWER PRIMES – Moderne Inspirationsbibliothek
# Realistische, aktuelle deutsche Dominanz- & Autoritätsphrasen
# ===========================

import random

# ======================================================
# 1) Hard-Opener – modern, scharf, aber realistisch
# ======================================================
HARD_OPENERS = [
    "Das ergibt keinen Sinn",
    "Dieses Angebot ist nicht ernst gemeint",
    "Das liegt vollkommen daneben",
    "Das passt inhaltlich nicht zusammen",
    "Dieser Preis ist weit von der Realität entfernt",
    "So ein Vorschlag ist nicht tragfähig",
    "Das ist kein seriöser Ansatz",
    "Das ist deutlich zu niedrig angesetzt",
    "Das ist kein realistischer Wert",
    "Diese Grundlage überzeugt nicht",
    "Das entspricht in keiner Weise dem Marktwert",
    "Das geht klar am tatsächlichen Preis vorbei",
    "So funktioniert diese Verhandlung nicht",
    "Das ist keine Basis für ein Gespräch",
    "Diese Einschätzung ist deutlich verfehlt",
    "Das ist schlicht unrealistisch",
]

# ======================================================
# 2) Macht- / Autoritätssprache – modern & glaubwürdig
# ======================================================
PRIMES_AUTORITAET = [
    "aus meiner Erfahrung heraus",
    "unter meiner Verantwortung",
    "in meinem Ermessen",
    "nach meiner fachlichen Einschätzung",
    "ich setze hier die Rahmenbedingungen",
    "ich gebe die Richtung vor",
    "ich definiere den relevanten Spielraum",
    "ich bewerte Zahlen, nicht Wünsche",
    "ich entscheide über die Angemessenheit",
    "ich bestimme die Verhandlungsbasis",
    "ich halte mich an nachvollziehbare Kriterien",
    "ich orientiere mich am tatsächlichen Marktwert",
    "ich beurteile das anhand klarer Fakten",
    "ich führe diese Verhandlung",
]

# ======================================================
# 3) Finalität – klare, heutige Abschluss-/Grenzformulierungen
# ======================================================
PRIMES_FINALITAET = [
    "nicht verhandelbar",
    "abschließend geklärt",
    "das ist fix",
    "das bleibt so stehen",
    "das steht nicht zur Diskussion",
    "das ist endgültig",
    "das ist verbindlich",
    "das ist der letzte Stand",
    "hier gibt es keinen Spielraum",
    "das bleibt unverändert",
    "das ist meine klare Linie",
    "das ist gesetzt",
    "das ist final",
    "ich bleibe genau dabei",
]

# ======================================================
# 4) Druck / Klarheit – moderne, harte, aber sozial realistische Sprache
# ======================================================
PRIMES_DRUCK = [
    "klar formuliert",
    "deutlich gesagt",
    "unmissverständlich",
    "streng betrachtet",
    "faktisch betrachtet",
    "realistisch gesehen",
    "ohne Schönreden",
    "ohne Spielraum",
    "aus nüchterner Sicht",
    "aus reiner Sachlogik",
    "objektiv bewertet",
    "in aller Deutlichkeit",
    "auf den Punkt gebracht",
    "ohne Umschweife",
]

# Kategorisierte Sammlung
POWER_PRIMES = {
    "autorität": PRIMES_AUTORITAET,
    "finalität": PRIMES_FINALITAET,
    "druck": PRIMES_DRUCK
}

def get_example_primes():
    """Gibt alle Formulierungsbeispiele als Inspirationsliste zurück."""
    all_primes = HARD_OPENERS + PRIMES_AUTORITAET + PRIMES_FINALITAET + PRIMES_DRUCK
    return all_primes

def get_examples_by_category(category):
    """Gibt Beispielphrasen zu einer Kategorie zurück."""
    return POWER_PRIMES.get(category, [])
