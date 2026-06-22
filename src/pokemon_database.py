import os
import sqlite3
import pymongo

from consts import ROLE_DEFENSIVE, ROLE_PHYSICAL_THREAT, ROLE_SPECIAL_THREAT, ROLE_SUPPORT, TAG_SET
from models.species_choice import SpeciesChoice



# started sqlite3 implementation
# dirname = os.path.dirname(__file__)
# db_path = os.path.join(dirname, '..\common\data\pokemon.db')
# pokemon_database = sqlite3.connect(db_path)

class PokemonDatabase():
    client_address: str = "mongodb://localhost:27017/"
    database_name: str = "mydatabase"
    species_choice: str = "species_choice"
    cobblemon_collection: str = "cobblemon_species"
    moves: str = "moves"
    move_descriptions: str = "move_descriptions"
    database: pymongo.database.Database = None
    client: pymongo.MongoClient = None

    def connect(self, client_address: str, database_name: str):
        self.client = pymongo.MongoClient(client_address)
        self.database = self.client[database_name]


    def __init__(self, client_address: str|None = None, database_name: str|None = None):
        if client_address is None:
            client_address = self.client_address
        if database_name is None:
            database_name = self.database_name
        self.connect(client_address=client_address, database_name=database_name)

    def does_db_exists(self, db_name=None):
        if db_name is None:
            db_name = self.db_name
        if db_name is None:
            print("db name does not exist")
            return
        
        dblist = self.client.list_database_names()
        if db_name in dblist:
            print("The database exists.")
        else:
            print("Database not found")

    def does_collection_exist(self, collection_name="customers"):
        collist = self.database.list_collection_names()
        if collection_name in collist:
            print(f"The collection {collection_name} exists.")

    def create_collection(self, client_address=None, database_name=None, collection_name="customers"):
        if client_address is None:
            client_address = self.client_address
        if database_name is None:
            database_name = self.database_name
        myclient = pymongo.MongoClient(client_address)
        mydb = myclient[database_name]

        mycol = mydb[collection_name]
    
    def write_moves_for_species_and_form(self, species:str, form:str, moves:list[str], update=False):
        for move in moves:
            move_data = {
                "species": species,
                "form": form,
                "move": move
            }
            if update:
                self.upsert_move(data=move_data)
            else:
                self.insert_move(data=move_data)

    def insert_move(self,data:dict):
        moves_collection = self.database[self.moves]
        x = moves_collection.insert_one(data)

    def upsert_move(self, data:dict):
        moves_collection = self.database[self.moves]
        x = moves_collection.update_one(data, { "$set": data }, upsert=True)

    def upsert_pokemon_selection_for_all_roles(self, record: SpeciesChoice):
        # print(f'upserting for {record["species"]}-{record["form"]} with ability {record["ability"]}')
        # ensure no role is set to write for all roles
        record.pop("role", None)

        self.insert_json_record(self.species_choice, key={"species":record["species"], "form":record["form"]}, data=record)
        

    def upsert_pokemon_selection(self, record: SpeciesChoice):
        species_choice_collection = self.database[self.species_choice]

        x = species_choice_collection.update_one({"species":record["species"], "form":record["form"], "role":record["role"]}, {'$set':record}, upsert=True)

    def get_species_by_role_and_tier(self, role, level, min_tier = 16, max_tier = 0):
        # print(f'getting species by role:{role} and tier:{max_tier}-{min_tier} ')
        species_choice_collection = self.database[self.species_choice]

        rows = list(species_choice_collection.find({ "role": role, "minimum_level":{"$lte":level}, "tier": { "$lte": min_tier, "$gte": max_tier}}))
        # print(f'found {len(rows)}')
        return rows
    
    def get_species_by_type_and_tier(self, type, level, min_tier = 16, max_tier = 0):
        # print(f'getting species by role:{role} and tier:{max_tier}-{min_tier} ')
        species_choice_collection = self.database[self.species_choice]

        primary_rows = list(species_choice_collection.find({ "primary_type": type, "minimum_level":{"$lte":level}, "tier": { "$lte": min_tier, "$gte": max_tier}}))
        secondary_rows = list(species_choice_collection.find({ "secondary_type": type, "minimum_level":{"$lte":level}, "tier": { "$lte": min_tier, "$gte": max_tier}}))

        # print(f'found {len(rows)}')
        return primary_rows + secondary_rows

    def insert_record_from_tier_list(self, name:str, form:str, tier:str, tags:str):
        choice_template = SpeciesChoice(species=name, form=form, tier=tier)
        for tag_option in TAG_SET:
            choice_template[tag_option] = False
        roles = []
        for tag in tags.split(';'):
            tag_formatted = tag.lower().replace(' ', '_')
            if 'physical' in tag_formatted:
                roles.append(ROLE_PHYSICAL_THREAT)
            elif 'special' in tag_formatted:
                roles.append(ROLE_SPECIAL_THREAT)
            elif 'support' in tag_formatted:
                roles.append(ROLE_SUPPORT)
            elif ROLE_DEFENSIVE == tag_formatted:
                choice_template[ROLE_DEFENSIVE] = True
            elif tag_formatted in TAG_SET:
                choice_template[tag_formatted] = True
        for role in roles:
            choice_copy = choice_template.copy()
            choice_copy["role"] = role
            self.upsert_pokemon_selection(choice_copy)

    def delete_by_key(self, collection_name:str, key):
        collection = self.database[collection_name]

        x = collection.delete_many(key)
    
    def insert_json_record(self, collection_name:str, key:dict, data: dict):
        collection = self.database[collection_name]
        update = {'$set':data}
        # print(f'inserting json record via upsert')
        # print('key:')
        # print(key)
        # print('update:')
        # print(update)
        x = collection.update_one(key, update, upsert=True)

    def insert_move_description(self, move_name:str, move_description:dict):
        self.insert_json_record(collection_name=self.move_descriptions, key={"move": move_name}, data=move_description)

    def find_move_description(self, move_name:str) -> dict:
        collection = self.database[self.move_descriptions]
        return collection.find_one({"move": move_name})

    def find_all_moves_for_pokemon(self, species, form) -> list[dict]:
        return self.find_all_records(self.moves, { "species": species, "form": form })

    def find_all_records(self, collection_name:str, query:dict) -> list:
        collection = self.database[collection_name]

        return list(collection.find(query))
    
    def update_species_form_items(self, species: str, form:str, required_item:str):
        print(f'inserting required item {required_item} into {species}-{form}')
        return self.insert_json_record(collection_name=self.species_choice, key={ "species": species, "form": form }, data={ "required_item": required_item})
