
from consts import ELECTRIC, FAIRY, FLYING, ICE, NORMAL


def type_change_boost(old_type, new_type, base_power):
    if old_type == NORMAL:
        return new_type, base_power * 1.2
    else: 
        return old_type, base_power

def pixilate(old_type, base_power):
    return type_change_boost(old_type=old_type,new_type=FAIRY,base_power=base_power)

def aerilate(old_type, base_power):
    return type_change_boost(old_type=old_type,new_type=FLYING,base_power=base_power)

def refrigerate(old_type, base_power):
    return type_change_boost(old_type=old_type,new_type=ICE,base_power=base_power)

def galvanize(old_type, base_power):
    return type_change_boost(old_type=old_type,new_type=ELECTRIC,base_power=base_power)

def normalize(old_type, base_power):
    if old_type != NORMAL:
        return NORMAL, base_power * 1.2

type_changing_abilities = {
    'normalize': normalize,
    'pixilate': pixilate,
    'aerilate': aerilate,
    'refrigerate': refrigerate,
    'galvanize': galvanize,
}

def check_type_changing_moves(ability, old_type: str, base_power: int):
    if ability in type_changing_abilities:
        return type_changing_abilities[ability](old_type, base_power)
    else:
        return old_type, base_power