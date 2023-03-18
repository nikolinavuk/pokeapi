import requests
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel("INFO")


# for pokemon in dict_response

# STARTING_OFFSET = 0
# LIMIT = 100


def get_pokemon()-> dict:
    POKEMON_SPECIES_URL = "https://pokeapi.co/api/v2/pokemon-species/"
    SELECTED_GAMES = ["red", "blue", "leafgreen", "white"]
    STARTING_OFFSET = 0
    LIMIT = 100

    pokemon_by_version = {version: [] for version in SELECTED_GAMES}

    while True:
        try:
            pokemon_species_request = requests.get(
                f"{POKEMON_SPECIES_URL}?offset={STARTING_OFFSET}&limit={LIMIT}"
            )
        except requests.exceptions.ConnectionError() as error:
            logger.info("Something went wrong with the call.")
            raise error

        pokemon_species_request_dict = pokemon_species_request.json()
        
        get_pokemon_results = pokemon_species_request_dict["results"]

        if len(get_pokemon_results) == 0:
            break

        for pokemon_url in get_pokemon_results:
            pokemon_id_url = pokemon_url["url"]

            try:
                individual_pokemon_request = requests.get(pokemon_id_url)
            except requests.exceptions.ConnectionError() as error:
                logger.info("Something went wrong with the call.")
                raise error

            individual_pokemon_dict = individual_pokemon_request.json()

            if len(individual_pokemon_dict["flavor_text_entries"]) > 0:
                for game_version in individual_pokemon_dict["flavor_text_entries"]:
                    version_name = game_version["version"]["name"]

                    if version_name in SELECTED_GAMES and game_version["flavor_text"]:
                        pokemon_by_version[version_name].append(pokemon_url["name"])

                    break

        if pokemon_species_request_dict["next"]:
            break
        else:
            STARTING_OFFSET += LIMIT
    return pokemon_by_version


if __name__ == "__main__":
    pokemon_by_version = get_pokemon()
    print(pokemon_by_version)
