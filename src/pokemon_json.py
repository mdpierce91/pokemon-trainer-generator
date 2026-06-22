import csv
import os
import json
import traceback

from pydantic import ValidationError

from models.cobblemon_form import CobblemonSpecies
from data import process_name

def import_all_pokemon(validation = False) -> list[dict]:
    pokemon_list = []
    try:
        print(f'start import all pokemon')
        dirname = os.path.dirname(__file__)
        species_directory = '..\\common\\cobblemon\\species'
        for root, dirs, files in os.walk(os.path.join(dirname, species_directory)):
            print(f'File count: {len(files)}')
            try:
                for filename in files:
                    if filename.endswith(".json"): 
                        rel_file = os.path.join(root, filename)
                        with open(rel_file, 'r') as json_data:
                            try:
                                if validation:
                                    # open with class validation
                                    single_pokemon = CobblemonSpecies.model_validate_json(json_data.read())
                                    # print(f'loaded from json files {single_pokemon.name} with {len(single_pokemon.forms or [])} forms')
                                    
                                    pokemon_list.append(single_pokemon)
                                else:
                                    # open without validation
                                    single_pokemon = json.load(json_data)
                                    pokemon_list.append(single_pokemon)
                            except ValidationError as e:
                                print(f'Failed to validate {filename}')
                                print(e)
                                raise e
                            except Exception as e:
                                print(f'Unexpected error when validating {filename}')
                                print(e)
                                print(traceback.format_exc())
                                raise e

            except Exception as e:
                print(f'Failed to open {filename}')
                print(e)
                raise e
        return pokemon_list
    except Exception as e:
        print(f'failed to import all pokemon')
        print(e)
        raise e

def import_mega_stones():
    results = []
    try:
        dirname = os.path.dirname(__file__)
        file_location = '..\\common\\data\\mega_stones.csv'
        combined_file = os.path.join(dirname, file_location)
        with open(combined_file, 'r') as pokemon_csv:
            reader = csv.reader(pokemon_csv, delimiter=",")
            for i, line in enumerate(reader):
                try:
                    species = process_name(line[0])
                    mega_name = line[1].lower()
                    # one word stone name
                    stone_name = line[2].lower().replace(' ','_')
                    form = "mega"
                    # split out the 'mega x'/mega z etc
                    mega_name_pieces = mega_name.split(' ')
                    if len(mega_name_pieces) > 2:
                        form = f"mega-{mega_name_pieces[-1]}"
                    results.append({
                        "species": species,
                        "form": form,
                        "required_item": stone_name,
                    })
                except Exception as e:
                    print(f'failed to import mega')
                    print(line)
                    print(traceback.format_exc())
                    
        file_location = '..\\common\\data\\mega_showdown_stones.json'
        rel_file = os.path.join(dirname, file_location)
        with open(rel_file, 'r') as json_data:
            try:
                json_msd_stones = json.load(json_data)
                mega_showdown_stones = json_msd_stones["values"]
                for mega_stone in results:
                    for mega_showdown_stone in mega_showdown_stones:
                        if mega_stone["required_item"] in mega_showdown_stone:
                            mega_stone["required_item"] = mega_showdown_stone
                            break
                    if not mega_stone.get("required_item", "").startswith("mega_showdown:"):
                        mega_stone["required_item"] = mega_stone["required_item"].replace("_", "")
                    
            except Exception as e:
                print(f'failed to import mega')
                print(line)
                print(traceback.format_exc())
        return results
                
    except Exception as e:
        print(f'failed to import all mega stones')
        print(e)
        raise e