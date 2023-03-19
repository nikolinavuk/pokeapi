
# Lego Pokemon Api Task

This repo is to solve the mandatory requirements from the POKE API task at lego.

## Installation

1. To be able to run the code install the requirements using:

    ```terminal
    make install_requirements
    ```

## Primary Requirements

1. The name, id, base_experience, weight, height and order of all Pokémon that appear in the any of the games `red`, `blue`, `leafgreen` or `white`.
2. The name of the `slot 1` (and if available `2`) type of each of the Pokémon's types.
3. The Body Mass Index of the Pokémon (hint: The formula for `BMI` is weight (kg) / height (m2))
4. The first letter of names of the Pokémon should be capitalized.
5. The url of the `front_default sprite`.
6. Prepare the data in an appropriate data format. Consider if it should be multiple or a single file.

## Running the Application

1. To run the app go inside the `poke_api.py`
2. You can provide custom parameters in the `main` function:
   1. OFFSET = 0
   2. LIMIT = 150
   3. GAME_VERSIONS = ["red", "blue", "leafgreen", "white"]

## Bonus Requirements

- Inside the repo there is an experimental folder

## Working with the code

- The code is written in Jupyter notebooks to speed up development, and to not spam the endpoints
