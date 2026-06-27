import argparse
import csv
import random
import traceback
from pokemon_database import PokemonDatabase
from tier_list import STRING_TO_INT_TIERS


def choose_n_pokemon():
    # get command line args
    args = get_args()
    number_of_pokemon = args.count
    example_flag = args.example_flag

    print("connecting Database")
    database = PokemonDatabase()
    try:
        all_pokemon_choices = database.get_all_species_choices()
        int_to_string_tiers ={v: k for k, v in STRING_TO_INT_TIERS.items()}
        
        selected_list = set()
        while len(selected_list) < number_of_pokemon:
            selected_pokemon = random.choice(all_pokemon_choices)
            print(selected_pokemon)
            species = selected_pokemon.get("species", None)
            form = selected_pokemon.get("form", None)
            tier = selected_pokemon.get("tier", None)
            if not species or not form or not tier or tier not in int_to_string_tiers:
                all_pokemon_choices.remove(selected_pokemon)
                continue
            else:
                poke_tuple = f'{species}-{form}',int_to_string_tiers[tier]

                selected_list.add(poke_tuple)
                all_pokemon_choices.remove(selected_pokemon)
        # selected_list = random.choices(population=all_pokemon_choices, k=number_of_pokemon )
        output_file="./_output/draft_output.csv"
        with open(output_file, "w+", newline='') as output_file:
            writer = csv.writer(output_file)
            writer.writerow(["Pokemon","Tier"])
            for pokemon in selected_list:
                writer.writerow([pokemon[0],pokemon[1]])
            
    except Exception as e:
        print(f'Exception in main')
        print(e)
        print(traceback.format_exc())
        database.client.close()
        raise e

    

def get_args():
    parser = argparse.ArgumentParser(description="Main")
    parser.add_argument('--example_flag', action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('--count', type=int)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    choose_n_pokemon()