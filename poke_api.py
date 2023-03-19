import requests
import logging
import time
import requests_cache
import json
import os


logger = logging.getLogger(__name__)
logger.setLevel("INFO")
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)


def save_response(data: list, file_name: str, directory_name: str) -> None:
    for version in data:
        filename = os.path.join(f"{directory_name}", f"{file_name}")
        with open(filename, "w") as file:
            try:
                json.dump(data, file)
            except Exception as error:
                print(f"Failed to save file {filename}: {error}")

    return None


def split_data(data: list, directory_name: str):
    increment = 20
    chunks = [data[i : i + increment] for i in range(0, len(data), increment)]

    for i, chunk in enumerate(chunks):
        with open(f"{directory_name}/pokemon_file_{i+1}.json", "w") as f:
            json.dump(chunk, f)


def get_pokemon_species_payload(
    starting_offset: int, payload_limit: int, session: requests.Session
) -> dict:
    all_url = "https://pokeapi.co/api/v2/pokemon-species/"

    try:
        pokemon_species_dict_response = session.get(
            f"{all_url}?offset={starting_offset}&limit={payload_limit}"
        ).json()
    except requests.exceptions.ConnectionError:
        time.sleep(secs=2**starting_offset)

        logger.info(f"Retrying to get pokemon_species payload")

        pokemon_species_dict_response = get_pokemon_species_payload(
            offset=starting_offset, limit=payload_limit, session=session
        )
    return pokemon_species_dict_response


def filter_pokemon_data(pokemon_data: dict, game_version: list, offset: int) -> dict:
    pokemon_by_version = {version: [] for version in game_version}

    for pokemon in pokemon_data["results"]:
        individual_pokemon = pokemon["url"]
        try:
            pokemon_info_dict_response = requests.get(url=individual_pokemon).json()
        except requests.exceptions.ConnectionError:
            time.sleep(secs=2**offset)
            continue
        if len(pokemon_info_dict_response["flavor_text_entries"]) > 0:
            for flavor_text_entry in pokemon_info_dict_response["flavor_text_entries"]:
                version_name = flavor_text_entry["version"]["name"]
                if version_name in game_version:
                    url = pokemon["url"].split("/")[-2]
                    pokemon_by_version[version_name].append(url)
    return pokemon_by_version


def get_pokemon_in_versions(
    starting_offset: int,
    payload_limit: int,
    session: requests.Session,
    game_version: list,
) -> set:
    requests_cache.install_cache()

    pokemon_urls = set()

    while True:
        pokemon_ids = get_pokemon_species_payload(
            starting_offset=starting_offset,
            payload_limit=payload_limit,
            session=session,
        )

        pokemon_by_version = filter_pokemon_data(
            pokemon_data=pokemon_ids, game_version=game_version, offset=starting_offset
        )

        for version, pokemon_list in pokemon_by_version.items():
            pokemon_urls.update(pokemon_list)

        if not pokemon_ids["next"]:
            break
        else:
            starting_offset += payload_limit

    return pokemon_urls


def process_pokemon(session: requests.Session, offset: int, pokemon_ids: set) -> list:
    pokemon_url = "https://pokeapi.co/api/v2/pokemon"
    pokemon_list = []
    pokemon_ids = pokemon_ids

    for pokemon in pokemon_ids:
        while True:
            try:
                pokemon_data = session.get(f"{pokemon_url}/{pokemon}").json()
                break
            except requests.exceptions.RequestException:
                time.sleep(2**offset)
                continue

        wanted_slots = [1, 2]  # list

        slots = {
            type_dict.get("slot"): type_dict.get("type").get("name")
            for type_dict in pokemon_data["types"]
            if type_dict.get("slot") in wanted_slots
        }

        stats = {
            "name": pokemon_data["name"].capitalize(),
            "id": pokemon_data["id"],
            "base_experience": pokemon_data["base_experience"],
            "weight": pokemon_data["weight"],
            "height": pokemon_data["height"],
            "order": pokemon_data["order"],
            "slot 1": slots.get(1),
            "bmi": round(pokemon_data["weight"] / (pokemon_data["height"] ** 2), 4),
            "front_default": pokemon_data["sprites"]["front_default"],
        }

        if len(slots) > 1:
            stats["slot 2"] = slots.get(2)

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

    return pokemon_list


if __name__ == "__main__":
    OFFSET = 0
    LIMIT = 150
    SESSION = requests.Session()
    GAME_VERSIONS = ["red", "blue", "leafgreen", "white"]

    logger.info(f"Getting pokemon from selected game versions...")

    pokemon_by_version = get_pokemon_in_versions(
        starting_offset=OFFSET,
        payload_limit=LIMIT,
        session=SESSION,
        game_version=GAME_VERSIONS,
    )

    save_response(
        data=list(pokemon_by_version),
        file_name="pokemon_ids.json",
        directory_name="filtered_pokemon_ids",
    )

    print(len(pokemon_by_version))

    processed_pokemon = process_pokemon(
        session=SESSION, offset=OFFSET, pokemon_ids=pokemon_by_version
    )

    print(len(processed_pokemon))

    split_data(data=processed_pokemon, directory_name="pokemon_stats")

    # split_json(data=processed_pokemon)

    # take those ids and create files
