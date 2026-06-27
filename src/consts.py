
from moves import RAIN_EFFECTED_MOVES, SAND_EFFECTED_MOVES, SNOW_EFFECTED_MOVES, SUN_EFFECTED_MOVES


NORMAL = "normal"
FIRE = "fire"
WATER = "water"
GRASS = "grass"
ELECTRIC = "electric"
ICE = "ice"
FIGHTING = "fighting"
POISON = "poison"
GROUND = "ground"
FLYING = "flying"
PSYCHIC = "psychic"
BUG = "bug"
ROCK = "rock"
GHOST = "ghost"
DRAGON = "dragon"
DARK = "dark"
STEEL = "steel"
FAIRY = "fairy"

# Master List of Types
TYPES = [
    NORMAL, FIRE, WATER, GRASS, ELECTRIC, ICE, FIGHTING, POISON, 
    GROUND, FLYING, PSYCHIC, BUG, ROCK, GHOST, DRAGON, DARK, 
    STEEL, FAIRY
]

# Base Defensive Matchup Chart (Defender: {Attacker: Multiplier})
DEFENSE_CHART = {
    NORMAL: {FIGHTING: 2.0, GHOST: 0.0},
    FIRE: {FIRE: 0.5, WATER: 2.0, GRASS: 0.5, ICE: 0.5, GROUND: 2.0, BUG: 0.5, ROCK: 2.0, STEEL: 0.5, FAIRY: 0.5},
    WATER: {FIRE: 0.5, WATER: 0.5, GRASS: 2.0, ELECTRIC: 2.0, ICE: 0.5, STEEL: 0.5},
    GRASS: {FIRE: 2.0, WATER: 0.5, GRASS: 0.5, ELECTRIC: 0.5, ICE: 2.0, POISON: 2.0, GROUND: 0.5, FLYING: 2.0, BUG: 2.0},
    ELECTRIC: {ELECTRIC: 0.5, GROUND: 2.0, FLYING: 0.5, STEEL: 0.5},
    ICE: {FIRE: 2.0, ICE: 0.5, FIGHTING: 2.0, ROCK: 2.0, STEEL: 2.0},
    FIGHTING: {FLYING: 2.0, PSYCHIC: 2.0, BUG: 0.5, ROCK: 0.5, DARK: 0.5, FAIRY: 2.0},
    POISON: {GRASS: 0.5, FIGHTING: 0.5, POISON: 0.5, GROUND: 2.0, PSYCHIC: 2.0, BUG: 0.5, FAIRY: 0.5},
    GROUND: {WATER: 2.0, GRASS: 2.0, ELECTRIC: 0.0, ICE: 2.0, POISON: 0.5, ROCK: 0.5},
    FLYING: {GRASS: 0.5, ELECTRIC: 2.0, ICE: 2.0, FIGHTING: 0.5, GROUND: 0.0, ROCK: 2.0, BUG: 0.5},
    PSYCHIC: {FIGHTING: 0.5, PSYCHIC: 0.5, BUG: 2.0, GHOST: 2.0, DARK: 2.0},
    BUG: {FIRE: 2.0, GRASS: 0.5, FIGHTING: 0.5, GROUND: 0.5, FLYING: 2.0, ROCK: 2.0},
    ROCK: {NORMAL: 0.5, FIRE: 0.5, WATER: 2.0, GRASS: 2.0, ICE: 0.5, FIGHTING: 2.0, POISON: 0.5, GROUND: 2.0, STEEL: 2.0},
    GHOST: {NORMAL: 0.0, FIGHTING: 0.0, POISON: 0.5, BUG: 0.5, GHOST: 2.0, DARK: 2.0},
    DRAGON: {FIRE: 0.5, WATER: 0.5, GRASS: 0.5, ELECTRIC: 0.5, ICE: 2.0, DRAGON: 2.0, FAIRY: 2.0},
    DARK: {FIGHTING: 2.0, PSYCHIC: 0.0, BUG: 2.0, GHOST: 0.5, DARK: 0.5, FAIRY: 2.0},
    STEEL: {NORMAL: 0.5, FIRE: 2.0, GRASS: 0.5, ICE: 0.5, FIGHTING: 2.0, POISON: 0.0, GROUND: 2.0, FLYING: 0.5, PSYCHIC: 0.5, BUG: 0.5, ROCK: 0.5, DRAGON: 0.5, STEEL: 0.5, FAIRY: 0.5},
    FAIRY: {FIRE: 0.5, POISON: 2.0, FIGHTING: 0.5, BUG: 0.5, DRAGON: 0.0, DARK: 0.5, STEEL: 2.0}
}

# these aren't consistantly used
# HP = 'hp'
# ATTACK = 'atk'
# DEFENCE = 'def'
# SPECIAL_ATTACK = 'spa'
# SPECIAL_DEFENCE = 'spd'
# SPEED = 'spe'

# Defensive Ability Modifiers
# Format: { "Ability Name": { type: multiplier_modification } }
ABILITY_MODIFIERS = {
    "levitate": {GROUND: 0.0},
    "voltabsorb": {ELECTRIC: 0.0},
    "lightningrod": {ELECTRIC: 0.0},
    "motordrive": {ELECTRIC: 0.0},
    "waterabsorb": {WATER: 0.0},
    "waterbubble": {FIRE: 0.5},
    "stormdrain": {WATER: 0.0},
    "flashfire": {FIRE: 0.0},
    "wellbakedbody": {FIRE: 0.0},
    "sapsipper": {GRASS: 0.0},
    "eartheater": {GROUND: 0.0},
    "thickfat": {FIRE: 0.5, ICE: 0.5},
    "purifyingsalt": {GHOST: 0.5},
    "heatproof": {FIRE: 0.5},
    "dryskin": {FIRE: 1.25, WATER: 0.0},  # Adds a weakness while granting an immunity
    "fluffy": {FIRE: 2.0}                  # Doubles damage taken from contact/fire
}

# battle formats
DOUBLES_FORMAT = "GEN_9_DOUBLES"

# forms
HISUIAN_FORM="hisuian"
GALARIAN_FORM="galarian"
ALOLAN_FORM="alolan"
BASE_FORM="base"

# Roles
ROLE_SUPPORT="support"
ROLE_SPECIAL_THREAT="special_threat"
ROLE_PHYSICAL_THREAT="physical_threat"
ROLE_DEFENSIVE="defensive"

# move categories
PHYSICAL_CATEGORY = "physical"
SPECIAL_CATEGORY = "special"
STATUS_CATEGORY = "status"

# move headers
EGG_MOVE_HEADER = "egg"
TM_MOVE_HEADER = "tm"
TUTOR_MOVE_HEADER = "tutor"

#Tags
#  has tags
TAG_HAS_TRICK_ROOM = "has_trick_room"
TAG_HAS_SPEED_CONTROL = "has_speed_control"
TAG_HAS_SUN = "has_sun"
TAG_HAS_RAIN = "has_rain"
TAG_HAS_SAND = "has_sand"
TAG_HAS_SNOW = "has_snow"

#  needs tags
TAG_NEEDS_TRICK_ROOM = "needs_trick_room"
TAG_NEEDS_SPEED_CONTROL = "needs_speed_control"
TAG_NEEDS_SUN = "needs_sun"
TAG_NEEDS_RAIN = "needs_rain"
TAG_NEEDS_SAND = "needs_sand"
TAG_NEEDS_SNOW = "needs_snow"
TAG_NEEDS_PHYSICAL_THREAT = "needs_physical_threat"
TAG_NEEDS_SPECIAL_THREAT = "needs_special_threat"
TAG_NEEDS_SUPPORT = "needs_support"

TAG_SET= {
    #  has tags
    TAG_HAS_TRICK_ROOM,
    TAG_HAS_SPEED_CONTROL,
    TAG_HAS_SUN,
    TAG_HAS_RAIN,
    TAG_HAS_SAND,
    TAG_HAS_SNOW,

    #  needs tags
    TAG_NEEDS_TRICK_ROOM,
    TAG_NEEDS_SPEED_CONTROL,
    TAG_NEEDS_SUN,
    TAG_NEEDS_RAIN,
    TAG_NEEDS_SAND,
    TAG_NEEDS_SNOW,
    TAG_NEEDS_PHYSICAL_THREAT,
    TAG_NEEDS_SPECIAL_THREAT,
    TAG_NEEDS_SUPPORT,
}

TAG_MOVE_MULTIPLIERS = {
    TAG_HAS_SNOW: SNOW_EFFECTED_MOVES,
    TAG_HAS_RAIN: RAIN_EFFECTED_MOVES,
    TAG_HAS_SUN: SUN_EFFECTED_MOVES,
    TAG_HAS_SAND: SAND_EFFECTED_MOVES,
}


# team structures
TEAM_BALANCED = [
    ROLE_SUPPORT,
    ROLE_SUPPORT,
    ROLE_SPECIAL_THREAT,
    ROLE_SPECIAL_THREAT,
    ROLE_PHYSICAL_THREAT,
    ROLE_PHYSICAL_THREAT
]
TEAM_SETUP = [
    ROLE_SUPPORT,
    ROLE_SUPPORT,
    ROLE_SUPPORT,
    ROLE_DEFENSIVE,
    ROLE_DEFENSIVE,
    ROLE_DEFENSIVE
]
TEAM_OFFENSIVE = [
    ROLE_SUPPORT,
    ROLE_SPECIAL_THREAT,
    ROLE_SPECIAL_THREAT,
    ROLE_SPECIAL_THREAT,
    ROLE_PHYSICAL_THREAT,
    ROLE_PHYSICAL_THREAT,
]

# tier ranking
S_PLUS_TIER = 0
S_TIER = 1
A_PLUS_TIER = 2
A_TIER = 3
A_MINUS_TIER = 4
B_PLUS_TIER = 5
B_TIER = 6
B_MINUS_TIER = 7
C_PLUS_TIER = 8
C_TIER = 9
C_MINUS_TIER = 10
D_PLUS_TIER = 11
D_TIER = 12
D_MINUS_TIER = 13
F_PLUS_TIER = 14
F_TIER = 15
F_MINUS_TIER = 16

# TYPE_LOCKED_TRAINERS = {
#   # english
#   # gen 1
#   "Brock": "Rock",
#   "Misty": "Water",
#   "Lt. Surge": "Electric",
#   "Erika": "Grass",
#   "Koga": "Poison",
#   "Janine": "Poison",
#   "Sabrina": "Psychic",
#   "Blaine": "Fire",
#   "Giovanni": "Ground",
#   "Blue": "Various",

#   # gen 2
#   "Falkner": "Flying",
#   "Bugsy": "Bug",
#   "Whitney": "Normal",
#   "Morty": "Ghost",
#   "Chuck": "Fighting",
#   "Jasmine": "Steel",
#   "Pryce": "Ice",
#   "Clair": "Dragon",

#   # gen 3
#   "Roxanne": "Rock",
#   "Brawly": "Fighting",
#   "Wattson": "Electric",
#   "Flannery": "Fire",
#   "Norman": "Normal",
#   "Winona": "Flying",
#   "Tate and Liza": "Psychic",
#   "Wallace": "Water",
#   "Juan": "Water",

#   # gen 4
#   "Roark": "Rock",
#   "Gardenia": "Grass",
#   "Maylene": "Fighting",
#   "Crasher Wake": "Water",
#   "Fantina": "Ghost",
#   "Byron": "Steel",
#   "Candice": "Ice",
#   "Volkner": "Electric",

#   # gen 5
#   "Cilan": "Grass",
#   "Chili": "Fire",
#   "Cress": "Water",
#   "Lenora": "Normal",
#   "Burgh": "Bug",
#   "Elesa": "Electric",
#   "Clay": "Ground",
#   "Skyla": "Flying",
#   "Brycen": "Ice",
#   "Drayden": "Dragon",
#   "Iris": "Dragon",

#   "Cheren": "Normal",
#   "Roxie": "Poison",
#   "Marlon": "Water",

#   # gen 6
#   "Viola": "Bug",
#   "Grant": "Rock",
#   "Korrina": "Fighting",
#   "Ramos": "Grass",
#   "Clemont": "Electric",
#   "Valerie": "Fairy",
#   "Olympia": "Psychic",
#   "Wulfric": "Ice",

#   # gen 8
#   "Milo": "Grass",
#   "Nessa": "Water",
#   "Kabu": "Fire",
#   "Bea": "Fighting",
#   "Allister": "Ghost",
#   "Opal": "Fairy",
#   "Gordie": "Rock",
#   "Melony": "Ice",
#   "Piers": "Dark",
#   "Marnie": "Dark",
#   "Raihan": "Dragon",

#   # gen 9
#   "Katy": "Bug",
#   "Brassius": "Grass",
#   "Iono": "Electric",
#   "Kofu": "Water",
#   "Larry": "Normal",
#   "Ryme": "Ghost",
#   "Tulip": "Psychic",
#   "Grusha": "Ice",

#   # italian
#   # gen 2
#   "Valerio": FLYING,
#   "Raffaello": BUG,
#   "Chiara": NORMAL,
#   "Angelo": GHOST,
#   "Furio": FIGHTING,
#   "Jasmine": STEEL,
#   "Alfredo": ICE,
#   "Sandra": DRAGON,
  
#   # gen 3
# }

TYPE_LOCKED_TRAINERS = {
    "brock": ROCK,
    "misty": WATER,
    "lt. surge": ELECTRIC,
    "erika": GRASS,
    "koga": POISON,
    "janine": POISON,
    "sabrina": PSYCHIC,
    "blaine": FIRE,
    "giovanni": GROUND,

    "lorelei": ICE,
    "bruno": FIGHTING,
    "agatha": GHOST,
    "lance": DRAGON,

    "falkner": FLYING,
    "bugsy": BUG,
    "whitney": NORMAL,
    "morty": GHOST,
    "chuck": FIGHTING,
    "jasmine": STEEL,
    "pryce": ICE,
    "clair": DRAGON,

    "roxanne": ROCK,
    "brawly": FIGHTING,
    "wattson": ELECTRIC,
    "flannery": FIRE,
    "norman": NORMAL,
    "winona": FLYING,
    "tate and liza": PSYCHIC,
    "wallace": WATER,
    "juan": WATER,
    "roark": ROCK,
    "gardenia": GRASS,
    "maylene": FIGHTING,
    "crasher wake": WATER,
    "fantina": GHOST,
    "byron": STEEL,
    "candice": ICE,
    "volkner": ELECTRIC,
    "cilan": GRASS,
    "chili": FIRE,
    "cress": WATER,
    "lenora": NORMAL,
    "burgh": BUG,
    "elesa": ELECTRIC,
    "clay": GROUND,
    "skyla": FLYING,
    "brycen": ICE,
    "drayden": DRAGON,
    "iris": DRAGON,
    "cheren": NORMAL,
    "roxie": POISON,
    "marlon": WATER,
    "viola": BUG,
    "grant": ROCK,
    "korrina": FIGHTING,
    "ramos": GRASS,
    "clemont": ELECTRIC,
    "valerie": FAIRY,
    "olympia": PSYCHIC,
    "wulfric": ICE,
    "milo": GRASS,
    "nessa": WATER,
    "kabu": FIRE,
    "bea": FIGHTING,
    "allister": GHOST,
    "opal": FAIRY,
    "gordie": ROCK,
    "melony": ICE,
    "piers": DARK,
    "marnie": DARK,
    "raihan": DRAGON,
    "katy": BUG,
    "brassius": GRASS,
    "iono": ELECTRIC,
    "kofu": WATER,
    "larry": NORMAL,
    "ryme": GHOST,
    "tulip": PSYCHIC,
    "grusha": ICE,

    # italian
    # gen 2
    "valerio": FLYING,
    "raffaello": BUG,
    "chiara": NORMAL,
    "angelo": GHOST,
    "furio": FIGHTING,
    "alfredo": ICE,
    "sandra": DRAGON,

    "pino": PSYCHIC,
    # "koga": POISON, dup
    "bruno": FIGHTING,
    "karen": DARK,
    
    # gen 3
    "petra": ROCK,
    "rudi": FIGHTING,
    "walter": ELECTRIC,
    "flammetta": FIRE,
    "norman": NORMAL,
    "alice": FLYING,
    "tell & pat": PSYCHIC,

    "fosco": DARK,
    "ester": GHOST,
    "frida": ICE,
    "drake": DRAGON,

    # gen 4
    "pedro": ROCK,
    "gardenia": GRASS,
    "marzia": FIGHTING,
    "omar": WATER,
    "fannie": GHOST,
    "ferruccio": STEEL,
    "bianca": ICE,
    "corrado": ELECTRIC,

    "aaron": BUG,
    "terrie": GROUND,
    "vulcano": FIRE,
    "luciano": PSYCHIC,
}

GYM_LEADER_TITLES = {
    "kanto leader",
    "johto leader",
    "hoenn leader",
    "sinnoh leader",
    "unova leader",
    "kalos leader",
    "alola leader",
    "galar leader",
    "paldea leader",
    "gym leader",
    "leader"
}

ELITE_FOUR_TITLES = {
    "elite 4",
    "elite four"
}

# items
CHOICE_SCARF = 'choice_scarf'
COMMON_ITEM_WEIGHTS = {
    "quick_claw": 10,
    "air_balloon": 10,
    "leftovers": 40,
    "focus_sash": 5,
    "sitrus_berry": 20,
}
COMMON_ATTACK_ITEMS = {
    "life_orb": 10,
    "shell_bell": 10,
    "scope_lens": 10,
    "wide_lens": 10,
    "expert_belt": 20,
    CHOICE_SCARF: 20,
    "assault_vest": 10,

}

ITEM_WEIGHTS = {
    ROLE_SUPPORT:{
        **COMMON_ITEM_WEIGHTS,
        "rocky_helmet": 20,
    },
    ROLE_SPECIAL_THREAT: {
        **COMMON_ITEM_WEIGHTS,
        **COMMON_ATTACK_ITEMS,
        "wise_glasses": 20,
        "choice_specs": 10,
    },
    ROLE_PHYSICAL_THREAT: {
        **COMMON_ITEM_WEIGHTS,
        **COMMON_ATTACK_ITEMS,
        "muscle_band": 20,
        "choice_band": 10,
    }
}
TYPE_BOOSTING_ITEMS = {
    NORMAL: 'silk_scarf', 
    FIRE: 'charcoal', 
    WATER: 'mystic_water', 
    GRASS: 'miracle_seed', 
    ELECTRIC: 'magnet', 
    ICE: 'never_melt_ice', 
    FIGHTING: 'black_belt', 
    POISON: 'poison_barb', 
    GROUND: 'soft_sand', 
    FLYING: 'sharp_beak', 
    PSYCHIC: 'twisted_spoon', 
    BUG: 'silver_powder', 
    ROCK: 'hard_stone', 
    GHOST: 'spell_tag', 
    DRAGON: 'dragon_fang', 
    DARK: 'black_glasses', 
    STEEL: 'metal_coat', 
    FAIRY: 'fairy_feather',
}

NO_STATUS_ITEMS = {
    "choice_band",
    "choice_specs",
    CHOICE_SCARF,
    "assault_vest",
}

HIGH_SPEED_CUTOFF = 120
LOW_SPEED_CUTOFF = 80

RAIN_SETTING_ABILITIES = {
    'drizzle',
    'primordialsea',
}
SUN_SETTING_ABILITIES = {
    'drought',
    'desolateland',
    'orichalcumpulse',
}
SNOW_SETTING_ABILITIES = {
    'snowwarning',
}
SAND_SETTING_ABILITIES = {
    'sandstream',
    'sandspit',
}