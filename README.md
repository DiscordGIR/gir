# Botty McBotface
Moderation bot for r/Jailbreak

### Prerequisites
- Python
- `pipenv`
- `pyenv`
- Postgresql setup

### Setup
1. `pipenv install`
2. Switch to the virtual environment created
3. Create a file called `.env`. in the root of the project and define the following:
```
BOTTY_TOKEN      = ""
BOTTY_OWNER      = ""
BOTTY_DBHOST     = ""
BOTTY_DBUSER     = ""
BOTTY_DB         = ""
BOTTY_DBPASSWORD = ""
```
4. Set up Postgresql on your system (and...)