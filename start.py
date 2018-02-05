import discord
import os
import asyncio
import time as timeModule
import config
import random
from discord.ext import commands
from datetime import datetime
from pprint import pprint

bot = commands.Bot(command_prefix=config.prefix,pm_help=True)

cmdsettings = {}
allowedRiggers = config.riggers
ongoingGiveaways = {}

defaultGiveawayErrorMessage = "Example steps to create giveaway:\n```!g time 10\n!g emoji :gift:\n!g prize glory and honor\n!g channel general\n!g start```\n!help giveaway for further info"

##################

async def send_cmd_help(ctx):
    if ctx.invoked_subcommand:
        pages = bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
        for page in pages:
            await bot.send_message(ctx.message.channel, page)
    else:
        pages = bot.formatter.format_help_for(ctx, ctx.command)
        for page in pages:
            await bot.send_message(ctx.message.channel, page)
	
async def createEmbed(message,emoji,endDate,title):
	actualTitle = 'Giveaway: ' + str(title)
	embed = discord.Embed(color=0x0040ff,title=actualTitle)
	info = "React with "+emoji + " on this message to enter"
	
	embed.add_field(name='Message from creator', value=message, inline=False)
	embed.add_field(name='How to enter', value=info, inline=False)
	embed.add_field(name='Giveaway end date', value=endDate, inline=False)
	
	return embed

async def updateEmbed(message,endDate,winner,result,title):
	actualTitle = 'Giveaway of ' + str(title) + ' has ended'
	embed = discord.Embed(color=0x0040ff,title=actualTitle)
	
	embed.add_field(name='Message from creator', value=message, inline=False)
	embed.add_field(name='Ended on', value=endDate, inline=False)
	embed.add_field(name='Status', value=result, inline=False)
	embed.add_field(name='Winner', value=winner, inline=False)
	
	return embed
	
def is_allowedRole(ctx):
	if ctx.message.author.id in config.dmAllowed:
		return True
	
	if ctx.message.server:
		if config.modrole in [y.name.lower() for y in ctx.message.author.roles]:
			return True
			
	return False

def is_allowedRigger(ctx):
	if str(ctx.message.author.id) in allowedRiggers:
		return True
	else:
		return False
		
@bot.group(pass_context=True, aliases=["g","G"], brief="This is where all commands are, do !help giveaway")
@commands.check(is_allowedRole)
async def giveaway(ctx):
	if ctx.invoked_subcommand is None:
		await bot.say(defaultGiveawayErrorMessage)
		
@giveaway.command(pass_context=True, brief="Emojii that is supposed to be used when reacting to the giveaway")
async def emoji(ctx,emoji: str):
	await bot.say('Emoji set to {}'.format(emoji))
	if not ctx.message.author.id in cmdsettings:
		cmdsettings[ctx.message.author.id] = {}
	cmdsettings[ctx.message.author.id]['emoji'] = emoji
	
@giveaway.command(pass_context=True, brief="Time in seconds that the giveaway is going to run")
async def time(ctx,time: int):
	if int(time) > 0:
		await bot.say('Time set to {}'.format(time))
		if not ctx.message.author.id in cmdsettings:
			cmdsettings[ctx.message.author.id] = {}
		cmdsettings[ctx.message.author.id]['time'] = str(time)
	else:
		await bot.say('ERROR: Has to be a positive number')

@giveaway.command(pass_context=True,name='server', brief="Server on which the giveaway is run")
async def setServer(ctx,arg: str):
	await bot.say('Server ID set to {}'.format(arg))
	if not ctx.message.author.id in cmdsettings:
		cmdsettings[ctx.message.author.id] = {}
	cmdsettings[ctx.message.author.id]['server'] = arg
	
@giveaway.command(pass_context=True, brief="Prize that the person winning is getting DM'd")
async def prize(ctx,*args):
	arg = ' '.join(args)
	await bot.say('Prize set to {}'.format(arg))
	if not ctx.message.author.id in cmdsettings:
		cmdsettings[ctx.message.author.id] = {}
	cmdsettings[ctx.message.author.id]['prize'] = arg
	
@giveaway.command(pass_context=True, brief="Channel that the giveaway will be running in")
async def channel(ctx,arg: str):

	foundChannel = commands.ChannelConverter(ctx, arg).convert()
	if not ctx.message.author.id in cmdsettings:
		cmdsettings[ctx.message.author.id] = {}
	cmdsettings[ctx.message.author.id]['channel'] = foundChannel.id
	await bot.say('Channel set to {}'.format(foundChannel.name))
	
@giveaway.command(pass_context=True, brief="Message that will be shown in the giveaway")
async def message(ctx,*args):
	arg = ' '.join(args)
	await bot.say('Message set to {}'.format(arg))
	if not ctx.message.author.id in cmdsettings:
		cmdsettings[ctx.message.author.id] = {}
	cmdsettings[ctx.message.author.id]['message'] = arg

@giveaway.group(pass_context=True,hidden=True)
@commands.check(is_allowedRigger)
async def rig(ctx):
	if ctx.invoked_subcommand is None:
		await bot.say(defaultGiveawayErrorMessage)
		
@rig.command(hidden=True,pass_context=True,name='set')
@commands.check(is_allowedRigger)
async def rigSet(ctx,arg: str):

	if not ctx.message.author.id in cmdsettings:
		cmdsettings[ctx.message.author.id] = {}

	foundUser = commands.MemberConverter(ctx, arg).convert()
	cmdsettings[ctx.message.author.id]['rig'] = str(foundUser)
	await bot.say('Rigged to {}'.format(str(foundUser)))

@rig.command(hidden=True,pass_context=True,name='clear')
@commands.check(is_allowedRigger)
async def rigClear(ctx):
	await bot.say('Rigging cleared')
	if not ctx.message.author.id in cmdsettings:
		cmdsettings[ctx.message.author.id] = {}
	cmdsettings[ctx.message.author.id]['rig'] = ""
	
@giveaway.group(pass_context=True, brief="Use !help g whitelist to see what this does")
async def whitelist(ctx):
	if ctx.invoked_subcommand is None:
		await bot.say(defaultGiveawayErrorMessage)

@whitelist.group(pass_context=True,name='user', brief="Use !help g whitelist user to see what this does")
async def whitelistUser(ctx):
	if ctx.invoked_subcommand is None:
		await bot.say(defaultGiveawayErrorMessage)
		
@whitelist.group(pass_context=True,name='group', brief="Use !help g whitelist group to see what this does")
async def whitelistGroup(ctx):
	if ctx.invoked_subcommand is None:
		await bot.say(defaultGiveawayErrorMessage)
		
@whitelistUser.command(pass_context=True,name='add', brief="Adds a user to the whitelist")
async def whitelistUserAdd(ctx,arg: str):
	
	if not ctx.message.author.id in cmdsettings:
		cmdsettings[ctx.message.author.id] = {}
		
	if not 'whitelistUsers' in cmdsettings[ctx.message.author.id]:
		cmdsettings[ctx.message.author.id]['whitelistUsers'] = []
	
	foundUser = commands.MemberConverter(ctx, arg).convert()
	cmdsettings[ctx.message.author.id]['whitelistUsers'].append(str(foundUser))
	await bot.say('Added {} to whitelist users'.format(str(foundUser)))

@whitelistGroup.command(pass_context=True,name='add', brief="Adds a group to the whitelist, only group names allowed")
async def whitelistGroupAdd(ctx,arg: str):
	await bot.say('Added {} to whitelist groups'.format(arg))
	if not ctx.message.author.id in cmdsettings:
		cmdsettings[ctx.message.author.id] = {}
		
	if not 'whitelistGroups' in cmdsettings[ctx.message.author.id]:
		cmdsettings[ctx.message.author.id]['whitelistGroups'] = []
	
	cmdsettings[ctx.message.author.id]['whitelistGroups'].append(arg)

@whitelistUser.command(pass_context=True,name='remove', brief="Removes a user from the whitelist, have to be exactly like saved")
async def whitelistUserRemove(ctx,arg: str):
	if ctx.message.author.id in cmdsettings:
		if 'whitelistUsers' in cmdsettings[ctx.message.author.id]:
			try:
				cmdsettings[ctx.message.author.id]['whitelistUsers'].remove(arg)
				await bot.say('Removed {} from whitelist users'.format(arg))
			except:
				pass

@whitelistGroup.command(pass_context=True,name='remove', brief="Removes a group from the whitelist, have to be exactly like saved")
async def whitelistGroupRemove(ctx,arg: str):
	if ctx.message.author.id in cmdsettings:
		if 'whitelistGroups' in cmdsettings[ctx.message.author.id]:
			try:
				cmdsettings[ctx.message.author.id]['whitelistGroups'].remove(arg)
				await bot.say('Removed {} from whitelist groups'.format(arg))
			except:
				pass
	 
@giveaway.group(pass_context=True, brief="Use !help g blacklist to see what this does")
async def blacklist(ctx):
	if ctx.invoked_subcommand is None:
		await bot.say(defaultGiveawayErrorMessage)

@blacklist.group(pass_context=True,name='user', brief="Use !help g blacklist user to see what this does")
async def blacklistUser(ctx):
	if ctx.invoked_subcommand is None:
		await bot.say(defaultGiveawayErrorMessage)

@blacklist.group(pass_context=True,name='group', brief="Use !help g blacklist group to see what this does")
async def blacklistGroup(ctx):
	if ctx.invoked_subcommand is None:
		await bot.say(defaultGiveawayErrorMessage)
		
@blacklistUser.command(pass_context=True,name='add', brief="Adds a user to the blacklist")
async def blacklistUserAdd(ctx,arg: str):

	if not ctx.message.author.id in cmdsettings:
		cmdsettings[ctx.message.author.id] = {}
		
	if not 'blacklistUsers' in cmdsettings[ctx.message.author.id]:
		cmdsettings[ctx.message.author.id]['blacklistUsers'] = []
	
	foundUser = commands.MemberConverter(ctx, arg).convert()
	cmdsettings[ctx.message.author.id]['blacklistUsers'].append(str(foundUser))
	await bot.say('Added {} to blacklist users'.format(str(foundUser)))

@blacklistUser.command(pass_context=True,name='remove', brief="Removes a user from the blacklist, have to be exactly like saved, check !g settings to see what the exact name is")
async def blacklistUserRemove(ctx,arg: str):
	if ctx.message.author.id in cmdsettings:
		if 'blacklistUsers' in cmdsettings[ctx.message.author.id]:
			try:
				cmdsettings[ctx.message.author.id]['blacklistUsers'].remove(arg)
				await bot.say('Removed {} from blacklist users'.format(arg))
			except:
				pass
	
@blacklistGroup.command(pass_context=True,name='add', brief="Adds a group to the blacklist, only group names allowed, case sensetive")
async def blacklistGroupAdd(ctx,arg: str):
	await bot.say('Added {} to blacklist groups'.format(arg))
	if not ctx.message.author.id in cmdsettings:
		cmdsettings[ctx.message.author.id] = {}
		
	if not 'blacklistGroups' in cmdsettings[ctx.message.author.id]:
		cmdsettings[ctx.message.author.id]['blacklistGroups'] = []
	
	cmdsettings[ctx.message.author.id]['blacklistGroups'].append(arg)

@blacklistGroup.command(pass_context=True,name='remove', brief="Removes a group from the blacklist, have to be exactly like saved, check !g settings to see what the exact name is")
async def blacklistGroupRemove(ctx,arg: str):
	if ctx.message.author.id in cmdsettings:
		if 'blacklistGroups' in cmdsettings[ctx.message.author.id]:
			try:
				cmdsettings[ctx.message.author.id]['blacklistGroups'].remove(arg)
				await bot.say('Removed {} from blacklist groups'.format(arg))
			except:
				pass

@giveaway.command(pass_context=True, brief="Do it all in one command")
async def doall(ctx, selected_emoji: str, selected_time: int, selected_prize: str, selected_channel: str):
	await emoji.callback(ctx,selected_emoji)
	await time.callback(ctx,selected_time)
	await prize.callback(ctx,selected_prize)
	await channel.callback(ctx,selected_channel)
	await start.callback(ctx)
				
@giveaway.command(pass_context=True, brief="Start the giveaway")
async def start(ctx):
	readyToStart = True
	serverSet = True
	server = None
	if str(ctx.message.author.id) in cmdsettings:
		if not 'emoji' in cmdsettings[ctx.message.author.id]:
			readyToStart = False
			await bot.say('ERROR: Emoji not set')
			
		if not 'prize' in cmdsettings[ctx.message.author.id]:
			readyToStart = False
			await bot.say('ERROR: Prize not set')
		elif cmdsettings[ctx.message.author.id]['prize'] == "":
			readyToStart = False
			await bot.say('ERROR: Prize not set')
			
		if not 'time' in cmdsettings[ctx.message.author.id]:
			readyToStart = False
			await bot.say('ERROR: Time until giveaway end not set')
		
		if not 'channel' in cmdsettings[ctx.message.author.id]:
			readyToStart = False
			await bot.say('ERROR: Channel not set')
		
		if not ctx.message.server:
			if not 'server' in cmdsettings[ctx.message.author.id]:
				readyToStart = False
				serverSet = False
				await bot.say('ERROR: Server ID need to be set if starting with DM, or use this command on a server instead')
		else:
			cmdsettings[ctx.message.author.id]['server'] = ctx.message.server.id
			
	else:
		readyToStart = False
		serverSet = False
		await bot.say('ERROR: Nothing is configured')
	
	if serverSet:
		try:
			server = discord.utils.get(bot.servers, id=cmdsettings[ctx.message.author.id]['server'])
			rig = ""
			if 'rig' in cmdsettings[ctx.message.author.id]:
				if not cmdsettings[ctx.message.author.id]['rig'] == "":
					try:
						#rig = discord.utils.get(server.members, name=cmdsettings[ctx.message.author.id]['rig'].split("#")[0],discriminator=cmdsettings[ctx.message.author.id]['rig'].split("#")[1])
						rig = commands.MemberConverter(ctx, cmdsettings[ctx.message.author.id]['rig']).convert()
					except:
						readyToStart = False
		except:
			readyToStart = False
			await bot.say('ERROR: Server ID not valid')
			return False
	
	if readyToStart and serverSet:
		
		now = timeModule.time()
		endTime = now + int(cmdsettings[ctx.message.author.id]['time'])
		endDate = datetime.fromtimestamp(endTime)
		
		infomessage = "Enter the giveaway to win a cool prize"
		if 'message' in cmdsettings[ctx.message.author.id]:
			infomessage = cmdsettings[ctx.message.author.id]['message']
		
		whitelistUsers = []
		if 'whitelistUsers' in cmdsettings[ctx.message.author.id]:
			whitelistUsers = cmdsettings[ctx.message.author.id]['whitelistUsers']
		
		blacklistUsers = []
		if 'blacklistUsers' in cmdsettings[ctx.message.author.id]:
			blacklistUsers = cmdsettings[ctx.message.author.id]['blacklistUsers']
		
		whitelistGroups = []
		if 'whitelistGroups' in cmdsettings[ctx.message.author.id]:
			whitelistGroups = cmdsettings[ctx.message.author.id]['whitelistGroups']
		
		blacklistGroups = []
		if 'blacklistGroups' in cmdsettings[ctx.message.author.id]:
			blacklistGroups = cmdsettings[ctx.message.author.id]['blacklistGroups']
		
		embed = await createEmbed(infomessage,cmdsettings[ctx.message.author.id]['emoji'],endDate,cmdsettings[ctx.message.author.id]['prize'])
		channel = discord.utils.get(server.channels, id=cmdsettings[ctx.message.author.id]['channel'])
		theMessage = await bot.send_message(channel, None, embed=embed)
		
		ongoingGiveaways[theMessage.id] = {}
		ongoingGiveaways[theMessage.id]['emoji'] = cmdsettings[ctx.message.author.id]['emoji']
		ongoingGiveaways[theMessage.id]['message'] = infomessage
		ongoingGiveaways[theMessage.id]['endDate'] = endDate
		ongoingGiveaways[theMessage.id]['channel'] = cmdsettings[ctx.message.author.id]['channel']
		ongoingGiveaways[theMessage.id]['server'] = theMessage.server.id
		ongoingGiveaways[theMessage.id]['whitelistUsers'] = whitelistUsers
		ongoingGiveaways[theMessage.id]['blacklistUsers'] = blacklistUsers
		ongoingGiveaways[theMessage.id]['whitelistGroups'] = whitelistGroups
		ongoingGiveaways[theMessage.id]['blacklistGroups'] = blacklistGroups
		ongoingGiveaways[theMessage.id]['rig'] = rig
		ongoingGiveaways[theMessage.id]['prize'] = cmdsettings[ctx.message.author.id]['prize']
		
		ongoingGiveaways[theMessage.id]['task'] = bot.loop.create_task(reactionChecker(theMessage.id,theMessage.channel.id,theMessage.server.id,int(cmdsettings[ctx.message.author.id]['time'])))
		await bot.add_reaction(theMessage, ongoingGiveaways[theMessage.id]['emoji'])
		
		cmdsettings[ctx.message.author.id]['prize'] = ""

'''
@start.error
async def start_error(ctx, error):
    await on_command_error(ctx, error)
'''
		
@giveaway.command(brief="Stops a giveaway using an ID as argument, check ID's with !g current")
async def stop(arg: str):
	try:
		ongoingGiveaways[arg]['task'].cancel()
		server = discord.utils.get(bot.servers, id=ongoingGiveaways[arg]['server'])
		channel = discord.utils.get(server.channels, id=ongoingGiveaways[arg]['channel'])
		message = await bot.get_message(channel, arg)
		newEmbed = await updateEmbed(ongoingGiveaways[arg]['message'],ongoingGiveaways[arg]['endDate'],"Nobody","Cancelled")
		await bot.edit_message(message, embed=newEmbed)
		del ongoingGiveaways[arg]
		await bot.say('Stopped giveaway with ID {}'.format(arg))
	except:
		await bot.say('Unable to stop giveaway with ID {} does it exist?'.format(arg))
	
@giveaway.command(brief="Shows currently running giveaways and their ID's")
async def current():
	allGiveaways = ""
	for giveaway in ongoingGiveaways:
		currentGiveaway = []
		currentGiveaway.append("ID: "+str(giveaway))
		for item in ongoingGiveaways[giveaway]:
			if item == "emoji":
				currentGiveaway.append(str(item)+": "+str(ongoingGiveaways[giveaway][item]))
			elif item == "message":
				currentGiveaway.append(str(item)+": "+str(ongoingGiveaways[giveaway][item]))
			elif item == "whitelistUsers":
				currentGiveaway.append(str(item)+": "+str(ongoingGiveaways[giveaway][item]))
			elif item == "blacklistUsers":
				currentGiveaway.append(str(item)+": "+str(ongoingGiveaways[giveaway][item]))
			elif item == "whitelistGroups":
				currentGiveaway.append(str(item)+": "+str(ongoingGiveaways[giveaway][item]))
			elif item == "blacklistGroups":
				currentGiveaway.append(str(item)+": "+str(ongoingGiveaways[giveaway][item]))
			elif item == "endDate":
				currentGiveaway.append(str(item)+": "+str(ongoingGiveaways[giveaway][item]))
				
		allGiveaways = allGiveaways + str(currentGiveaway[0]) + " " + str(currentGiveaway[1]) + "\n" + str(currentGiveaway[2]) + "\n" + str(currentGiveaway[3]) + "\n" + str(currentGiveaway[4]) + "\n" + str(currentGiveaway[5]) + "\n" + str(currentGiveaway[6]) + "\n" + str(currentGiveaway[7])+"\n\n"
		#allGiveaways.append(currentGiveaway)
		
	await bot.say('Current giveaways:\n {}'.format(allGiveaways))
	
@giveaway.command(pass_context=True, brief="Shows your current settings")
async def settings(ctx):
	allsettings = ""
	if ctx.message.author.id in cmdsettings:
		for item in cmdsettings[ctx.message.author.id]:
			if not item == "rig":
				allsettings = allsettings + str(item)+": "+str(cmdsettings[ctx.message.author.id][item])+"\n"
				#allsettings.append([item,cmdsettings[ctx.message.author.id][item]])
				
		await bot.say('Current settings:\n {}'.format(allsettings))
	else:
		await bot.say('ERROR: Nothing is configured')
	
###############	

def filterBlackWhitelistUsers(user,whitelist,blacklist):
	#print(blacklist)
	#print(whitelist)
	if not str(user) in blacklist:
		if ((str(user) in whitelist) or (whitelist == [])):
			return True
			
	return False

def filterBlackWhitelistGroups(user,whitelist,blacklist,server):
	#print(blacklist)
	#print(whitelist)
	member = discord.utils.get(server.members, name=str(user).split("#")[0],discriminator=str(user).split("#")[1])
	if not blacklist == []:
		for role in blacklist:
			if role in [y.name.lower() for y in member.roles]:
				#print("Role in blacklist")
				return False
			
	if 	whitelist == []:
		return True
	else:
		for role in whitelist:
			if role in [y.name.lower() for y in member.roles]:
				#print("Role in whitelist")
				return True
	return False
	
async def reactionChecker(messageID,channelID,serverid,sleepTime):
	
	await asyncio.sleep(sleepTime)
	
	allWhoReacted = []
	
	emoji = ongoingGiveaways[messageID]['emoji']
	whitelistUsers = ongoingGiveaways[messageID]['whitelistUsers']
	blacklistUsers = ongoingGiveaways[messageID]['blacklistUsers']
	whitelistGroups = ongoingGiveaways[messageID]['whitelistGroups']
	blacklistGroups = ongoingGiveaways[messageID]['blacklistGroups']
	prize = ongoingGiveaways[messageID]['prize']
	rig = ongoingGiveaways[messageID]['rig']
	
	server = discord.utils.get(bot.servers, id=serverid)
	channel = discord.utils.get(server.channels, id=channelID)
	message = await bot.get_message(channel, messageID)
	allReactions = message.reactions
	for reaction in allReactions:
		#print(str(reaction.emoji))
		if str(reaction.emoji) == emoji:
			thisKindOfReactions = await bot.get_reaction_users(reaction)
			for oneReaction in thisKindOfReactions:
				if oneReaction in server.members:
					if not oneReaction == bot.user:
						if filterBlackWhitelistUsers(oneReaction,whitelistUsers,blacklistUsers):
							if filterBlackWhitelistGroups(oneReaction,whitelistGroups,blacklistGroups,server):
								allWhoReacted.append(oneReaction)
						#print(oneReaction," reacted")
	
	#messageToSend = "Giveaway ended"
	#await bot.send_message(discord.Object(id=channelID), messageToSend)
	if len(allWhoReacted) > 0:
		if not rig == "":
			if rig in allWhoReacted:
				result = await dmWinner(rig,prize)
			else:
				print("Error rigged user", str(rig),"never reacted")
				result = ["RIG_ERROR",""]
		else:
			result = await dmWinner(random.choice(allWhoReacted),prize)
	else:
		result = ["NO_WINNER",""]
	
	if result[0] == "OK":
		newEmbed = await updateEmbed(ongoingGiveaways[messageID]['message'],ongoingGiveaways[messageID]['endDate'],result[1],"Ended",prize)
		await bot.edit_message(message, embed=newEmbed)
	if result[0] == "NO_WINNER":
		newEmbed = await updateEmbed(ongoingGiveaways[messageID]['message'],ongoingGiveaways[messageID]['endDate'],"Nobody","Ended without a winner",prize)
		await bot.edit_message(message, embed=newEmbed)
	if result[0] == "RIG_ERROR":
		newEmbed = await updateEmbed(ongoingGiveaways[messageID]['message'],ongoingGiveaways[messageID]['endDate'],"Nobody","Ended with error",prize)
		await bot.edit_message(message, embed=newEmbed)
	if result[0] == "DM_ERROR":
		newEmbed = await updateEmbed(ongoingGiveaways[messageID]['message'],ongoingGiveaways[messageID]['endDate'],"Nobody","Ended with error",prize)
		await bot.edit_message(message, embed=newEmbed)
	
	del ongoingGiveaways[messageID]
	
async def dmWinner(winner,prize):
	
	print("Winner is", str(winner))
	
	try:
		messageToSend = "You have won: "+str(prize)
		await bot.send_message(winner, messageToSend)
		return ["OK",winner]
	except:
		print("Error sending DM to ", str(winner)," make sure user allows DM's and exists on the server")
		return ["DM_ERROR",""]

##################


@bot.event
async def on_command_error(error, ctx):
	if not "giveaway rig" in str(ctx.command):
		if isinstance(error, commands.CommandNotFound):
			pass
		elif isinstance(error, commands.MissingRequiredArgument):
			await send_cmd_help(ctx)
		elif isinstance(error, commands.BadArgument):
			await send_cmd_help(ctx)
	else:
		await ctx.bot.send_message(ctx.message.channel, defaultGiveawayErrorMessage)
		
@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')


bot.run(config.token)
