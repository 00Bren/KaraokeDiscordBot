import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
from discord.utils import get
import time
import fileinput
import webbrowser
import os
import traceback
import sys
import math

userSongsDictionary = {}
users = set()
userTurns = []
admins = set()
lastPlayedTime = 0

def setupAdmins(): 
    file = open("./admins.txt", "r")
    ADMINS = file.read()
    file.close()
    ADMINS = ADMINS.split("\n")
    admins.update(ADMINS)

def isSuperAdmin(username):
    ## TODO - add this to a text file. 
    return False
    
def isAdmin(username):
    global admins
    if(isSuperAdmin(username)):
        return True
    elif(username in admins):
        return True
    else: 
        return False

def isYoutubeUrl(url):
    return "www.youtube.com" in url or "youtu.be" in url
    
def enQueueSong(user, songUrl):
    global userSongsDictionary
    global users
    global userTurns
    if not user in userSongsDictionary:
        userSongsDictionary[user] = []
    userSongsDictionary[user].append(songUrl)
    if user not in users:
        users.add(user)
        userTurns.append(user)

def dequeueSong():
    global userSongsDictionary
    global users
    global userTurns
    
    if len(userTurns) == 0:
        raise Exception("no users in song queue")
    
    nextUser = userTurns.pop(0)
    nextSong = userSongsDictionary[nextUser].pop(0)
    
    #Update Queues based on if the user has any songs left to play. 
    if len(userSongsDictionary[nextUser]) > 0:
        userTurns.append(nextUser)
    else: 
        users.remove(nextUser)
    
    return nextSong

async def addSong(username, user_message, message, client):
    global userSongsDictionary
    global users
    global userTurns    
    print("here")
    if " " not in user_message:
        await message.channel.send("Must provide arguments")
        return
    print (user_message)
    print (type(user_message))
    url = user_message.split(" ")[1]

    if not isYoutubeUrl(url):
        await message.channel.send(url + " is not a youtube url. Not adding to Queue. ")
        return 
    enQueueSong(username, url)
    await message.channel.send(f"added <" + url + "> to queue")

async def playNext(message, username, client):
    global userSongsDictionary
    global users
    global userTurns
    global lastPlayedTime
    if len(users) == 0:
        await message.channel.send("No songs in the queue. Try again after 'addSong'.")
        return
    
    currentTime = time.time()
    if lastPlayedTime + 15 > currentTime:
        await message.channel.send("You must wait 15 seconds between playing songs. It has been " + str(math.floor(currentTime - lastPlayedTime)) + " seconds")
        return
    else: 
        lastPlayedTime = currentTime    
    
    nextUser = userTurns[0]
    nextSong = dequeueSong()
    webbrowser.open_new_tab(nextSong)  # Go to example.com
    await message.channel.send(f'Opening {nextSong} for {nextUser} on bren\'s computer.')

async def nextSong(message, username, client):
    global userSongsDictionary
    global users
    global userTurns    
    if len(users) == 0:
        await message.channel.send("No songs in the queue. Try again after 'addSong'.")
        return         
    user = userTurns[0]
    nextSong = userSongsDictionary[user][0]
    await message.channel.send(f'NextSong is {nextSong}.')
    await message.channel.send(f'it was requested by {user}.')

async def myNextSong(message, username, client):
    global userSongsDictionary
    global users
    global userTurns    
    if userSongsDictionary[username] == None or len(userSongsDictionary[username]) == 0:
        await message.channel.send("No songs in the queue. Try again after 'addSong'.")
        return         
        
    userNextSong = userSongsDictionary[username][0]
    await message.channel.send(f'Your next song is {userNextSong}.')

async def deleteMyNextSong(message, username, client):
    global userSongsDictionary
    global users
    global userTurns    
    if userSongsDictionary[username] == None or len(userSongsDictionary[username]) == 0:
        await message.channel.send("No songs in the queue. Try again after 'addSong'.")
        return         
        
    userNextSong = userSongsDictionary[username].pop(0)
    if (len(userSongsDictionary[username]) == 0):
        users.remove(username)
        userTurns.remove(username)

    await message.channel.send(f'Deleted {userNextSong} from queue. ')

async def listSongs(message, username, client):
    global userSongsDictionary
    global users
    global userTurns
    if len(users) == 0:
        await message.channel.send("No songs in the queue. Try again after 'addSong'.")
        return         
    for user in userTurns:
        userSongs = ""
        for song in userSongsDictionary[user]:
            userSongs += song + "\n"
        await message.channel.send(f"{user}'s queue is:\n{userSongs}.")
        
async def listQueue(message, username, client):
    global users
    global userTurns
    if len(users) == 0:
        await message.channel.send("No songs in the queue. Try again after 'addSong'.")
        return    
    userQueue = ""
    userNumber = 1
    for user in userTurns:
        userQueue += f"{userNumber}. {user}\n"
        userNumber += 1
    await message.channel.send(f"Queue Order is:\n{userQueue}")
        
async def listMySongs(message, username, client):
    global userSongsDictionary
    global users
    if len(users) == 0:
        await message.channel.send("No songs in the queue. Try again after 'addSong'.")
        return         
    userSongs = ""
    for song in userSongsDictionary[username]:
        userSongs += song + "\n"
    await message.channel.send(f"{username}'s queue is:\n{userSongs}.")

async def skipSong(message, username, client):
    global userSongsDictionary
    global users
    global userTurns
    if len(users) == 0:
        await message.channel.send("No songs in the queue. Try again after 'addSong'.")
        return     
    user = userTurns[0]
    if (isAdmin(username) or user == username):
        userTurns.append(userTurns.pop(0))
        await message.channel.send(f"{user} added to the end of the queue.")
        await nextSong(message, username, client)
    else:
        await message.channel.send(f"{username} cannot skip other users")

async def deleteNext(message, username, client):
    global userSongsDictionary
    global users
    global userTurns
    if len(users) == 0:
        await message.channel.send("No songs in the queue. Try again after 'addSong'.")
        return      
    user = userTurns[0]
    if (isAdmin(username) or user == username):
        userSongsDictionary[user].pop(0)
        if (len(userSongsDictionary[user]) == 0):
            users.remove(user)
            userTurns.pop(0)
        await message.channel.send(f"{username} song removed from their queue.")
    else:
        await message.channel.send(f"{username} cannot delete other users' songs")
        
async def restart(message, client):
    username = str(message.author)
    if not isAdmin(username):
        await message.channel.send("You do not have permissions to shut down the bot")
        return
    await message.channel.send("Restarting: BEEP BOOP")
    os.execl(sys.executable, sys.executable, *sys.argv)
    

async def end(message, client): 
    print('entering end')
    username = str(message.author)
    if not isAdmin(username):
        await message.channel.send("You do not have permissions to shut down the bot")
        return
    await message.channel.send("Shutting Down. ")
    exit()
    
async def proxy(message, user_message, client):
    commands = user_message.split(" ")
    if (len(commands) < 3):
        await message.channel.send("Proxy Failed. Inputted incorrectly. ")
        return None
    proxyUser = commands[1]
    message = ""
    for i in range(len(commands)):
        if i > 1:
            message += commands[i] + " "
    return [proxyUser, message]

def run_discord_bot():

    file = open("./token.txt", "r")
    TOKEN = file.read()
    file.close()
    intents = discord.Intents().all()
    #intents = discord.Intents().default()
    #intents.members = True
    client = discord.Client(intents=intents)
    __COMMAND_PREFIX__ = '.'
    
    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')
        
    @client.event
    async def on_message(message):
        try:
            if message.author == client.user:
                return
            
            username = str(message.author)
            user_message = str(message.content)
            channel = str(message.channel)
            
            print(f'{username} said: "{user_message}" in ({channel})!')
            
            if not user_message.startswith(__COMMAND_PREFIX__):
                return
                
            command = user_message.split(" ")[0]
            
            command = command.lower()
            
            if user_message.startswith(__COMMAND_PREFIX__ + 'hi'):
                await message.channel.send("hi.")
                return
            if user_message.startswith(__COMMAND_PREFIX__ + 'proxy'):
                proxyUserAndMessage = await proxy(message, user_message, client)
                if proxyUserAndMessage is not None:
                    username = proxyUserAndMessage[0]
                    message.author = proxyUserAndMessage[0]
                    user_message = proxyUserAndMessage[1]
            if user_message.startswith(__COMMAND_PREFIX__ + 'end'):
                await end(message, client)
                return
            if user_message.startswith(__COMMAND_PREFIX__ + 'restart'):
                await restart(message, client)
                return                
            if user_message.startswith(__COMMAND_PREFIX__ + 'add'):
                await addSong(username, user_message, message, client)
                return            
            if user_message.startswith(__COMMAND_PREFIX__ + 'addSong'.lower()):
                await addSong(username, user_message, message, client)
                return
            if user_message.startswith(__COMMAND_PREFIX__ + 'playNext'.lower()):
                await playNext(message, username, client)
                return
            if user_message.startswith(__COMMAND_PREFIX__ + 'play'):
                await playNext(message, username, client)
                return
            if user_message.startswith(__COMMAND_PREFIX__ + 'nextSong'.lower()):
                await nextSong(message, username, client)
                return
            if user_message.startswith(__COMMAND_PREFIX__ + 'next'):
                await nextSong(message, username, client)
                return
            if user_message.startswith(__COMMAND_PREFIX__ + 'myNextSong'.lower()):
                await myNextSong(message, username, client)
                return
            if user_message.startswith(__COMMAND_PREFIX__ + 'myNext'.lower()):
                await myNextSong(message, username, client)
                return
            if user_message.startswith(__COMMAND_PREFIX__ + 'deleteMyNextSong'.lower()):
                await deleteMyNextSong(message, username, client)
                return
            if user_message.startswith(__COMMAND_PREFIX__ + 'deleteMyNext'.lower()):
                await deleteMyNextSong(message, username, client)
                return
            if user_message.startswith(__COMMAND_PREFIX__ + 'listSongs'.lower()):
                await listSongs(message, username, client)
                return                
            if user_message.startswith(__COMMAND_PREFIX__ + 'listQueue'.lower()):
                await listQueue(message, username, client)
                return    
            if user_message.startswith(__COMMAND_PREFIX__ + 'listMySongs'.lower()):
                await listMySongs(message, username, client)
                return
            if user_message.startswith(__COMMAND_PREFIX__ + 'mySongs'.lower()):
                await listMySongs(message, username, client)
                return
            if user_message.startswith(__COMMAND_PREFIX__ + 'myQueue'.lower()):
                await listMySongs(message, username, client)
                return
            if user_message.startswith(__COMMAND_PREFIX__ + 'skipSong'.lower()):
                await skipSong(message, username, client)
                return
            if user_message.startswith(__COMMAND_PREFIX__ + 'skip'):
                await skipSong(message, username, client)
                return            
            if user_message.startswith(__COMMAND_PREFIX__ + 'deleteNext'.lower()):
                await deleteNext(message, username, client)
                return                      
            if user_message.startswith(__COMMAND_PREFIX__ + 'delete'):
                await deleteNext(message, username, client)
                return    
        except Exception:
            print ("exception")
            traceback.print_exc()

    client.run(TOKEN)

setupAdmins()
run_discord_bot()
