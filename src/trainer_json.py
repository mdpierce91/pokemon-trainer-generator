import os
import json
import time

from data import process_name
from models.cobbleverse_trainer import CobbleverseTrainer, CobbleverseTrainerFile
from trainers import get_type_lock

# search_keyword is exclusive from gym leaders
def open_all_trainer_json_files(only_gym_leaders=False, limit = None, search_keyword = None) -> list[CobbleverseTrainerFile]:
    trainer_list: list[CobbleverseTrainerFile] = []
    type_locked_trainers: list[CobbleverseTrainerFile] = []
    count = 0
    try:
        dirname = os.path.dirname(__file__)
        directory_path = os.path.join(dirname, '..\\common\\datapacks\\doctors-double-battle-everything\\data\\rctmod\\trainers\\')
        directory = os.fsencode(directory_path)

        for file in os.listdir(directory):
            try:
                if limit and count > limit:
                    break
                filename = os.fsdecode(file)
                if filename.endswith(".json"): 
                    # print(f'filename{filename}')
                    full_path = os.path.join(dirname, directory_path, filename)
                    # print(f'full path: {full_path}')
                    with open(full_path, 'r') as json_data:
                        trainer_data = CobbleverseTrainer.model_validate_json(json_data.read())
                        trainer = CobbleverseTrainerFile(filename=filename, data=trainer_data)
                        # TODO implement combination of search and gym leaders
                        # if search is passed, only add it if it succeed, otherwise add
                        if not search_keyword or search_keyword in trainer_data.name.literal.lower():
                            trainer_list.append(trainer)
                        type_lock = get_type_lock(trainer.data.name.literal)
                        if not type_lock and trainer.data.identity:
                            type_lock = get_type_lock(trainer.data.identity)
                        if type_lock:
                            type_locked_trainers.append(trainer)
                        # print(f'trainer added to list')
                    count += 1
            except Exception as e:
                print(f'Failed to open trainer file {filename}')
                print(e)
                raise e
        if not search_keyword and only_gym_leaders:
            return type_locked_trainers
        return trainer_list
    except Exception as e:
        print(f'Failed to load trainer directory')
        print(e)
        raise e
        return trainer_list

def fix_trainers(existing_trainers_path: str):
    dirname = os.path.dirname(__file__)
    directory_path = os.path.join(dirname, existing_trainers_path)
    directory = os.fsencode(directory_path)

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".json"): 
            print(f'filename{filename}')
            full_path = os.path.join(dirname, directory_path, filename)
            print(f'full path: {full_path}')
            trainer_data = None
            with open(full_path, 'r') as json_data:
                trainer_data = CobbleverseTrainer.model_validate_json(json_data.read())

            if trainer_data:
                # fix pokemon species
                for member in trainer_data.team:
                    original_name = member.species
                    processed_name = process_name(member.species)
                    if original_name != processed_name:
                        print(f'replacing {original_name} with {processed_name}')
            
            with open(full_path, 'w') as file_to_overwrite:
                json.dump(trainer_data.model_dump(by_alias=True, exclude_unset=True, exclude_none=True), file_to_overwrite, indent=4, ensure_ascii=False)

def clean_nones(value):
    """
    Recursively remove all None values from dictionaries and lists, and returns
    the result as a new dictionary or list.
    """
    if isinstance(value, list):
        return [clean_nones(x) for x in value if x is not None]
    elif isinstance(value, dict):
        return {
            key: clean_nones(val)
            for key, val in value.items()
            if val is not None
        }
    else:
        return value