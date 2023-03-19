
# Pokemon Api Task  <!-- omit in toc -->

This repo is to solve the mandatory requirements from the POKE API.

- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Bonus Requirements](#bonus-requirements)
- [Working with the code](#working-with-the-code)
- [Future Work](#future-work)

---

## Installation

1. The application was written in `python 3.8.16`
2. To be able to run the code install the requirements using:

    ```terminal
    make install_requirements
    ```

## Running the Application

1. The easiest way is to:

    ```terminal
    make poke_api.py
    ```

2. To run the app go inside the `poke_api.py`
3. You can provide custom parameters in the `main` function:
   1. OFFSET = 0
   2. LIMIT = 150
   3. GAME_VERSIONS = ["red", "blue", "leafgreen", "white"]

## Bonus Requirements

- Inside the repo there is a development folder which addresses some ideas such as GDPR request
- To use it make sure to have the requirements/local.txt installed

    ```terminal
    make install_local
    ```

## Working with the code

- The code is written in Jupyter notebooks to speed up development, and to not spam the endpoints

## Future Work

1. Add unit tests
2. Consider timeouts when making API calls?
3. Async calls? Yes or no?
4. Faker and Mimesis to obfuscate data
