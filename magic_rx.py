import discord
from discord.ext import commands, tasks
from itertools import cycle
import asyncio
import datetime
import random


client = commands.Bot(command_prefix="rx!", help_command=None, intents=discord.Intents.all())

prefix = str(client.command_prefix)
status = cycle([f"{prefix} | reisgoldmanX"])


@client.event
async def on_ready():
    await asyncio.sleep(5)
    await client.wait_until_ready()
    change_status.start()
    print("Bot is ready.")


@client.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(client.latency * 1000)}ms latency.")


@client.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)


@client.command(aliases=["uinfo", "uinf", "ui"])
@commands.has_permissions(administrator=True)
async def userinfo(ctx, member: discord.Member):

    roles_mention = []  # Getting Users roles
    for role in member.roles:
        if role.name != "@everyone":
            roles_mention.append(role.mention)
    roles = ", ".join(roles_mention)

    if member is None:  # Counting user invites
        member = ctx.author
    totalInvites = 0
    for i in await member.guild.invites():
        if i.inviter == member:
            totalInvites += i.uses

    create = member.created_at + datetime.timedelta(hours=+3)
    join = member.joined_at + datetime.timedelta(hours=+3)

    embed = discord.Embed(title=f"User {member.name}'s info!", description=f"`{member.name}` has invited `{totalInvites}` people to the server so far!", color=discord.Colour.dark_blue())
    embed.set_thumbnail(url=member.avatar_url)
    embed.add_field(name='User created account at', value="{:%d/%m/%Y - %H:%M}".format(create))
    embed.add_field(name='User joined at', value="{:%d/%m/%Y - %H:%M}".format(join))
    embed.add_field(name="User's status", value=f" {member.status}")
    try:
        embed.add_field(name="User's biography", value=f" {member.activity}")
    except:
        embed.add_field(name="User's biography", value=f"None")
    embed.add_field(name="User is on phone?", value=f" {member.is_on_mobile()}")
    embed.add_field(name="User premium since", value=f" {member.premium_since}")
    embed.add_field(name="User's name in guild", value=f" {member.display_name}")
    embed.add_field(name="User's Discord name", value=f" {member.name + '#' + member.discriminator}")
    try:
        embed.add_field(name="User's current activity", value=f" {member.activities[-1]}")
    except:
        embed.add_field(name="User's current activity", value=f"None")
    embed.add_field(name="User roles", value=f"{roles}")
    embed.set_footer(text=f"User ID: {member.id}")

    await ctx.send(embed=embed)


async def msg_count(add: int, msg: list, time):
    for i in range(0, 24):
        if time.hour == i:
            msg[i] += add


@client.command(aliases=["swin", "sw", "si"])
@commands.has_permissions(administrator=True)
async def serverinfo(ctx):

    time_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    async for x in ctx.guild.fetch_members(limit=None):
        if not x.bot:
            join = x.joined_at + datetime.timedelta(hours=+3)
            await msg_count(1, time_list, join)

    count_list = [0, 0, 0]
    for i in ctx.guild.members:
        if str(i.status).lower() == "online":
            count_list[0] += 1
        elif str(i.status).lower() == "dnd":
            count_list[1] += 1
        elif str(i.status).lower() == "offline":
            count_list[2] += 1

    name = str(ctx.guild.name)
    icon = str(ctx.guild.icon_url)
    description = "**Description:** " + str(ctx.guild.description)
    owner = str(ctx.guild.owner)
    region = str(ctx.guild.region).upper()
    verification = str(ctx.guild.verification_level)
    member_count = str(ctx.guild.member_count)
    channel_count = str(len(ctx.guild.channels))
    role_count = str(len(ctx.guild.roles))
    created_at = ctx.guild.created_at.strftime("**Date:** %Y/%m/%d \n**Time:** %H:%M:%S")

    embed = discord.Embed(
        title=name + " Server Information",
        description=description,
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=icon)
    embed.add_field(name="Owner:", value=owner, inline=True)
    embed.add_field(name="Region:", value=region, inline=True)
    embed.add_field(name="Server Verification:", value=verification)
    embed.add_field(name="Member Count:", value=member_count, inline=True)
    embed.add_field(name="Channel Count:", value=channel_count)
    embed.add_field(name="Role Count:", value=role_count)
    embed.add_field(name="Created at:", value=created_at)
    embed.add_field(name="Activity count:",
                    value=f"Online: **{count_list[0]}**, \nDoNotDisturb: **{count_list[1]}**,  \nOffline: **{count_list[2]}**")
    embed.add_field(name="Members join times", value=f"{time_list}")
    embed.set_footer(text=f"Command User: {ctx.author.name},    Bot developed by: reisgoldmanX")
    await ctx.send(embed=embed)


player1 = ""
player2 = ""
turn = ""
gameOver = True

board = []

winningConditions = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6]
]


@client.command(aliases=['ttt'])
async def tictactoe(ctx, p2: discord.Member):
    emoji = '✅'
    await ctx.message.add_reaction(emoji)

    msg = await ctx.send("**10** seconds lef to accept.")
    for i in range(10):
        await msg.edit(content=f"**{10 - i}** seconds left to accept.")

        await asyncio.sleep(1)
        users = await ctx.message.reactions[0].users().flatten()
        if p2 in users:
            break
    await msg.delete()
    users = await ctx.message.reactions[0].users().flatten()
    if p2 in users:
        await ctx.send(f"{ctx.author.mention} == :regional_indicator_x:\n{p2.mention} == :o2:", delete_after=15)

        global count
        global player1
        global player2
        global turn
        global gameOver

        if gameOver:
            global board
            board = [":white_large_square:", ":white_large_square:", ":white_large_square:",
                     ":white_large_square:", ":white_large_square:", ":white_large_square:",
                     ":white_large_square:", ":white_large_square:", ":white_large_square:"]
            turn = ""
            gameOver = False
            count = 0

            player1 = ctx.author
            player2 = p2

            line = ""
            for x in range(len(board)):
                if x == 2 or x == 5 or x == 8:
                    line += " " + board[x]
                    await ctx.send(line, delete_after=45)
                    line = ""
                else:
                    line += " " + board[x]

            num = random.randint(1, 2)
            if num == 1:
                turn = player1
                await ctx.send("It is <@" + str(player1.id) + ">'s turn.", delete_after=15)
            elif num == 2:
                turn = player2
                await ctx.send("It is <@" + str(player2.id) + ">'s turn.", delete_after=15)
        else:
            await ctx.send("**A game is already in progress! Finish it before starting a new one.**", delete_after=15)
    else:
        await ctx.send("**Don't make me wait bitch!**", delete_after=15)


@client.command()
async def place(ctx, pos: int):
    global turn
    global player1
    global player2
    global board
    global count
    global gameOver

    if not gameOver:
        mark = ""
        if turn == ctx.author:
            if turn == player1:
                mark = ":regional_indicator_x:"
            elif turn == player2:
                mark = ":o2:"
            if 0 < pos < 10 and board[pos - 1] == ":white_large_square:":
                board[pos - 1] = mark
                count += 1

                line = ""
                for x in range(len(board)):
                    if x == 2 or x == 5 or x == 8:
                        line += " " + board[x]
                        await ctx.send(line, delete_after=40)
                        line = ""
                    else:
                        line += " " + board[x]

                checkWinner(winningConditions, mark)

                if gameOver is True:
                    await ctx.send(mark + " **wins!**")
                elif count >= 9:
                    gameOver = True
                    await ctx.send("It's a **tie!**")

                if turn == player1:
                    turn = player2
                elif turn == player2:
                    turn = player1
            else:
                await ctx.send("Be sure to choose an integer between 1 and 9 (inclusive) and an unmarked tile.",
                               delete_after=20)
        else:
            await ctx.send("**It is not your turn.**", delete_after=20)
    else:
        await ctx.send(f"Please start a new game using the **{prefix}tictactoe <mention>** command.", delete_after=20)


def checkWinner(winningConditions, mark):
    global gameOver
    for condition in winningConditions:
        if board[condition[0]] == mark and board[condition[1]] == mark and board[condition[2]] == mark:
            gameOver = True


@tictactoe.error
async def tictactoe_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ttthelp(ctx)
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please make sure to mention/ping players Example: <@788052789745549324>.")


@place.error
async def place_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("**Please enter a position you would like to mark.**", delete_after=30)
    elif isinstance(error, commands.BadArgument):
        await ctx.send("**Please make sure to enter an integer.**", delete_after=30)


async def ttthelp(ctx):
    table = ":one:  :two:  :three:\n:four:  :five:  :six:\n:seven:  :eight:  :nine:"
    desc = "A game in which two players alternately put Xs and Os in compartments of a figure formed by two vertical lines crossing two horizontal lines and each tries to get a row of three Xs or three Os before the opponent does.\n\n**The board's delete after 40 seconds so be fast!**"

    embed = discord.Embed(title="Tictactoe help", description=desc, colour=discord.Colour.dark_blue())
    embed.add_field(name="Starting the game.",
                    value=f"Usage: {prefix}tictactoe **<mention>**\nMentioned player has to press the already existing reaction in 10 seconds to play the game.",
                    inline=False)
    embed.add_field(name="Marking a position",
                    value=f"The board counts from left to right.\n{table}\nUsage: {prefix}place **<position>**",
                    inline=False)
    await ctx.send(embed=embed, delete_after=120)


@client.command()
async def avatar(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.message.author
    embed = discord.Embed(title=f"Avatar of  {member.name + '#' + member.discriminator}", color=ctx.author.color)
    embed.set_image(url=member.avatar_url_as(size=2 ** 10))
    await ctx.send(embed=embed)




@client.command()
async def cry(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.message.author

    cryer = random.choice(crying)
    embed = discord.Embed(title=" ", color=ctx.author.color)
    embed.set_author(name=f"{member.display_name} is crying..", icon_url=ctx.author.avatar_url)
    embed.set_image(url=cryer)
    await ctx.send(embed=embed)


@client.command()
async def kill(ctx, member: discord.Member):
    kill2 = random.choice(kill1)
    suicide = random.choice(skill)
    if ctx.message.author.mention == member.mention:
        embed = discord.Embed(title=" ", color=ctx.author.color)
        embed.set_author(name=f"{ctx.message.author.name} kills him/her self.", icon_url=ctx.author.avatar_url)
        embed.set_image(url=suicide)
        await ctx.send(embed=embed)

    else:
        embed = discord.Embed(title=" ", color=ctx.author.color)
        embed.set_author(name=f"{ctx.message.author.name} kills {member.name}", icon_url=ctx.author.avatar_url)
        embed.set_image(url=kill2)
        embed.set_footer(text="Developer: reisgoldmanX")
        await ctx.send(embed=embed)


@commands.cooldown(1, 60 * 20, commands.BucketType.guild)
@client.command()
async def killall(ctx):
    allkill = random.choice(killal)
    embed = discord.Embed(title=" ", color=ctx.author.color)
    embed.set_image(url=allkill)
    embed.set_footer(text="This command has 20 minute cool down after usage.")
    await ctx.send(f"{ctx.message.author.mention} kills @everyone !", embed=embed)


@client.command()
async def punch(ctx, member: discord.Member):
    spunch2 = random.choice(spunch1)
    punch2 = random.choice(punch1)
    if ctx.message.author.mention == member.mention:
        embed = discord.Embed(title=" ", color=ctx.author.color)
        embed.set_author(name=f"{ctx.message.author.name} hits him/her self.", icon_url=ctx.author.avatar_url)
        embed.set_image(url=spunch2)
        await ctx.send(embed=embed)

    else:
        embed = discord.Embed(title=" ", color=ctx.author.color)
        embed.set_author(name=f"{ctx.message.author.name} punches {member.name}", icon_url=ctx.author.avatar_url)
        embed.set_image(url=punch2)
        embed.set_footer(text="Developer: reisgoldmanX")
        await ctx.send(embed=embed)


@client.command()
async def kiss(ctx, member: discord.Member):
    kiss2 = random.choice(kiss1)
    skiss2 = random.choice(skiss1)

    if ctx.message.author.mention == member.mention:
        embed = discord.Embed(title=" ", color=ctx.author.color)
        embed.set_author(name=f"{ctx.message.author.name} kisses him/her self.", icon_url=ctx.author.avatar_url)
        embed.set_image(url=skiss2)
        await ctx.send(embed=embed)

    else:
        embed = discord.Embed(title=" ", color=ctx.author.color)
        embed.set_author(name=f"{ctx.message.author.name} kisses {member.name}.", icon_url=ctx.author.avatar_url)
        embed.set_image(url=kiss2)
        embed.set_footer(text=f"The bot is currently in {len(list(client.guilds))} servers.!")
        await ctx.send(embed=embed)


@client.command()
async def hug(ctx, member: discord.Member):
    hug2 = random.choice(hug1)
    shug2 = random.choice(shug1)
    if ctx.message.author.mention == member.mention:
        embed = discord.Embed(title=" ", color=ctx.author.color)
        embed.set_author(name=f"{ctx.message.author.name} hugs him/her self.", icon_url=ctx.author.avatar_url)
        embed.set_image(url=shug2)
        await ctx.send(embed=embed)

    else:
        embed = discord.Embed(title=" ", color=ctx.author.color)
        embed.set_author(name=f"{ctx.message.author.name} hugs {member.name}.", icon_url=ctx.author.avatar_url)
        embed.set_image(url=hug2)
        embed.set_footer(text="Developer: reisgoldmanX")
        await ctx.send(embed=embed)


@commands.cooldown(1, 60 * 20, commands.BucketType.guild)
@client.command()
async def hugall(ctx):
    allhug = random.choice(hugal)
    embed = discord.Embed(title="", color=ctx.author.color)
    embed.set_image(url=allhug)
    embed.set_footer(text="This command has 20 minute cool down after usage.")
    await ctx.send(f"{ctx.message.author.mention} hugs @everyone !", embed=embed)


@client.command()
async def mat(ctx, num1: float, operator, num2: float):
    if operator == "+":
        await ctx.send(f"{num1} {operator} {num2} = **{num1 + num2}**")
    if operator == "-":
        await ctx.send(f"{num1} {operator} {num2} = **{num1 - num2}**")
    if operator == "*":
        await ctx.send(f"{num1} {operator} {num2} = **{num1 * num2}**")
    if operator == "/":
        await ctx.send(f"{num1} {operator} {num2} = **{num1 / num2}**")
    if operator == ">":
        if num1 > num2:
            await ctx.send("`True`")
        else:
            await ctx.send("`False`")
    if operator == "<":
        if num1 < num2:
            await ctx.send("`True`")
        else:
            await ctx.send("`False`")
    if operator == "==":
        if num1 == num2:
            await ctx.send("`True`")
        else:
            await ctx.send("`False`")


@client.command(pass_context=True)
async def help(ctx):
    embed = discord.Embed(title="Help", colour=discord.Colour.dark_orange())
    embed.add_field(name="Prefix", value=f"The Bots prefix is **{client.command_prefix}** . ", inline=False)
    embed.add_field(name="ping", value=f"Returns the latency of the bot.\nUsage: {prefix}ping", inline=False)
    embed.add_field(name="mat", value="A basic calculator works with two integers and a operator.", inline=False)
    embed.add_field(name="punch", value=f"Sends a gif message with punching content.\nUsage: {prefix}punch **<mention>**",
                    inline=False)
    embed.add_field(name="kill", value=f"Sends a gif message with killing content.\nUsage: {prefix}kill **<mention>**",
                    inline=False)
    embed.add_field(name="hug", value=f"Sends a gif message with a hug content.\nUsage: {prefix}hug **<mention>**",
                    inline=False)
    embed.add_field(name="kiss", value=f"Sends a gif message with a kiss content.\nUsage: {prefix}kiss **<mention>**",
                    inline=False)
    embed.add_field(name="cry", value=f"Sends a gif message with a crying content.\nUsage: {prefix}cry",
                    inline=False)
    embed.add_field(name="hugall", value=f"Same as hug but this command hugs everyone and it has a 20 minute cooldown.",
                    inline=False)
    embed.add_field(name="killall",
                    value="Same as kill but this command hugs everyone and it has a 20 minute cooldown.", inline=False)
    embed.add_field(name="avatar", value=f"Sends users avatar.\nUsage: {prefix}avatar **<mention>**", inline=False)
    embed.add_field(name="ship",
                    value=f"Sends a love possibility percentage.\nUsage: {prefix}ship **<mention1>** **<mention2>**",
                    inline=False)
    embed.add_field(name="tictactoe",
                    value=f"Starts the XOX game.\nTo get more help: {prefix}tictactoe\nUsage: {prefix}tictactoe **<mention>**",
                    inline=False)
    embed.add_field(name="react", value=f"Reacts a message.\nUsage: {prefix}react>", inline=False)
    await ctx.send(embed=embed, delete_after=110)

    em = discord.Embed(title="Admin help", description="These commands can only be used by the server owner.",
                       colour=discord.Colour.dark_blue())
    em.add_field(name="serverinfo", value="Sends a table containing server information.", inline=False)
    em.add_field(name="userinfo", value=f"Sends a table containing user information.\nUsage: {prefix}userinfo **<mention>**",
                 inline=False)
    em.add_field(name="clear",
                 value=f"Deletes the specified number of messages in the used channel.\nUsage: {prefix}clear **<amount>**",
                 inline=False)
    em.add_field(name="!Help!",
                 value="For more help join to the [Rx bot-support](https://discord.gg/sAjP38mxHC) server.",
                 inline=False)
    em.add_field(name="!Bot!",
                 value="Invite the bot to your server.[Invite link](https://discord.com/oauth2/authorize?client_id=787609174476587018&permissions=8&scope=bot)",
                 inline=False)
    em.set_footer(text=f"Help requested by:  {ctx.author.name}   Developer: reisgoldmanX")
    await ctx.send(embed=em, delete_after=110)


@client.command(pass_context=True)
async def mathhelp(ctx):
    embed = discord.Embed(colour=discord.Colour.dark_blue())
    embed.set_author(name="Master magician math chart")
    embed.add_field(name="Operator's",
                    value="( + )  Used for addition.\n( - )  Used for extraction.\n( * )  Used for multiplication.\n( / )  Used for division.\n",
                    inline=False)
    embed.add_field(name="Comparison Operator's", value="( > ) Greater than.\n( < ) Less than.\n( == ) Equal to")
    embed.add_field(name="Usage", value=f"Example: {prefix}mat **<number1>** **<operator>** **<number2>**", inline=False)
    await ctx.send(embed=embed)


@mat.error
async def mat_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await mathhelp(ctx)
    if isinstance(error, discord.ext.commands.errors.CommandInvokeError):
        await mathhelp(ctx)


@hugall.error
async def hugall_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = 'Please wait ** {:.1f}s ** and try again.'.format(error.retry_after)
        await ctx.send(msg, delete_after=10)
    else:
        raise error


@killall.error
async def killall_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = 'Please wait ** {:.1f}s ** and try again.'.format(error.retry_after)
        await ctx.send(msg, delete_after=10)
    else:
        raise error


@commands.cooldown(1, 10 * 1, commands.BucketType.guild)
@client.command()
async def react(ctx, choice: int, *, msg_id: int):
    msg = await ctx.fetch_message(msg_id)

    arti1 = ["🇦", "🇷", "🇹", "🇮", "1️⃣"]
    eksi1 = ["🇪", "🇰", "🇸", "ℹ️", "1️⃣"]
    katiliyorum = ["🇰", "🇦", "🇹", "🇮", "🇱", "ℹ️", "🇾", "🇴", "🇷", "🇺", "🇲"]
    bravo = ["🇧", "🇷", "🇦", "🇻", "🇴", "👏"]
    kalp = ["🇰", "🇦", "🇱", "🇵"]
    wiu = ["🇼", "ℹ️", "🇺"]

    mal = ["🇲", "🇦", "🇱"]
    aoc = ["🇦", "🇴", "🇨"]
    orospu = ["🇴", "🇷", "🅾️", "🇸", "🇵", "🇺"]
    sikeyim = ["🇸", "🇮", "🇰", "🇪", "🇾", "ℹ️", "🇲"]
    sex = ["🇸", "🇪", "🇽"]
    amk = ["🇦", "🇲", "🇰"]
    gay = ["🇬", "🇦", "🇾"]
    lez = ["🇱", "🇪", "🇿"]

    reactions = {1: arti1, 2: eksi1, 3: katiliyorum,
                 4: bravo, 5: kalp, 6: wiu,
                 7: mal, 8: aoc, 9: orospu,
                 10: sikeyim, 11: sex, 12: amk,
                 13: gay, 14: lez}

    for k, j in reactions.items():
        if int(k) == int(choice):
            for i in j:
                await msg.add_reaction(i)

    await ctx.message.delete()
    link = f"https://discord.com/channels/{msg.guild.id}/{msg.channel.id}/{msg.id}"
    await ctx.send(link, delete_after=20)


async def react_help(ctx):
    emojis = """
**1.**   🇦 🇷 🇹 🇮 1️⃣
**2.**   🇪 🇰 🇸 ℹ️ 1️⃣
**3.**   🇰 🇦 🇹 🇮 🇱 ℹ️ 🇾 🇴 🇷 🇺 🇲
**4.**   🇧 🇷 🇦 🇻 🇴 👏
**5.**   🇰 🇦 🇱 🇵
**6.**   🇼 ℹ️ 🇺
**7.**   🇲 🇦 🇱
**8.**   🇦 🇴 🇨
**9.**   🇴 🇷 🅾️ 🇸 🇵 🇺
**10.**  🇸 🇮 🇰 🇪 🇾 ℹ️ 🇲
**11.**  🇸 🇪 🇽
**12.**  🇦 🇲 🇰
**13.**  🇬 🇦 🇾
**14.**  🇱 🇪 🇿
"""

    embed = discord.Embed(colour=discord.Colour.dark_blue())
    embed.set_author(name="Master magician reactor")
    embed.add_field(name="Choices", value=emojis, inline=False)
    embed.add_field(name="Usage", value=f"Example: {prefix}react **<Choice>** **<Msg id>**", inline=False)
    await ctx.send(embed=embed, delete_after=15)


@react.error
async def react_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await react_help(ctx)
    elif isinstance(error, discord.ext.commands.errors.CommandInvokeError):
        await react_help(ctx)
    elif isinstance(error, commands.CommandOnCooldown):
        msg = 'Please wait ** {:.1f}s ** and try again.'.format(error.retry_after)
        await ctx.send(msg, delete_after=float(error.retry_after))
    else:
        raise error


@client.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)


@tasks.loop(seconds=30)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))

client.run("BOT_TOKEN")
