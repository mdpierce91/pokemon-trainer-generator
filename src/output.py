import json
import os

from models.cobbleverse_trainer import CobbleverseTrainer
from trainer_json import clean_nones

def write_trainer_to_file(timestamp: str, trainer_file: CobbleverseTrainer,filename:str):
    dirname = os.path.dirname(__file__)
    file_location = f'..\\_output\\datapack\\{timestamp}\\data\\rctmod\\trainers\\{filename}'
    combined_file = os.path.join(dirname, file_location)
    abs_path = os.path.abspath(combined_file)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, 'w') as json_file:
        json.dump(trainer_file.model_dump(by_alias=True, exclude_unset=True, exclude_none=True), json_file, indent=4, ensure_ascii=False)
        