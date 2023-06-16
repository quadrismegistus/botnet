## setup
import os,asyncio
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


import discord
intents = discord.Intents.all()
from sydcity import *


## server

bot=discord.Bot(intents=intents)
convos = {}

@bot.event
async def on_message(message):
    # botname = bot.user.display_name
    botname = 'Marxbot'
    howstr='a rogue communist algorithm'
    
    whitelist = [
        'communis',
        'system',
        'capitalis',
        'politi',
        'cats'
    ]

    if message.author.id == bot.user.id: return

    if bot.user.mentioned_in(message) or bot.user.display_name in str(message.content) or any(word in message.content for word in whitelist):
        async with message.channel.typing():
            mkey=message.author.id
            if not mkey in convos: convos[mkey] = Speeches()
            convo = convos[mkey]
            convo.add_speech(
                Speech(
                    who=message.author.display_name, 
                    what=message.content.replace(
                        f'<@{bot.user.id}>', 
                        botname
                    )
                )
            )
            sp = convo.dialogue_generate_for(
                who=botname,
                how=howstr,
                save=True,
                # intro='INT. DIVE BAR - NIGHT'
                temp=1.0
            )

            res = nodblspc(sp.what)

        await message.channel.send(res, reference=message)





get_model()
print('>> running')
bot.run(TOKEN)