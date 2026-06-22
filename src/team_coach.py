

import traceback

from consts import *
from models.species_choice import SpeciesChoice
from type import get_defensive_chart


class TeamCoach():

    __slots__ = ('type_lock', 
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
    )
    
    def __init__(self, type_lock:str|None=None, chosen_item:str|None = None,role_weight_unit: int = 10):
        self.type_lock=type_lock
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


