
from typing import TypedDict



class SpeciesChoice(TypedDict):
    role: str
    species: str
    form: str
    minimum_level: int
    # int from 0 up, 0 being the highest tier
    tier: int
    primary_type: str
    secondary_type: str|None
    ability: str

    # type effectiveness
    normal_effect: float
    fire_effect: float
    water_effect: float
    grass_effect: float
    electric_effect: float
    ice_effect: float
    fighting_effect: float
    poison_effect: float
    ground_effect: float
    flying_effect: float
    psychic_effect: float
    bug_effect: float
    rock_effect: float
    ghost_effect: float
    dragon_effect: float
    dark_effect: float 
    steel_effect: float
    fairy_effect: float
    # tags
    has_rain:bool
    has_sand:bool
    has_snow:bool
    has_speed_control:bool
    has_sun:bool
    has_trick_room: bool
    needs_rain: bool
    needs_sand: bool
    needs_snow: bool
    needs_speed_control: bool
    needs_sun: bool
    needs_trick_room: bool

    # TODO why are these here?
    needs_physical_threat: bool
    needs_special_threat: bool
    needs_support: bool

    # def __init__(self, species, primary_type, ability, secondary_type:str|None = None, form:str=BASE_FORM, defensive_type_chart={}):
    #     self.species = species
    #     self.form = form
    #     self.primary_type = primary_type
    #     self.ability = ability
    #     self.secondary_type = secondary_type
        # # doesn't work with TypedDict
    #     self.apply_type_chart(defensive_type_chart=defensive_type_chart)

    # def __getitem__(self, key):
    #     return getattr(self, key)
        
    # def __setitem__(self, key, value):
    #     return setattr(self, key, value)

    # def apply_type_chart(self, defensive_type_chart:dict[str,float]):
    #     for key, value in defensive_type_chart.items():
    #         try:
    #             key_string = f'{key}_effect'
    #             self[key_string] = value
    #         except Exception as e:
    #             print(f"failed to apply type {key}-{value} to specieschoice")
    #             print(e)
    #             print(traceback.format_exc())


    
# def create_species_choice_from_data(role, tier, species, primary_type, ability, secondary_type:str|None = None, form:str=BASE_FORM, defensive_type_chart={}) -> SpeciesChoice:
#     species_choice = SpeciesChoice(role=role, tier=tier, species=species,ability=ability,form=form,primary_type=primary_type,secondary_type=secondary_type)
#     species_choice = apply_type_chart(species_choice=species_choice, defensive_type_chart=defensive_type_chart)
#     return species_choice
