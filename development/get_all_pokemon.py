import requests
import sys

# for pokemon in dict_response
# all_url = "https://pokeapi.co/api/v2/pokemon/"
all_url = "https://pokeapi.co/api/v2/pokemon-species/"
wanted_games = ["red"]  # , "blue"]  # , "leafgreen", "white"]

pokemon_by_version = {version: [] for version in wanted_games}

# limit the calls, use pagination
offset = 0
limit = 100

while True:
    dict_response = requests.get(f"{all_url}?{offset}&{limit}").json()
    get_pokemon = dict_response["results"]

    if len(get_pokemon) == 0:
        break

    for pokemon in get_pokemon:
        # print(pokemon["url"])
        get_url = requests.get(pokemon["url"]).json()

        # check if poekmon exists in any of the listed games
        # check = any(item in game_indices for item in wanted_games)
        for game_index in get_url["game_indices"]:
            if game_index["version"]["name"] in wanted_games:
                pokemon_by_version[game_index["version"]["name"]].append(
                    pokemon["name"]
                )

    offset += limit

red_pokemon = set(
    pokemon_by_version["red"]
)  # this only prints 20 pokemon... probably pagination
print(red_pokemon)

types = dict_response["types"]
print("TYPES: ", types)

wanted_slots = [1, 2]  # list
available_slots = [d["slot"] for d in types]
attack_types = [d["type"] for d in types]


# check =  all(item in available_slots  for item in wanted_slots)
slots = {}
if all(item in available_slots for item in wanted_slots):
    print("Slot 1 and 2 Exist")
    for item in types:
        type_dict = item.get("slot")
        attack_name = item.get("type").get("name")
        slots[f"slot {type_dict}"] = attack_name


else:
    print("Not exist")

print(slots)

default_sprites = dict_response["sprites"]["front_default"]
print(default_sprites)

stats = {
    "name": pokemon_name.capitalize(),
    "id": dict_response["id"],
    "base_experience": dict_response["base_experience"],
    "weight": dict_response["weight"],
    "height": dict_response["height"],
    "order": dict_response["order"],
    "slot 1": slots.get("slot 1"),
    "slot 2": slots.get("slot 2"),
    "bmi": round(dict_response["weight"] / (dict_response["height"] ** 2), 4),
    "front_default": dict_response["sprites"]["front_default"],
}

print(stats)
