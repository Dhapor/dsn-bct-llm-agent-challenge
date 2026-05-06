"""
Sample item catalog derived from Yelp, Amazon Reviews, and Goodreads datasets.
In production, replace with full dataset. Items are domain-agnostic (restaurants,
books, products, movies) to demonstrate cross-domain recommendation (Task B).
"""

SAMPLE_ITEMS: list[dict] = [
    # --- Nigerian Restaurants ---
    {"id": "ng_r001", "name": "Yellow Chilli", "category": "restaurant", "cuisine": "Nigerian", "location": "Lagos", "avg_rating": 4.3, "price_range": "$$$", "tags": ["upscale", "nigerian", "lagos"], "description": "Upscale Nigerian cuisine in Lagos. Famous for oxtail and jollof rice."},
    {"id": "ng_r002", "name": "Mama Cass", "category": "restaurant", "cuisine": "Nigerian", "location": "Lagos", "avg_rating": 4.1, "price_range": "$$", "tags": ["local", "nigerian", "fast food", "affordable"], "description": "Popular fast-food chain serving Nigerian staples like jollof rice, egusi, and pounded yam."},
    {"id": "ng_r003", "name": "Kilimanjaro", "category": "restaurant", "cuisine": "Nigerian", "location": "Lagos", "avg_rating": 4.0, "price_range": "$$", "tags": ["nigerian", "grills", "suya"], "description": "Known for grills, suya and Nigerian continental dishes."},
    {"id": "ng_r004", "name": "Nkoyo", "category": "restaurant", "cuisine": "Nigerian", "location": "Abuja", "avg_rating": 4.5, "price_range": "$$$", "tags": ["fine dining", "nigerian", "abuja"], "description": "Award-winning fine dining Nigerian restaurant in Abuja."},
    {"id": "ng_r005", "name": "Bukka Hut", "category": "restaurant", "cuisine": "Nigerian", "location": "Lagos", "avg_rating": 4.2, "price_range": "$", "tags": ["local", "affordable", "traditional"], "description": "Budget-friendly bukka-style traditional Nigerian food."},

    # --- International Restaurants ---
    {"id": "int_r001", "name": "Nandos Lagos", "category": "restaurant", "cuisine": "South African", "location": "Lagos", "avg_rating": 4.0, "price_range": "$$", "tags": ["peri-peri", "chicken", "international"], "description": "Famous peri-peri chicken chain popular across Africa."},
    {"id": "int_r002", "name": "Chicken Republic", "category": "restaurant", "cuisine": "Fast Food", "location": "Lagos", "avg_rating": 3.8, "price_range": "$", "tags": ["fast food", "chicken", "affordable", "nationwide"], "description": "Nigeria's favourite fast food chain. Affordable chicken meals nationwide."},
    {"id": "int_r003", "name": "The Place Restaurant", "category": "restaurant", "cuisine": "Continental", "location": "Lagos", "avg_rating": 4.1, "price_range": "$$", "tags": ["continental", "bar", "relaxed"], "description": "Chill spot with continental food and drinks. Great for hangouts."},

    # --- Books (Goodreads-style) ---
    {"id": "bk_001", "name": "Things Fall Apart", "category": "book", "author": "Chinua Achebe", "genre": "African Literature", "avg_rating": 4.6, "tags": ["classic", "nigerian", "literature", "igbo", "africa"], "description": "Chinua Achebe's masterpiece about pre-colonial Igbo society and the impact of colonialism."},
    {"id": "bk_002", "name": "Half of a Yellow Sun", "category": "book", "author": "Chimamanda Ngozi Adichie", "genre": "Historical Fiction", "avg_rating": 4.5, "tags": ["nigeria", "biafra", "war", "adichie", "literature"], "description": "A powerful novel set during the Nigerian Civil War by Chimamanda Ngozi Adichie."},
    {"id": "bk_003", "name": "Purple Hibiscus", "category": "book", "author": "Chimamanda Ngozi Adichie", "genre": "Fiction", "avg_rating": 4.3, "tags": ["nigeria", "coming of age", "family", "adichie"], "description": "A coming-of-age story set in post-colonial Nigeria by Adichie."},
    {"id": "bk_004", "name": "Americanah", "category": "book", "author": "Chimamanda Ngozi Adichie", "genre": "Literary Fiction", "avg_rating": 4.4, "tags": ["diaspora", "nigeria", "race", "identity", "romance"], "description": "A novel about identity, race, and love across Nigeria and America."},
    {"id": "bk_005", "name": "Season of Migration to the North", "category": "book", "author": "Tayeb Salih", "genre": "African Literature", "avg_rating": 4.2, "tags": ["africa", "postcolonial", "classic"], "description": "A postcolonial African classic exploring identity and cultural clash."},
    {"id": "bk_006", "name": "Atomic Habits", "category": "book", "author": "James Clear", "genre": "Self-Help", "avg_rating": 4.5, "tags": ["productivity", "habits", "self-help", "popular"], "description": "Practical guide to building good habits and breaking bad ones."},
    {"id": "bk_007", "name": "The Richest Man in Babylon", "category": "book", "author": "George S. Clason", "genre": "Finance", "avg_rating": 4.3, "tags": ["finance", "wealth", "personal finance", "classic"], "description": "Timeless financial wisdom through Babylonian parables."},

    # --- Movies / Nollywood ---
    {"id": "mv_001", "name": "The Black Book", "category": "movie", "genre": "Action/Thriller", "origin": "Nollywood", "avg_rating": 4.2, "tags": ["nollywood", "action", "thriller", "netflix", "nigerian"], "description": "Nigerian action thriller on Netflix following a deacon seeking justice."},
    {"id": "mv_002", "name": "A Tribe Called Judah", "category": "movie", "genre": "Crime Drama", "origin": "Nollywood", "avg_rating": 4.4, "tags": ["nollywood", "crime", "drama", "comedy", "nigerian"], "description": "Funke Akindele's blockbuster crime drama about a mother and her sons."},
    {"id": "mv_003", "name": "Gangs of Lagos", "category": "movie", "genre": "Crime Drama", "origin": "Nollywood", "avg_rating": 4.0, "tags": ["nollywood", "lagos", "crime", "prime video"], "description": "Gritty crime drama set in the streets of Lagos on Prime Video."},
    {"id": "mv_004", "name": "Lionheart", "category": "movie", "genre": "Drama", "origin": "Nollywood", "avg_rating": 3.9, "tags": ["nollywood", "drama", "business", "genevieve"], "description": "Genevieve Nnaji directorial debut — first Netflix Nollywood original."},
    {"id": "mv_005", "name": "Black Panther", "category": "movie", "genre": "Action/Superhero", "origin": "Hollywood", "avg_rating": 4.3, "tags": ["marvel", "action", "africa", "superhero", "wakanda"], "description": "Marvel's groundbreaking African-themed superhero film."},
    {"id": "mv_006", "name": "Coming to America", "category": "movie", "genre": "Comedy", "origin": "Hollywood", "avg_rating": 4.1, "tags": ["comedy", "africa", "nigeria", "eddie murphy", "classic"], "description": "Eddie Murphy classic comedy about an African prince in America."},

    # --- Consumer Products (Amazon-style) ---
    {"id": "pr_001", "name": "Tecno Camon 30 Pro", "category": "electronics", "brand": "Tecno", "avg_rating": 4.1, "price_range": "$$", "tags": ["smartphone", "camera", "affordable", "tecno", "nigeria"], "description": "Mid-range smartphone with excellent camera, popular in Nigeria."},
    {"id": "pr_002", "name": "Infinix Hot 40i", "category": "electronics", "brand": "Infinix", "avg_rating": 3.9, "price_range": "$", "tags": ["smartphone", "budget", "infinix", "nigeria"], "description": "Budget smartphone with long battery life — bestseller in Nigeria."},
    {"id": "pr_003", "name": "Scanfrost Standing Fan", "category": "home appliance", "brand": "Scanfrost", "avg_rating": 4.0, "price_range": "$", "tags": ["fan", "home", "cooling", "nigeria", "affordable"], "description": "Reliable standing fan with 3 speed settings. Nigerian market staple."},
    {"id": "pr_004", "name": "Thermocool Chest Freezer", "category": "home appliance", "brand": "Thermocool", "avg_rating": 4.2, "price_range": "$$$", "tags": ["freezer", "storage", "home appliance", "nigeria"], "description": "Large-capacity chest freezer for Nigerian households and small businesses."},
    {"id": "pr_005", "name": "Ariel Washing Powder", "category": "household", "brand": "Ariel", "avg_rating": 4.4, "price_range": "$", "tags": ["laundry", "cleaning", "household", "trusted"], "description": "Popular laundry powder trusted by Nigerian families for decades."},

    # --- Music ---
    {"id": "mu_001", "name": "Asake - Work of Art", "category": "music", "genre": "Afrobeats", "artist": "Asake", "avg_rating": 4.5, "tags": ["afrobeats", "asake", "nigerian", "album"], "description": "Asake's acclaimed album blending Afrobeats and street-pop."},
    {"id": "mu_002", "name": "Burna Boy - African Giant", "category": "music", "genre": "Afrofusion", "artist": "Burna Boy", "avg_rating": 4.6, "tags": ["afrofusion", "burna boy", "grammy", "nigerian"], "description": "Grammy-winning album by the African Giant himself."},
    {"id": "mu_003", "name": "Wizkid - Made in Lagos", "category": "music", "genre": "Afrobeats", "artist": "Wizkid", "avg_rating": 4.7, "tags": ["afrobeats", "wizkid", "classic", "nigerian", "global"], "description": "Wizkid's global crossover album — a modern Afrobeats classic."},
]


def get_all_items() -> list[dict]:
    return SAMPLE_ITEMS


def get_items_by_category(category: str) -> list[dict]:
    return [i for i in SAMPLE_ITEMS if i["category"] == category]


def get_item_by_id(item_id: str) -> dict | None:
    return next((i for i in SAMPLE_ITEMS if i["id"] == item_id), None)
