

import random
import discord
from discord.ext import commands
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)

token ='MTA3ODk3OTU4MDA2NjUzMzM5Ng.GO_d7t.DYasqEjtuLAFFWlPC8oT2HlOmhbhJ-PKYcmbhs'

attackers = {
    1: "Thatcher",
    2: "Maverick",
    3: "Nomad",
    4: "Zero",
    5: "Ace",
    6: "Brava",
    7: "Finka",
    8: "Hibana",
    9: "Iana",
    10: "Jackal",
    11: "Sledge",
    12: "Twitch",
    13: "Zofia",
    14: "Ash",
    15: "Blackbeard",
    16: "Buck",
    17: "Capitao",
    18: "Flores",
    19: "Grim",
    20: "IQ",
    21: "Lion",
    22: "Osa",
    23: "Thermite",
    24: "Amaru",
    25: "Dokkaebi",
    26: "Fuze",
    27: "Gridlock",
    28: "Kali",
    29: "Nøkk",
    30: "Sens",
    31: "Ying",
    32: "Blitz",
    33: "Glaz",
    34: "Montagne"
}

defenders = {
    1: "Jäger",
    2: "Valkyrie",
    3: "Aruni",
    4: "Azami",
    5: "Bandit",
    6: "Ela",
    7: "Kaid",
    8: "Kapkan",
    9: "Mira",
    10: "Mozzie",
    11: "Smoke",
    12: "Wamai",
    13: "Alibi",
    14: "Echo",
    15: "Lesion",
    16: "Maestro",
    17: "Melusi",
    18: "Mute",
    19: "Pulse",
    20: "Solis",
    21: "Thorn",
    22: "Thunderbird",
    23: "Vigil",
    24: "Castle",
    25: "Doc",
    26: "Frost",
    27: "Goyo",
    28: "Oryx",
    29: "Rook",
    30: "Tachanka",
    31: "Warden",
    32: "Caveira",
    33: "Clash"
}

rankedmaps = {
    1: "Nighthaven Labs",
    2: "Kafe Dostoyevsky",
    3: "Oregon",
    4: "Border",
    5: "Chalet",
    6: "Clubhouse",
    7: "Stadium",
    8: "Bank",
    9: "Consulate",
    10: "Coastline",
    11: "Villa",
    12: "Theme Park",
    13: "Kanal",
    14: "Outback",
    15: "Emerald Plains",
    16: "Skyscraper"
}


    

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
    
    await ctx.send("Attacker assignments:")
    for member, attacker in attacker_assignments.items():
        await ctx.send(f"{member}: {attacker}")

    
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
    
    await ctx.send("Attacker assignments:")
    for member, defender in defender_assignments.items():
        await ctx.send(f"{member}: {defender}")

@bot.command()

async def map(ctx):
    await ctx.send(rankedmaps(random.randint(1,16)))



    

bot.run(token)

