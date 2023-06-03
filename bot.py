import random
import discord
import asyncio
import json
from discord import Button, ButtonStyle
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


try:    # TARKISTA ONKO CONFIG FILEÄ (KÄYTÄN ESIM LOCAALISSA AJOSSA DEVAAMISEEN)
    from config import TOKEN
    token = TOKEN
    print("config file found, using dev token")
except ImportError:  # JOS EI, BOTTI ON TODENNÄKÖISESTI PILVESSÄ JA JOSSAIN ON ENV
    print("No config.py, using environment variable")
    token = os.environ["TOKEN"]

collection = db["diskodb"]

def writeLocalJson():       # DATABASE HAKU KAIKKI LOCAALIIN JSONIIN, TEHDÄÄN KÄYNNISTÄMISEN JA ASETUSPÄIVITYKSIEN YHTEYDESSÄ, JOTTA BOTTI EI TARVITSE JOKA KOMENTOON YHTEYTTÄ DATABASEEN
    all_data = list(collection.find())
    with open('data.json', 'w') as file:
        json.dump(all_data, file)

def startup():             # KÄYNNISTYKSESSÄ TARKISTETAAN ONKO DATABASESSA DATAA, JOS EI OLE, LUODAAN TYHJÄ JSON FILE
    data = list(collection.find())
    if data:
        # jos on dataa
        print("Database data found, loading...")
        with open('data.json', 'w') as file:
            json.dump(data, file)
    else:
        # jos ei ole dataa
        print("No database data found, creating file...")
        with open('data.json', 'w') as file:
            json.dump({}, file)
        print("Empty file created.")
        


class QueChannelSetup(discord.ui.Select):  # VALIKKO OLIO SETUPPI / SELECT OLIO
    def __init__(self, voice_channels):
        Options = []
        for channel in voice_channels:      # KÄY LÄPI KAIKKI SERVERIN KANAVAT JA LISÄÄ NE VALIKKOON
            Options.append(discord.SelectOption(label=channel.name, value=str(channel.id)))

        super().__init__(placeholder="Valitse kanava jonotustoiminnolle", max_values=1, min_values=1, options=Options)
    async def callback(self, interaction: discord.Interaction):
        selected_option_value = self.values[0]
        selected_option_label = next((option.label for option in self.options if option.value == selected_option_value), None)
        await interaction.response.send_message(f"Valitun jonotuskanavan nimi on: {selected_option_label}", ephemeral=True)
        self.view.value = self.values[0]
        self.view.stop()  # EI poista valikko näkyvistä mutta se ei enään toimi -> ihan ok
        

class QueChannelSetupView(discord.ui.View):  # VALIKKO VIEW, saa ja välittää eteenpäin voice channelit
    def __init__(self, *, timeout=15, voice_channels):
        super().__init__(timeout=timeout)
        self.value = None
        self.add_item(QueChannelSetup(voice_channels))

    


class Queue:            # JONO OLIO, sisältää taulukon jonottajista ja getterit ja setterit yms jonosta poistumiset yms, SAA GUILD ID:n jotta oliot erotetaan per palvelin
    def __init__(self, guild_id):
        self.guild_id = guild_id
        self.queue = []
        print("Queue created")

    async def add_to_queue(self, member):  # user id kanssa pelataan taulukossa
        self.queue.append(member)
        await member.send("Liityit jonoon")

    async def remove_from_queue(self, user):
        if user in self.queue:
            self.queue.remove(user)
            await user.send("Poistuit jonosta")

    async def print_queue(self):
        queue_string = ', '.join([user.name for user in self.queue])
        return queue_string if queue_string else 'Jono on tyhjä.'

    async def get_queue(self):
        return self.queue

 ## ------------------- BOT COMMANDS ------------------- ##   
        
startup()
print("Bot starting...")
queues = {}   # JONOT, KEY = GUILD ID, VALUE = QUEUE OLIO

async def join_queue(guild_id, member): # JONON LISÄYS FUNCTIO, tarkistaa onko jonoa olemassa, tarpeen tullen luo. Tarkistus jonon tarpeestä tehtävä aiemmin!!
    if guild_id in queues:
        await queues[guild_id].add_to_queue(member)
    else:
        queues[guild_id] = Queue(guild_id)
        await queues[guild_id].add_to_queue(member)

async def leave_queue(guild_id, member):    # JONOSTA POISTUMINEN
    if guild_id in queues:
        await queues[guild_id].remove_from_queue(member)
    else:
        member.send("Et ole jonossa")
        return


@bot.command()
async def join(ctx):    # bottikomento jonoon liittyminen
    guild_id = str(ctx.guild.id)
    guild_data = collection.find_one({"_id": guild_id}) # TARKISTAA ONKO JONOTUSTOIMINTO KÄYTÖSSÄ
    if not guild_data:
        await ctx.send("Serverillä ei ole jonotustoimintoa käytössä")
        return
    #TARVITSEEKO TÄHÄN TARKISTUKSEN ONKO JONOLLE TARVETTA? esim vertaus jonotuskanavan jäsenmäärä vrt jäsen cap--------------------------------------------------------
    await join_queue(guild_id, ctx.author) # LISÄÄ JONOOON

@bot.command()
async def leave(ctx):  # bottikomento jonosta poistuminen
    guild_id = str(ctx.guild.id)
    guild_data = collection.find_one({"_id": guild_id})
    if not guild_data:
        await ctx.send("Serverillä ei ole jonotustoimintoa käytössä")
        return
    
    await leave_queue(guild_id, ctx.author)

@bot.command()
async def showque(ctx): # bottikomento jonon näyttäminen
    guild_id = str(ctx.guild.id)
    guild_data = collection.find_one({"_id": guild_id})
    if not guild_data:
        await ctx.send("Serverillä ei ole jonotustoimintoa käytössä")
        return
    
    queue = queues.get(guild_id)
    if not queue:
        await ctx.send("Jonoa ei ole")
        return
    queue_string = await queue.print_queue()
    await ctx.send(f"Jonossa on: {queue_string}")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def setQueChannel(ctx):                                        #SET QUE CHANNEL
    guild_id = str(ctx.guild.id)  # kääntö stringiksi hakua varten

    guild_data = collection.find_one({"_id": guild_id})
    if guild_data:
        await ctx.send("Serverillä on jo jonotustoiminto käytössä, poista se ensin")
        return
    voice_channels = ctx.guild.voice_channels
    if not voice_channels:  # check if the list is empty
        await ctx.send("Serverillä ei ole äänikanavia.")
        return

    view = QueChannelSetupView(voice_channels=voice_channels) # VALIKKO VIEW
    await ctx.send("Valitse kanava jolle jonotustoiminto otetaan",  view=view)
    await view.wait()
    if not view.value:
        await ctx.send("Jonotuskanavaa ei asetettu")
        return
    que_channel_id = view.value

    try:
        await ctx.send("Anna maximipelaajamäärä jonotuskanavalle (pelkkä luku)") # aseta kanavan cap
        msg = await bot.wait_for("message", check=lambda message: message.author == ctx.author, timeout=30)
        que_channel_cap = msg.content
    except asyncio.TimeoutError:
        await ctx.send("Aikakatkaisu, jonotuskanavaa ei asetettu")
        return
    except ValueError:
        await ctx.send("Et antanut lukua oikein, jonotuskanavaa ei asetettu")
        return


    collection.insert_one({"_id": guild_id, "settings": {"que_channel": que_channel_id, "que_channel_cap": que_channel_cap}}) # LISÄÄ DATABASEEN
    print("Tallennettu")
    writeLocalJson() # DATABASESTA UUSIN VERSIO LOCAALIIN
    

    
@bot.command()
@commands.has_permissions(manage_channels=True)
async def removeQueChannel(ctx): # POISTAA JONOKANAVA-ASETUKSEN, tarkistaa ensin onko
    guild_id = str(ctx.guild.id)
    guild_data = collection.find_one({"_id": guild_id})
    if not guild_data:
        await ctx.send("Serverillä ei ole jonotustoimintoa käytössä")
        return
    collection.delete_one({"_id": guild_id})
    writeLocalJson()
    await ctx.send("Jonotustoiminto poistettu")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def checkQueChannel(ctx): # TARKISTAA ONKO JONOKANAVA ASETETTU JA KERTOO MIKÄ SE ON
    guild_id = str(ctx.guild.id)
    guild_data = collection.find_one({"_id": guild_id})
    if not guild_data:
        await ctx.send("Serverillä ei ole jonotustoiminnolla varustettua kanavaa")
    else:
        que_channel_id = guild_data.get('que_channel')
        que_channel = bot.get_channel(int(que_channel_id))
        if que_channel:
            await ctx.send(f"Jonotuskanavaksi asetettu kanava on: {que_channel.name}")
        else:
            await ctx.send("Jonotuskanavaa ei löytynyt, se voi olla poistettu")


@bot.command() # GOOD VIBES
async def vibes(ctx):
    await ctx.send("Good vibes!")

@bot.command() # R6 SIEGEEN TEHTY RANDOM TIIMI GENERAATTORI, KATSOO VOICECHANNELIN JÄSENET JOSTA KOMENTO TULEE JA ARPOO SIITÄ KAKSI TIIMIÄ
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
async def attRoulette(ctx):  # KÄYTTÄÄ ATTACKER LISTAA, KYSYY BANNIT JA TEKEE UUDEN LISTAN JOSSA BANNITUT KARSITTU JA ARPOO VOICE CHANNELIN JÄSENILLE OPERAATTORIT
    if ctx.author.voice is None:
        await ctx.send("Et ole millään kanavalla!")
        return
    
    voice_channel = ctx.author.voice.channel
    
    members = voice_channel.members

    if len(members) < 2:
       await ctx.send("Olet yksin, tylsää")
       return
    
    # Varoita jos yli 5 kanavalla, jatka silti
    if len(members) > 5:
        await ctx.send("Teitä on yli 5, kaikille arvotaan, pelasi tai ei.")
    
    # kysy ketkä bannittu, tähän onko järkevämpää vaihtoehtoa? Ongelma: menulistan/ dropdownin max pituus on 25
        await ctx.send("Mitkä hyökkääjät on bannittu? Erottele pilkulla (esim Thatcher, Ash) Jos ei bannia vastaa välilyönnillä (Esim Ash,  )(Esim  ,  )")
        
        msg = await bot.wait_for("message", check=lambda message: message.author == ctx.author)
        banned_attackers = [attacker.strip().lower() for attacker in msg.content.split(",") if attacker.strip()]
  

    
    
    # lista saatavilla olevista
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
async def defRoulette(ctx): # KÄYTTÄÄ DEFENDER LISTAA, KYSYY BANNIT JA TEKEE UUDEN LISTAN JOSSA BANNITUT KARSITTU JA ARPOO VOICE CHANNELIN JÄSENILLE OPERAATTORIT
    if ctx.author.voice is None:
        await ctx.send("Et ole millään kanavalla!")
        return
    
    voice_channel = ctx.author.voice.channel
    
    members = voice_channel.members

    if len(members) < 2:
        await ctx.send("Olet yksin, tylsää")
        return
    
    # Varoita jos yli 5 kanavalla, jatka silti
    if len(members) > 5:
        await ctx.send("Teitä on yli 5, kaikille arvotaan, pelasi tai ei.")
    
    # kysy bannit
    await ctx.send("Mitkä puolustajat on bannittu? Erottele pilkulla (esim Bandit, Jager) Jos ei bannia vastaa välilyönnillä (Esim Ash,  )(Esim  ,  )")
    
    msg = await bot.wait_for("message", check=lambda message: message.author == ctx.author)
    response = await client.wait_for('message')
    banned_defenders = [defender.strip().lower() for defender in msg.content.split(",") if defender.strip()]
    

    
    # Listaa jäljelläolevat
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


# --------------------------------- BOT EVENTS --------------------------------- #

@bot.event  
async def on_voice_state_update(member, before,after): # JONOKANAVAN TILAN VALVONTA, JOS KANAVALLE TULEE CAPIN YLITTÄVÄ MÄÄRÄ, BOT KYSYY HALUAAKO PELAAJA JONOON
    if before.channel is None and after.channel is not None:
        joined_channel = after.channel

    elif before.channel is not None and after.channel is None:
        joined_channel = before.channel

    else:
        return
    
    guild_id = str(joined_channel.guild.id)
    guild_data = collection.find_one({"_id": guild_id})
    if not guild_data: # JOS EI OLE JONOKANAVAA
        return

    # JOS JONOKANAVA ASETUS ON OLEMASSA
    que_channel_id = guild_data['settings'].get('que_channel') 
    que_channel_cap = int(guild_data['settings'].get('que_channel_cap', 0))

    if str(joined_channel.id) == que_channel_id:
        # Kyseessä on jonokanava
        num_members = len(joined_channel.members)
        print(f"Jonokanavalla on {num_members} pelaajaa")

        if num_members >= que_channel_cap:
            # kanava on täynnä
            newest_member = joined_channel.members[-1]
            await newest_member.send("Kanavalla näyttää olevan jo "+ que_channel_cap + " pelaajaa, haluatko liittyä jonoon?", components=[[
                Button(style=ButtonStyle.green, label="Kyllä", custom_id="join_que"),
                Button(style=ButtonStyle.red, label="Ei", custom_id="dont_join_que")
            ]])   # uusimmalle liittyjälle nappi haluaako jonoon
            def check(res):
                return newest_member.author == res.user and res.channel == newest_member.channel
            try:
                res = await bot.wait_for("button_click", check=check, timeout=30)
                if res.component.custom_id == "join_que":
                    await newest_member.send(f"{newest_member.mention} liittyi jonoon")
                    await join_queue(guild_id, newest_member)

                elif res.component.custom_id == "dont_join_que":
                    await newest_member.send(f"{newest_member.mention} ei liittynyt jonoon")

            except asyncio.TimeoutError:
                await newest_member.send("Aikakatkaisu, et liittynyt jonoon")
                return

    #jos joku lähtee jonokanavalta, seuraavan jonottajan kutsu, hylkäysvaihtoehdot jne skippauslogiikka. 
           

            
# TÄYTYY TESTATA JONOA JONKUN KANSSA; LAITA CAPPI YHTEEN JA LIITY TOISENA


bot.run(token)

