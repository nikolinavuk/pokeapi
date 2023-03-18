import requests
import json


# for pokemon in dict_response
all_url = "https://pokeapi.co/api/v2/pokemon-species/"
wanted_games = ["red", "blue", "leafgreen", "white"]

pokemon_by_version = {version: [] for version in wanted_games}

# limit the calls, use pagination
offset = 0
limit = 100

pokemon_count = 0

# while pokemon_count < 200:
while True:
    dict_response = requests.get(f"{all_url}?offset={offset}&limit={limit}").json()
    get_pokemon = dict_response["results"]

    if len(get_pokemon) == 0:
        break

    for pokemon in get_pokemon:
        individual_pokemon = pokemon["url"]

        get_url = requests.get(individual_pokemon).json()

        if len(get_url["flavor_text_entries"]) > 0:
            for game_version in get_url["flavor_text_entries"]:
                version_name = game_version["version"]["name"]

                if version_name in wanted_games and game_version["flavor_text"]:
                    pokemon_by_version[version_name].append(pokemon["name"])

                break
    if dict_response["next"]:
        break
    else:
        offset += limit

pokemon_red = set(pokemon_by_version["red"])
pokemon_blue = set(pokemon_by_version["blue"])
pokemon_leaf_green = set(pokemon_by_version["leafgreen"])
pokemon_white = set(pokemon_by_version["white"])

filtered_pokemon = sorted(
    list(pokemon_red.union(pokemon_blue, pokemon_leaf_green, pokemon_white))
)
# print(filtered_pokemon)
# print(type(filtered_pokemon))


# make a call with the names only from the deduplicated set

pokemon_url = "https://pokeapi.co/api/v2/pokemon"
pokemon_list = []

for pokemon in filtered_pokemon:
    pokemon_data = requests.get(f"{pokemon_url}/{pokemon}").json()

    wanted_slots = [1, 2]  # list
    available_slots = [type_dict["slot"] for type_dict in pokemon_data["types"]]
    # attack_types = [d["type"] for d in pokemon_data]

    # check =  all(item in available_slots  for item in wanted_slots)
    slots = []
    if any(slot in available_slots for slot in wanted_slots):
        for type_dict in pokemon_data["types"]:
            slot = type_dict.get("slot")
            attack_name = type_dict.get("type").get("name")
            slots.append({slot: attack_name})

    default_sprites = pokemon_data["sprites"]["front_default"]

    # dynamically populate slot 2

    stats = {
        "name": pokemon_data["name"].capitalize(),
        "id": pokemon_data["id"],
        "base_experience": pokemon_data["base_experience"],
        "weight": pokemon_data["weight"],
        "height": pokemon_data["height"],
        "order": pokemon_data["order"],
        "slot 1": slots[0].get(1),
        "bmi": round(pokemon_data["weight"] / (pokemon_data["height"] ** 2), 4),
        "front_default": pokemon_data["sprites"]["front_default"],
    }

    # remove slot 2 is empty
    # only add slot 2 if it exists
    # print(len(slots))

    if len(slots) > 1:
        stats["slot 2"] = slots[1].get(2)

        # Move "slot 2" after "slot 1" in the dictionary
        new_stats = {}
        for key, value in stats.items():
            if key == "slot 1":
                new_stats[key] = value
                if "slot 2" in stats:
                    new_stats["slot 2"] = stats["slot 2"]
            elif key != "slot 2":
                new_stats[key] = value

        stats = new_stats

    pokemon_list.append(stats)

print(pokemon_list)

increment = 20
chunks = [
    pokemon_list[i : i + increment] for i in range(0, len(pokemon_list), increment)
]

for i, chunk in enumerate(chunks):
    with open(f"my_file_{i+1}.json", "w") as f:
        json.dump(chunk, f)
