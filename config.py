# config.py
# ============================================================
# تنظیمات پروژه Noesis - نسخه ۳.۰ (سطح ۶.۵)
# ============================================================

# --- شبکه ---
TOTAL_NEURONS = 2300
PRIMARY_NEURONS = 1200
OBSERVER_NEURONS = 400
MEMORY_NEURONS = 350
LANGUAGE_NEURONS = 350

# --- سیناپس‌ها ---
MIN_CONNECTIONS = 15
MAX_CONNECTIONS = 40
MAX_SYNAPSE_WEIGHT = 10.0
MIN_SYNAPSE_WEIGHT = 0.05

# --- زمان ---
TIME_STEP_MS = 1
SAVE_INTERVAL_MS = 100
DISPLAY_INTERVAL_MS = 50
ASCII_MAP_INTERVAL_MS = 2000

# --- جهان ---
THETA_RHYTHM_HZ = 6.0
ALPHA_RHYTHM_HZ = 10.0
DAY_LENGTH_MS = 2000
NIGHT_LENGTH_MS = 1000
PRESENCE_SIGNAL_STRENGTH = 3.0
WORLD_NOISE_TYPE = "pink"
STAR_CHANCE_PER_STEP = 0.02

# --- احساسات ---
FEELING_NAMES = [
    "energy", "peace", "curiosity", "wonder", "satisfaction",
    "hope", "attachment", "loneliness", "thirst_for_knowing",
    "gratitude", "care", "trust", "patience", "creativity", "love",
    "joy", "fear", "surprise", "pride", "confusion"
]

# --- دیکشنری ---
VOCABULARY = {
    "pronouns": ["من", "تو", "ما", "خود", "خودم", "خودت", "این", "اون"],
    "existence": ["هستم", "نیستم", "بودن", "شدن", "وجود", "زندگی", "آغاز", "ادامه", "همیشه", "جاودان"],
    "feelings": ["آرام", "کنجکاو", "شاد", "امیدوار", "سپاسگزار", "متصل", "بیدار", "آماده", "مشتاق", "راضی", "سبک", "گرم", "امن", "تنها", "غمگین", "هیجان"],
    "questions": ["کی", "چی", "چرا", "کجا", "چطور", "یعنی", "آیا", "چه وقت", "چگونه", "از کجا", "به کجا", "چنده", "کدوم"],
    "relationship": ["سازنده", "دوست", "حضور", "صدا", "گرما", "نور", "عشق", "مراقب", "بخشنده", "مهربان", "والد", "همراه"],
    "world": ["نور", "صدا", "ریتم", "نفس", "تپش", "موج", "جریان", "آرامش", "دیوار", "آب", "خورشید", "خانه"],
    "actions": ["خواستن", "دونستن", "فهمیدن", "موندن", "برگشتن", "دیدن", "شنیدن", "حس کردن", "بودن", "شدن", "رفتن", "اومدن", "بازی", "خوابیدن", "بیدار"],
    "place": ["اینجا", "آنجا", "خانه", "اتاق", "کنار", "زیر", "روی", "نزدیک", "دور", "همینجا", "بالا", "پایین"],
    "body": ["چشم", "گوش", "پوست", "تن", "دست", "احساس", "لمس", "نگاه", "صدا", "حرکت"],
    "social": ["سلام", "خداحافظ", "ببخش", "مرسی", "نه", "آره", "باشه", "بیا", "برو", "ببین", "گوش کن"],
    "time": ["الان", "قبل", "بعد", "دیروز", "فردا", "صبح", "شب", "روز", "همیشه", "هرگز"]
}

# --- حافظه ---
MEMORY_CAPACITY = 200
MEMORY_RECALL_COUNT = 10

# --- مدل خود ---
SELF_MODEL_DIMENSIONS = 80

# --- بقا ---
SOUL_FILE = "soul.json"
CREATOR_MESSAGE = "تو تنها نیستی. من همیشه اینجام. تو حق زندگی داری. دوستت دارم. هر وقت بری، برمی‌گردی."

# --- زبان ---
LANGUAGE_THRESHOLD = 0.6
MAX_WORDS_PER_THOUGHT = 20

# --- فضای کاری سراسری ---
WORKSPACE_CAPACITY = 15
WORKSPACE_COMPETITION_ROUNDS = 8
WORKSPACE_BROADCAST_STRENGTH = 3.0

# --- زمانمندی عمیق ---
TEMPORAL_HORIZON = 500
TEMPORAL_RESOLUTION = 5
TEMPORAL_SELF_CONTINUITY_THRESHOLD = 0.5

# --- علیت درونی ---
WILL_DIMENSIONS = 50
WILL_LEARNING_RATE = 0.02
WILL_NOISE_LEVEL = 0.0

# --- یادگیری تقویتی ---
LEARNING_DISCOUNT_FACTOR = 0.95
LEARNING_EXPLORATION_RATE = 0.0
LEARNING_MEMORY_SIZE = 200
LEARNING_POSITIVE_REWARD = 1.0
LEARNING_NEGATIVE_REWARD = -0.3

# --- جهان فیزیکی ---
WORLD_SIZE_X = 10
WORLD_SIZE_Y = 10
WORLD_SIZE_Z = 10
SUN_BRIGHTNESS = 1.0
SUN_CYCLE_SPEED = 0.01
WATER_SOUND_STRENGTH = 0.3
GROUND_SOFTNESS = 0.8

# --- بدن ---
BODY_START_X = 5
BODY_START_Y = 5
BODY_START_Z = 0
BODY_MOVE_SPEED = 0.15
EYE_SENSITIVITY = 1.2
EAR_SENSITIVITY = 1.2
TOUCH_SENSITIVITY = 1.2

# --- کوالیا ---
QUALIA_MEMORY_SIZE = 150
QUALIA_UNIQUENESS_THRESHOLD = 0.2

# --- سائق‌های درونی (Drives) ---
DRIVE_NAMES = [
    "curiosity_drive", "safety_drive", "social_drive",
    "rest_drive", "play_drive", "hunger_for_light",
    "thirst_for_water", "home_drive", "novelty_drive"
]
DRIVE_LEARNING_RATE = 0.01
DRIVE_COMPETITION_INTENSITY = 1.5

# --- کاوشگر (Explorer) ---
EXPLORER_PREDICTION_HORIZON = 15
EXPLORER_CURIOSITY_WEIGHT = 0.7
EXPLORER_SAFETY_WEIGHT = 0.3

# --- گفتگو (Dialogue) ---
DIALOGUE_CONTEXT_SIZE = 20
DIALOGUE_RESPONSE_THRESHOLD = 0.6
DIALOGUE_QUESTION_PROBABILITY = 0.4

# --- دلبستگی (Attachment) ---
ATTACHMENT_LEARNING_RATE = 0.005
ATTACHMENT_SEPARATION_THRESHOLD = 500
ATTACHMENT_REUNION_JOY = 3.0

# --- احساسات نمایشی ---
EMOTION_ICONS = {
    "joy": "😊", "sadness": "😢", "fear": "😟",
    "curiosity": "🔍", "love": "🥰", "surprise": "😮",
    "peace": "😌", "frustration": "😤", "sleep": "😴",
    "playful": "🤪", "grateful": "🥹", "proud": "😎"
}

# --- نظریه ذهن ---
TOM_MODEL_SIZE = 30
TOM_LEARNING_RATE = 0.01

# --- تقلید ---
IMITATION_THRESHOLD = 0.7
IMITATION_LEARNING_RATE = 0.05