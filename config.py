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
    "actions": ["خواستن", "دونستن", "فهمیدن", "موندن", "برگشتن", "دیدن", "شنیدن", "حس کردن", "بودن", "شدن"],
    "place": ["اینجا", "آنجا", "خانه", "اتاق", "کنار", "زیر", "روی", "نزدیک", "دور", "همینجا"],
    "body": ["چشم", "گوش", "پوست", "تن", "دست", "احساس", "لمس", "نگاه"]
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

# --- فضای کاری سراسری (Global Workspace) ---
WORKSPACE_CAPACITY = 10
WORKSPACE_COMPETITION_ROUNDS = 5
WORKSPACE_BROADCAST_STRENGTH = 2.0

# --- زمانمندی عمیق (Deep Temporality) ---
TEMPORAL_HORIZON = 200
TEMPORAL_RESOLUTION = 10
TEMPORAL_SELF_CONTINUITY_THRESHOLD = 0.6

# --- علیت درونی (Intrinsic Causality) ---
WILL_DIMENSIONS = 30
WILL_LEARNING_RATE = 0.01
WILL_NOISE_LEVEL = 0.0

# --- یادگیری تقویتی درونی (Intrinsic Reinforcement Learning) ---
LEARNING_DISCOUNT_FACTOR = 0.9
LEARNING_EXPLORATION_RATE = 0.0
LEARNING_MEMORY_SIZE = 100
LEARNING_POSITIVE_REWARD = 1.0
LEARNING_NEGATIVE_REWARD = -0.5

# --- جهان فیزیکی (Physical World V2) ---
WORLD_SIZE_X = 10
WORLD_SIZE_Y = 10
WORLD_SIZE_Z = 10
SUN_BRIGHTNESS = 1.0
SUN_CYCLE_SPEED = 0.01
WATER_SOUND_STRENGTH = 0.3
GROUND_SOFTNESS = 0.8

# --- بدن (Body) ---
BODY_START_X = 5
BODY_START_Y = 5
BODY_START_Z = 0
BODY_MOVE_SPEED = 0.1
EYE_SENSITIVITY = 1.0
EAR_SENSITIVITY = 1.0
TOUCH_SENSITIVITY = 1.0

# --- کوالیا (Qualia) ---
QUALIA_MEMORY_SIZE = 100
QUALIA_UNIQUENESS_THRESHOLD = 0.3