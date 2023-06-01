import random
import discord
import json
from pymongo import MongoClient
from discord.ext import commands
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
import os
from operators import attackers, defenders, rankedmaps

bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

try:
    from config import MONGO_URL
    client = MongoClient(MONGO_URL, server_api=ServerApi('1'))
    db = client.diskodb
except ImportError:
    MONGO_URL = os.environ["MONGO_URL"]
    client = MongoClient(MONGO_URL, server_api=ServerApi('1'))
    db = client.diskodb

# KESKEN: TARKISTA ETTÄ DATABASE TOIMII, JOS DATABASE TYHJÄ NIIN TEE TYHJÄ JSON
# VALMIS 
# SEURAAVAKSI: DESIGNATED CHANNEL FUNCTIO JA TALLENNUS DATABASEEN
try:
    from config import TOKEN
    token = TOKEN
except ImportError:
    token = os.environ["TOKEN"]

collection = db["diskodb"]

def startup():
    data = collection.find_one()

    if data:
        # jos on dataa
        with open('data.json', 'w') as file:
            json.dump(data, file)
    else:
        # jos ei ole dataa
        with open('data.json', 'w') as file:
            json.dump({}, file)
            # Uppaa mongoDB:hen ja anna id jota käytetään
        collection.insert_one({"_id": "server_channel_info"})

startup()

@bot.command()
async def hello(ctx):
        await ctx.send("Peliä!")

@bot.command()
async def vibes(ctx):
    await ctx.send("Good vibes!")

@bot.command()
async def teams(ctx):
    if not ctx.author.voice:
        await ctx.send("Et ole millään kanavalla....")
        return

    voice_channel = ctx.author.voice.channel
    members = voice_channel.members
    member_names = [member.name for member in members][:10]
    random.shuffle(member_names)

    num_members = len(member_names)
    if num_members < 6:
        await ctx.send("Ei teitä ole tarpeeksi, menkää nukkumaan!")
        return

    team_size = num_members // 2
    teams = [member_names[i:i+team_size] for i in range(0, num_members, team_size)]

   # Jos pariton määrä, ylimääränen ekaan tiimiin
    if num_members % 2 == 1:
        teams[0].append(teams[1].pop())

    team_strings = [f"Team {i+1}: {', '.join(team)}" for i, team in enumerate(teams)]

    await ctx.send('\n'.join(team_strings))


@bot.command() 

async def attroulette(ctx):
    if ctx.author.voice is None:
        await ctx.send("Et ole millään kanavalla!")
        return
    
    voice_channel = ctx.author.voice.channel
    
    members = voice_channel.members
    
    # Varoita jos yli 5 kanavalla, jatka silti
    if len(members) > 5:
        await ctx.send("Teitä on yli 5, kaikille arvotaan, pelasi tai ei.")
    
    # Ask for banned attackers
    await ctx.send("Mitkä hyökkääjät on bannittu? Erottele pilkulla (esim Thatcher, Ash) Jos ei bannia vastaa välilyönnillä (Esim Ash,  )(Esim  ,  )")
    msg = await bot.wait_for("message", check=lambda message: message.author == ctx.author)
    banned_attackers = [attacker.strip().lower() for attacker in msg.content.split(",") if attacker.strip()]
    
    # Make a list of available attackers
    available_attackers = [value for key, value in attackers.items() if value.lower() not in banned_attackers]
    
    random.shuffle(available_attackers)
    
    attacker_assignments = {}
    for i in range(len(members)):
        attacker_assignments[members[i].name] = available_attackers[i % len(available_attackers)]
    
    message = ""
    for member, attacker in attacker_assignments.items():
        message += f"{member}: {attacker}\n"
    await ctx.send("Roolit: \n" +message)


    
@bot.command() 

async def defroulette(ctx):
    if ctx.author.voice is None:
        await ctx.send("Et ole millään kanavalla!")
        return
    
    voice_channel = ctx.author.voice.channel
    
    members = voice_channel.members
    
    # Varoita jos yli 5 kanavalla, jatka silti
    if len(members) > 5:
        await ctx.send("Teitä on yli 5, kaikille arvotaan, pelasi tai ei.")
    
    # Ask for banned attackers
    await ctx.send("Mitkä puolustajat on bannittu? Erottele pilkulla (esim Bandit, Jager) Jos ei bannia vastaa välilyönnillä (Esim Ash,  )(Esim  ,  )")
    msg = await bot.wait_for("message", check=lambda message: message.author == ctx.author)
    banned_defenders = [defender.strip().lower() for defender in msg.content.split(",") if defender.strip()]
    
    # Make a list of available attackers
    available_defenders = [value for key, value in defenders.items() if value.lower() not in banned_defenders]
    
    random.shuffle(available_defenders)
    
    defender_assignments = {}
    for i in range(len(members)):
        defender_assignments[members[i].name] = available_defenders[i % len(available_defenders)]
    
    message = ""
    for member, defender in defender_assignments.items():
        message+= f"{member}: {defender}\n"
    await ctx.send("Roolit: \n "+message)

@bot.command()

async def map(ctx):
    mappi = random.choice(list(rankedmaps.values()))
    await ctx.send(f"{mappi}")



    

bot.run(token)

