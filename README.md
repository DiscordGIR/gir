# GIR (Botty McBotface)
![](https://media.discordapp.net/attachments/688121419980341282/787792406443458610/gggggggir.png)

Moderation bot for r/Jailbreak

### Prerequisites for setup
- Python
- `poetry`
- `pyenv`
- MongoDB server

### Setup
1. `pyenv install 3.9.0`
2. `pyenv shell`
3. `poetry install` (use flag `--no-dev` for prod)
4. `poetry shell`
5. Create a file called `.env`. in the root of the project and define the following:
```
BOTTY_TOKEN      = "DISCORD TOKEN"
BOTTY_OWNER      = OWNER ID (int)
BOTTY_MAINGUILD  = MAIN GUILD ID (int)
BOTTY_NSAGUILD   = NSA GUILD ID (int)

-- you only need BOTTY_ENV if using locally
BOTTY_ENV        = "DEVELOPMENT"
```
6. Set up mongodb on your system
7. `python main.py` - if everything was set up properly you're good to go!

### First time use

If you aren't porting from Janet, you don't have any baseline data for the bot to work. I wrote a short script `setup.py` which you should fill in with data from your own server, then run `python setup.py`
