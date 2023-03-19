import requests
import logging
import time
import requests_cache

logger = logging.getLogger(__name__)
logger.setLevel("INFO")


def save_response():
    return None


def get_pokemon_species(offset: int, limit: int, session: requests.Session):
    all_url = "https://pokeapi.co/api/v2/pokemon-species/"

    try:
        pokemon_species_dict_response = session.get(
            f"{all_url}?offset={offset}&limit={limit}"
        ).json()
    except requests.exceptions.ConnectionError:
        time.sleep(secs=2**offset)

        pokemon_species_dict_response = get_pokemon_species(
            offset=offset, limit=limit, session=session
        )
    return pokemon_species_dict_response


def filter_pokemon_data(pokemon_data: dict, wanted_games: list, offset: int) -> dict:
    pokemon_by_version = {version: [] for version in wanted_games}
    pokemon_urls = set()

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
                if version_name in wanted_games:
                    url = pokemon["url"].split("/")[-2]
                    pokemon_by_version[version_name].append(
                        url
                    )
    return pokemon_by_version


def get_pokemon() -> set:
    wanted_games = ["red", "blue", "leafgreen", "white"]
    OFFSET = 0
    LIMIT = 150

    SESSION = requests.Session()
    requests_cache.install_cache()  # 56 seconds

    pokemon_urls = set()

    while True:
        pokemon_ids = get_pokemon_species(offset=OFFSET, limit=LIMIT, session=SESSION)

        pokemon_by_version = filter_pokemon_data(
            pokemon_ids, wanted_games, offset=OFFSET
        )

        for version, pokemon_list in pokemon_by_version.items():
            pokemon_urls.update(pokemon_list)
        if not pokemon_ids["next"]:
            break
        else:
            OFFSET += LIMIT

    return pokemon_urls


if __name__ == "__main__":
    pokemon_by_version = get_pokemon()
    print(pokemon_by_version)
