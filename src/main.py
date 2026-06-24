import argparse
import os
import json
import sys
import time
import traceback

from pydantic import TypeAdapter

from models.cobblemon_form import CobblemonSpecies
from consts import *
from generater import generate_trainer
from models.species_choice import SpeciesChoice
from data import apply_type_chart, chart_pokemon_defenses, create_from_cobblemon_species, process_cobblemon_data_for_database, process_move_data_for_database, process_pokemon_data_for_database
from output import write_trainer_to_file
from pokemon_database import PokemonDatabase
from pokemon_json import import_all_pokemon, import_mega_stones
from tier_list import clean_cobblemon_db, clean_species_db, write_tier_list_to_db
from trainer_json import fix_trainers, open_all_trainer_json_files, remove_null_values
from consts import BUG, FAIRY, FIRE, FLYING, GHOST, NORMAL, STEEL
from type import get_defensive_chart, test_type_chart

dirname = os.path.dirname(__file__)

def main():
    print("Starting main")
    
    # get command line args
    args = get_args()
    import_move_descriptions = args.import_move_descriptions
    import_species = args.import_species
    clean_database = args.clean_database
    generate_trainers = args.generate_trainers
    only_gym_leaders = args.only_gym_leaders
    search_trainer = args.search_trainer
    if search_trainer is str:
        search_trainer = search_trainer.lower()

    print("connecting Database")
    database = PokemonDatabase()
    try:
        # TODO pass paths to functions
        if import_move_descriptions:
            write_move_descriptions_to_db(database=database)

        # this includes moves for every species
        if import_species:
            # run this one first
            write_tier_list_to_db(database=database)
            write_cobblemon_collection(database=database)
            write_species_collection(database=database)
            mega_stones =  import_mega_stones()
            write_mega_stones_to_db(database=database, mega_stones=mega_stones)

        if clean_database:
            clean_cobblemon_db(database=database)
            clean_species_db(database=database)
  

        if generate_trainers:
            # TODO move methods into coach      
            all_trainers = open_all_trainer_json_files(only_gym_leaders=only_gym_leaders, search_keyword=search_trainer)
            timestamp = str(time.time())
            for trainer in all_trainers:
                trainer_file = generate_trainer(pokemon_database=database, trainer_shell=trainer.data)
                # Write the trainer to a file
                write_trainer_to_file(timestamp=timestamp, trainer_file=trainer_file, filename=trainer.filename)

        database.client.close()


    except Exception as e:
        print(f'Exception in main')
        print(e)
        print(traceback.format_exc())
        raise e
        # pokemon_database.client.close()

def get_args() -> argparse.Namespace:
    print("collecting args")
    parser = argparse.ArgumentParser(description="Main")
    parser.add_argument('--import_move_descriptions', action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('--import_species', action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('--clean_database', action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('--generate_trainers', action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('--only_gym_leaders', action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('--search_trainer', default=None)
    
    args = parser.parse_args()
    return args


def write_mega_stones_to_db(database: PokemonDatabase, mega_stones: list[dict]):
    for mega_stone in mega_stones:
        database.update_species_form_items(species=mega_stone["species"], form=mega_stone["form"], required_item=mega_stone["required_item"])

def write_move_descriptions_to_db(database: PokemonDatabase):
    dirname = os.path.dirname(__file__)
    file_location = '..\\common\\data\\showdown_moves.json'
    combined_file = os.path.join(dirname, file_location)
    with open(combined_file, 'r') as moves_json:
        moves_data = json.load(moves_json)
        for json_key, move_info in moves_data.items():
            try:
                processed_move_info = process_move_data_for_database(json_key=json_key, move_info=move_info)
                database.insert_move_description(move_name=processed_move_info["name"], move_description=processed_move_info)
            except Exception as e:
                print(f"failed to add move {move_info['name']} to list")
                print(e)
                print(traceback.format_exc())

def write_species_collection(database: PokemonDatabase,update=False):
    imported_pokemon = import_all_pokemon(validation=True)
    print(f'finished importing pokemon to memory')
    for single_pokemon in imported_pokemon:
        processed_pokemon = process_cobblemon_data_for_database(single_pokemon)
        write_to_db_from_cobblemon_files(database, processed_pokemon,update=update)


def write_cobblemon_collection(database: PokemonDatabase):
    imported_pokemon = import_all_pokemon(validation=False)
    print(f'finished importing pokemon to memory')

    print(f'start writing to cobblemon collection')
    for single_pokemon in imported_pokemon:
        processed_pokemon = process_pokemon_data_for_database(single_pokemon)
        database.insert_json_record(collection_name=database.cobblemon_collection,key={"name":processed_pokemon["name"]}, data=processed_pokemon)


def write_to_db_from_cobblemon_files(database: PokemonDatabase, cobblemon_species, update=False):
    # print(f'inserting all forms of {cobblemon_species.name}')

    # print(f'inserting base form of {cobblemon_species.name}')
    write_from_cobblemon_form(database=database,species=cobblemon_species.name,form=BASE_FORM,cobblemon_form=cobblemon_species,update=update)

    if cobblemon_species.forms:
        for form in cobblemon_species.forms:
            write_from_cobblemon_form(database=database,species=cobblemon_species.name, cobblemon_form=form, form=form.name,update=update)
    
def write_from_cobblemon_form(database: PokemonDatabase, species: str,  cobblemon_form, form=BASE_FORM, update=False):

    choices_with_diff_abilities = create_from_cobblemon_species(database=database, species_choice=SpeciesChoice(species=species, form=form), cobblemon_species=cobblemon_form)
    for choice in choices_with_diff_abilities:
        # print(f'inserting species {species}-{form} with ability {choice["ability"]}')
        database.upsert_pokemon_selection_for_all_roles(record=choice)

    if cobblemon_form.moves is not None:
        database.write_moves_for_species_and_form(species=species,form=form, moves=cobblemon_form.moves, update=update)

def create_defences_chart(database):
    cobblemon_pokemon = database.find_all_records(collection_name=database.cobblemon_collection, query={})
    list_adapter = TypeAdapter(list[CobblemonSpecies])
    species_list = list_adapter.validate_python(cobblemon_pokemon)
    chart_pokemon_defenses(species_list)

if __name__ == "__main__":
    main()