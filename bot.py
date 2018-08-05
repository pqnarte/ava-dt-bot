import random
import urllib
import asyncio
import aiohttp
import json
import discord
import os
from discord import Game
from discord.ext.commands import Bot
from io import BytesIO
import xml.etree.ElementTree as ET
from discord.ext import commands
from weapon import Weapon
import sqlite3

ava_logo_url='https://upload.wikimedia.org/wikipedia/commons/1/15/Alliance-of-valiant-arms-logo.png'
BOT_PREFIX = ("?")
general_weapon_stats = ['Hit Damage','Range','Single Fire Acc','Auto Fire Acc','Recoil Control','Fire Rate','Mag Capacity','Mobility']

bot = Bot(command_prefix=BOT_PREFIX)
bot.remove_command('help')
conn = sqlite3.connect('weapon.db'); #Bom para testar
c = conn.cursor()

print(discord.__version__)


@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name='AVA Dog Tag', type=1), status=None, afk=False)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#general commands
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@bot.command(pass_context = True)
async def help(ctx):
    author = ctx.message.author
    embed = discord.Embed(description = "<> = optional\n/ = or", colour=0x00ffff)
    embed.set_author(name='Possible commands:')
    embed.add_field(name=BOT_PREFIX+'info @user',value='Returns @user info', inline = False)
    embed.add_field(name=BOT_PREFIX+'serverinfo',value='Returns server info', inline = False)
    #embed.add_field(name=BOT_PREFIX+'clean_database',value='Cleans everything in the database, (to be removed)', inline = False)
    text = BOT_PREFIX+"weapon\t<remove (weapon / mods / all mods)>\n\t\t\t\t\t <(weapon_name / add) <mods>>"
    description = ("Possible uses:\n"+
                    BOT_PREFIX+"weapon: displays all weapons arranged by classes\n"+
                    BOT_PREFIX+"weapon weapon_name: displays the weapon stats\n"+
                    BOT_PREFIX+"weapon weapon_name mods: display all the mods of the weapon and related stat modifications\n"+
                    BOT_PREFIX+"weapon add: adds a weapon to the database\n"+
                    BOT_PREFIX+"weapon add mods: adds one mod to the weapon, if that mod has more than 1 stat effect, use the code again with the same mod name\n"+
                    BOT_PREFIX+"weapon remove weapon: removes a weapon from the database\n"+
                    BOT_PREFIX+"weapon remove mods: removes a specific mod from a weapon\n"+
                    BOT_PREFIX+"weapon remove all mods: removes all mods stored in the database of that weapon")
    embed.add_field(name=text,value=description, inline = False)
    await bot.send_message(author, embed=embed)

@bot.command(pass_context=True)
async def info(ctx, user: discord.Member):
	embed = discord.Embed(description="Here's what I could find.",color = 0x00ff00)
	embed.set_author(name=format(user.name), icon_url=user.avatar_url)
	embed.add_field(name="Nickname",value=user.display_name, inline = True)
	embed.add_field(name="ID",value=user.id, inline = True)
	embed.add_field(name="Status",value=user.status, inline = True)
	embed.add_field(name="Highest Role",value=user.top_role, inline = True)
	embed.add_field(name="Joined", value=user.joined_at.strftime('%a, %b %d, %Y %I:%M %p'), inline = True)
	embed.add_field(name="Registered", value=user.created_at.strftime('%a, %b %d, %Y %I:%M %p'), inline = True)
	if not format(user.game) == "None":
		embed.set_footer(text="Playing "+format(user.game))
	roles = ""
	count = 0
	for role in user.roles:
		if count > 0:
			if count > 1:
				roles+=",\t"
			roles+=format(role)
		count += 1
	if count > 1 :
		embed.add_field(name="Roles ["+str(count-1)+"]", value=roles, inline = False)
	embed.set_thumbnail(url=user.avatar_url)
	await bot.say(embed=embed)

@bot.command(pass_context=True)
async def serverinfo(ctx):
	embed = discord.Embed(description="Here's what I could find.", color = 0x00ff00)
	embed.set_author(name="Server Info", icon_url=ctx.message.server.icon_url)
	embed.add_field(name="Owner",value=ctx.message.server.owner, inline = False)
	embed.add_field(name="Name",value=ctx.message.server.name)
	embed.add_field(name="ID", value=ctx.message.server.id)
	embed.add_field(name="Number of roles", value = len(ctx.message.server.roles))
	embed.add_field(name="Number of members", value = len(ctx.message.server.members))
	embed.add_field(name="Server created at",value = ctx.message.server.created_at.strftime('%a, %b %d, %Y %I:%M %p'), inline = False)
	embed.set_thumbnail(url=ctx.message.server.icon_url)
	await bot.say(embed=embed)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#AVA functions
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def add_weapon(weap):
    with conn:
        c.execute("INSERT INTO weapons VALUES (:weaponName, :description, :weaponClass, :imageURL)",
            {'weaponName': weap.weaponName, 'description': weap.description, 'weaponClass': weap.weaponClass, 'imageURL': weap.imageURL})
        c.execute("DELETE FROM weapons WHERE rowid NOT IN (SELECT max(rowid) FROM weapons GROUP BY weaponName)")

def add_stats(weaponName, stats):
    with conn:
        c.execute("""INSERT INTO stats VALUES (
        :weaponName, :hitDamage, :range, :singleFireAcc, :autoFireAcc, :recoilControl, :fireRate, :magCapacity, :mobility)""",
        {'weaponName':weaponName, 'hitDamage':stats.hitDamage, 'range': stats.range, 'singleFireAcc':stats.singleFireAcc,
         'autoFireAcc':stats.autoFireAcc, 'recoilControl':stats.recoilControl, 'fireRate':stats.fireRate, 'magCapacity':stats.magCapacity,
         'mobility' :stats.mobility})
        c.execute("DELETE FROM stats WHERE rowid NOT IN (SELECT max(rowid) FROM stats GROUP BY weaponName)")

def add_mods(weaponName, mod):
    print('ADD MODS FUNCTION')
    print (weaponName + ',' +mod.modName + ',' +mod.modStat + ',' +mod.valueModifier)
    with conn:
        c.execute("INSERT INTO mods VALUES (:weaponName, :modName, :modStat, :valueModifier)",
            {'weaponName': weaponName, 'modName': mod.modName, 'modStat': mod.modStat, 'valueModifier': mod.valueModifier})

def get_weapon(weaponName):
    print('GET WEAPON FUNCTION')
    string = ""
    weapon = c.execute("SELECT * FROM weapons WHERE weaponName=:weaponName", {'weaponName': weaponName}).fetchone()
    weapon = ';'.join(weapon)
    return weapon

def get_weapons_by_type(weaponClass):
    string = ""
    weapon_of_type = c.execute("SELECT weaponName FROM weapons WHERE weaponClass=:weaponClass", {'weaponClass': weaponClass}).fetchall()
    for weapon in weapon_of_type:
        string += str(weapon).translate({ord(i):None for i in "'(),"}) +'\n'
    return string

def get_stats(weaponName):
    weapon_stats = c.execute("SELECT * FROM stats WHERE weaponName=:weaponName", {'weaponName': weaponName}).fetchone()
    weapon_stats = ';'.join(weapon_stats[1:])
    print('GET STATS FUNCTION')
    print(weapon_stats)
    return weapon_stats

def get_mods(weaponName):
    string = ""
    mod_names = c.execute("SELECT modName FROM mods WHERE weaponName=:weaponName AND rowid IN (SELECT rowid FROM mods GROUP BY modName)", {'weaponName': weaponName}).fetchall()
    print('GET MODS FUNCTION')
    print(mod_names)
    print()
    for singlemod in mod_names:
        temp_string = str(singlemod).translate({ord(i):None for i in "' (),"})
        string += temp_string +'\n'
    string = string[:-1]
    return string

def get_mod_values(weaponName,modName):
    string = ""
    mod_values = c.execute("SELECT modStat, valueModifier FROM mods WHERE weaponName=:weaponName AND modName=:modName", {'weaponName': weaponName,'modName':modName}).fetchall()
    print('GET MOD VALUES FUNCTION')
    print(weaponName+';'+modName)
    print(mod_values)
    print()
    for singlevalue in mod_values:
        string += str(singlevalue).translate({ord(i):None for i in "'() "}) + '\n'
    print(string)
    return string

def remove_weapon(weaponName):
    print('REMOVE WEAPON FUNCTION')
    print(weaponName)
    with conn:
        c.execute("DELETE FROM weapons WHERE weaponName = :weaponName",
        {'weaponName':weaponName})
        c.execute("DELETE FROM stats WHERE weaponName = :weaponName",
        {'weaponName':weaponName})
        c.execute("DELETE FROM mods WHERE weaponName = :weaponName",
        {'weaponName':weaponName})

def remove_mod(weaponName, modName):
    print('REMOVE MOD FUNCTION')
    print(weaponName, modName)
    with conn:
        c.execute("DELETE FROM mods WHERE weaponName = :weaponName AND modName = :modName",
        {'weaponName':weaponName, 'modName':modName})

def remove_allmods(weaponName):
    print('REMOVE ALL MODS FUNCTION')
    print(weaponName)
    with conn:
        c.execute("DELETE FROM mods WHERE weaponName = :weaponName",{'weaponName':weaponName})

def clear_database():
    with conn:
        c.execute("DELETE from weapons")
        c.execute("DELETE from mods")
        c.execute("DELETE from stats")

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#AVA Commands
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@bot.command(pass_context = True)
async def weapon(ctx, *args):
    user = ctx.message.author.name
    if len(args) == 0:
        notfound=0
        description = "Type '"+BOT_PREFIX+"weapon weapon_name' for the stats"
        embed = discord.Embed(title = "Possible weapon names are: ",description=description,color=0x00ff00)
        embed.set_thumbnail(url=ava_logo_url)
        all_types = c.execute("SELECT weaponClass FROM weapons WHERE rowid IN (SELECT min(rowid) FROM weapons GROUP BY weaponClass)").fetchall()
        print(all_types)
        for one_type in all_types:
            one_type = str(one_type).translate({ord(i):None for i in "'(),"})
            embed.add_field(name=one_type+"'s:",value=get_weapons_by_type(one_type), inline = False)
        await bot.say(embed=embed)
    else:
        if args[0].upper() == 'ADD' and ("473846017033502731" in role.id for role in ctx.message.author.roles):
            if not args[-1].upper() == 'MODS':

                await bot.say('Add your weapon')
                await bot.say('`(weaponName, description, weapon_Class, image_URL)`')
                msg = await bot.wait_for_message(author = ctx.message.author)
                msg = msg.content.split(';')
                description = msg[1].lstrip()
                input = msg[0].lstrip().upper()
                msg = ';'.join(msg).translate({ord(i):None for i in "'() "}).split(';')
                await bot.say('Adding weapon ' + input)
                add_weapon(Weapon(input,description,msg[2],msg[3]))
                await bot.say('Weapon '+input+' added to the database\nNow type the stats separated by spaces:')
                await bot.say('`(hitDamage, range, singleFireAcc, autoFireAcc, recoilControl, fireRate, magCapacity, mobility)`')
                msg = await bot.wait_for_message(author = ctx.message.author)
                msg = msg.content.translate({ord(i):None for i in "'() "}).split(';')
                print(msg)
                add_stats(input,Weapon.Stats(msg[0],msg[1],msg[2],msg[3],msg[4],msg[5],msg[6],msg[7]))
                await bot.say('Stats added')
            else:
                await bot.say('Add your weapon mod')
                await bot.say('`(weaponName, modName, modStat, valueModifier)`')
                msg = await bot.wait_for_message(author = ctx.message.author)
                msg = msg.content.translate({ord(i):None for i in "'() "}).split(';')
                print(msg)
                add_mods(msg[0].upper(),Weapon.Mod(msg[1],msg[2],msg[3]))
                await bot.say('Mods added')
        elif args[0].upper() == 'REMOVE' and ("473846017033502731" in role.id for role in ctx.message.author.roles):
            text = ' '.join(args[1:]).upper()
            if (text == 'WEAPON'):
                await bot.say('Type the name of the weapon you want to remove')
                msg = await bot.wait_for_message(author = ctx.message.author)
                remove_weapon(msg.content.upper())
                await bot.say(msg.content.upper()+' removed')
            elif (text == 'ALL MODS'):
                await bot.say('Type the name of the weapon you want to remove the mods from')
                msg = await bot.wait_for_message(author = ctx.message.author)
                remove_allmods(msg.content.upper())
                await bot.say(msg.content.upper()+' mods removed')
            elif (text == 'MODS'):
                await bot.say('Type the name and the weapon mod you want to remove')
                await bot.say('`(weaponName, modName)`')
                msg = await bot.wait_for_message(author = ctx.message.author)
                msg = msg.content.translate({ord(i):None for i in "'() "}).split(';')
                remove_mod(msg[0].upper(),msg[1])
        elif args[-1].upper() == 'MODS':
            print('MAIN FUNCTION MODS')
            input = ' '.join(args[:-1]).upper()
            print(input)
            mods = get_mods(input).split('\n')
            print('MAIN FUNCTION MODS')
            print(input)
            embed = discord.Embed(title=input+' mods')
            embed.set_thumbnail(url=ava_logo_url)
            for mod in mods:
                print(input + '.' + mod)
                stats = get_mod_values(input,mod).split(';')
                print('MAIN FUNCTION')
                print(stats)
                print()
                stats = ': '.join(stats)
                print(mod)
                print(stats)
                embed.add_field(name=str(mod),value=str(stats), inline = False)
            await bot.say(embed=embed)
        else:
            weaponName = ' '.join(args).upper()
            weapon_stats = str(get_stats(weaponName)).split(';')
            weapon_info = str(get_weapon(weaponName)).split(';')
            print('MAIN FUNCTION STATS')
            print(weaponName)
            print(weapon_stats)
            print(weapon_info)
            embed = discord.Embed(title=weaponName,description=weapon_info[1], color = 0x00ff00)
            embed.set_thumbnail(url=ava_logo_url)
            imageURL = str(weapon_info[-1])
            print(imageURL)
            if not imageURL == 'N/A':
                embed.set_image(url=imageURL)
            #embed.set_image(url=imageURL)
            for i in range(len(weapon_stats)):
                stat = weapon_stats[i]
                print(stat)
                print(general_weapon_stats[i])
                embed.add_field(name=str(general_weapon_stats[i]+':'),value=str(weapon_stats[i]))
            print('print embed')
            await bot.say(embed=embed)


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#AVA ADMIN Commands
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@bot.command()
async def clean_database():
    clear_database()



#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#temporary commands
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@bot.command()
async def logout():
    await bot.say('Cya!')
    await bot.logout()

@bot.command()
async def initializedata():
    remove_allmods('UZI')
    add_weapon(Weapon('UZI', 'SIMPLE SMG', 'SMG', 'simpleURL.png'))
    add_weapon(Weapon('MP7A1', 'SIMPLE SMG', 'SMG', 'simpleURL.png'))
    add_weapon(Weapon('MP7A1', 'LATEST SMG', 'SMG', 'simpleURL.png'))
    add_weapon(Weapon('Random smg', 'SIMPLE SMG', 'SMG', 'simpleURL.png'))
    add_weapon(Weapon('not sniper', 'LATEST SMG', 'SMG', 'simpleURL.png'))
    add_stats('UZI',Weapon.Stats(1,2,3,4,5,6,7,8))
    add_mods('UZI',Weapon.Mod('Barrel #1','autoFireAcc','+2'))
    add_mods('UZI',Weapon.Mod('Barrel #1','singleFireAcc','-2'))
    add_mods('UZI',Weapon.Mod('Barrel #2','autoFireAcc','+2'))
    add_mods('UZI',Weapon.Mod('Barrel #2','singleFireAcc','-5'))
    add_weapon(Weapon('sv98', 'SIMPLE sniper', 'SNIPER', 'simpleURL.png'))
    add_weapon(Weapon('sv98', 'SIMPLE sniper', 'SNIPER', 'simpleURL.png'))
    await bot.say('Data initialized')


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Bot services
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
