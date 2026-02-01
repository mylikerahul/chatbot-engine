"""
French language translations.
"""

FRENCH = {
    "meta": {
        "code": "fr",
        "name": "French",
        "native_name": "Français",
        "direction": "ltr"
    },
    
    "greetings": {
        "hello": "Bonjour! Je suis ShopBuddy, votre assistant shopping intelligent. Comment puis-je vous aider aujourd'hui?",
        "welcome": "Bienvenue! Je peux vous aider à trouver des produits, comparer les prix et obtenir des recommandations.",
        "good_morning": "Bonjour! Prêt à vous aider avec vos achats.",
        "good_afternoon": "Bon après-midi! Que cherchez-vous aujourd'hui?",
        "good_evening": "Bonsoir! Laissez-moi vous aider à trouver ce dont vous avez besoin."
    },
    
    "farewells": {
        "bye": "Au revoir! Bon shopping!",
        "see_you": "À bientôt! N'hésitez pas à revenir.",
        "take_care": "Prenez soin de vous! J'espère avoir été utile."
    },
    
    "thanks": {
        "welcome": "Je vous en prie! Besoin d'autre chose?",
        "glad_to_help": "Content d'avoir pu aider! Autre chose à savoir?",
        "my_pleasure": "Avec plaisir! Faites-moi savoir si vous avez besoin d'aide."
    },
    
    "help": {
        "intro": "Voici ce que je peux faire pour vous:",
        "commands": [
            "**Recherche de produits**: 'montrer les meilleurs produits', 'articles les mieux notés'",
            "**Filtre de prix**: 'moins de 1000', 'plus de 5000', 'entre 500 et 2000'",
            "**Tri**: 'moins cher d'abord', 'mieux noté', 'plus cher'",
            "**Comparer**: 'comparer le top 3', 'lequel est meilleur'",
            "**Résumer**: 'résumer cette page', 'qu'y a-t-il sur cette page'"
        ],
        "tip": "Écrivez naturellement - je comprends les requêtes conversationnelles!"
    },
    
    "products": {
        "found": "{count} articles trouvés:",
        "no_items": "Aucun article trouvé sur cette page.",
        "filtered": "{count} articles filtrés selon vos critères:",
        "top_rated": "Produits les mieux notés:",
        "cheapest": "Options les plus abordables:",
        "expensive": "Choix premium:",
        "recommendation": "Basé sur les notes et le prix, je recommande:",
        "compare_header": "Comparaison des articles sélectionnés:",
        "price": "Prix",
        "rating": "Note",
        "no_match": "Aucun produit ne correspond à vos filtres. Essayez d'autres critères."
    },
    
    "filters": {
        "applied": "Filtres appliqués: {filters}",
        "under": "Moins de {amount}",
        "above": "Plus de {amount}",
        "between": "Entre {min} et {max}",
        "sorted_by_price_asc": "Trié par prix (croissant)",
        "sorted_by_price_desc": "Trié par prix (décroissant)",
        "sorted_by_rating": "Trié par note (meilleur d'abord)"
    },
    
    "errors": {
        "no_products_page": "Je ne vois pas de produits sur cette page. Veuillez naviguer vers une page de liste de produits.",
        "connection_failed": "Échec de connexion. Assurez-vous que le serveur fonctionne.",
        "ai_unavailable": "Le service IA est temporairement indisponible. Utilisation des réponses de base.",
        "unknown_query": "Je ne suis pas sûr de comprendre. Pourriez-vous reformuler?",
        "try_again": "Quelque chose s'est mal passé. Veuillez réessayer."
    },
    
    "site_messages": {
        "detected": "Détecté: {site}",
        "items_found": "{count} articles trouvés sur cette page",
        "no_items_found": "Aucun article détecté sur cette page",
        "page_type": "Type de page: {type}",
        "navigate_suggestion": "Naviguez vers une page de liste de produits pour de meilleurs résultats."
    },
    
    "actions": {
        "show_all": "Tout Afficher",
        "best_rated": "Mieux Noté",
        "cheapest": "Moins Cher",
        "summarize": "Résumer",
        "compare": "Comparer",
        "clear": "Effacer Chat"
    },
    
    "ui": {
        "placeholder": "Demandez-moi n'importe quoi...",
        "send": "Envoyer",
        "typing": "Réflexion...",
        "powered_by": "Propulsé par ShopBuddy AI"
    }
}