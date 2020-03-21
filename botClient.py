import discord
import time
import asyncio
import pickle

VOTE_TIMEOUT = 2
SIMP_BASETIME = 7.5
VOTE_TIME = 30

reserved = ['simpintro','simp','unsimp','unsimpall']
class BotClient( discord.Client ):
    blacklist = {}
    simped = {}
    simptime = []
    inprogress = 0
    def __init__(self, ):
        super().__init__()
        self.blacklist = {}
        self.simped = {}
        self.simptime = {}
        self.inprogress = 0

    async def on_ready( self ):
        print( 'Logged on as {0}!'.format( self.user ) )

    async def on_message( self, message ):
        #Ignore own messages
        if message.author == self.user:
            return
        if len(message.content) > 0:
            command = message.content.lower().split()[0]
        else:
            command = " "
        if command[0] == "^":
            if command[1:] == "simpintro":
                await message.channel.send("I'm SimpBot")
            elif command[1:] == "simp":
                await message.guild.get_member(self.user.id).remove_roles(message.guild.get_role(675743974140411905),reason="SimpBot unsimp")
                if self.inprogress:
                    await message.channel.send("Vote in progress, please wait")
                    return
                if message.author not in self.blacklist:
                    self.blacklist[message.author] = time.time()
                if time.time() >= self.blacklist[message.author]:
                    try:
                        simpeeID = int(message.content.lower().split()[1][2:-1])
                    except:
                        try:
                            simpeeID = int(message.content.lower().split()[1][3:-1])
                        except:
                            await message.channel.send("No! Bad!")
                            return
                    simpee = message.guild.get_member(simpeeID)
                    if simpee:
                        self.blacklist[message.author] = time.time() + VOTE_TIMEOUT*60
                        await self.wait_on_simp(message, simpee)
                    else:
                        await message.channel.send("Could not find user.")
                        print("Search string: %s, Full Array: %s" % (message.content.lower().split()[1],str(message.content.lower().split())))
                else:
                    await message.channel.send("Please wait %d seconds before simping again %s" % (self.blacklist[message.author]-time.time(), message.author.name))
            elif command[1:] == "unsimp":
                pass
            elif command[1:] == "unsimpall":
                pass
            elif command[1:] == "reset":
                guild = message.guild
                role = []
                role.append(guild.get_role('675729195372118026'))
                role.append(guild.get_role('675731528520564736'))
                role.append(guild.get_role('676370808553078814'))
                if message.author.top_role in roles:
                    self.inprogress = 0
                    await message.channel.send("Vote timer reset")
    async def wait_on_simp( self, message, simpee ):
        channel = message.channel
        if simpee in self.simped and self.simped[simpee] < time.time():
            await channel.send("%s is already simped!" % simpee.name)
            return
        online_members = 0
        members = message.guild.members
        for member in members:
            if str(member.status) == "online":
                online_members += 1
        self.inprogress = 1
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.reset_progress())
        msg = await channel.send("Vote to @simp %s initiated by %s\nYou have 30 seconds to get to net votes of %d to simp." % (simpee.name, message.author.name, online_members/4))
        emoji = discord.utils.get(msg.guild.emojis, name='simp')
        emoji2 = discord.utils.get(msg.guild.emojis, name='unsimp')
        await msg.add_reaction(emoji)
        await msg.add_reaction(emoji2)
        timeout = VOTE_TIME
        start_time = time.time()
        yes_count = no_count = 0
        votes_for_l = []
        votes_against_l = []
        msg = discord.utils.get(await msg.channel.history().flatten(), id=msg.id)
        while timeout > 0 and (yes_count-no_count < online_members/2):
            timeout -= 5
            votes_for_l = []
            votes_against_l = []
            sleep_time = (VOTE_TIME-timeout) - (time.time()-start_time)
            if sleep_time < 0:
                sleep_time = 0
            #print(str(time.time()-start_time),str(timeout),str(sleep_time))
            await asyncio.sleep(sleep_time)
            msg = discord.utils.get(await msg.channel.history().flatten(), id=msg.id)
            online_members = yes_count = no_count = 0
            members = msg.guild.members
            for member in members:
                if str(member.status) == "online":
                    online_members += 1
            for reaction in msg.reactions:
                if reaction.emoji == emoji:
                    yes_count = reaction.count
                    votes_for_l = await reaction.users().flatten()
                elif reaction.emoji == emoji2:
                    no_count = reaction.count
                    votes_against_l = await reaction.users().flatten()
            await msg.edit(content="Vote to @simp %s initiated by %s\nYou have %d seconds to get to net votes of %d to simp." % (simpee.name, message.author.name, timeout, online_members/4))
        task.cancel()
        self.inprogress = 0
        if yes_count-no_count >= online_members/4-1:
            emoji = discord.utils.get(msg.guild.emojis, name='simp')
            if simpee in self.simptime:
                if self.simptime[simpee] == 0:
                    mult = 1
                elif self.simptime[simpee] < 64:
                    mult = self.simptime[simpee] *2
                else:
                    mult = self.simptime[simpee]
            else:
                mult = 1
            simptime = SIMP_BASETIME * mult
            votes_for = ""
            votes_against = ""
            for user in votes_for_l:
                votes_for += user.name + ", "
            votes_for = votes_for[:-2]
            for user in votes_against_l:
                votes_against += user.name + ", "
            votes_against = votes_against[:-2]
            await msg.channel.send("%s has been simped for %d minutes" % (simpee.name,simptime))
            await msg.channel.send(emoji)
            await msg.edit(content="Vote to @simp %s initiated by %s\nVotes for: %s\nVotes against: %s" % (simpee.name, message.author.name,votes_for,votes_against))
            await simpee.add_roles(msg.guild.get_role(675743974140411905),reason="SimpBot vote passed")
            self.simped[simpee] = time.time() + simptime*60
            self.simptime[simpee] = mult
            await asyncio.sleep(simptime*60)
            self.simptime[simpee] = mult
            await simpee.remove_roles(msg.guild.get_role(675743974140411905),reason="SimpBot timeout over")
            print("Unsimping %s" % simpee.name)
            self.simped.pop(simpee)
            await asyncio.sleep(simptime*60)
            if not simpee in self.simped:
                self.simptime[simpee] = 0
        else:
            await msg.channel.send("Simp vote for %s failed" % simpee.name)
    
    async def reset_progress(self):
        if self.inprogress == 1:
            await asyncio.sleep(30)
            if self.inprogress == 1:
                self.inprogress = 2
            await asyncio.sleep(30)
            if self.inprogress == 2:
                self.inprogress = 0