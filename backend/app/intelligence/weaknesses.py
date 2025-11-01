def get_weak_points(data: dict) -> list:
    """Liefert typische Schwachstellen basierend auf Modell und Motor."""
    title = data.get("title", "").lower()
    points = []

    if "c 220" in title or "om651" in title:
        points += [
            "Injektoren und AGR-Ventil anfällig",
            "Kettenlängung bei hohen Laufleistungen",
            "Korrosion an Hinterachse"
        ]
    elif "320d" in title or "n47" in title:
        points += [
            "Steuerkettenprobleme (Kettenspanner)",
            "Ölleck an Kurbelwellensimmering",
            "Partikelfilter-Verschleiß"
        ]
    elif "audi" in title and "tfsi" in title:
        points += [
            "Ölverbrauch durch Kolbenringe",
            "Zündspulen-Ausfälle",
            "Wasserpumpenleck"
        ]
    else:
        points.append("Keine häufigen Schwachstellen registriert")

    return points
