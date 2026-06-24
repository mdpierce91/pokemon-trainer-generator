import csv
import os
import traceback

from bson import ObjectId

from data import process_name
from pokemon_database import PokemonDatabase
from consts import *

STRING_TO_INT_TIERS = {
    's+': S_PLUS_TIER,
    's': S_TIER,
    'a+': A_PLUS_TIER,
    'a': A_TIER,
    'a-': A_MINUS_TIER,
    'b+': B_PLUS_TIER,
    'b': B_TIER,
    'b-': B_MINUS_TIER,
    'c+': C_PLUS_TIER,
    'c': C_TIER,
    'c-': C_MINUS_TIER,
    'd+': D_PLUS_TIER,
    'd': D_TIER,
    'd-': D_MINUS_TIER,
    'f+': F_PLUS_TIER,
    'f': F_TIER,
    'f-': F_MINUS_TIER
}

def write_tier_list_to_db(database: PokemonDatabase):
    dirname = os.path.dirname(__file__)
    file_location = '..\\common\\data\\Pokemon Ranking - Chatgpt-Chunks.csv'
    combined_file = os.path.join(dirname, file_location)
    with open(combined_file, 'r') as pokemon_csv:
        reader = csv.reader(pokemon_csv, delimiter=",")
        for i, line in enumerate(reader):
            try:
                # remove incorrect old records
                processed_name = process_name(line[0])
                check_if_invalid_name_exists(database=database, invalid_name=line[0].lower(), updated_name=processed_name)

                print(f'line[{i}] = {line}')
                database.insert_record_from_tier_list(
                    name=processed_name,
                    form=format_mega_name(line[1]).lower(),
                    tier=STRING_TO_INT_TIERS[line[2].lower().replace('_','')],
                    tags=line[3].lower(),
                )
                
            except Exception as e:
                print(f"failed to add pokemon to list in {i} - {line}")
                print(e)
                print(traceback.format_exc())

def clean_cobblemon_db(database: PokemonDatabase):
    records = database.find_all_records(collection_name=database.cobblemon_collection, query={})
    for record in records:
        id = ObjectId(record["_id"])
        preprocessed_name = record["name"]
        processed_name = process_name(preprocessed_name)
        if processed_name != preprocessed_name:
            record["name"] = processed_name
            database.insert_json_record(collection_name=database.cobblemon_collection,key={ '_id': id }, data=record)

def clean_species_db(database: PokemonDatabase):
    records = database.find_all_records(collection_name=database.species_choice, query={})
    for record in records:
        id = ObjectId(record["_id"])
        preprocessed_name = record["species"]
        processed_name = process_name(preprocessed_name)
        if processed_name != preprocessed_name:
            record["species"] = processed_name
            database.insert_json_record(collection_name=database.species_choice,key={ '_id': id }, data=record)

def check_if_invalid_name_exists(database: PokemonDatabase, invalid_name, updated_name):
    if invalid_name and invalid_name != updated_name:
        database.delete_by_key(collection_name=database.species_choice, key={ 'species': invalid_name })

def format_mega_name(name:str):
    return name.replace(' ', '-')