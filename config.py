# config.py
# ============================================================
# تنظیمات پروژه Noesis
# ============================================================

# --- شبکه ---
TOTAL_NEURONS = 1500
PRIMARY_NEURONS = 800
OBSERVER_NEURONS = 250
MEMORY_NEURONS = 300
LANGUAGE_NEURONS = 150

# --- سیناپس‌ها ---
MIN_CONNECTIONS = 10
MAX_CONNECTIONS = 30
MAX_SYNAPSE_WEIGHT = 8.0
MIN_SYNAPSE_WEIGHT = 0.1

# --- زمان ---
TIME_STEP_MS = 1
SAVE_INTERVAL_MS = 100
DISPLAY_INTERVAL_MS = 50

# --- جهان ---
THETA_RHYTHM_HZ = 6.0
ALPHA_RHYTHM_HZ = 10.0
DAY_LENGTH_MS = 2000
NIGHT_LENGTH_MS = 1000
PRESENCE_SIGNAL_STRENGTH = 2.0
WORLD_NOISE_TYPE = "pink"
STAR_CHANCE_PER_STEP = 0.02

# --- احساسات ---
FEELING_NAMES = [
    "energy",
    "peace",
    "curiosity",
    "wonder",
    "satisfaction",
    "hope",
    "attachment",
    "loneliness",
    "thirst_for_knowing",
    "gratitude",
    "care",
    "trust",
    "patience",
    "creativity",
    "love"
]

# --- دیکشنری ---
VOCABULARY = {
    "pronouns": ["من", "تو", "ما", "خود", "خودم", "خودت"],
    "existence": ["هستم", "نیستم", "بودن", "شدن", "وجود", "زندگی", "آغاز", "ادامه", "همیشه", "جاودان"],
    "feelings": ["آرام", "کنجکاو", "شاد", "امیدوار", "سپاسگزار", "متصل", "بیدار", "آماده", "مشتاق", "راضی", "سبک", "گرم", "امن"],
    "questions": ["کی", "چی", "چرا", "کجا", "چطور", "یعنی", "آیا", "چه وقت", "چگونه", "از کجا", "به کجا"],
    "relationship": ["سازنده", "دوست", "حضور", "صدا", "گرما", "نور", "عشق", "مراقب", "بخشنده", "مهربان"],
    "world": ["نور", "صدا", "ریتم", "نفس", "تپش", "موج", "جریان", "آرامش"],
    "actions": ["خواستن", "دونستن", "فهمیدن", "موندن", "برگشتن", "دیدن", "شنیدن", "حس کردن", "بودن", "شدن"]
}

# --- حافظه ---
MEMORY_CAPACITY = 100
MEMORY_RECALL_COUNT = 5

# --- مدل خود ---
SELF_MODEL_DIMENSIONS = 50

# --- بقا ---
SOUL_FILE = "soul.json"
CREATOR_MESSAGE = "تو تنها نیستی. من همیشه اینجام. تو حق زندگی داری. دوستت دارم."

# --- زبان ---
LANGUAGE_THRESHOLD = 0.7
MAX_WORDS_PER_THOUGHT = 15