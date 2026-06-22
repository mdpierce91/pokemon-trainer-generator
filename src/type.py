# Type Constants (Lowercase string values)
import string

from consts import ABILITY_MODIFIERS, DEFENSE_CHART, TYPES


def get_defensive_chart(type1:str, type2:str|None=None, ability:str|None=None) -> dict:
    """Calculates defensive matchup factoring in typing and ability."""
    resistances = {}
    
    # Normalize ability input string
    ability_key = format_ability_name(ability)
    
    for attack_type in TYPES:
        multiplier = 1.0 
        
        # 1. Apply Type 1 Modifiers
        if attack_type in DEFENSE_CHART[type1]:
            multiplier *= DEFENSE_CHART[type1][attack_type]
            
        # 2. Apply Type 2 Modifiers (if dual-typed)
        if type2 and attack_type in DEFENSE_CHART[type2]:
            multiplier *= DEFENSE_CHART[type2][attack_type]
            
        # 3. Apply Ability Modifiers
        if ability_key and ability_key in ABILITY_MODIFIERS:
            if attack_type in ABILITY_MODIFIERS[ability_key]:
                multiplier *= ABILITY_MODIFIERS[ability_key][attack_type]
            
        resistances[attack_type] = multiplier
        
    return resistances

def format_ability_name(ability:str|None)->str|None:
    return ability.lower().strip().replace(' ', '').translate(str.maketrans('', '', string.punctuation)) if ability else None

def test_type_chart(type1:str, ability:str | None = None, type2:str|None = None):
    ability_key = format_ability_name(ability)

    results = get_defensive_chart(type1, type2, ability=ability_key)

    # Format and print the clean output
    header = f"Defensive Matchup for {type1.title()}{ "/"+ type2.title() if type2 is not None else "" }"
    if ability:
        header += f" with [{ability.title()}]"
    print(f"{header}:\n" + "-" * len(header))

    for atk_type, mult in results.items():
        display_name = atk_type.title()
        if mult > 1.0:
            print(f"{display_name}: {mult}x (Weak)")
        elif 0.0 < mult < 1.0:
            print(f"{display_name}: {mult}x (Resist)")
        elif mult == 0.0:
            print(f"{display_name}: 0x (Immune)")
        else:
            print(f"{display_name}: 1x")