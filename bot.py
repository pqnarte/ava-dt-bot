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
from map import Map
import sqlite3

ava_logo_url='https://upload.wikimedia.org/wikipedia/commons/1/15/Alliance-of-valiant-arms-logo.png'
BOT_PREFIX = (".")
general_weapon_stats = ['Hit Damage','Range','Single Fire Acc','Auto Fire Acc','Recoil Control','Fire Rate','Mag Capacity','Mobility']

bot = Bot(command_prefix=BOT_PREFIX)
bot.remove_command('help')
conn = sqlite3.connect('weapon.db') #Bom para testar
c = conn.cursor()
connmap = sqlite3.connect('map.db')
cm = connmap.cursor()

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
    help_string = ("""```fix
 -----------------------------------------------------------------------------------------------------
|                                            Help Commands                                            |
 ----------------------------------------------------------------------------------------------------- ```

__**General commands:**__
```md
# .info @user
> Shows some info about the @user

# .serverinfo
> Shows some info about the server

# .check_if_admin
> Checks if you can do the admin commands```

__**AVA Dog Tag commands:**__
```md
# .weapons
> Presents you a simple list of all the weapons available

# .pistols
> Presents you a simple list of all the pistols available

# .weapon <weapon_name_here>
> Shows all the stats about the weapon you select

# .maplist
> Presents you a simple list of all the maps available

# .map <map_name_here>
> Shows the map image for all to see```

__**AVA Dog Tag Admin commands:**__
```md
# .add <weapon/mod/map>
> Adds stuff to the database

# .remove <weapon/mod/all mods/map>
> Removes stuff to the database

# .update <weapon/mod/map/weapon_stats>
> Updates some info on the database

# .clean_database
> Erases the database for a fresh start (WARNING)```""")
    await bot.send_message(author, help_string)
    await bot.say(str(author.display_name)+", I sent you a private message with the help commands.")

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
def add_map(map):
    with connmap:
        cm.execute("INSERT INTO maps VALUES (:mapName, :maplayoutURL, :mapvideo)",
            {'mapName': map.mapName, 'maplayoutURL': map.maplayoutURL, 'mapvideo': map.mapvideo})

def add_weapon(weap):
    with conn:
        c.execute("INSERT INTO weapons VALUES (:weaponName, :description, :weaponClass, :imageURL)",
            {'weaponName': weap.weaponName, 'description': weap.description, 'weaponClass': weap.weaponClass, 'imageURL': weap.imageURL})

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
    weapon = c.execute("SELECT * FROM weapons WHERE weaponName=:weaponName", {'weaponName': weaponName}).fetchone()
    weapon = ';'.join(weapon)
    return weapon

def get_map(mapName):
    map = cm.execute("SELECT * FROM maps WHERE mapName=:mapName", {'mapName': mapName}).fetchone()
    map = ';'.join(map)
    print(map)
    return map

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

def remove_last_weapon():
    with conn:
        c.execute("DELETE FROM weapons WHERE rowid IN (SELECT max(rowid) FROM weapons)")

def remove_duplicate_weapons():
    with conn:
        c.execute("DELETE FROM weapons WHERE rowid NOT IN (SELECT max(rowid) FROM weapons GROUP BY weaponName)")

def remove_duplicate_maps():
    with connmap:
        cm.execute("DELETE FROM maps WHERE rowid NOT IN (SELECT max(rowid) FROM maps GROUP BY mapName)")

def remove_map(mapName):
    with connmap:
        cm.execute("DELETE FROM maps WHERE mapName = :mapName",
        {'mapName':mapName})

def remove_weapon(weaponName):
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

def check_admin_status(ctx):
    for role in ctx.message.author.roles:
        if "454211665542512642" == role.id or "454100947115835392" == role.id:
            return True
    if "180787341248561152" == ctx.message.author.id:
        return True
    return False

def remove_leads(args):
    print(args)
    temp = args.split(';')
    for j in range(len(temp)):
        temp[j] = temp[j].lstrip()
    args = ';'.join(temp)
    print(args)
    return args


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#AVA Commands
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@bot.command()
async def weapons():
    embed = discord.Embed(color=0xff0000)
    embed.set_thumbnail(url=ava_logo_url)
    all_types = c.execute("SELECT weaponClass FROM weapons WHERE rowid IN (SELECT min(rowid) FROM weapons GROUP BY weaponClass)").fetchall()
    print(all_types)
    for one_type in all_types:
        one_type = str(one_type).translate({ord(i):None for i in "'(),"})
        embed.add_field(name="\u200b \n"+one_type+"'s:",value=get_weapons_by_type(one_type), inline = False)
    await bot.say(embed=embed)

@bot.command()
async def maplist():
    try:
        embed = discord.Embed(color=0xff0000)
        embed.set_thumbnail(url=ava_logo_url)
        all_types = cm.execute("SELECT mapName FROM maps").fetchall()
        print(all_types)
        string = ""
        for one_type in all_types:
            string += str(one_type).translate({ord(i):None for i in "'(),"}) + '\n'
        embed.add_field(name="\u200b\n",value=string, inline = False)
        await bot.say(embed=embed)
    except Exception:
        await bot.say("Something wrong..")

@bot.command()
async def pistols():
    await bot.say("*To be implemented*")

@bot.command()
async def map(*args):
    if len(args) == 0:
        await bot.say("You need to type the map name!!\n If you don't know what weapons are availabe type: `.maplist`")
    else:
        mapName = ' '.join(args).upper()
        try:
            map_info = str(get_map(mapName)).split(';')
            embed = discord.Embed(title=mapName + ' map layout: ', color = 0x00ffff)
            embed.set_thumbnail(url=ava_logo_url)
            embed.set_image(url=map_info[1])
            await bot.say(embed=embed)
            await bot.say(map_info[2]+"\nCheck a video about the map! Or click the link for better resolution!")
        except Exception:
            await bot.say(mapName+" not found, sorry.")

@bot.command()
async def weapon(*args):
    if len(args) == 0:
        await bot.say("You need to type the weapon name!!\n If you don't know what weapons are availabe type: `.weapons` or `.pistols`")
    else:
        if args[-1].upper() == 'MODS':
            input = ' '.join(args[:-1]).upper()
            mods = get_mods(input).split('\n')
            embed = discord.Embed(title=input+' mods')
            embed.set_thumbnail(url=ava_logo_url)
            for mod in mods:
                stats = get_mod_values(input,mod).split(';')
                stats = ': '.join(stats)
                embed.add_field(name=str(mod),value=str(stats), inline = False)
            await bot.say(embed=embed)
        else:
            weaponName = ' '.join(args).upper()
            try:
                weapon_stats = str(get_stats(weaponName)).split(';')
                weapon_info = str(get_weapon(weaponName)).split(';')
                embed = discord.Embed(title=weaponName,description=weapon_info[1], color = 0x00ff00)
                embed.set_thumbnail(url=ava_logo_url)
                imageURL = str(weapon_info[-1])
                if not imageURL == 'N/A':
                    embed.set_image(url=imageURL)
                for i in range(len(weapon_stats)):
                    stat = weapon_stats[i]
                    embed.add_field(name=str(general_weapon_stats[i]+':'),value=str(weapon_stats[i]))
                await bot.say(embed=embed)
            except Exception:
                await bot.say(weaponName+" not found, sorry.")


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#AVA ADMIN Commands
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@bot.command(pass_context = True)
async def clean_database(ctx):
    if check_admin_status(ctx):
        await bot.say("Are you sure you want to delete everything?\nThis cannot be undo\n`yes`   or   `no`")
        msg = await bot.wait_for_message(author = ctx.message.author)
        if msg.content.upper() == "YES":
            await bot.say("Database cleaned")
        else:
            await bot.say("Process canceled")

@bot.command(pass_context = True)
async def add(ctx, *args):
    if check_admin_status(ctx):
        if len(args) == 0:
            await bot.say("You have to choose to add a weapon, mod or map!\nExample: .add weapon")
        else:
            args = ' '.join(args)
            if args.upper() == 'WEAPON':
                await bot.say('Add your weapon, if you have no image_URL, type N/A instead')
                await bot.say('`weaponName; description; weapon_Class; image_URL`')
                msg = await bot.wait_for_message(author = ctx.message.author)
                msg = remove_leads(msg.content).split(';')
		weaponName = msg[0].upper()
                try:
                    add_weapon(Weapon(weaponName,msg[1],msg[2],msg[3]))
                    await bot.say('Weapon '+msg[0].upper()+' added to the database\nNow type the stats separated by ";":')
                except Exception:
                    await bot.say("You didn't type the values well...")
                await bot.say('`Hit Damage; Range; Single Fire Acc; Auto Fire Acc; Recoil Control; Fire Rate; Mag Capacity; Mobility`')
                msg = await bot.wait_for_message(author = ctx.message.author)
                msg = remove_leads(msg.content).split(';')
                try:
                    add_stats(weaponName,Weapon.Stats(msg[0],msg[1],msg[2],msg[3],msg[4],msg[5],msg[6],msg[7]))
                    await bot.say('Stats added')
                    remove_duplicate_weapons()
                except Exception:
                    await bot.say("You didn't type the values well...")
                    await bot.say("Weapon removed from the database..")
                    remove_last_weapon()
            elif args.upper() == 'MOD':
                await bot.say('Add your weapon mod')
                await bot.say('`Weapon Name; Mod Name; Mod Stat; Stat Value Modifier`')
                msg = await bot.wait_for_message(author = ctx.message.author)
                msg = remove_leads(msg.content).split(';')
                add_mods(msg[0].upper(),Weapon.Mod(msg[1],msg[2],msg[3]))
            elif args.upper() == 'MAP':
                try:
                    await bot.say('Add your map!')
                    await bot.say('`Map Name; Map layout URL; Map Video Link`')
                    msg = await bot.wait_for_message(author = ctx.message.author)
                    msg = remove_leads(msg.content).split(';')
                    add_map(Map(msg[0].upper(),msg[1],msg[2]))
                    await bot.say('Map '+msg[0].upper()+' added to the database')
                    remove_duplicate_maps()
                except Exception:
                    await bot.say("You didn't type the values well...")
            else:
                await bot.say("That's not possible, sorry.")
    else:
        await bot.say("You don't have permissions to add stuff!")

@bot.command(pass_context = True)
async def remove(ctx, *args):
    if check_admin_status(ctx):
        if len(args) == 0:
            await bot.say("You have to choose to remove a weapon, mod or map!\nExample: .remove weapon")
        else:
            args = ' '.join(args)
            if args.upper() == 'WEAPON':
                await bot.say('Type the name of the weapon you want to remove')
                msg = await bot.wait_for_message(author = ctx.message.author)
                remove_weapon(msg.content.upper())
                await bot.say(msg.content.upper()+' removed')
            elif args.upper() == 'ALL MODS':
                await bot.say('Type the name of the weapon you want to remove the mods from')
                msg = await bot.wait_for_message(author = ctx.message.author)
                remove_allmods(msg.content.upper())
                await bot.say(msg.content.upper()+' mods removed')
            elif args.upper() == 'MOD':
                await bot.say('Type the name and the weapon mod you want to remove')
                await bot.say('`weaponName; modName`')
                msg = await bot.wait_for_message(author = ctx.message.author)
                msg = remove_leads(msg.content).split(';')
                remove_mod(msg[0].upper(),msg[1])
            elif args.upper() == 'MAP':
                await bot.say('Type the name of the map you want to remove from the database')
                msg = await bot.wait_for_message(author = ctx.message.author)
                remove_map(msg.content.upper())
                await bot.say(msg.content.upper()+' map removed')
            else:
                await bot.say("That's not possible, sorry.")
    else:
        await bot.say("You don't have permissions to add stuff!")

@bot.command(pass_context = True)
async def update(ctx):
    if check_admin_status(ctx):
        await bot.say("*To be implemented*")
    else:
        await bot.say("You don't have permissions to update stuff!")

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#temporary commands
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@bot.command(pass_context = True)
async def check_if_admin(ctx):
    if check_admin_status(ctx):
        await bot.say('You have BIG permissions! :O')
    else:
        await bot.say("You can't do the big stuff, sry")
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
