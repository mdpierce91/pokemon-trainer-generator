

import random
import traceback

from models.cobblemon_form import CobblemonSpecies
from models.cobbleverse_trainer import CobbleverseTrainer, TeamMember
from consts import *
from data import get_defenses_score, score_move_power
from models.species_choice import SpeciesChoice
from pokemon_database import PokemonDatabase
from models.role_choice import RoleChoice
from special_species import SpecialSpecies
from models.tier_range import TierRange
from trainers import get_type_lock
from type import get_defensive_chart


class TeamCoach():

    __slots__ = ('type_lock', 
        'database',
        'has_trick_room', 
        'has_speed_control', 
        'needs_speed_control', 
        'needs_trick_room', 
        'physical_threats',
        'special_threats',
        'supports',
        'has_sun',
        'has_rain',
        'has_sand',
        'has_snow',
        'needs_sun',
        'needs_rain',
        'needs_sand',
        'needs_snow',
        'weight_unit',
        'tags_weighted',
        'weaknesses',
        'chosen_item',
        'roles_weighted',
        'role_weight_unit',
        'team_roles',
        'trainer_shell',
    )
    
    
    def __init__(self, database: PokemonDatabase, trainer_shell: CobbleverseTrainer, chosen_item:str|None = None,role_weight_unit: int = 10):
        self.database = database
        self.trainer_shell=trainer_shell
        self.type_lock=self.get_type_lock(trainer_shell)
        self.chosen_item=chosen_item
        self.role_weight_unit = role_weight_unit
        self.has_trick_room = False
        self.has_speed_control = False
        self.needs_speed_control = 0
        self.needs_trick_room = 0
        self.physical_threats = 0
        self.special_threats = 0
        self.supports = 0
        self.has_sun = False
        self.has_rain = False
        self.has_sand = False
        self.has_snow = False
        self.needs_sun = 0
        self.needs_rain = 0
        self.needs_sand = 0
        self.needs_snow = 0
        self.weight_unit = 50
        team_roles = []
    # Starting Tag Weights
        self.tags_weighted = {
            TAG_HAS_TRICK_ROOM: self.weight_unit * 0.2,
            TAG_HAS_SPEED_CONTROL: self.weight_unit * 2,
            TAG_HAS_SUN: 0,
            TAG_HAS_RAIN: 0,
            TAG_HAS_SAND: 0,
            TAG_HAS_SNOW: 0,
            TAG_NEEDS_TRICK_ROOM: 0,
            TAG_NEEDS_SPEED_CONTROL: 0,
            TAG_NEEDS_SUN: 0,
            TAG_NEEDS_RAIN: 0,
            TAG_NEEDS_SAND: 0,
            TAG_NEEDS_SNOW: 0,
            TAG_NEEDS_PHYSICAL_THREAT: 0,
            TAG_NEEDS_SPECIAL_THREAT: 0,
        }
        self.weaknesses = {}
        # Starting Role Weights
        self.roles_weighted = {
            # ROLE_DEFENSIVE: role_weight_unit * 5,
            ROLE_PHYSICAL_THREAT: role_weight_unit * 5,
            ROLE_SPECIAL_THREAT: role_weight_unit * 5,
            ROLE_SUPPORT: role_weight_unit * 5,
        }

    # def __setattr__(self, name, value):
    #     super(TeamCoach, self).setattr(name, value)

    @staticmethod
    def get_type_lock(trainer_shell):
        type_lock = get_type_lock(trainer_shell.name.literal)
        if not type_lock and trainer_shell.identity:
            type_lock = get_type_lock(trainer_shell.identity)
        return type_lock

    def update_tags(self, new_team_member: SpeciesChoice, role:str):
        self.has_rain = self.has_rain or new_team_member.get(TAG_HAS_RAIN, False)
        self.has_sand = self.has_sand or new_team_member.get(TAG_HAS_SAND, False)
        self.has_snow = self.has_snow or new_team_member.get(TAG_HAS_SNOW, False)
        self.has_sun = self.has_sun or new_team_member.get(TAG_HAS_SUN, False)
        self.has_speed_control = self.has_speed_control or new_team_member.get(TAG_HAS_SPEED_CONTROL, False)
        self.has_trick_room = self.has_trick_room or new_team_member.get(TAG_HAS_TRICK_ROOM, False)
        if new_team_member.get(TAG_NEEDS_SUN, False):
            self.needs_sun += 1
        elif new_team_member.get(TAG_NEEDS_RAIN, False):
            self.needs_rain += 1
        elif new_team_member.get(TAG_HAS_SAND, False):
            self.needs_sand += 1
        elif new_team_member.get(TAG_HAS_SNOW, False):
            self.needs_snow += 1
        if role == ROLE_PHYSICAL_THREAT:
            self.physical_threats += 1
        elif role == ROLE_SPECIAL_THREAT:
            self.special_threats += 1
        elif role == ROLE_SUPPORT:
            self.supports += 1
        self.update_weights(new_team_member=new_team_member)
        
    def update_weights(self,new_team_member:dict|None=None):
        if self.has_speed_control:
            self.tags_weighted[TAG_NEEDS_SPEED_CONTROL] = self.weight_unit * 2
        if self.has_trick_room:
            self.tags_weighted[TAG_NEEDS_TRICK_ROOM] = self.weight_unit * 2

        # weather tags
        if self.has_sun:
            self.tags_weighted[TAG_NEEDS_SUN] = self.weight_unit * 2
            self.tags_weighted[TAG_NEEDS_RAIN] = 0
            self.tags_weighted[TAG_NEEDS_SAND] = 0
            self.tags_weighted[TAG_NEEDS_SNOW] = 0
        elif self.has_rain:
            self.tags_weighted[TAG_NEEDS_SUN] = 0
            self.tags_weighted[TAG_NEEDS_RAIN] = self.weight_unit * 2
            self.tags_weighted[TAG_NEEDS_SAND] = 0
            self.tags_weighted[TAG_NEEDS_SNOW] = 0
        elif self.has_sand:
            self.tags_weighted[TAG_NEEDS_SUN] = 0
            self.tags_weighted[TAG_NEEDS_RAIN] = 0
            self.tags_weighted[TAG_NEEDS_SAND] = self.weight_unit * 2
            self.tags_weighted[TAG_NEEDS_SNOW] = 0
        elif self.has_snow:
            self.tags_weighted[TAG_NEEDS_SUN] = 0
            self.tags_weighted[TAG_NEEDS_RAIN] = 0
            self.tags_weighted[TAG_NEEDS_SAND] = 0
            self.tags_weighted[TAG_NEEDS_SNOW] = self.weight_unit * 2
        if self.supports == 0:
            self.tags_weighted[TAG_NEEDS_SUPPORT] = self.weight_unit * 2
        elif self.supports == 1:
            self.tags_weighted[TAG_NEEDS_SUPPORT] = self.weight_unit

        # physical/special balancing
        if self.physical_threats > self.special_threats:
            diff = self.physical_threats - self.special_threats
            self.tags_weighted[TAG_NEEDS_PHYSICAL_THREAT] = self.weight_unit
            self.tags_weighted[TAG_NEEDS_SPECIAL_THREAT] = max(self.weight_unit * diff, 1)
        elif self.physical_threats < self.special_threats:
            diff = self.special_threats - self.physical_threats
            self.tags_weighted[TAG_NEEDS_PHYSICAL_THREAT] = self.weight_unit
            self.tags_weighted[TAG_NEEDS_SPECIAL_THREAT] = max(self.weight_unit * diff, 1)
        else: 
            self.tags_weighted[TAG_NEEDS_PHYSICAL_THREAT] = self.weight_unit
            self.tags_weighted[TAG_NEEDS_SPECIAL_THREAT] = self.weight_unit

        if new_team_member is not None:
            self.update_weaknesses(new_team_member)
        
    def update_weaknesses(self, new_team_member: SpeciesChoice):
        try:
            defensive_type_chart = get_defensive_chart(type1=new_team_member["primary_type"], type2=new_team_member["secondary_type"], ability=new_team_member["ability"])
            for type,multiplier in defensive_type_chart.items():
                # neutral, no change
                if multiplier == 1:
                    continue
                # weak, increase by one
                increment = 1
                # resistant or immune, reduce by one
                if multiplier < 1:
                    increment = -1
                
                if type in self.weaknesses:
                    self.weaknesses[type] += increment
                else:
                    self.weaknesses[type] = increment
        except Exception as e:
            print("Failed to update weaknesses")
            print(e)
            print(traceback.format_exc())

    # choose a list of roles to replace the team of a given trainer
    def choose_roles_for_trainer(self) -> list[RoleChoice]:
        try:
            team_roles: list[RoleChoice] = []
            print(f'choosing roles for team')
            highest_level = 1
            # for each pokemon in shell choose a role
            for team_member in self.trainer_shell.team:
                print(f'choosing a pokemon to replace:{team_member.species} for level:{team_member.level}')
                if team_member.level > highest_level:
                    highest_level = team_member.level
                
                new_choice = self.choose_role(level=team_member.level)

                # add chosen role to the team list
                team_roles.append(new_choice)
                # reduce weight of role that was just chosen
                self.roles_weighted[new_choice.role] *= 0.5
                
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
                new_choice = self.choose_role(level=team_member.level)

                # add chosen role to the team list
                team_roles.append(new_choice)
                # reduce weight of role that was just chosen
                self.roles_weighted[new_choice.role] *= 0.5

            self.team_roles = team_roles
            return team_roles
        except Exception as e:
            print("Failed to generate list of roles for team")
            print(e)
            raise e        
        
    def choose_role(self, level):
        # split the weighted roles into the format the random.choices expects
        role_keys = []
        role_weights = []
        for k,v in self.roles_weighted.items():
            role_keys.append(k)
            role_weights.append(v)
        # choose role
        chosen_role = random.choices(population=role_keys, weights=role_weights)[0]
        print(f'chose {chosen_role}')
        new_choice = RoleChoice(role=chosen_role, level=level)
        return new_choice

    # choose pokemon species for a given trainer from a list of roles
    def choose_species_for_trainer(self) -> list[TeamMember]:
        try:
            print(f'choosing species for team')

            team: list[TeamMember] = []
            for role_choice in self.team_roles:
                print(f'choose pokemon for role: {role_choice.role} and level: {role_choice.level}')
                #     choose a tier
                #         based on existing team and level
                tier_range = self.choose_species_tier(role_choice.level)

                #     choose from tag weights
                #       speed control
                tags = self.choose_tags()

                #     choose a pokemon given role and level and existing team types and roles
                #         get name, form, ability
                #         select name, form, list[ability] from RoleChoices
                matches = self.get_list_of_matches(role=role_choice.role, level=role_choice.level, tier_range=tier_range)

                
                matches = self.remove_current_team_from_matches(team=team,matches=matches)
                
                # if gym leader, need to filter pokemon with type bias
                if self.type_lock:
                    primary_biased_matches = list(filter(lambda matched_primary_type: matched_primary_type.get("primary_type",None) == self.type_lock, matches))
                    secondary_biased_matches = list(filter(lambda matched_secondary_type: matched_secondary_type.get("secondary_type",None) == self.type_lock, matches))
                    mixed_biased_matches = primary_biased_matches + secondary_biased_matches
                    # no matches
                    if not mixed_biased_matches or len(mixed_biased_matches) == 0:
                        # try again with no role specified
                        mixed_biased_matches = self.database.get_species_by_type_and_tier(
                            type=self.type_lock,
                            level=role_choice.level,
                            max_tier=tier_range.high,
                            min_tier=tier_range.low
                        )

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

                cobblemon_raw_species: dict = self.database.find_all_records(collection_name=self.database.cobblemon_collection, query={"name": chosen_pokemon["species"]},)[0]
                cobblemon_species = CobblemonSpecies.model_validate(cobblemon_raw_species)

                self.chosen_item = self.choose_item(chosen_pokemon=chosen_pokemon, cobblemon_species=cobblemon_species, role_choice=role_choice)
                
                chosen_moves: dict = self.choose_moves_for_pokemon(chosen_pokemon=chosen_pokemon, cobblemon_species=cobblemon_species, tags=tags, role_choice=role_choice)

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
                    form=chosen_pokemon["form"] if chosen_pokemon["form"] != BASE_FORM else None,
                    gender="FEMALE",
                    level=role_choice.level,
                    heldItem=[self.chosen_item],
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
                self.update_tags(chosen_pokemon, role_choice.role)
            self.trainer_shell.team = team
            return team
        except Exception as e:
            print(f'Failed to choose species for trainer')
            print(e)
            raise e
        
    def choose_species_tier(self, level:int) -> TierRange:
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
        
    def choose_tags(self):
        tags = []
        try:
            for key,value in self.tags_weighted.items():
                try:
                    if value == 0:
                        continue
                    else:
                        chosen_tag = random.choices(population=[key, None], weights=[value, self.weight_unit])[0]
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
        
    def get_list_of_matches(self, level:int, role:str, tier_range: TierRange):
        try:
            print("getting list of matches")
            matches = self.database.get_species_by_role_and_tier(role=role, level=level, min_tier=tier_range.low, max_tier=tier_range.high)
            if matches:
                return matches
            else:
                raise TypeError("no matches found")
        except Exception as e:
            print(f'Failed to get list of matches for level:{level} role:{role}, tier: {tier_range.low}-{tier_range.high}')
            print(e)
            print(traceback.format_exc())
            raise e
    
    def remove_current_team_from_matches(self, team, matches):
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
        
    def choose_item(self, chosen_pokemon:dict, cobblemon_species: CobblemonSpecies, role_choice: RoleChoice, has_status: bool = False) -> str | None:
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

    def choose_moves_for_pokemon(self, chosen_pokemon: dict, cobblemon_species: CobblemonSpecies, tags: list, role_choice: RoleChoice)->dict:
        chosen_moves = {}
        original_item = self.chosen_item
        
        # dicts to hold moves that fit certain tags so we can choose from them to add to the final moveset
        speed_control_moves = {}
        support_moves = {}
        stab_attacks = {}
        coverage_attacks = {}

        # if form is a mega or gmax, get base form moves
        query_form = chosen_pokemon['form']
        if query_form.startswith('mega'):
            query_form = BASE_FORM
        elif query_form.startswith('gmax'):
            query_form = BASE_FORM
            
        # choose moveset based on level role form and ability
        # get all moves for pokemon
        moves: list[dict] = self.database.find_all_moves_for_pokemon(species=chosen_pokemon['species'], form=query_form)
        # filter out legacy moves
        legacy_filtered_moves = list(filter(lambda sus_move: not sus_move["move"].startswith("legacy:"), moves))

        # try once to use base form moves if we didn't get any moves for chosen form
        if len(legacy_filtered_moves) == 0:
            moves = self.database.find_all_moves_for_pokemon(species=chosen_pokemon['species'], form=BASE_FORM)
            # filter out legacy moves
            legacy_filtered_moves = list(filter(lambda sus_move: not sus_move["move"].startswith("legacy:"), moves))

        # if no moves found, error out
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

            move_description = self.database.find_move_description(move_name=move_name)
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
            if self.chosen_item in NO_STATUS_ITEMS:
                if attack_moves_count == 0 and stab_attacks:
                    # choose a stab move if we don't have any attacking moves yet
                    chosen_move = self.choose_move_from_set(
                        move_set=stab_attacks, 
                        chosen_moves=chosen_moves, 
                        chosen_pokemon=chosen_pokemon, 
                        cobblemon_species=cobblemon_species,
                        role_choice=role_choice, 
                        tags=tags,
                    )
                    attack_moves_count += 1
                else:
                    chosen_move = self.choose_move_from_set(
                        move_set=stab_attacks | coverage_attacks, 
                        chosen_moves=chosen_moves, 
                        chosen_pokemon=chosen_pokemon, 
                        cobblemon_species=cobblemon_species,
                        role_choice=role_choice, 
                        tags=tags,
                    )
                    attack_moves_count += 1

            elif TAG_HAS_SPEED_CONTROL in tags and speed_control_moves_count == 0 and speed_control_moves:
                # choose a speed control move if we don't have one yet and there are some available
                chosen_move = self.choose_move_from_set(
                    move_set=speed_control_moves, 
                    chosen_moves=chosen_moves, 
                    chosen_pokemon=chosen_pokemon, 
                    cobblemon_species=cobblemon_species,
                    role_choice=role_choice, 
                    tags=tags,
                )
                speed_control_moves_count += 1
            elif attack_moves_count == 0 and stab_attacks:
                # choose a stab move if we don't have any attacking moves yet
                chosen_move = self.choose_move_from_set(
                    move_set=stab_attacks, 
                    chosen_moves=chosen_moves, 
                    chosen_pokemon=chosen_pokemon, 
                    cobblemon_species=cobblemon_species,
                    role_choice=role_choice, 
                    tags=tags,
                )
                attack_moves_count += 1
            elif attack_moves_count == 0 and coverage_attacks:
                # choose a coverage move if for some reason we don't have any attacking move or stab options
                chosen_move = self.choose_move_from_set(
                    move_set=coverage_attacks, 
                    chosen_moves=chosen_moves, 
                    chosen_pokemon=chosen_pokemon, 
                    cobblemon_species=cobblemon_species,
                    role_choice=role_choice, 
                    tags=tags,
                )
                attack_moves_count += 1
            elif role_choice.role == ROLE_SUPPORT and support_moves:
                chosen_move = self.choose_move_from_set(
                    move_set=support_moves, 
                    chosen_moves=chosen_moves, 
                    chosen_pokemon=chosen_pokemon, 
                    cobblemon_species=cobblemon_species,
                    role_choice=role_choice, 
                    tags=tags,
                )
                support_moves_count += 1
            else:
                chosen_move = self.choose_move_from_set(
                    move_set=stab_attacks|coverage_attacks|support_moves|speed_control_moves, 
                    chosen_moves=chosen_moves, 
                    chosen_pokemon=chosen_pokemon, 
                    cobblemon_species=cobblemon_species,
                    role_choice=role_choice, 
                    tags=tags,
                )

            # if we succeded to get a move, add it to the set
            if chosen_move:
                chosen_moves[chosen_move["name"]] = chosen_move
            else:
                break

        # if regular method fails, try from all moves for pokemon
        if len(chosen_moves) < 4:
            for i in range(4):
                new_move = self.choose_move_from_set(
                    move_set=stab_attacks|coverage_attacks|support_moves|speed_control_moves,
                    chosen_moves=chosen_moves, 
                    chosen_pokemon=chosen_pokemon, 
                    cobblemon_species=cobblemon_species,
                    role_choice=role_choice, 
                    tags=tags,
                )
                if new_move:
                    chosen_moves[new_move["name"]] = new_move

        # extra check to change item if its currently set to a no-status item and we have status moves(excluding tailwind)
        if self.chosen_item in NO_STATUS_ITEMS:
            for move_name, move_description in chosen_moves.items():
                # exclude tailwind
                # if move_name == 'tailwind':
                #     # TODO: tailwind
                #     pass
                # TODO exceptions for scarf and good scarf moves
                if move_description.get("category", None) == STATUS_CATEGORY:
                    # choose a different move if we have at least one status move
                    self.chosen_item = self.choose_item(
                        chosen_pokemon=chosen_pokemon, 
                        cobblemon_species=cobblemon_species, 
                        role_choice=role_choice, 
                        has_status=True
                    )
                    break

        # if still no moves, fallback to splash
        if len(chosen_moves) == 0:
            return {"splash": {}}
        
        if original_item != self.chosen_item:
            print(f'original item was {original_item}')
            print(f"final item {self.chosen_item}")
        
        return chosen_moves

    def choose_move_from_set(self, move_set: dict, chosen_moves: dict, chosen_pokemon: dict, cobblemon_species: CobblemonSpecies, role_choice: RoleChoice, tags: list):
        weighted_options = {}
        default_weight = 1000
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
        tags_set = set(tags)
        primary_type = chosen_pokemon.get("primary_type", None)
        secondary_type = chosen_pokemon.get("secondary_type", None)
        pokemon_types.add(primary_type)
        pokemon_types.add(secondary_type)
        chosen_ability = chosen_pokemon.get('ability', None)

        form_base_stats = cobblemon_species.form_stats(chosen_pokemon.get("form", None))
        atk_stat = float(form_base_stats.attack)
        spa_stat = float(form_base_stats.special_attack)
        
        atk_spa_ratio = atk_stat/spa_stat
        spa_atk_ratio = spa_stat/atk_stat

        effective_speed = form_base_stats.speed
        if self.chosen_item == CHOICE_SCARF:
            effective_speed *= 1.5


        chosen_types = {}
        for chosen_name, chosen_description in chosen_moves.items():
            chosen_type = chosen_description.get("type", None)
            chosen_power = chosen_description.get("basePower", 0)
            if chosen_type and chosen_power > 0:
                if chosen_type in chosen_types:
                    chosen_types[chosen_type] *= 10
                else:
                    chosen_types[chosen_type] = default_weight
        

        # check every move
        for move_name, move_description in move_set.items():
            # ignore duplicates
            if move_name in chosen_moves:
                continue
            
            if move_description is None:
                continue
            
            ## doubles staples that need no introduction
            # protect
            if move_name == 'protect':
                weighted_options[move_name] = int(default_weight * 10)
                continue

            # fake out
            if move_name == 'fakeout':
                weighted_options[move_name] = int(default_weight * 10)
                continue

            # move data accessing
            move_score = default_weight
            power = move_description.get("basePower", 0)
            move_type = move_description.get("type", None)
            move_category = move_description.get("category", None)
            # does not include self stat changes or secondary effect changes
            stat_changes = move_description.get("boosts", None)
            flags = move_description.get("flags", {})

            # trick room
            if move_name == "trickroom":
                # if tag is set to get trickroom, return it
                if TAG_HAS_TRICK_ROOM in tags_set:
                    return move_set[move_name]
                if self.needs_trick_room > 0:
                    weighted_options[move_name] = int(default_weight * self.needs_trick_room)
                    continue
                if effective_speed < LOW_SPEED_CUTOFF:
                    weighted_options[move_name] = int(default_weight * 4)
                    continue
            # tailwind
            if move_name == "tailwind":
                if TAG_HAS_SPEED_CONTROL in tags_set:
                    return move_set[move_name]
                if self.needs_speed_control > 0:
                    weighted_options[move_name] = int(default_weight * self.needs_speed_control)
                    continue
                weighted_options[move_name] = int(default_weight * 10)
                continue
            # wide guard
            if move_name == "wideguard":
                weighted_options[move_name] = int(default_weight * 4)
                continue   

            ## tags
            # tags for THIS pokemon
            # TODO there is probably a matrix multiplication way to do this way more efficently
            for tag_name in tags:
                if tag_name in TAG_MOVE_MULTIPLIERS and move_name in TAG_MOVE_MULTIPLIERS[tag_name]:
                    move_score *= TAG_MOVE_MULTIPLIERS[tag_name][move_name]



            ## weather
            # if we have a weather tag and no auto-setting ability, ensure we have a weather setting move
            if TAG_HAS_SNOW:
                if chosen_ability != 'snowwarning' and move_name in ['snowscape','hail','chillyreception']:
                    move_score *= 10
            elif TAG_HAS_RAIN:
                if chosen_ability != 'drizzle' and chosen_ability != 'primordialsea' and move_name == 'raindance':
                    move_score *= 10
                if move_type == WATER and move_category != STATUS_CATEGORY:
                    move_score *= 1.5
            elif TAG_HAS_SUN:
                if chosen_ability != 'drought' and chosen_ability != 'desolateland' and chosen_ability != 'orichalcumpulse' and move_name == 'sunnyday':
                    move_score *= 10
                if move_type == FIRE and move_category != STATUS_CATEGORY:
                    move_score *= 1.5
            elif TAG_HAS_SAND:
                if chosen_ability != 'sandstream' and move_name == 'sandstorm':
                    move_score *= 10

            # TODO weather ball


            # TODO tags for this team


            ## Multipliers (order doesn't matter)

            # weight moves based on power
            if move_category == STATUS_CATEGORY or power > 0:
                power_scale = default_weight
                if role_choice.role != ROLE_SUPPORT:
                    power_scale = default_weight * 4

                power_ratio = score_move_power(power)
                move_score += power_scale * power_ratio

                # increase weight of priority attacks
                if move_description.get("priority", 0) > 0:
                    move_score *= 3

                # reduce weight of recoil attacks
                recoil_values = move_description.get("recoil", [])
                if len(recoil_values) > 0:
                    move_score *= 0.9

                # reduce weight of static recoil attacks
                if move_description.get("mindBlownRecoil", None):
                    move_score *= 0.85

                # increase weight of draining attacks
                if move_description.get("drain", None):
                    move_score *= 1.25

                # reduce weight of self KO moves
                if not move_description.get("selfdestruct", None):
                    move_score *= 0.1
                
                # increase weight of stab attacks
                if move_type in pokemon_types:
                    move_score *= 2
                
                # if mixed or support ratio by pref stat
                if move_category == PHYSICAL_CATEGORY:
                    move_score *= atk_spa_ratio
                elif move_category == SPECIAL_CATEGORY:
                    move_score *= spa_atk_ratio 

                # TODO move exceptions
                # if not a support, de prioritize foul play
                if move_name == 'foulplay' and role_choice.role != ROLE_SUPPORT:
                    move_score *= 0.25
    
            elif move_category == STATUS_CATEGORY or power == 0:
                
                # support moves
                if role_choice.role == ROLE_SUPPORT:
                    # stat changes
                    if stat_changes:
                        # reduce benefit of slow pokemon
                        if effective_speed <= HIGH_SPEED_CUTOFF:
                            move_score *= 0.25

                        move_score *= abs(stat_changes.get("atk", 1))
                        move_score *= abs(stat_changes.get("spa", 1))
                        move_score *= abs(stat_changes.get("def", 1))
                        move_score *= abs(stat_changes.get("spd", 1))
                        move_score *= abs(stat_changes.get("spe", 0))
                        # score speed changes much higher
                        if "spd" in move_score:
                            move_score *= 4
                            
                    # healing moves
                    if flags and 'heal' in flags:
                        move_score *= 1.5

                    status = move_description.get("status", None)
                    if status:
                        move_score *= STATUS_VALUE_MULTIPLIERS.get(status, 1)
            else:
                print(f'found type of move outside of normal catgories: {move_category} with power: {power}')

            
            
            
            if role_choice.role != ROLE_SUPPORT and move_category == STATUS_CATEGORY:
                move_score *= 0.25

            # flags weighting
            for flag, value in flags.items():
                # recharge moves ie. Hyper Beam
                if flag == "recharge":
                    move_score *= 0.25
                # charge moves ie. Solar Beam
                elif flag == "charge":
                    move_score *= 0.1

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
            if chosen_ability != "noguard" and chosen_ability != "compoundeyes":
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
            
            # switching/swapping moves
            if move_description.get("selfSwitch", None):
                move_score *= 3

            # specific move weighting by name
            if move_name in MOVES_WEIGHT_BY_NAME:
                move_score *= MOVES_WEIGHT_BY_NAME[move_name]



            ## Static changes (order matters)
            # reduce weight of moves of the same type already in moveset(only for attacks)
            if power > 0:
                if move_type and move_type in chosen_types:
                    # subtract value from chosen type dict from score
                    move_score = max(1, move_score - chosen_types[move_type])
                # old version
                # if move_type:
                #     for existing_move_name, existing_move_description in chosen_moves.items():
                #         if existing_move_description.get("type", None) == move_type:
                #             move_score *= 0.25

            # don't choose unusable moves
            if move_name in BAD_MOVES_SET:
                move_score = 1
            
            # greatly reduce wrong category of moves
            if role_choice.role == ROLE_PHYSICAL_THREAT and move_category == SPECIAL_CATEGORY and role_choice.level > 25:
                move_score = 1
            elif role_choice.role == ROLE_SPECIAL_THREAT and move_category == PHYSICAL_CATEGORY and role_choice.level > 25:
                move_score = 1     
                

            weighted_options[move_name] = max(int(move_score), 1)

        if len(weighted_options) == 0:
            print(f"failed to choose move")
            return None

        # choose from weighted options
        chosen_move_name = random.choices(population=list(weighted_options.keys()), weights=list(weighted_options.values()))[0]
        return move_set[chosen_move_name]  
