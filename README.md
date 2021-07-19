# GIR (Botty McBotface)
![](https://media.discordapp.net/attachments/688121419980341282/787792406443458610/gggggggir.png)

Moderation bot for r/Jailbreak

### Prerequisites for setup
> Note: the setup instructions assume you're using macOS or a Linux based distro. I have not tested on Windows, but I assume it would work with some effort.
- Python
- `poetry`
- `pyenv`
- MongoDB server
- [Spotify developer account](https://developer.spotify.com/dashboard/)

If you want to use the `!canijailbreak` (`!cij`) command, you will need to request an API key from the developer of [canijailbreak2.com](https://canijailbreak2.com)
### Setup
1. `pyenv install 3.9.1`
2. `pyenv shell 3.9.1`
3. `poetry install` (use flag `--no-dev` for prod)
4. `poetry shell`
5. Create a file called `.env`. in the root of the project and define the following:

```
BOTTY_TOKEN      = "DISCORD TOKEN"
BOTTY_OWNER      = OWNER ID (int)
BOTTY_MAINGUILD  = MAIN GUILD ID (int)

LAVALINK_PASS          = "yourpasswwordhere"
SPOTIFY_CLIENT_ID      = "YOUR SPOTIFY CLIENT ID"
SPOTIFY_CLIENT_SECRET" = "YOUR SPOTIFY SECRET"

# the below is for the canijailbreak command
CIJ_KEY = "CIJ TOKEN"
```

6. Download the latest version of the Lavalink jar file from [here](https://github.com/freyacodes/Lavalink/releases/), and put it in the root of the project
7. Set up the `application.yml` as shown in the example [here](https://github.com/freyacodes/Lavalink/blob/master/LavalinkServer/application.yml.example ), also in the root of the project. Use the same password as in the `.env` file. You need not change anything else.
8. Run Lavalink with `java -jar Lavalink.jar`
9. Set up mongodb on your system (and see *First time use* to populate the database with initial data)
10. Run `python scrape_emojis.py`. This will pull emoji data needed for `!jumbo`. You only need to do this once (or any time you want to update the list of emojis).
11. `python main.py` - if everything was set up properly you're good to go!

### First time use

If you aren't porting from Janet, you don't have any baseline data for the bot to work. I wrote a short script `setup.py` which you should fill in with data from your own server, then run `python setup.py`
