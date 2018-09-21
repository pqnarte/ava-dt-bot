import asyncio

import os

import discord
from discord import Game
from discord.ext.commands import Bot
from discord.ext import commands

from datetime import datetime

from bs4 import BeautifulSoup
import requests

BOT_PREFIX = (".")

ava_logo_url='https://upload.wikimedia.org/wikipedia/commons/1/15/Alliance-of-valiant-arms-logo.png'
Category_link = "http://ava-dog-tag.wikia.com/wiki/Category:"
weapon_categories = ['Pointman','Rifleman','Sniper','Secondary']
map_categories = ['Annihilation','Demolition']

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Bot services (Top)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

bot = Bot(command_prefix=BOT_PREFIX)
bot.remove_command('help')

print(discord.__version__)


@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name='Type .help for commands', type=1), status=None, afk=False)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#General functions
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def remove_leads(args):
    temp = args.split(';')
    for j in range(len(temp)):
        temp[j] = temp[j].lstrip()
    args = ';'.join(temp)
    return args
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#general commands
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@bot.command(pass_context = True)
async def help(ctx):
    author = ctx.message.author
    help_string = ("""```fix
-------------------------------------------------------------------------------------------
---------------------------------------Help Commands---------------------------------------
-------------------------------------------------------------------------------------------```
__**AVA Dog Tag commands:**__
```md
# .weapons
> Presents you a simple list of all the weapons available
# .weapon <weapon_name_here>
> Shows all the stats about the weapon you select
# .maps
> Presents you a simple list of all the maps available
# .map <map_name_here>
> Shows all the info about the map you select```

Created by xVisions""")
    await bot.send_message(author, help_string)
    message = await bot.say(str(author.display_name)+", I sent you a private message with the help commands.")
    await asyncio.sleep(10)
    await bot.delete_message(message)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#AVA functions
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_weapon_data(weapon_link):
    data = []
    r = requests.get(weapon_link)
    soup = BeautifulSoup(r.text,'html.parser')
    #description = soup.find("meta",  property="og:description")
    Image_tag = soup.find('figure',attrs={'class':'pi-item pi-image'})
    Image_url = ''
    if Image_tag is not None:
        Image_url = Image_tag.find('a')['href']
    embed = discord.Embed(color = 0x00ff00)
    results = soup.find_all('div',attrs={'class':'pi-item pi-data pi-item-spacing pi-border-color'})
    for result in results:
        name_tag= result.find("h3")
        value_tag = result.find('div')
        data.append([name_tag.text,value_tag.text])
    #result = [data,description["content"],Image_url]
    result = [data,Image_url]
    return result

def get_map_data(map_link):
    data = []
    r = requests.get(map_link)
    soup = BeautifulSoup(r.text,'html.parser')
    #description = soup.find("meta",  property="og:description")
    Image_tag = soup.find('figure',attrs={'class':'pi-item pi-image'})
    Image_url = Image_tag.find('a')['href']
    embed = discord.Embed(color = 0x00ff00)
    results = soup.find_all('div',attrs={'class':'pi-item pi-data pi-item-spacing pi-border-color'})
    for result in results:
        name_tag= result.find("h3")
        value_tag = result.find('div')
        data.append([name_tag.text,value_tag.text])
    #result = [data,description["content"],Image_url]
    result = [data,Image_url]
    return result

def get_weapon_link(name):
    results = []
    for category in weapon_categories:
        link = Category_link+category
        r = requests.get(link)
        soup = BeautifulSoup(r.text,'html.parser')
        maps = soup.find_all('div',attrs={'class':"mw-content-ltr"})
        maps = maps[-1].find_all('a')
        for map in maps:
            link = map['href']
            if (name.upper() in link.upper()):
                results.append([map['title'],'http://ava-dog-tag.wikia.com'+link])
    return results

def get_map_link(name):
    results = []
    for category in map_categories:
        link = Category_link+category
        r = requests.get(link)
        soup = BeautifulSoup(r.text,'html.parser')
        maps = soup.find_all('div',attrs={'class':"mw-content-ltr"})
        maps = maps[-1].find_all('a')
        for map in maps:
            link = map['href']
            if (name.upper() in link.upper()):
                results.append([map['title'],'http://ava-dog-tag.wikia.com'+link])
    return results

def get_names_by_category(Category):
    names = []
    r = requests.get(Category_link+Category)
    soup = BeautifulSoup(r.text,'html.parser')
    results = soup.find_all('div',attrs={'class':"mw-content-ltr"})
    results = results[-1].find_all('a')
    for result in results:
        names.append(result.text)
    names.sort()
    return names

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#AVA Commands
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@bot.command(pass_context=True)
async def weapon(ctx,*args):
    if(len(args) > 0):
        i = 0
        link_data = get_weapon_link(' '.join(args))
        selected = True
        if len(link_data) > 1:
            selected = False
            string = ""
            for index in range(len(link_data)):
                string += '('+str(index+1)+') '+link_data[index][0]+'\n'
            await bot.say('Found several weapons in wikia, choose a number:')
            await bot.say(string)
            msg = await bot.wait_for_message(author = ctx.message.author)
            msg = remove_leads(msg.content)
            if int(float(msg))-1 in range(len(link_data)):
                selected = True
                i = int(float(msg))-1
            else:
                await bot.say('Not a valid answer, request canceled')
        if selected:
            try:
                weapon_data = get_weapon_data(link_data[i][1])
                embed = discord.Embed(title=link_data[i][0],url = link_data[i][1], color = 0x00ff00)
                embed.set_thumbnail(url=ava_logo_url)
                if len(weapon_data[1]) > 0:
                    embed.set_image(url=weapon_data[1])
                for field in weapon_data[0]:
                    embed.add_field(name=field[0],value=field[1])
                owner = await bot.get_user_info(os.getenv('OWNER_ID'))
                embed.set_footer(text='Created by '+owner.name+'#'+owner.discriminator
                    +' | '+datetime.now().strftime('%c'))
                await bot.say(embed=embed)
            except:
                await bot.say('No weapons found with the name '+' '.join(args))
    else:
        await bot.say("You need to type the weapon name after `.weapon`")

@bot.command(pass_context=True)
async def map(ctx,*args):
    if(len(args) > 0):
        i = 0
        link_data = get_map_link(' '.join(args))
        selected = True
        if len(link_data) > 1:
            selected = False
            string = ""
            for index in range(len(link_data)):
                string += '('+str(index+1)+') '+link_data[index][0]+'\n'
            await bot.say('Found several maps in wikia, choose a number:')
            await bot.say(string)
            msg = await bot.wait_for_message(author = ctx.message.author)
            msg = remove_leads(msg.content)
            if int(float(msg))-1 in range(len(link_data)):
                selected = True
                i = int(float(msg))-1
            else:
                await bot.say('Not a valid answer, request canceled')
        if selected:
            try:
                map_data = get_map_data(link_data[i][1])
                embed = discord.Embed(title=link_data[i][0],url=link_data[i][1], color = 0x00ff00)
                embed.set_thumbnail(url=ava_logo_url)
                embed.set_image(url=map_data[1])
                for field in map_data[0]:
                    embed.add_field(name=field[0],value=field[1])
                owner = await bot.get_user_info(os.getenv('OWNER_ID'))
                embed.set_footer(text='Created by '+owner.name+'#'+owner.discriminator
                    +' | '+datetime.now().strftime('%c'))
                await bot.say(embed=embed)
            except:
                await bot.say('No maps found with the name '+' '.join(args))
    else:
        await bot.say("You need to type the map name after `.map`")

@bot.command(pass_context=True)
async def weapons(ctx):
    weapons = []
    for index in range(len(weapon_categories)):
        weapons.append(get_names_by_category(weapon_categories[index]))
    embed = discord.Embed(title='Weapons list', color = 0x00ff00)
    embed.set_thumbnail(url=ava_logo_url)
    for index in range(len(weapon_categories)):
        string = ""
        for subindex in range(len(weapons[index])):
            string += weapons[index][subindex]+'\n'
        embed.add_field(name='\u200b \n'+weapon_categories[index]+':',value=string,inline=False)
    owner = await bot.get_user_info(os.getenv('OWNER_ID'))
    embed.set_footer(text='Created by '+owner.name+'#'+owner.discriminator
        +' | '+datetime.now().strftime('%c'))
    await bot.say(embed=embed)

@bot.command(pass_context=True)
async def maps(ctx):
    maps = []
    for index in range(len(map_categories)):
        maps.append(get_names_by_category(map_categories[index]))

    embed = discord.Embed(title='Maps list', color = 0x00ff00)
    embed.set_thumbnail(url=ava_logo_url)
    for index in range(len(map_categories)):
        string = ""
        for subindex in range(len(maps[index])):
            string += maps[index][subindex]+'\n'
        embed.add_field(name='\u200b \n'+map_categories[index]+':',value=string,inline=False)
    owner = await bot.get_user_info(os.getenv('OWNER_ID'))
    embed.set_footer(text='Created by '+owner.name+'#'+owner.discriminator
        +' | '+datetime.now().strftime('%c'))
    await bot.say(embed=embed)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#AVA ADMIN Commands
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#temporary functions
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#temporary commands
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Bot services (Bottom)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



async def list_servers():
    await bot.wait_until_ready()
    while not bot.is_closed:
        print("Current servers:")
        for server in bot.servers:
            print(server.name)
        await asyncio.sleep(600)


bot.loop.create_task(list_servers())
bot.run(os.getenv('TOKEN'))
