

import traceback
import plotly.express as px
import plotly.graph_objects as go

from consts import BASE_FORM
from models.species_choice import SpeciesChoice
from models.cobblemon_form import BaseStats, CobblemonForm, CobblemonSpecies
from pokemon_database import PokemonDatabase
from type import get_defensive_chart

def apply_type_chart(species_choice: SpeciesChoice, defensive_type_chart: list) -> SpeciesChoice:
    for key, value in defensive_type_chart.items():
        try:
            key_string = f'{key}_effect'
            species_choice[key_string] = value
        except Exception as e:
            print(f"failed to apply type {key}-{value} to specieschoice")
            print(e)
            print(traceback.format_exc())
    return species_choice

def set_minimum_level_for_species(database: PokemonDatabase, species_choice: SpeciesChoice, cobblemon_species: CobblemonForm):
    minimum_level_key = 'minimum_level'
    found = False

    name_form_result = species_choice['species'] if species_choice['form'] == BASE_FORM else species_choice['species'] + " " + species_choice['form']
    print(f'setting min level for: {name_form_result}')
    if cobblemon_species.preEvolution:
        pre_evolution:str = cobblemon_species.preEvolution
        print(f'looking for {pre_evolution}')
        pre_evolution_records:list = database.find_all_records(database.cobblemon_collection, { "name": pre_evolution })
        if not pre_evolution_records:
            print(f'could not find pre-evolution records for {species_choice['species']} under name{pre_evolution}')
            species_choice[minimum_level_key] = 20
        else:
            for pre_evolution_record in pre_evolution_records:
                if "evolutions" not in pre_evolution_record:
                    print(f'{species_choice['species']} has no evolutions in this record')
                    continue
                for evolution in pre_evolution_record["evolutions"]:
                    if "result" not in evolution:
                        print(f'missing result(name) in evolution')
                        print(evolution)
                        continue
                    # found evolution
                    if evolution["result"] == name_form_result:
                        found = True
                        print(f'found preEvolution')
                        if "requirements" not in evolution:
                            print(f'missing requirements in evolution')
                            print(evolution)
                            continue
                        for requirement in evolution["requirements"]:
                            print(type(requirement))
                            print(requirement)
                            print("minLevel" in requirement)
                            if "minLevel" in requirement:
                                # Get level requirement for evolution
                                species_choice[minimum_level_key] = requirement["minLevel"]
                                return species_choice
                        # No level requirement on evolution
                        print(f'{pre_evolution} to {species_choice['species']} does not require a min level')
                        species_choice[minimum_level_key] = 1
                        return species_choice
                        
           
        if not found:
            print(f'no records found for pre-evolution: {pre_evolution}')
    else:
        # no pre-evolution, min should be 1
        print(f'no preEvolution listed, setting to 1')
        species_choice[minimum_level_key] = 1
 
    if minimum_level_key not in species_choice:
        # fallback
        print(f'failed to set minimum level, defaulting to 1')
        species_choice[minimum_level_key] = 1
    return species_choice

def get_abilites_for_species(database: PokemonDatabase, species_choice: SpeciesChoice, cobblemon_species: CobblemonForm) -> list[str]:
    try:
        # print(f'retrieving abilities for {species_choice['species']}-{species_choice['form']}')
        # read from the database
        cobblemon_records = database.find_all_records(collection_name=database.cobblemon_collection, query={ "name": species_choice['species']})

        if not cobblemon_records:
            print(f"could not find records for {species_choice['species']}")
            return []
        
        for record in cobblemon_records:
            # base form
            if species_choice['form'] == BASE_FORM:
                return record['abilities']
            else:
                # missing forms
                if 'forms' not in record:
                    print(f'no forms in record')
                    print(record)
                    continue
                else:
                    for form in record["forms"]:
                        # found form
                        if form["name"] == species_choice['form']:
                            if 'abilities' in record['forms']:
                                # get abilties from form
                                return record['forms']['abilities']
                            else:
                                # assume form has same abilities as base form
                                return record['abilities']
                    # if we are here, we have failed to find the correct form
                    print(f'failed to find matching form for {species_choice['species']}-{species_choice['form']}')
                    return []
    except Exception as e:
        print(f'failed to set abilities for {species_choice['species']}-{species_choice['form']}')
        print(e)
        raise e
        
def create_from_cobblemon_species(database: PokemonDatabase, species_choice: SpeciesChoice, cobblemon_species: CobblemonForm) -> list[SpeciesChoice]:
    # print(f'creating species from cobblemon {species_choice['species']}-{species_choice['form']}')
    # print(cobblemon_species.abilities)
    result = []

    # set minimum level from DB records
    species_choice = set_minimum_level_for_species(database=database, species_choice=species_choice, cobblemon_species=cobblemon_species)

    species_choice['primary_type'] = cobblemon_species.primaryType
    species_choice['secondary_type'] = cobblemon_species.secondaryType

    if not cobblemon_species.abilities:
        cobblemon_species.abilities = get_abilites_for_species(database=database, species_choice=species_choice, cobblemon_species=cobblemon_species)

    for ability in cobblemon_species.abilities:
        species_choice_with_ability = species_choice.copy()
        species_choice_with_ability['ability'] = ability
        species_choice_with_ability = apply_type_chart(
            species_choice=species_choice_with_ability, 
            defensive_type_chart=get_defensive_chart(
                type1=species_choice_with_ability["primary_type"], 
                type2=species_choice_with_ability["secondary_type"], 
                ability=ability
            )
        )
        result.append(species_choice_with_ability)
    return result

def process_pokemon_data_for_database(data: dict):
    name_key = 'name'
    forms_key = 'forms'
    forms_name_key = 'name'
    evolutions_key = 'evolutions'
    evolutions_name_key = 'result'
    try:
        # lower name
        data[name_key] = process_name(data[name_key])
        # lower forms names
        if forms_key in data:
            for index, form in enumerate(data[forms_key]):
                data[forms_key][index][forms_name_key] = process_name(data[forms_key][index][forms_name_key])
        # evolution names
        if evolutions_key in data:
            for index, evolution in enumerate(data[evolutions_key]):
                data[evolutions_key][index][evolutions_name_key] = process_name(data[evolutions_key][index][evolutions_name_key])

        return data

    except Exception as e:
        print(f'failed to process pokemon data')
        print(data)
        print(e)
        print(traceback.format_exc())

def process_cobblemon_data_for_database(data: CobblemonSpecies):
    try:
        # lower name
        data.name = process_name(data.name)
        # lower forms names
        if data.forms:
            for index, form in enumerate(data.forms):
                data.forms[index].name = process_name(form.name)
        # evolution names
        if data.evolutions:
            for index, evolution in enumerate(data.evolutions):
                data.evolutions[index].result = process_name(evolution.result)

        return data

    except Exception as e:
        print(f'failed to process pokemon data')
        print(data)
        print(e)
        print(traceback.format_exc())

def process_move_data_for_database(json_key:str, move_info: dict):
    name_key = 'name'
    display_name_key = 'display_name'
    type_key = 'type'
    category_key = 'category'
    target_key = 'target'
    try:
        # add display name
        move_info[display_name_key] = move_info[name_key]
        # swap name to key from json
        move_info[name_key] = process_name(json_key)
        # type
        move_info[type_key] = process_value(move_info[type_key])
        # category
        move_info[category_key] = process_value(move_info[category_key])
        # target
        move_info[target_key] = process_value(move_info[target_key])

        return move_info

    except Exception as e:
        print(f'failed to process move data')
        print(move_info)
        print(e)
        print(traceback.format_exc())

def process_value(value):
    return value.lower()

def process_name(name):
    # punctuation
    processed_name = name.lower().replace(' ', '').replace('.', '').replace('-','').replace('\'','').replace(':','')
    # exceptions
    return processed_name

def chart_pokemon_defenses(species_list: list[CobblemonSpecies]):
    data = []
    for species in species_list:
        base_stats = species.baseStats
        total = get_defenses_score(base_stats)
        physical_defence = base_stats.hp * base_stats.defence
        special_defence = base_stats.hp * base_stats.special_defence
        data.append({ 
            "name": f'{species.name} {BASE_FORM}', 
            "total": total, 
            "physical_defence": physical_defence,
            "special_defence": special_defence
        })

        if species.forms is not None:
            for form in species.forms:
                base_stats = species.form_stats(form.name)
                total = get_defenses_score(base_stats)
                physical_defence = base_stats.hp * base_stats.defence
                special_defence = base_stats.hp * base_stats.special_defence
                data.append({ 
                    "name": f'{species.name} {form.name}', 
                    "total": total, 
                    "physical_defence": physical_defence,
                    "special_defence": special_defence
                })
    sorted_data = sorted(data, key=lambda d: d["total"], reverse=True)
    titles = []
    effective_physical_health = []
    effective_special_health = []
    for row in sorted_data:
        titles.append(row["name"])
        effective_physical_health.append(row["physical_defence"])
        effective_special_health.append(row["special_defence"])
    # fig = px.bar(sorted_data, x="name", y="total",orientation='h')
    fig = go.Figure()
    # special
    fig.add_trace(go.Bar(
        y=titles,
        x=effective_special_health,
        name='Special',
        orientation='h',
        marker=dict(
            color='hotpink',
            line=dict(color='deeppink', width=3)
        )
    ))
    # physical
    fig.add_trace(go.Bar(
        y=titles,
        x=effective_physical_health,
        name='Defence',
        orientation='h',
        marker=dict(
            color='dimgray',
            line=dict(color='black', width=3)
        )
    ))
    
    fig.update_layout(barmode='stack')
    fig.write_html("_output\\data\\defences_bar_chart.html")
    fig.show()

def get_defenses_score(base_stats: BaseStats):
    return (base_stats.hp * base_stats.defence) + (base_stats.hp * base_stats.special_defence)

# score the value of a moves power scaled exponentially with a cap of power at max_value, 
# the default max_value is set 140
# returns a value between 0-1
# any value over max_value is capped at 1.0
def score_move_power(value, max_value=140, scaling=0.5, limit=100):
    limit_ratio = float(limit/100)
    min_result = limit_ratio*0.01
    max_result = limit_ratio*0.99
    return min(1.0, max(min_result, min_result +  max_result * (value / max_value) ** scaling))