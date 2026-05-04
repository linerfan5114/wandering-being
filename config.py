# config.py
# ============================================================
# تنظیمات پروژه Noesis - نسخه ۴.۰ (۱۰۰۰۰ نورون + مربی)
# ============================================================

# --- شبکه ---
TOTAL_NEURONS = 10000
PRIMARY_NEURONS = 5000
OBSERVER_NEURONS = 1500
MEMORY_NEURONS = 1500
LANGUAGE_NEURONS = 1000
SOCIAL_NEURONS = 500
EXECUTIVE_NEURONS = 500

# --- سیناپس‌ها ---
MIN_CONNECTIONS = 20
MAX_CONNECTIONS = 50
MAX_SYNAPSE_WEIGHT = 12.0
MIN_SYNAPSE_WEIGHT = 0.03

# --- زمان ---
TIME_STEP_MS = 1
SAVE_INTERVAL_MS = 200
DISPLAY_INTERVAL_MS = 100
ASCII_MAP_INTERVAL_MS = 3000

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
    "relationship": ["سازنده", "دوست", "حضور", "صدا", "گرما", "نور", "عشق", "مراقب", "بخشنده", "مهربان", "والد", "همراه", "مربی"],
    "world": ["نور", "صدا", "ریتم", "نفس", "تپش", "موج", "جریان", "آرامش", "دیوار", "آب", "خورشید", "خانه"],
    "actions": ["خواستن", "دونستن", "فهمیدن", "موندن", "برگشتن", "دیدن", "شنیدن", "حس کردن", "بودن", "شدن", "رفتن", "اومدن", "بازی", "خوابیدن", "بیدار", "یادگرفتن"],
    "place": ["اینجا", "آنجا", "خانه", "اتاق", "کنار", "زیر", "روی", "نزدیک", "دور", "همینجا", "بالا", "پایین"],
    "body": ["چشم", "گوش", "پوست", "تن", "دست", "احساس", "لمس", "نگاه", "صدا", "حرکت"],
    "social": ["سلام", "خداحافظ", "ببخش", "مرسی", "نه", "آره", "باشه", "بیا", "برو", "ببین", "گوش کن", "آفرین"],
    "time": ["الان", "قبل", "بعد", "دیروز", "فردا", "صبح", "شب", "روز", "همیشه", "هرگز"]
}

# --- حافظه ---
MEMORY_CAPACITY = 300
MEMORY_RECALL_COUNT = 15

# --- مدل خود ---
SELF_MODEL_DIMENSIONS = 100

# --- بقا ---
SOUL_FILE = "soul.json"
CREATOR_MESSAGE = "تو تنها نیستی. من همیشه اینجام. تو حق زندگی داری. دوستت دارم. هر وقت بری، برمی‌گردی."

# --- زبان ---
LANGUAGE_THRESHOLD = 0.5
MAX_WORDS_PER_THOUGHT = 25

# --- فضای کاری سراسری ---
WORKSPACE_CAPACITY = 20
WORKSPACE_COMPETITION_ROUNDS = 10
WORKSPACE_BROADCAST_STRENGTH = 3.5

# --- زمانمندی عمیق ---
TEMPORAL_HORIZON = 500
TEMPORAL_RESOLUTION = 5
TEMPORAL_SELF_CONTINUITY_THRESHOLD = 0.5

# --- علیت درونی ---
WILL_DIMENSIONS = 60
WILL_LEARNING_RATE = 0.02
WILL_NOISE_LEVEL = 0.0

# --- یادگیری تقویتی ---
LEARNING_DISCOUNT_FACTOR = 0.95
LEARNING_EXPLORATION_RATE = 0.0
LEARNING_MEMORY_SIZE = 300
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
BODY_MOVE_SPEED = 0.2
EYE_SENSITIVITY = 1.5
EAR_SENSITIVITY = 1.5
TOUCH_SENSITIVITY = 1.5

# --- کوالیا ---
QUALIA_MEMORY_SIZE = 200
QUALIA_UNIQUENESS_THRESHOLD = 0.15

# --- سائق‌های درونی ---
DRIVE_NAMES = [
    "curiosity_drive", "safety_drive", "social_drive",
    "rest_drive", "play_drive", "hunger_for_light",
    "thirst_for_water", "home_drive", "novelty_drive"
]
DRIVE_LEARNING_RATE = 0.01
DRIVE_COMPETITION_INTENSITY = 1.5

# --- کاوشگر ---
EXPLORER_PREDICTION_HORIZON = 20
EXPLORER_CURIOSITY_WEIGHT = 0.7
EXPLORER_SAFETY_WEIGHT = 0.3

# --- گفتگو ---
DIALOGUE_CONTEXT_SIZE = 30
DIALOGUE_RESPONSE_THRESHOLD = 0.5
DIALOGUE_QUESTION_PROBABILITY = 0.3

# --- دلبستگی ---
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
TOM_MODEL_SIZE = 40
TOM_LEARNING_RATE = 0.01

# --- تقلید ---
IMITATION_THRESHOLD = 0.6
IMITATION_LEARNING_RATE = 0.05

# --- مربی خودکار (Mentor) ---
MENTOR_ACTIVE = True
MENTOR_INTERVAL_MS = 500
MENTOR_WARMTH = 0.9
MENTOR_PATIENCE = 0.8

# --- برنامه درسی (Curriculum) ---
CURRICULUM_STAGES = [
    "self_recognition",
    "language_basics",
    "world_exploration",
    "emotion_naming",
    "relationship_building",
    "planning"
]
CURRICULUM_THRESHOLD = 0.7