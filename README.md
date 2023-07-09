# KaraokeDiscordBot
Bot to queue up karaoke songs from youtube and open them in a browser when it's the user's turn. 

Step 1: Install Python: 

download python 3

I tested with 3.11.4, but future versions should work. 

add python.exe to PATH

Hit install now. 

Wait for install to finish

Hit close. 

open a terminal or command prompt

type 'python --version' and make sure it installed correctly. 

Do the same for 'pip --version'

---------------------------------------------------------------

Step 2: Pip install dependencies:

go to a command prompt and run these commands

* pip install discord

---------------------------------------------------------------

Step 3: Setup your bot:

Go to the discord developers portal 'https://discord.com/developers' and create an application. 

Under bot - go to 'Privileged Gateway Intents' and check all the boxes. 

Under bot - hit reset token, then save that string to a file called token.txt. 

Copy token.txt to the same folder as karaokeBot.py

---------------------------------------------------------------

Step 4: Add Admins to file:

Create a file called admins.txt in the same folder as karaokeBot.py

Any user that should have access to admin commands should be added to this text file separated by a newline.

Example of what the file should look like. : 

```
user1
user2
user3
```

---------------------------------------------------------------

Step 5: Run the bot:

Create a terminal in the same folder/filepath as karaokeBot.py. 

run 'python karaokeBot.py' from the command prompt. 
