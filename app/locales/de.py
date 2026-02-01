"""
German language translations.
"""

GERMAN = {
    "meta": {
        "code": "de",
        "name": "German",
        "native_name": "Deutsch",
        "direction": "ltr"
    },
    
    "greetings": {
        "hello": "Hallo! Ich bin ShopBuddy, Ihr intelligenter Einkaufsassistent. Wie kann ich Ihnen heute helfen?",
        "welcome": "Willkommen! Ich kann Ihnen helfen, Produkte zu finden, Preise zu vergleichen und Empfehlungen zu erhalten.",
        "good_morning": "Guten Morgen! Bereit, Ihnen beim Einkaufen zu helfen.",
        "good_afternoon": "Guten Tag! Was suchen Sie heute?",
        "good_evening": "Guten Abend! Lassen Sie mich Ihnen helfen, das zu finden, was Sie brauchen."
    },
    
    "farewells": {
        "bye": "Auf Wiedersehen! Viel Spaß beim Einkaufen!",
        "see_you": "Bis bald! Kommen Sie jederzeit wieder.",
        "take_care": "Passen Sie auf sich auf! Ich hoffe, ich konnte helfen."
    },
    
    "thanks": {
        "welcome": "Gern geschehen! Brauchen Sie noch etwas?",
        "glad_to_help": "Freut mich, dass ich helfen konnte! Noch etwas?",
        "my_pleasure": "Mit Vergnügen! Lassen Sie mich wissen, wenn Sie weitere Hilfe benötigen."
    },
    
    "help": {
        "intro": "Das kann ich für Sie tun:",
        "commands": [
            "**Produktsuche**: 'zeige beste Produkte', 'bestbewertete Artikel'",
            "**Preisfilter**: 'unter 1000', 'über 5000', 'zwischen 500 und 2000'",
            "**Sortierung**: 'günstigste zuerst', 'bestbewertet', 'teuerste'",
            "**Vergleichen**: 'vergleiche Top 3', 'welches ist besser'",
            "**Zusammenfassen**: 'fasse diese Seite zusammen', 'was ist auf dieser Seite'"
        ],
        "tip": "Schreiben Sie einfach natürlich - ich verstehe Konversationsanfragen!"
    },
    
    "products": {
        "found": "{count} Artikel gefunden:",
        "no_items": "Keine Artikel auf dieser Seite gefunden.",
        "filtered": "{count} Artikel nach Ihren Kriterien gefiltert:",
        "top_rated": "Bestbewertete Produkte:",
        "cheapest": "Günstigste Optionen:",
        "expensive": "Premium-Auswahl:",
        "recommendation": "Basierend auf Bewertungen und Preis empfehle ich:",
        "compare_header": "Vergleich der ausgewählten Artikel:",
        "price": "Preis",
        "rating": "Bewertung",
        "no_match": "Keine Produkte entsprechen Ihren Filtern. Versuchen Sie andere Kriterien."
    },
    
    "filters": {
        "applied": "Angewandte Filter: {filters}",
        "under": "Unter {amount}",
        "above": "Über {amount}",
        "between": "Zwischen {min} und {max}",
        "sorted_by_price_asc": "Nach Preis sortiert (aufsteigend)",
        "sorted_by_price_desc": "Nach Preis sortiert (absteigend)",
        "sorted_by_rating": "Nach Bewertung sortiert (beste zuerst)"
    },
    
    "errors": {
        "no_products_page": "Ich sehe keine Produkte auf dieser Seite. Bitte navigieren Sie zu einer Produktlistenseite.",
        "connection_failed": "Verbindung fehlgeschlagen. Stellen Sie sicher, dass der Server läuft.",
        "ai_unavailable": "KI-Dienst vorübergehend nicht verfügbar. Verwende Basisantworten.",
        "unknown_query": "Ich bin nicht sicher, ob ich das verstehe. Könnten Sie das umformulieren?",
        "try_again": "Etwas ist schief gelaufen. Bitte versuchen Sie es erneut."
    },
    
    "site_messages": {
        "detected": "Erkannt: {site}",
        "items_found": "{count} Artikel auf dieser Seite gefunden",
        "no_items_found": "Keine Artikel auf dieser Seite erkannt",
        "page_type": "Seitentyp: {type}",
        "navigate_suggestion": "Navigieren Sie zu einer Produktlistenseite für bessere Ergebnisse."
    },
    
    "actions": {
        "show_all": "Alle Anzeigen",
        "best_rated": "Bestbewertet",
        "cheapest": "Günstigste",
        "summarize": "Zusammenfassen",
        "compare": "Vergleichen",
        "clear": "Chat Löschen"
    },
    
    "ui": {
        "placeholder": "Fragen Sie mich alles...",
        "send": "Senden",
        "typing": "Denke nach...",
        "powered_by": "Powered by ShopBuddy AI"
    }
}