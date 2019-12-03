import discord
import yaml
from pathlib import Path

apikey = Path('apikey.yaml')

with apikey.open('r') as file:
    key = yaml.load(file, Loader=yaml.SafeLoader)

client = discord.Client()

@client.event
async def on_ready():
    print(f'connected as {client.user}')

@client.event
async def on_message(msg: discord.Message):
    if msg.author == client.user:
        return
    print(msg.channel)
    print(msg.content)
    if msg.author.display_name == 'Stream':
        await msg.channel.send('shut the fcuk up')

client.run(key['DISCORD_TOKEN'])
