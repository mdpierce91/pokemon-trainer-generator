import random
import csv
import traceback

class PokemonChoice():
    name_and_form: str
    tier: str
    notes: str

    def __init__(self, name=None, form=None, tier=None, notes=None, *params):
        self.name_and_form = f'{name}-{form}'
        self.tier = tier
        self.notes = notes
        pass

def get_random_int_inclusive(min_val, max_val):
    print(f"choosing a number between {min_val} and {max_val}")
    result = random.randint(min_val, max_val)  # inclusive on both ends
    print(f"chose {result}")
    return result


def choose_list_of_random_pokemon(list_of_pokemon: list[list[str]], number_of_choices) -> dict[PokemonChoice]:
    modified_list_of_pokemon = list_of_pokemon.copy()
    chosen_pokemon:dict[PokemonChoice] = {}

    number_of_pokemon = len(list_of_pokemon)
    print(f"Size of list is {number_of_pokemon}")

    for _ in range(1000):
        chosen_number = get_random_int_inclusive(
            0, len(modified_list_of_pokemon) - 1
        )

        choice = modified_list_of_pokemon[chosen_number]
        print(f"chose {choice}")

        if len(choice) < 4:
            print(f"pokemon format wrong")
            continue
        # Assumes each Pokémons name is the first item in the list
        name_and_form = f'{choice[0]}-{choice[1]}'
        if name_and_form in chosen_pokemon:
            continue
        chosen_pokemon[name_and_form] = PokemonChoice(name=choice[0],form=choice[1], tier=choice[2], notes=choice[3])

        print(f"Chosen number {chosen_number} - {name_and_form}")

        if len(chosen_pokemon) >= number_of_choices:
            break

    return chosen_pokemon

def get_pokemon_list_from_csv(file_name = "./common/data/Pokemon Ranking - Chatgpt-Chunks.csv"):
    pokemon_list = []
    with open(file_name, 'r') as pokemon_csv:
        reader = csv.reader(pokemon_csv, delimiter=",")
        for i, line in enumerate(reader):
            try:
                print(f'line[{i}] = {line}')
                print(type(line))
                pokemon_list.append(line)
            except Exception as e:
                print(f"failed to add pokemon to list in {i} - {line}")
                print(e)
                print(traceback.format_exc())
    
    return pokemon_list

def draft_pokemon(number_of_choices= 200, output_file="./_output/draft_output.csv"):
    pokemon_list = get_pokemon_list_from_csv()
    chosen_set = choose_list_of_random_pokemon(list_of_pokemon=pokemon_list, number_of_choices=number_of_choices)
    with open(output_file, "w+", newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(["Pokemon","Tier","Notes"])
        for pokemon in chosen_set.values():
            writer.writerow([pokemon.name_and_form,pokemon.tier,pokemon.notes])

draft_pokemon(number_of_choices=1)