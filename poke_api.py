"""This module generates data for each pokemon available in a given version.
"""
import logging
import time
import json
import os
import requests
import requests_cache


logger = logging.getLogger(__name__)
logger.setLevel("INFO")
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)


def save_response(data: list, file_name: str, directory_name: str) -> None:
    """Save the data into a file for local caching if needed.

    Args:
        data (list): Data which will be saved
        file_name (str): Name of the file
        directory_name (str): Location of the file

    Raises:
        IOError: Exception if something goes wrong when we save the file
    """

    logger.info("Saving IDS in a file.")

    for version in data:
        filename = os.path.join(f"{directory_name}", f"{file_name}")
        with open(file=filename, mode="w", encoding="utf-8") as file:
            try:
                json.dump(data, file)
            except IOError as error:
                logger.error("Failed to save file %s : %s", filename, error)

    return None


def split_data(data: list, directory_name: str) -> None:
    """Save data into multiple files, in a given directory.

    Args:
        data (list): Data which will be saved.
        directory_name (str): Name of the directory to store data.
    """

    increment = 20  # TODO: Based on what 20??

    chunks = [data[i : i + increment] for i in range(0, len(data), increment)]

    for i, chunk in enumerate(chunks):
        with open(
            file=f"{directory_name}/pokemon_file_{i+1}.json", mode="w", encoding="utf-8"
        ) as file_name:
            try:
                json.dump(chunk, file_name)

            except IOError as error:
                logger.error("Failed to save file %s : %s", file_name, error)
    logger.info("Saved data into files.")


def get_pokemon_species_payload(
    starting_offset: int, payload_limit: int, session: requests.Session
) -> dict:
    """Retrieve the payload from the pokemon_species endpoint.

    Args:
        starting_offset (int): Starting number of pokemon
        payload_limit (int): Limit the requested amount of data
        session (requests.Session): Session object from the request library

    Returns:
        dict: Payload containing the pokemon species information
    """

    pokemon_species_url = "https://pokeapi.co/api/v2/pokemon-species/"

    try:
        pokemon_species_dict_response = session.get(
            f"{pokemon_species_url}?offset={starting_offset}&limit={payload_limit}"
        ).json()
    except requests.exceptions.ConnectionError:
        time.sleep(secs=2**starting_offset)

        logger.info("Retrying to get pokemon_species payload.")

        pokemon_species_dict_response = get_pokemon_species_payload(
            starting_offset=starting_offset,
            payload_limit=payload_limit,
            session=session,
        )
    return pokemon_species_dict_response


def filter_pokemon_data(
    pokemon_data: dict, game_versions: list, starting_offset: int
) -> dict:
    """Filter out pokemon to only look for the ones in the requested game version (colour).

    Args:
        pokemon_data (dict): Dictionary with all information for a pokemon
        game_version (list): Requested versions of the game
        starting_offset (int): Starting number of pokemon

    Returns:
        dict: A list of relevant IDs from only the wanted game versions.
    """
    pokemon_ids_in_version = {version: [] for version in game_versions}

    for pokemon in pokemon_data["results"]:
        individual_pokemon = pokemon["url"]
        try:
            pokemon_info_dict_response = requests.get(
                url=individual_pokemon
            ).json()  # TODO: consider timeouts?
        except requests.exceptions.ConnectionError:
            time.sleep(secs=2**starting_offset)
            continue

        if len(pokemon_info_dict_response["flavor_text_entries"]) > 0:
            for flavor_text_entry in pokemon_info_dict_response["flavor_text_entries"]:
                version_name = flavor_text_entry["version"]["name"]
                if version_name in game_versions:
                    url = pokemon["url"].split("/")[-2]
                    pokemon_ids_in_version[version_name].append(url)

    return pokemon_ids_in_version


def get_pokemon_in_versions(
    starting_offset: int,
    payload_limit: int,
    session: requests.Session,
    game_versions: list,
) -> set:
    """Fetch pokemon IDs which only appear in a requested game.

    Args:
        starting_offset (int): Starting number of pokemon
        payload_limit (int): Limit the requested amount of data
        session (requests.Session): Session object
        game_version (list): _description_

    Returns:
        set: Deduplicated list of pokemon IDs
    """
    requests_cache.install_cache()

    # pokemon_urls = set()
    pokemon_ids = set()

    while True:
        pokemon_species_payload = get_pokemon_species_payload(
            starting_offset=starting_offset,
            payload_limit=payload_limit,
            session=session,
        )

        processed_pokemon_by_version = filter_pokemon_data(
            pokemon_data=pokemon_species_payload,
            game_versions=game_versions,
            starting_offset=starting_offset,
        )

        for version, pokemon_list in processed_pokemon_by_version.items():
            pokemon_ids.update(pokemon_list)

        if not pokemon_species_payload["next"]:
            break
        else:
            starting_offset += payload_limit

    return pokemon_ids


def process_pokemon(
    session: requests.Session, starting_offset: int, pokemon_ids: set
) -> list:
    """Process the data sheet from each pokemon using their IDs.

    Args:
        session (requests.Session): Session object
        starting_offset (int): Starting number of pokemon
        pokemon_ids (set): List of pokemon IDs

    Returns:
        list: List of all relevant pokemon  with extracted fields.
    """

    pokemon_url = "https://pokeapi.co/api/v2/pokemon"
    pokemon_list = []

    logger.info("Extracting data for each pokemon based on their ID ...")

    for pokemon in pokemon_ids:
        while True:
            try:
                pokemon_data = session.get(f"{pokemon_url}/{pokemon}").json()
                break
            except requests.exceptions.RequestException:
                time.sleep(2**starting_offset)
                continue

        wanted_slots = [1, 2]

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

    logger.info("Getting pokemon from selected game versions ...")

    pokemon_by_version = get_pokemon_in_versions(
        starting_offset=OFFSET,
        payload_limit=LIMIT,
        session=SESSION,
        game_versions=GAME_VERSIONS,
    )

    logger.info("Successfully obtained pokemon ids for selected game versions. ")
    logger.info("There are %s in selected pokemon games.", len(pokemon_by_version))

    save_response(
        data=list(pokemon_by_version),
        file_name="pokemon_ids.json",
        directory_name="filtered_pokemon_ids",
    )

    logger.info("Starting to process pokemon data ...")
    processed_pokemon = process_pokemon(
        session=SESSION, starting_offset=OFFSET, pokemon_ids=pokemon_by_version
    )

    logger.info("Successfully processed %s pokemon.", len(processed_pokemon))

    logger.info("Saving data...")
    split_data(data=processed_pokemon, directory_name="pokemon_stats")
