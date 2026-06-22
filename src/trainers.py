
from consts import ELITE_FOUR_TITLES, GYM_LEADER_TITLES, TYPE_LOCKED_TRAINERS
from models.cobbleverse_trainer import CobbleverseTrainer


# def is_type_locked(trainer: CobbleverseTrainer):
#     # see if this trainer should be type locked
#     # gym leader
#     if is_gym_leader(trainer=trainer):
#         return get_type_lock(trainer.name.literal)
#     # elite 4(four)
#     if is_elite_four(trainer=trainer):
#         return get_type_lock(trainer.name.literal)



#     # TODO: if island kahuna
    
# def is_gym_leader(trainer: CobbleverseTrainer):

#     lower_name: str= trainer.name.literal.lower()
#     lower_identity: str = trainer.get('identity', "").lower()

#     for option in GYM_LEADER_TITLES:
#         if lower_name.startswith(option) or lower_identity.startswith(option):
#             return True
        
#     return False

#     # literal_gym_leader = lower_name.startswith("Gym Leader") if trainer.name.literal else False
#     # literal_leader = lower_name.startswith("Leader") if trainer.name.literal else False
#     # identity_gym_leader = trainer.identity.startswith("Gym Leader") if trainer.identity else False
#     # identity_leader = trainer.identity.startswith("Leader") if trainer.identity else False
#     # result = literal_gym_leader or identity_gym_leader or literal_leader or identity_leader
#     # return result

# def is_elite_four(trainer: CobbleverseTrainer):
#     # gym leader starts with options
    
#     lower_name: str= trainer.name.literal.lower()
#     lower_identity: str = trainer.get('identity', "").lower()

#     for option in ELITE_FOUR_TITLES:
#         if lower_name.startswith(option) or lower_identity.startswith(option):
#             return True
        
#     return False
    
# def get_type_lock_old(name: str):
#     lower_name= name.lower()
#     stripped_name = lower_name
#     if lower_name not in TYPE_LOCKED_TRAINERS:
#         if "gym leader " in lower_name:
#             stripped_name = lower_name.replace("gym leader ", '')
#         elif "leader " in lower_name:
#             stripped_name = lower_name.replace("leader ", '')
#         elif "elite 4 " in lower_name:
#             stripped_name = lower_name.replace("elite 4 ", '')
#         elif "elite four " in lower_name:
#             stripped_name = lower_name.replace("elite four ", '')

#     return TYPE_LOCKED_TRAINERS[stripped_name]



def get_type_lock(name: str | None) -> str | None:

    if not name:
        return None
    
    lower_name = name.lower()

    # as is
    if lower_name in TYPE_LOCKED_TRAINERS:
        return TYPE_LOCKED_TRAINERS[lower_name]
    
    # gym leader
    for option in GYM_LEADER_TITLES:
        if lower_name.startswith(option):
            stripped = lower_name.replace(option, '').replace(' ', '')
            if stripped in TYPE_LOCKED_TRAINERS:
                return TYPE_LOCKED_TRAINERS[stripped]
            
    # elite four
    for option in ELITE_FOUR_TITLES:
        if lower_name.startswith(option):
            stripped = lower_name.replace(option, '').replace(' ', '')
            if stripped in TYPE_LOCKED_TRAINERS:
                return TYPE_LOCKED_TRAINERS[stripped]  

    return None     
    

    