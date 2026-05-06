"""
Nigerian linguistic and cultural contextualization layer.
Injects Naija tone, Pidgin markers, and cultural references into prompts.
This is an explicit bonus scoring criterion in the competition rubric.
"""

NIGERIAN_FOOD_REFS = [
    "jollof rice", "egusi soup", "suya", "puff puff", "chin chin",
    "pepper soup", "banga soup", "afang", "amala", "eba", "pounded yam",
    "akara", "moi moi", "ofada rice", "nkwobi",
]

NIGERIAN_EXPRESSIONS = {
    "very good": ["e sweet me die", "e too sweet", "sharp sharp good"],
    "very bad": ["e no good at all", "rubbish", "e pain me", "e be like punishment"],
    "amazing": ["e go wound you", "e dey craze", "no dulling", "e be fire"],
    "recommend": ["I go tell my people", "abeg go there", "no think am twice"],
    "disappointed": ["them don disappoint", "e pain me well well", "na wa o"],
    "service": ["them service na top", "the people wey dey work there"],
    "expensive": ["the price dey bite", "e cost sha", "dem wan kill person with price"],
    "affordable": ["the price friendly", "e reasonable", "value for money dey there"],
}

NAIJA_INTENSIFIERS = ["well well", "die", "die die", "finish", "sotay", "gan"]

LOCATION_SPECIFIC = {
    "Lagos": ["VI", "Lekki", "Ikeja", "Surulere", "Yaba", "Ajah"],
    "Abuja": ["Wuse", "Maitama", "Garki", "Gwarinpa", "Jabi"],
    "Port Harcourt": ["GRA", "Trans Amadi", "Rumuola"],
    "Ibadan": ["Bodija", "Ring Road", "Dugbe"],
    "Kano": ["Sabon Gari", "Bompai", "Nassarawa"],
}


def get_nigerian_persona_prompt(user_location: str, uses_pidgin: bool) -> str:
    """
    Returns a system-level instruction to make generated content sound Nigerian.
    Calibrated by location and whether the user already writes in Pidgin.
    """
    city = next((city for city in LOCATION_SPECIFIC if city.lower() in user_location.lower()), "Lagos")
    local_areas = LOCATION_SPECIFIC.get(city, LOCATION_SPECIFIC["Lagos"])

    base = f"""You are simulating a Nigerian user from {city}.

Cultural context to weave in naturally (not forcefully):
- Reference local landmarks or areas when relevant (e.g., {', '.join(local_areas[:3])})
- Nigerian food and lifestyle references feel natural to this user
- Comparisons to local equivalents are common ("better than mama put", "like mama kitchen")
- Community and social trust matter ("my people recommended this", "I hear say...")
- Value consciousness: Nigerians are price-aware and mention value for money"""

    if uses_pidgin:
        base += """

Language style: This user naturally code-switches between English and Nigerian Pidgin.
- Use Pidgin expressions organically (not every sentence, but naturally scattered)
- Examples: "e sweet me", "abeg", "oga", "wahala", "e no bad", "e dey", "na so"
- Avoid stereotypes — write as an educated Nigerian would actually write online"""
    else:
        base += """

Language style: This user writes in standard English but with Nigerian cultural sensibility.
- Occasional Pidgin words are fine but not required
- Nigerian idioms and cultural references come naturally"""

    return base


def get_nigerian_recommendation_context(user_location: str) -> str:
    """Context for recommendations that feel locally relevant to a Nigerian user."""
    city = next((city for city in LOCATION_SPECIFIC if city.lower() in user_location.lower()), "Lagos")
    return f"""When making recommendations for this user in {city}, Nigeria:
- Prioritize availability in Nigeria (items/services actually accessible locally)
- Consider price sensitivity — highlight value propositions
- Naija social proof matters: "people dey go there" / "popular spot"
- Include cross-category recommendations (e.g., Nollywood films, Nigerian cuisine, local events)
- Handle that some global platform items may not be locally available — suggest alternatives"""
