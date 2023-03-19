install_requirements:
	pip install -r requirements.txt

clean_pyenv:
	pip uninstall -y -r <(pip freeze)

run_pokemon_api:
	python poke_api.py