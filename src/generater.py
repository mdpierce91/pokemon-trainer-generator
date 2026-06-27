import math
import random
import traceback

from data import get_defenses_score, score_move_power
from models.cobblemon_form import CobblemonSpecies
from models.cobbleverse_trainer import CobbleverseAI, CobbleverseAIData, CobbleverseTrainer, TeamMember
from pokemon_database import PokemonDatabase
from special_species import SpecialSpecies
from team_coach import TeamCoach
from consts import *
from models.tier_range import TierRange
from trainers import get_type_lock




def generate_trainer(trainer_shell: CobbleverseTrainer, pokemon_database: PokemonDatabase, role_weight_unit: int = 10, replace_ai=True,battle_format=DOUBLES_FORMAT):
    try:
        # TODO: update items and item choice logic
        # TODO: rate/fix good vs bad abilities
        print(f'start generate trainer')

        coach = TeamCoach(database=pokemon_database, trainer_shell=trainer_shell)

        team_roles: list[str] = coach.choose_roles_for_trainer()
        new_team: list[TeamMember] = coach.choose_species_for_trainer()
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
        print(f'  {TAG_HAS_TRICK_ROOM}: {coach.has_trick_room}')
        print(f'  {TAG_NEEDS_TRICK_ROOM}: {coach.needs_trick_room}')
        print(f'  {TAG_HAS_SPEED_CONTROL}: {coach.has_speed_control}')
        print(f'  {TAG_NEEDS_SPEED_CONTROL}: {coach.needs_speed_control}')
        print(f'  has_mega: {coach.has_mega}')
        print(f'  {TAG_HAS_SUN}: {coach.has_sun}')
        print(f'  needs_sun: {coach.needs_sun}')
        print(f'  {TAG_HAS_RAIN}: {coach.has_rain}')
        print(f'  needs_rain: {coach.needs_rain}')
        print(f'  {TAG_HAS_SAND}: {coach.has_sand}')
        print(f'  needs_sand: {coach.needs_sand}')
        print(f'  {TAG_HAS_SNOW}: {coach.has_snow}')
        print(f'  needs_snow: {coach.needs_snow}')
        print(f'  {TAG_NEEDS_PHYSICAL_THREAT}: {coach.physical_threats}')
        print(f'  {TAG_NEEDS_SPECIAL_THREAT}: {coach.special_threats}')
        print(f'  {TAG_NEEDS_SUPPORT}: {coach.supports}')
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
