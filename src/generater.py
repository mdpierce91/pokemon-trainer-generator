import math
import random
import traceback

from data import get_defenses_score
from models.cobblemon_form import CobblemonSpecies
from models.cobbleverse_trainer import CobbleverseAI, CobbleverseAIData, CobbleverseTrainer, TeamMember
from pokemon_database import PokemonDatabase
from special_species import SpecialSpecies
from team_coach import TeamCoach
from consts import *
from trainers import get_type_lock


class RoleChoice():
    role: str | None
    level: int | None

    def __init__(self, role: str| None = None, level: int | None = None):
        self.role = role
        self.level = level
        pass

class TierRange():
    low: int
    high: int

    def __init__(self, low:int=F_MINUS_TIER, high:int=S_PLUS_TIER):
        self.low = low
        self.high = high
        pass

def generate_trainer(trainer_shell: CobbleverseTrainer, pokemon_database: PokemonDatabase, role_weight_unit: int = 10, replace_ai=True,battle_format=DOUBLES_FORMAT):
    try:
        # TODO: update items and item choice logic
        # TODO: add protect unique move
        # TODO: rate/fix good vs bad abilities
        print(f'start generate trainer')
        
        type_lock = get_type_lock(trainer_shell.name.literal)
        if not type_lock and trainer_shell.identity:
            type_lock = get_type_lock(trainer_shell.identity)

        coach = TeamCoach(type_lock=type_lock)

        # Starting Role Weights
        roles_weighted = {
            # ROLE_DEFENSIVE: role_weight_unit * 5,
            ROLE_PHYSICAL_THREAT: role_weight_unit * 5,
            ROLE_SPECIAL_THREAT: role_weight_unit * 5,
            ROLE_SUPPORT: role_weight_unit * 5,
        }

        team_roles: list[str] = choose_roles_for_trainer(coach=coach,trainer_shell=trainer_shell, roles_weighted=roles_weighted)
        new_team: list[TeamMember] = choose_species_for_trainer(database=pokemon_database, coach=coach, trainer_shell=trainer_shell,team_roles=team_roles)
        trainer_shell.team = new_team
        if replace_ai:
            trainer_shell.ai = CobbleverseAI(
                type="rb",
                data=CobbleverseAIData(
                    canTera= True,
                )
            )
        trainer_shell.battleFormat = battle_format

        # print team to console
        print(f'generated new team for trainer: {trainer_shell.name.literal}')
        for new_member in trainer_shell.team:
            description = f'  lvl:{new_member.level} {new_member.species}'
            if new_member.form is not None:
                description += f'-{new_member.form}'
            print(description)

        return trainer_shell


    except Exception as e:
        print("Failed to generate trainer from shell")
        print(e)
        print(trainer_shell)
        print(traceback.format_exc())
        raise e

# choose a list of roles to replace the team of a given trainer
def choose_roles_for_trainer(coach: TeamCoach, trainer_shell: CobbleverseTrainer, roles_weighted: dict[str,int]) -> list[RoleChoice]:
    try:
        team_roles: list[RoleChoice] = []
        print(f'choosing roles for team')
        highest_level = 1
        # for each pokemon in shell choose a role
        for team_member in trainer_shell.team:
            print(f'choosing a pokemon to replace:{team_member.species} for level:{team_member.level}')
            if team_member.level > highest_level:
                highest_level = team_member.level
            
            new_choice = choose_role(roles_weighted=roles_weighted,level=team_member.level)

            # add chosen role to the team list
            team_roles.append(new_choice)
            # reduce weight of role that was just chosen
            roles_weighted[new_choice.role] *= 0.5
            
        min_team_size = 2
        if highest_level > 40:
            min_team_size = 6
        elif highest_level > 35:
            min_team_size = 5
        elif highest_level > 25:
            min_team_size = 4
        elif highest_level > 15:
            min_team_size = 3
        for i in range(min_team_size - len(team_roles)):
            print(f'choosing a pokemon for level:{highest_level} to fill to min team')
            new_choice = choose_role(roles_weighted=roles_weighted,level=team_member.level)

            # add chosen role to the team list
            team_roles.append(new_choice)
            # reduce weight of role that was just chosen
            roles_weighted[new_choice.role] *= 0.5


        return team_roles
    except Exception as e:
        print("Failed to generate list of roles for team")
        print(e)
        raise e        
    
def choose_role(roles_weighted, level):
    # split the weighted roles into the format the random.choices expects
    role_keys = []
    role_weights = []
    for k,v in roles_weighted.items():
        role_keys.append(k)
        role_weights.append(v)
    # choose role
    chosen_role = random.choices(population=role_keys, weights=role_weights)[0]
    print(f'chose {chosen_role}')
    new_choice = RoleChoice(role=chosen_role, level=level)
    return new_choice

# choose pokemon species for a given trainer from a list of roles
def choose_species_for_trainer(database: PokemonDatabase, coach: TeamCoach, trainer_shell: CobbleverseTrainer, team_roles: list[RoleChoice]) -> list[TeamMember]:
    try:
        print(f'choosing species for team')

        team: list[TeamMember] = []
        for role_choice in team_roles:
            print(f'choose pokemon for role: {role_choice.role} and level: {role_choice.level}')
            #     choose a tier
            #         based on existing team and level
            tier_range = choose_species_tier(role_choice.level)

            #     choose from tag weights
            #       speed control
            tags = choose_tags(coach=coach)

            #     choose a pokemon given role and level and existing team types and roles
            #         get name, form, ability
            #         select name, form, list[ability] from RoleChoices
            matches = get_list_of_matches(database, role=role_choice.role, level=role_choice.level, tier_range=tier_range)

            
            matches = remove_current_team_from_matches(team=team,matches=matches)
            
            # if gym leader, need to filter pokemon with type bias
            if coach.type_lock:
                type_bias = coach.type_lock
                primary_biased_matches = list(filter(lambda matched_primary_type: matched_primary_type.get("primary_type",None) == type_bias, matches))
                secondary_biased_matches = list(filter(lambda matched_secondary_type: matched_secondary_type.get("secondary_type",None) == type_bias, matches))
                mixed_biased_matches = primary_biased_matches + secondary_biased_matches
                # no matches
                if not mixed_biased_matches or len(mixed_biased_matches) == 0:
                    # try again with no role specified
                    mixed_biased_matches = database.get_species_by_type_and_tier(type=type_bias,level=role_choice.level,max_tier=tier_range.high,min_tier=tier_range.low)

                if mixed_biased_matches and len(mixed_biased_matches):
                    matches = mixed_biased_matches
            
            print(f'Filtering matches by tags')
            tag_matches = matches.copy()
            for tag in tags:
                more_tags = list(filter(lambda matched_tag: tag in matched_tag and matched_tag[tag] == True, matches))
                # if nothing matches the tag filter, ignore this tag and move to the next tag
                if not more_tags:
                    print(f'no matches found for tag {tag}')
                    continue
                else:
                    tag_matches = more_tags
            print(f'finished filtering by tags, ended up with {len(tag_matches)} results')

            # TODO: filter by team weaknesses
            
            chosen_pokemon = random.choice(tag_matches if tag_matches and len(tag_matches) > 0 else matches)
            
            SpecialSpecies.check_and_apply(chosen_pokemon)

            cobblemon_raw_species: dict = database.find_all_records(collection_name=database.cobblemon_collection, query={"name": chosen_pokemon["species"]},)[0]
            cobblemon_species = CobblemonSpecies.model_validate(cobblemon_raw_species)

            coach.chosen_item = choose_item(chosen_pokemon=chosen_pokemon, cobblemon_species=cobblemon_species, role_choice=role_choice)
            
            chosen_moves: dict = choose_moves_for_pokemon(database=database, chosen_pokemon=chosen_pokemon, cobblemon_species=cobblemon_species, tags=tags, coach=coach, role_choice=role_choice)

            moves_list = list(chosen_moves.keys())[:4]



            # TODO get base stats here to set Ev's

            ev_max_attack = {
                "hp": 4,
                "atk": 252,
                "spe": 252
            }
            ev_split_hp_atk = {
                "hp": 128,
                "atk": 128,
                "spe": 252
            }
            ev_split_low_spe_atk = {
                "hp": 252,
                "atk": 252,
                "spe": 4
            }
            ev_max_spa = {
                "hp": 4,
                "spa": 252,
                "spe": 252
            }
            ev_split_hp_spa = {
                "hp": 128,
                "spa": 128,
                "spe": 252
            }
            ev_split_low_spe_spa = {
                "hp": 252,
                "spa": 252,
                "spe": 4
            }
            ev_max_hp_max_spe = {
                "hp": 252,
                "def": 4,
                "spe": 252
            }
            
            evs = None
            nature = 'serious'
            if role_choice.level >= 45:
                if role_choice.role == ROLE_PHYSICAL_THREAT:
                    evs = random.choice([ev_max_attack,ev_split_hp_atk,ev_split_low_spe_atk])
                    nature = random.choice(["adamant","jolly"])
                elif role_choice.role == ROLE_SPECIAL_THREAT:
                    evs = random.choice([ev_max_spa,ev_split_hp_spa,ev_split_low_spe_spa])
                    nature = random.choice(["modest","timid"])
                else:
                    evs = ev_max_hp_max_spe
                    


            # TODO: hardcoded values
            new_member = TeamMember(
                species=chosen_pokemon["species"],
                ability=chosen_pokemon["ability"],
                form=chosen_pokemon["form"],
                gender="FEMALE",
                level=role_choice.level,
                heldItem=coach.chosen_item,
                moveset=moves_list,
                gimmicks=None,
                nature=nature,
                aspects=chosen_pokemon.get("aspects",None),
                ivs={
                    "hp": 31,
                    "atk": 31,
                    "def": 31,
                    "spa": 31,
                    "spd": 31,
                    "spe": 31
                },
                evs=evs,
            )
            team.append(new_member)
            coach.update_tags(chosen_pokemon, role_choice.role)
        return team
    except Exception as e:
        print(f'Failed to choose species for trainer')
        print(e)
        raise e
    
def choose_item(chosen_pokemon:dict, cobblemon_species: CobblemonSpecies, role_choice: RoleChoice, has_status: bool = False) -> str | None:
    # get required item
    required_item = chosen_pokemon.get("required_item", None)
    if required_item:
        return required_item
    
    item_options = []
    # choose an item based on level and role
    if role_choice.role in ITEM_WEIGHTS:
        item_options = ITEM_WEIGHTS[role_choice.role]
    else:
        print(f'unable to find items for {role_choice.role}, using common items')
        item_options = COMMON_ITEM_WEIGHTS

    base_stats = cobblemon_species.form_stats(chosen_pokemon.get("form", None))
    defensive_score = get_defenses_score(base_stats)
    # always give un-evolved pokemon eviolite
    if cobblemon_species.evolutions and len(cobblemon_species.evolutions) > 0 and role_choice.level > 30:
        return "eviolite"
    # Flygon's effective health
    if defensive_score > 12800:
        item_options["leftovers"] = 50
        item_options["sitrus_berry"] = 50
    elif defensive_score < 12800:
        item_options["focus_sash"] = 50
    
    if role_choice.role != ROLE_SUPPORT:
        # type boosting item
        item_options[TYPE_BOOSTING_ITEMS[cobblemon_species.primaryType]] = 10
        if cobblemon_species.secondaryType:
            item_options[TYPE_BOOSTING_ITEMS[cobblemon_species.secondaryType]] = 10
    
    # don't allow locked items if has_status is True
    # don't let species with low movesets use locked items
    if has_status or len(cobblemon_species.moves) < 20:
        for remove_item in NO_STATUS_ITEMS:
            item_options.pop(remove_item, None)


    return random.choices(population=list(item_options.keys()),weights=list(item_options.values()))[0]
    
def remove_current_team_from_matches(team, matches):
    # removed, changed rules to exclude same species even if different form
    # remove current team members
    current_members_set = set()
    for team_member in team:
    #     form = team_member.form 
    #     if "mega" in team_member.form:
    #         form = BASE_FORM
    #     elif "gmax" in team_member.form:
    #         form = BASE_FORM
    #     current_members_set.add((team_member.species,form))
        current_members_set.add(team_member.species)
    
    matches = list(filter(lambda remove_current: remove_current.get("species",None) not in current_members_set, matches))
    return matches
    
def choose_moves_for_pokemon(database: PokemonDatabase, chosen_pokemon: dict, cobblemon_species: CobblemonSpecies, tags: list, coach: TeamCoach, role_choice: RoleChoice)->dict:
    chosen_moves = {}
    original_item = coach.chosen_item
    
    # dicts to hold moves that fit certain tags so we can choose from them to add to the final moveset
    speed_control_moves = {}
    support_moves = {}
    stab_attacks = {}
    coverage_attacks = {}

    # if form is a mega or gmax, get base form abilities
    query_form = chosen_pokemon['form']
    if query_form.startswith('mega'):
        query_form = BASE_FORM
    elif query_form.startswith('gmax'):
        query_form = BASE_FORM
        
    # choose moveset based on level role form and ability
    # get all moves for pokemon
    moves: list[dict] = database.find_all_moves_for_pokemon(species=chosen_pokemon['species'], form=query_form)
    # filter out legacy moves
    legacy_filtered_moves = list(filter(lambda sus_move: not sus_move["move"].startswith("legacy:"), moves))

    # try once to use base form moves
    if len(legacy_filtered_moves) == 0:
        moves = database.find_all_moves_for_pokemon(species=chosen_pokemon['species'], form=BASE_FORM)
        # filter out legacy moves
        legacy_filtered_moves = list(filter(lambda sus_move: not sus_move["move"].startswith("legacy:"), moves))

    # if no moves found error out
    if len(legacy_filtered_moves) == 0:
        raise Exception(f"no moves found for level:{role_choice.level} role: {role_choice.role} {chosen_pokemon["species"]}-{chosen_pokemon["form"]}")

    # get a move from tags if applicible
    for move in legacy_filtered_moves:
        move_components = move["move"].split(":")
        move_name = move_components[-1]
        move_header = move_components[0] if len(move_components) > 1 else None
        min_level = int(move_components[0]) if move_header and move_header.isdigit() else 0


        # skip moves that have a minimum level requirement higher than the pokemon's level
        if min_level > role_choice.level:
            continue
        # skip tms if level is too low
        if move_header == TM_MOVE_HEADER and role_choice.level < 30:
            continue        

        # skip egg moves if level is too low
        if move_header == EGG_MOVE_HEADER and role_choice.level < 40:
            continue

        # skip tutor moves if level is too low
        if move_header == TUTOR_MOVE_HEADER and role_choice.level < 40:
            continue

        move_description = database.find_move_description(move_name=move_name)
        if move_description is None:
            print(f'failed to find move description for {move_name}')
            continue
        if move_name == "trickroom":
            if TAG_HAS_TRICK_ROOM in tags:
                chosen_moves[move_name] = move_description
        elif move_name in SPEED_CONTROL_MOVES:
            # TODO: has tailwind
            speed_control_moves[move_name] = move_description
        elif move_name == "sandstorm":
            if TAG_HAS_SAND in tags and chosen_pokemon['ability'] != "sandstream":
                chosen_moves[move_name] = move_description
        elif move_name == "raindance":
            if TAG_HAS_RAIN in tags and chosen_pokemon['ability'] != "drizzle":
                chosen_moves[move_name] = move_description
        elif move_name == "sunnyday":
            if TAG_HAS_SUN in tags and chosen_pokemon['ability'] != "drought":
                chosen_moves[move_name] = move_description
        elif move_name == "snowscape":
            if TAG_HAS_SNOW in tags and chosen_pokemon['ability'] != "snowwarning":
                chosen_moves[move_name] = move_description
        
        move_power = move_description.get("basePower", 0)
        if move_power > 0:
            move_type = move_description.get("type", None)
            if move_type == chosen_pokemon['primary_type'] or move_type == chosen_pokemon['secondary_type']:
                stab_attacks[move_name] = move_description
            else:
                coverage_attacks[move_name] = move_description
        else:
            support_moves[move_name] = move_description

    attack_moves_count = 0
    support_moves_count = 0
    speed_control_moves_count = 0
    while len(chosen_moves) < 4:
        chosen_move = None
        # only pick attacks if choiced item
        if coach.chosen_item in NO_STATUS_ITEMS:
            if attack_moves_count == 0 and stab_attacks:
                # choose a stab move if we don't have any attacking moves yet
                chosen_move = choose_move_from_set(
                    move_set=stab_attacks, 
                    chosen_moves=chosen_moves, 
                    chosen_pokemon=chosen_pokemon, 
                    role_choice=role_choice, 
                )
                attack_moves_count += 1
            else:
                chosen_move = choose_move_from_set(
                    move_set=stab_attacks | coverage_attacks, 
                    chosen_moves=chosen_moves, 
                    chosen_pokemon=chosen_pokemon, 
                    role_choice=role_choice, 
                )
                attack_moves_count += 1

        elif TAG_HAS_SPEED_CONTROL in tags and speed_control_moves == 0 and speed_control_moves:
            # choose a speed control move if we don't have one yet and there are some available
            chosen_move = choose_move_from_set(
                move_set=speed_control_moves, 
                chosen_moves=chosen_moves, 
                chosen_pokemon=chosen_pokemon, 
                role_choice=role_choice, 
            )
            speed_control_moves_count += 1
        elif attack_moves_count == 0 and stab_attacks:
            # choose a stab move if we don't have any attacking moves yet
            chosen_move = choose_move_from_set(
                move_set=stab_attacks, 
                chosen_moves=chosen_moves, 
                chosen_pokemon=chosen_pokemon, 
                role_choice=role_choice, 
            )
            attack_moves_count += 1
        elif attack_moves_count == 0 and coverage_attacks:
            # choose a coverage move if for some reason we don't have any attacking move or stab options
            chosen_move = choose_move_from_set(
                move_set=coverage_attacks, 
                chosen_moves=chosen_moves, 
                chosen_pokemon=chosen_pokemon, 
                role_choice=role_choice, 
            )
            attack_moves_count += 1
        elif role_choice.role == ROLE_SUPPORT and support_moves:
            chosen_move = choose_move_from_set(
                move_set=support_moves, 
                chosen_moves=chosen_moves, 
                chosen_pokemon=chosen_pokemon, 
                role_choice=role_choice, 
            )
            support_moves_count += 1
        else:
            chosen_move = choose_move_from_set(
                move_set=stab_attacks|coverage_attacks|support_moves|speed_control_moves, 
                chosen_moves=chosen_moves, 
                chosen_pokemon=chosen_pokemon, 
                role_choice=role_choice, 
            )

        # if we succeded to get a move, add it to the set
        if chosen_move:
            chosen_moves[chosen_move["name"]] = chosen_move
        else:
            break

    # if regular method fails, try from all moves for pokemon
    if len(chosen_moves) < 4:
        for i in range(4):
            new_move = choose_move_from_set(
                move_set=stab_attacks|coverage_attacks|support_moves|speed_control_moves,
                chosen_moves=chosen_moves, 
                chosen_pokemon=chosen_pokemon, 
                role_choice=role_choice, 
            )
            if new_move:
                chosen_moves[new_move["name"]] = new_move

    # extra check to change item if its currently set to a no-status item and we have status moves(excluding tailwind)
    if coach.chosen_item in NO_STATUS_ITEMS:
        for move_name, move_description in chosen_moves.items():
            # exclude tailwind
            # if move_name == 'tailwind':
            #     # TODO: tailwind
            #     pass
            if move_description.get("category", None) == STATUS_CATEGORY:
                # choose a different move if we have at least one status move
                coach.chosen_item = choose_item(
                    chosen_pokemon=chosen_pokemon, 
                    cobblemon_species=cobblemon_species, 
                    role_choice=role_choice, 
                    has_status=True
                )
                break

    # if still no moves, fallback to splash
    if len(chosen_moves) == 0:
        return {"splash": {}}
    
    if original_item != coach.chosen_item:
        print(f'original item was {original_item}')
        print(f"final item {coach.chosen_item}")
    
    return chosen_moves

def format_pokemon_for_trainer(database, chosen_pokemon, moves_list, item, coach, trainer_shell):
    print("TODO")
    pass
            

def choose_move_from_set(move_set: dict, chosen_moves: dict, chosen_pokemon: dict, role_choice: RoleChoice):
    weighted_options = {}
    default_weight = 100
    # # spread attacks
    # spread_attacks = {}
    # # hits partner
    # hits_partner = {}
    # # single target
    # single_target = {}
    # for move_name, move_description in move_set.items():
    #     target = move_description.get("target", None)
    #     if target in SINGLE_TARGET_MOVES:
    #         single_target[move_name] = move_description
    #     elif target in HITS_PARTNER_MOVES:
    #         hits_partner[move_name] = move_description
    #     elif target in SPREAD_MOVES:
    #         spread_attacks[move_name] = move_description
    #     else:
    #         print(f'unknown move target type: {target} for move {move_name}, ignoring move for attack choice')
    #         continue

    pokemon_types = set()
    primary_type = chosen_pokemon.get("primary_type", None)
    secondary_type = chosen_pokemon.get("secondary_type", None)
    pokemon_types.add(primary_type)
    pokemon_types.add(secondary_type)

    base_stats = chosen_pokemon.get("baseStats", {})
    atk_stat = float(base_stats.get("attack", 50))
    spa_stat = float(base_stats.get("special_attack", 50))
    
    atk_spa_ratio = atk_stat/spa_stat
    spa_atk_ratio = spa_stat/atk_stat

    # check every move
    for move_name, move_description in move_set.items():
        # ignore duplicates
        if move_name in chosen_moves:
            continue
        
        if move_description is None:
            continue
            
        if move_name == 'protect':
            weighted_options[move_name] = int(default_weight * 10)
            continue



        move_score = default_weight
        power = move_description.get("power", 0)

        # greatly reduce wrong category of moves
        move_category = move_description.get("category", None)
        if role_choice.role == ROLE_PHYSICAL_THREAT and move_category == SPECIAL_CATEGORY and role_choice.level > 25:
            move_score = 1
        elif role_choice.role == ROLE_SPECIAL_THREAT and move_category == PHYSICAL_CATEGORY and role_choice.level > 25:
            move_score = 1         

        if role_choice.role != ROLE_SUPPORT and move_category == STATUS_CATEGORY:
            move_score *= 0.25
        # special cases
        if move_name == "trickroom":
            # TODO: if the pokemon is slow, prefer trick room. if the pokemon is fast, avoid trick room
            move_score *= 4
        if move_name == "tailwind":
            move_score *= 4
        if move_name == "wideguard":
            move_score *= 4

        # weight moves based on power
        if power > 0:
            if power > 100:
                move_score += 2 * default_weight
            elif power > 70:
                move_score += default_weight
            elif power >= 40:
                pass
            else:
                move_score -= default_weight/2

            # increase weight of priority attacks
            if move_description.get("priority", 0) > 0:
                move_score *= 4

            # reduce weight of moves of the same type already in moveset(only for attacks)
            move_type = move_description.get("type", None)
            if move_type:
                for existing_move_name, existing_move_description in chosen_moves.items():
                    if existing_move_description.get("type", None) == move_type:
                        move_score *= 0.25
            
            # increase weight of stab attacks
            if move_type in pokemon_types:
                move_score *= 1.5
            
            # if mixed or support ratio by pref stat
            if move_category == PHYSICAL_CATEGORY:
                move_score *= atk_spa_ratio
            elif move_category == SPECIAL_CATEGORY:
                move_score *= spa_atk_ratio 

        # flags weighting
        flags = move_description.get("flags", {})
        for flag, value in flags.items():
            # recharge moves ie. Hyper Beam
            if flag == "recharge":
                move_score *= 0.5
            # charge moves ie. Solar Beam
            elif flag == "charge":
                move_score *= 0.25

            


        target = move_description.get("target", None)
        # weight spread moves
        if target in SPREAD_MOVES:
            move_score *= 2
        # weight moves that hit partner pokemon
        elif target in HITS_PARTNER_MOVES:
            move_score *= 0.75
        elif target in SINGLE_TARGET_MOVES:
            pass
        # else:
        #     print(f'unknown move target type: {target} for move {move_name}, ignoring move for attack choice')
        #     continue


        # weight moves based on accuracy
        # if the pokemon has no guard or compound eyes, ignore accuracy scaling
        if chosen_pokemon['ability'] != "noguard" and chosen_pokemon['ability'] != "compoundeyes":
            accuracy = move_description.get("accuracy", 100)
            if accuracy < 80:
                move_score = 1
            else:
                move_score *= float(accuracy)/100
            
        
        # weight moves based on secondary effects
        secondary_effect = move_description.get("secondary", {})
        # boosts are handled later
        if secondary_effect and secondary_effect.get("boosts", None):
            effect_chance = secondary_effect.get("chance", 100)
            # assume secondary effect is good
            move_score += (default_weight * 0.25) * (float(effect_chance) / 100.0)

        # weight self-stat changes
        self_effect = move_description.get("self", {}).get("boosts", {})
        self_effect_chance = move_description.get("self", {}).get("chance", 100)
        if not self_effect:
            self_effect = move_description.get("secondary_effect", {}).get("self", {}).get("boosts", {})
            self_effect_chance = move_description.get("secondary_effect", {}).get("self", {}).get("chance", 100)
        stat_value = 1.0
        cumulative_effect = 1.0
        for key, value in self_effect.items():
            if value > 0:
                # good effect
                cumulative_effect *= 1.5 * (float(self_effect_chance) / 100.0) * float(abs(value))
            else:
                # bad effect
                cumulative_effect *= 0.875 * (100.0/float(self_effect_chance)) * float(abs(value))
        move_score *= cumulative_effect

        weighted_options[move_name] = max(int(move_score), 1)

    if len(weighted_options) == 0:
        print(f"failed to choose move")
        return None

    # choose from weighted options
    chosen_move_name = random.choices(population=list(weighted_options.keys()), weights=list(weighted_options.values()))[0]
    return move_set[chosen_move_name]  

def choose_species_tier(level:int) -> TierRange:
    try:
        print(f'choosing tier from ')
        if level is None:
            print('level cannot be none')
            raise TypeError
        tier_range: TierRange = TierRange()
        
        if level > 70:
            tier_range.high = S_PLUS_TIER
            tier_range.low = C_PLUS_TIER
        elif level > 58:
            tier_range.high = A_PLUS_TIER
            tier_range.low = D_PLUS_TIER
        elif level > 44:
            tier_range.high = B_PLUS_TIER
            tier_range.low = D_MINUS_TIER
        elif level > 30:
            tier_range.high = C_PLUS_TIER
            tier_range.low = D_MINUS_TIER
        elif level > 20:
            tier_range.high = D_PLUS_TIER
            tier_range.low = F_MINUS_TIER
        elif level > 10:
            tier_range.high = D_MINUS_TIER
            tier_range.low = F_MINUS_TIER
        else:
            tier_range.high = F_PLUS_TIER
            tier_range.low = F_MINUS_TIER
        
        return tier_range
    except Exception as e:
        print(f'Failed to choose tier for species')
        print(e)
        raise e
    
def choose_tags(coach: TeamCoach):
    tags = []
    try:
        for key,value in coach.tags_weighted.items():
            try:
                if value == 0:
                    continue
                else:
                    chosen_tag = random.choices(population=[key, None], weights=[value, coach.weight_unit])[0]
                    if chosen_tag is not None:
                        tags.append(chosen_tag)
            except Exception as e:
                print(f'failed to read tag to choose')
                print(e)
        return tags

    except Exception as e:
        print(f'Failed to choose tier for species')
        print(e)
        print(traceback.format_exc())
        return tags
    
def get_list_of_matches(pokemon_database: PokemonDatabase, level:int, role:str, tier_range: TierRange):
    try:
        print("getting list of matches")
        matches = pokemon_database.get_species_by_role_and_tier(role=role, level=level, min_tier=tier_range.low, max_tier=tier_range.high)
        if matches:
            return matches
        else:
            raise TypeError("no matches found")
    except Exception as e:
        print(f'Failed to get list of matches for level:{level} role:{role}, tier: {tier_range.low}-{tier_range.high}')
        print(e)
        print(traceback.format_exc())
        raise e
