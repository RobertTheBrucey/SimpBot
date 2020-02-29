import discord
import time

VOTE_TIMEOUT = 5

reserved = ['simpintro','simp','unsimp']
class BotClient( discord.Client ):
    blacklist = {}
    def __init__(self, ):
        super().__init__()
        self.blacklist = {}

    async def on_ready( self ):
        print( 'Logged on as {0}!'.format( self.user ) )

    async def on_message( self, message ):
        #Ignore own messages
        if message.author == self.user:
            return

        command = message.content.lower().split()[0]
        if command[0] == "^":
            if command[1:] == "simpintro":
                await message.channel.send("I'm SimpBot")
            elif command[1:] == "simp":
                if message.author not in self.blacklist:
                    self.blacklist[message.author] = time.time()
                if time.time() >= self.blacklist[message.author]:
                    self.blacklist[message.author] = time.time() + VOTE_TIMEOUT*60
                    simpee = int(message.content.lower().split()[1][3:-1])
                    if message.guild.get_member(simpee) != None:
                        print("Simpee exists")
                else:
                    await message.channel.send("Please wait up to 5 minutes before simping again " + message.author.name)
            elif command[1:] == "unsimp":
                pass