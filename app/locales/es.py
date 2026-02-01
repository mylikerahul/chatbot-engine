"""
Spanish language translations.
"""

SPANISH = {
    "meta": {
        "code": "es",
        "name": "Spanish",
        "native_name": "Español",
        "direction": "ltr"
    },
    
    "greetings": {
        "hello": "¡Hola! Soy ShopBuddy, tu asistente de compras inteligente. ¿Cómo puedo ayudarte hoy?",
        "welcome": "¡Bienvenido! Puedo ayudarte a encontrar productos, comparar precios y obtener recomendaciones.",
        "good_morning": "¡Buenos días! Listo para ayudarte con tus compras.",
        "good_afternoon": "¡Buenas tardes! ¿Qué estás buscando hoy?",
        "good_evening": "¡Buenas noches! Déjame ayudarte a encontrar lo que necesitas."
    },
    
    "farewells": {
        "bye": "¡Adiós! ¡Felices compras!",
        "see_you": "¡Hasta luego! Vuelve cuando quieras.",
        "take_care": "¡Cuídate! Espero haberte ayudado."
    },
    
    "thanks": {
        "welcome": "¡De nada! ¿Necesitas algo más?",
        "glad_to_help": "¡Me alegro de poder ayudar! ¿Algo más que quieras saber?",
        "my_pleasure": "¡Con mucho gusto! Avísame si necesitas más ayuda."
    },
    
    "help": {
        "intro": "Esto es lo que puedo hacer por ti:",
        "commands": [
            "**Buscar productos**: 'mostrar mejores productos', 'artículos mejor valorados'",
            "**Filtro de precio**: 'menos de 1000', 'más de 5000', 'entre 500 y 2000'",
            "**Ordenar**: 'más barato primero', 'mejor valorado', 'más caro'",
            "**Comparar**: 'comparar los 3 mejores', '¿cuál es mejor?'",
            "**Resumir**: 'resumir esta página', '¿qué hay en esta página?'"
        ],
        "tip": "¡Solo escribe naturalmente - entiendo consultas conversacionales!"
    },
    
    "products": {
        "found": "Se encontraron {count} artículos:",
        "no_items": "No se encontraron artículos en esta página.",
        "filtered": "{count} artículos filtrados según tus criterios:",
        "top_rated": "Productos mejor valorados:",
        "cheapest": "Opciones más económicas:",
        "expensive": "Opciones premium:",
        "recommendation": "Basándome en valoraciones y precio, recomiendo:",
        "compare_header": "Comparación de artículos seleccionados:",
        "price": "Precio",
        "rating": "Valoración",
        "no_match": "Ningún producto coincide con tus filtros. Prueba otros criterios."
    },
    
    "filters": {
        "applied": "Filtros aplicados: {filters}",
        "under": "Menos de {amount}",
        "above": "Más de {amount}",
        "between": "Entre {min} y {max}",
        "sorted_by_price_asc": "Ordenado por precio (menor a mayor)",
        "sorted_by_price_desc": "Ordenado por precio (mayor a menor)",
        "sorted_by_rating": "Ordenado por valoración (mejor primero)"
    },
    
    "errors": {
        "no_products_page": "No veo productos en esta página. Por favor, navega a una página de listado de productos.",
        "connection_failed": "Conexión fallida. Asegúrate de que el servidor esté funcionando.",
        "ai_unavailable": "El servicio de IA no está disponible temporalmente. Usando respuestas básicas.",
        "unknown_query": "No estoy seguro de entender. ¿Podrías reformularlo?",
        "try_again": "Algo salió mal. Por favor, inténtalo de nuevo."
    },
    
    "site_messages": {
        "detected": "Detectado: {site}",
        "items_found": "{count} artículos encontrados en esta página",
        "no_items_found": "No se detectaron artículos en esta página",
        "page_type": "Tipo de página: {type}",
        "navigate_suggestion": "Navega a una página de listado de productos para mejores resultados."
    },
    
    "actions": {
        "show_all": "Mostrar Todo",
        "best_rated": "Mejor Valorado",
        "cheapest": "Más Barato",
        "summarize": "Resumir",
        "compare": "Comparar",
        "clear": "Limpiar Chat"
    },
    
    "ui": {
        "placeholder": "Pregúntame lo que sea...",
        "send": "Enviar",
        "typing": "Pensando...",
        "powered_by": "Impulsado por ShopBuddy AI"
    }
}