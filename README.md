# Botty McBotface
Moderation bot for r/Jailbreak

### Prerequisites
- Python
- `pipenv`
- `pyenv`
- MongoDB server

### Setup
1. `pipenv install`
2. Switch to the virtual environment created
3. Create a file called `.env`. in the root of the project and define the following:
```
BOTTY_TOKEN      = "DISCORD TOKEN"
BOTTY_OWNER      = OWNER ID (int)
BOTTY_MAINGUILD  = MAIN GUILD ID (int)
BOTTY_NSAGUILD   = NSA GUILD ID (int)

-- you only need BOTTY_ENV if using locally
BOTTY_ENV        = "DEVELOPMENT"

-- you only need these if you plan on using the old Postgres DB
-- (i.e when porting from Janet :)
BOTTY_DBHOST     = "127.0.0.1"
BOTTY_DBUSER     = "emy"
BOTTY_DB         = "janet"
BOTTY_DBPASSWORD = ""

```
4. Set up mongodb on your system
5. `python main.py` - if everything was set up properly you're good to go!

### First time use

If porting from Janet, run `python port.py` first (you will need the extra 4 env variables above if so).

If you aren't porting from Janet, you don't have any baseline data for the bot to work. I wrote a short script `setup.py` which you should fill in with data from your own server, then run `python setup.py`