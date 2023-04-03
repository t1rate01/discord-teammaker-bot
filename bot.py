

import random
import discord
from discord.ext import commands
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)

token ='YOUR TOKEN HERE'

@bot.command()

async def hello(ctx):
        await ctx.send("Hello!")

@bot.command()

async def vibes(ctx):
    await ctx.send("Good vibes!")

@bot.command()
async def teamshere(ctx):
    if not ctx.author.voice:
        await ctx.send("Et ole millään kanavalla....")
        return

    voice_channel = ctx.author.voice.channel
    members = voice_channel.members
    member_names = [member.name for member in members][:10]
    random.shuffle(member_names)

    num_members = len(member_names)
    if num_members < 2:
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

async def team(ctx):
    await ctx.send("Anna 10 nimeä pilkulla erotettuna")

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel
    
    try:
        msg = await bot.wait_for('message',check=check, timeout=45.0)
    except asyncio.TimeoutError:
        await ctx.send("Liian hidas! Yritä uudelleen!")
        return

    nicknames = msg.content.split(",")
    nicknames = [nickname.strip() for nickname in nicknames]

    if len(nicknames) != 10:
        await ctx.send("Sori, ei teitä ole tarpeeksi....")
        return

    random.shuffle(nicknames)
    team1 = nicknames[:5]
    team2 = nicknames[5:]

    await ctx.send(f"Tiimi 1: {', '.join(team1)}\nTiimi 2: {', '.join(team2)}")

bot.run(token)

