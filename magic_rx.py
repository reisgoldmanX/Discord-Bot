import discord
from discord.ext import commands, tasks
from itertools import cycle
import asyncio
import os
from discord import opus
from discord.utils import get
import youtube_dl
import datetime
import random
import requests
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO


client = commands.Bot(command_prefix="am!", help_command=None, intents=discord.Intents.all())

prefix = str(client.command_prefix)
status = cycle([f"{prefix} | reisgoldmanX"])



@client.event
async def on_ready():
    await asyncio.sleep(5)
    await client.wait_until_ready()
    change_status.start()
    print("Bot is ready.")


@client.event
async def on_member_join(member):
    guild = member.guild.id
    if guild == 813756240286580789:
        global last
        last = str(member.id)


@client.event
async def on_message(message):
    await client.process_commands(message)


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
async def ship(ctx, user: discord.Member = None, usr: discord.Member = None):
    if user is None:
        user = ctx.message.author
        usr = ctx.message.author

    font = ImageFont.truetype("arial.ttf", 27)
    sh = Image.open("rxship.png")

    u1 = user.avatar_url_as(size=128)
    dat = BytesIO(await u1.read())

    u2 = usr.avatar_url_as(size=128)
    data2 = BytesIO(await u2.read())
    chg = random.randint(0, 100)

    draw = ImageDraw.Draw(sh)
    text = f"%{chg}"

    draw.text((268, 125), text, (0, 0, 0), font=font)
    pt1 = Image.open(dat)
    pf = Image.open(data2)
    pfp2 = pf.resize((150, 150))
    pt = pt1.resize((150, 150))

    sh.paste(pfp2, (370, 73))
    sh.paste(pt, (81, 73))
    sh.save("ship.png")
    await ctx.send(file=discord.File("ship.png"))

kill1 = [
    "https://media1.giphy.com/media/9tXn7DEOsjifNDEenF/giphy.gif?cid=ecf05e47gaucn3tiyvf8jc03jaq7gbnurgxzx4n0klnelg6n&rid=giphy.gif",
    "https://media3.giphy.com/media/PnhOSPReBR4F5NT5so/giphy.gif?cid=ecf05e47gaucn3tiyvf8jc03jaq7gbnurgxzx4n0klnelg6n&rid=giphy.gif",
    "https://media2.giphy.com/media/l4nlWhecm3qN6cYtO9/giphy.gif?cid=ecf05e47cpjh8l4ssf89jzblu8su6rcmby3v7kdivobc9mtz&rid=giphy.gif",
    "https://media0.giphy.com/media/26xBIuyhb8U3VhGQo/giphy.gif?cid=ecf05e4784w0j7h8cm4ydjg01ej3ah2j8zzqirqxwwlpnu5q&rid=giphy.gif",
    "https://media0.giphy.com/media/l41lQoBdyggVzO8yA/giphy.gif?cid=ecf05e47f4puzt5nv54aoggykxo1raxxmzr26anw2q8t6ddn&rid=giphy.gif",
    "https://media3.giphy.com/media/CiZB6WIjaoXYc/giphy.gif?cid=ecf05e47gaucn3tiyvf8jc03jaq7gbnurgxzx4n0klnelg6n&rid=giphy.gif",
    "https://media1.giphy.com/media/3o6ozCytqK9iZYgoVO/giphy.gif?cid=ecf05e47tisc9nb8dtmv64alrfacbrlm7pmsiya1dnkiczsr&rid=giphy.gif",
    "https://media0.giphy.com/media/3o7bubOrApMZ4sNI1q/giphy.gif?cid=ecf05e47vbxcc66l6b2dri33za7e8ta3enjzxh8r9lwan1q2&rid=giphy.gif",
    "https://media0.giphy.com/media/3o6Zt7xWCLZD8f5ZsY/giphy.gif?cid=ecf05e47bb3xe8trv9pk9acdprkk65lzyyzfxnwmci07o8hi&rid=giphy.gif",
    "https://media0.giphy.com/media/l4Jz8aaFug1YDh49q/giphy.gif",
    "https://media3.giphy.com/media/3o7qE9nmeIsgoOBOSI/giphy.gif?cid=ecf05e47bhwmkouv72bz03fxy9zgh18h1crs84bqfbmxldz3&rid=giphy.gif",
    "https://i.kym-cdn.com/photos/images/original/001/890/995/e1c.gif",
    "https://cdn.discordapp.com/attachments/781946907567325194/815674476234670090/fffff.gif",
    "https://media1.tenor.com/images/430f0887ff001b2dbe3b768a1a7ced5f/tenor.gif",

]

skill = ["https://c.tenor.com/TBcOtF6I_1wAAAAM/dead-suicide.gif",
         "https://c.tenor.com/djMkLZMQfzkAAAAM/oso-bear.gif",
         "https://media3.giphy.com/media/l2JeiuwmhZlkrVOkU/giphy.gif?cid=ecf05e47qsq7ddy24tks6ipo410dknq0d1y4b3agt6k2uup0&rid=giphy.gif",
         "https://media2.giphy.com/media/l0HlJHBQkuVeDD29i/giphy.gif?cid=ecf05e47yrz8c6kjc8dy85g0oc1692vqnjcrvucwg02320fr&rid=giphy.gif",
         "https://media1.giphy.com/media/l2JdUTsQtfp130pAk/giphy.gif?cid=ecf05e471agbra8srkaqp5e94o1teb88feln4tmk1pr0mc28&rid=giphy.gif",
         "https://i.gifer.com/VBWs.gif",
         "https://i.gifer.com/DGAA.gif",
         "http://25.media.tumblr.com/7eb5485b5c8254d0d6e1ff92ed2d1463/tumblr_mu180tkfJ11su54ueo1_500.gif",
         "https://i.makeagif.com/media/2-09-2016/BJaf2S.gif",
         "http://3.bp.blogspot.com/-7D-4aJxgITI/Up6c9Yj3HyI/AAAAAAAAAxA/Rb9i8tmm9DA/s400/kill.gif",
         "https://media1.tenor.com/images/ddff6459bc5ac22df061c857f9342970/tenor.gif",
         "https://media1.tenor.com/images/45cba84e53e6bda9718c1fe11af67682/tenor.gif"
         ]

killal = ["https://media1.tenor.com/images/4164506fc74c0731c80aaf89f331f959/tenor.gif",
          "https://media1.tenor.com/images/de2c167bdc51f7384b3707dfd6bcdc39/tenor.gif",
          "https://media2.giphy.com/media/xT5LMtCSJ01RFP8GjK/giphy.gif?cid=ecf05e47nc8cswdr1kkvq4hw465xaust0cl5m8vro7s7j8q2&rid=giphy.gif",
          "https://media3.giphy.com/media/3o7aTu1MPDm08RnhO8/giphy.gif?cid=ecf05e476tcr73hcnxeo5ib4eg8sznlplzbimbbv1n0v6zyf&rid=giphy.gif",
          "https://media0.giphy.com/media/l3fZNEmZjRFgcsJ6U/giphy.gif?cid=ecf05e47ymcoq1da75m2orkliq8vyip49893w70r5rmh374b&rid=giphy.gif",
          "https://media1.tenor.com/images/24b6028fb3a1472be808b0805074ebcf/tenor.gif",
          "https://i.pinimg.com/originals/cc/87/65/cc87656cf72979fb8ee01c3eebc5cdff.gif",
          "https://cdn.discordapp.com/attachments/813756241775296523/815671339259265054/A85z.gif",
          "https://thumbs.gfycat.com/AnySadDouglasfirbarkbeetle-size_restricted.gif",
          "https://media1.tenor.com/images/fc8dd3e14824c100c9f3ab48ed031b04/tenor.gif",
          "https://thumbs.gfycat.com/ThankfulSimplisticDunlin-max-1mb.gif"
          ]

crying = ["https://media1.tenor.com/images/3c6c1f8fd7a88836ad0fcfacc0acc7f3/tenor.gif",
          "https://media1.tenor.com/images/c400b095f760f564cce405696e32c357/tenor.gif",
          "https://media1.tenor.com/images/8e6ec7090a58aa27504b1c8dd3671aa5/tenor.gif",
          "https://media1.tenor.com/images/8a4806e124382386aa816c1780614e5c/tenor.gif",
          "https://media1.tenor.com/images/d711c59b312ebb6691305f8def842e44/tenor.gif",
          "https://media1.tenor.com/images/4f0673fe4091e88cac9ef1b683f9f81c/tenor.gif",
          "https://media1.tenor.com/images/01cc20e8639fe26ec13b4ca762bbd4b1/tenor.gif",
          "https://media1.tenor.com/images/a9b946a2d108f53d4e02ec4f7f1ca255/tenor.gif",
          "https://media1.tenor.com/images/1bae3728cc119dccf7a1d3a5e342b9e2/tenor.gif",
          "https://cdn.discordapp.com/attachments/781946907567325194/835640869771673650/en_hikayeli_cry_gif.gif"
          ]


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


punch1 = [
    "https://media0.giphy.com/media/GoN89WuFFqb2U/giphy.gif?cid=ecf05e479dvzu5cuwxl4r7j2c2b29ccel9rbvs4k1l6gn6kw&rid=giphy.gif",
    "https://media1.giphy.com/media/P4l2ET85UuedO/giphy.gif?cid=ecf05e479dvzu5cuwxl4r7j2c2b29ccel9rbvs4k1l6gn6kw&rid=giphy.gif",
    "https://media4.giphy.com/media/iKGJeenxoC1iRDvzdb/giphy.gif?cid=ecf05e47dcgn2ev3tpas0szbd9c63iava9y9x2f8f6um7olu&rid=giphy.gif",
    "https://media0.giphy.com/media/3M5J7yedLPCSs/giphy.gif?cid=ecf05e47dcgn2ev3tpas0szbd9c63iava9y9x2f8f6um7olu&rid=giphy.gif",
    "https://media0.giphy.com/media/rcRwO8GMSfNV6/giphy.gif?cid=ecf05e47dcgn2ev3tpas0szbd9c63iava9y9x2f8f6um7olu&rid=giphy.gif",
    "https://media3.giphy.com/media/3oz8xyUoD2HlTIcdTW/giphy.gif?cid=ecf05e47gwyglwsv8qbi2bmcoov3539ghqvkggyb3002k5jk&rid=giphy.gif",
    "https://media3.giphy.com/media/dYLWFqSfCKWB5C8MEw/giphy.gif?cid=ecf05e479km4r5f05uoy6c5ui8x8id290m4i380e75o8wcud&rid=giphy.gif",
    "https://media2.giphy.com/media/tmyDAo1Si2KIg/giphy.gif?cid=ecf05e47vko6z2p8b4ebrt9ahv0092b8h37wns2k8sma2y5e&rid=giphy.gif",
    "https://media4.giphy.com/media/xUNemWOzznJDZpRDZm/giphy.gif?cid=ecf05e47jlc0h7pnsyx8xnjl06yv4c4d5ot75nskirzavcof&rid=giphy.gif",
    "https://media3.giphy.com/media/xT0BKiwgIPGShJNi0g/giphy.gif?cid=ecf05e47dcgn2ev3tpas0szbd9c63iava9y9x2f8f6um7olu&rid=giphy.gif",
    "https://media4.giphy.com/media/3ohc1e63jpDroNULUA/giphy.gif?cid=ecf05e47fb47650f30dea4ee6a4f76f2d7e11abcb91d422e&rid=giphy.gif",
    "https://media1.giphy.com/media/8c0YBK1CYTBRPr5YxF/giphy.gif?cid=ecf05e47969daa900093f644d5a3d4feb8370d30f0cd81ed&rid=giphy.gif",
    "https://media2.giphy.com/media/vcdZUjtcK8fPraAKm5/giphy.gif?cid=ecf05e47cc18be8d45f2b5c48fc13c5e3fd74ee68e151f5d&rid=giphy.gif",
    "https://media0.giphy.com/media/Z5zuypybI5dYc/giphy.gif?cid=ecf05e47ftstonfzijmo5vyjvglkpl1q33wy0qnok61zinev&rid=giphy.gif",
    "https://media3.giphy.com/media/YrfARBZkReL8Q/giphy.gif?cid=ecf05e47d377493c55efdc0b31615dd3c39420b936a76724&rid=giphy.gif",
    "https://media4.giphy.com/media/dDR1TIXAWcVoNaYcbj/giphy.gif?cid=ecf05e47r55cey6ftx313z4due9z7t8llozkxpm1mkubq1q1&rid=giphy.gif",
    "https://media3.giphy.com/media/eiw5mph3qBvdiiHxMa/giphy.gif?cid=ecf05e472x5ak7ei3nniw1r8r98pqc81muwudlahbicnse5f&rid=giphy.gif",
    "https://media3.giphy.com/media/c3JeqZlXrEVX2/giphy.gif?cid=ecf05e47lqw6ibaj8g308cvmdhfxh1gt79p8p2hl91azc9im&rid=giphy.gif",
    "https://media4.giphy.com/media/hrLXoGaQuz1FcI5XHo/giphy.gif?cid=ecf05e471lb95hv6ngxvusgsqukd75q1wbbbqluylnrc94kv&rid=giphy.gif",
    "https://media0.giphy.com/media/5BURcOrUW5RwgHJywv/giphy.gif?cid=ecf05e47flt4id6vy1ax83bjg7830tbttd41t8ijxrqa25zz&rid=giphy.gif",
    "https://media3.giphy.com/media/l41YysMYz71S0Jw3K/giphy.gif?cid=ecf05e478d3u71ff98ictc6na42ydl8d6hc27jbh708235p4&rid=giphy.gif",
    "https://media2.giphy.com/media/3o7btPrQRKmmaTQzuw/giphy.gif?cid=ecf05e47yr3qi5m17ou0k9gxjeym9dy0z7pyz6herw8m1bmj&rid=giphy.gif",
    "https://media1.giphy.com/media/MYDCi8OsGWhRKPYbly/giphy.gif?cid=ecf05e479o2e16giqr1xjscspre44c7o395axqf5smcsl74j&rid=giphy.gif"
]

spunch1 = [
    "https://media3.giphy.com/media/BHY3AK18ZSJEY/giphy.gif?cid=ecf05e47qif8fbklzxv7371wqkpz54cxaa87osu0mmwcpmal&rid=giphy.gif",
    "https://media3.giphy.com/media/3ohc0SXyU44FIUNOmI/giphy.gif?cid=ecf05e4733e084da868711f85181b6146e7679cdff366d0f&rid=giphy.gif",
    "https://media3.giphy.com/media/3otPoQzwZj5ZIDIjmg/giphy.gif?cid=ecf05e47czfywm3xu61qi9sa7varzjjibwxdsrk8afrtkzxj&rid=giphy.gif",
    "https://media4.giphy.com/media/xTeV7FKRuo5YX714L6/giphy.gif?cid=ecf05e47yvitblp1deu8wwpr64d9na9b3x2jg7a5gt7elm3c&rid=giphy.gif",
    "https://media3.giphy.com/media/dxJ0jmXBitv4Q/giphy.gif?cid=ecf05e47oaemek6rg6duupyd9lkkfo0vxm7zltfbouss709e&rid=giphy.gif",
    "https://media1.giphy.com/media/YmsrJ7AsmdtLO/giphy.gif?cid=ecf05e47oaemek6rg6duupyd9lkkfo0vxm7zltfbouss709e&rid=giphy.gif",
    "https://media3.giphy.com/media/7rJE4vH3ItKDu/giphy.gif?cid=ecf05e47oaemek6rg6duupyd9lkkfo0vxm7zltfbouss709e&rid=giphy.gif",
    "https://media4.giphy.com/media/l4Ep43foEMO4kjWec/giphy.gif?cid=ecf05e478i7og9wwacpgqu20oaxwvy42tim8icofblmonmat&rid=giphy.gif",
    "https://media3.giphy.com/media/xUNd9AWlNxNgnxiIxO/giphy.gif?cid=ecf05e478i7og9wwacpgqu20oaxwvy42tim8icofblmonmat&rid=giphy.gif",
    "https://media2.giphy.com/media/l2p0GP32oaHa0TYKWA/giphy.gif?cid=ecf05e478i7og9wwacpgqu20oaxwvy42tim8icofblmonmat&rid=giphy.gif"
]


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


kiss1 = [
    "https://media3.giphy.com/media/l2Je2M4Nfrit0L7sQ/giphy.gif?cid=ecf05e47szh4pioktxmkpr3lk28ckkmffsnu245296sqs61u&rid=giphy.gif",
    "https://media2.giphy.com/media/TfEtuvZ4sviFlgjdVT/giphy.gif?cid=ecf05e47szh4pioktxmkpr3lk28ckkmffsnu245296sqs61u&rid=giphy.gif",
    "https://media3.giphy.com/media/HKQZgx0FAipPO/giphy.gif?cid=ecf05e47szh4pioktxmkpr3lk28ckkmffsnu245296sqs61u&rid=giphy.gif",
    "https://media0.giphy.com/media/RW4Vf0698oX3W/giphy.gif?cid=ecf05e47szh4pioktxmkpr3lk28ckkmffsnu245296sqs61u&rid=giphy.gif",
    "https://media3.giphy.com/media/26tnbo7HDeYacLQK4/giphy.gif?cid=ecf05e47szh4pioktxmkpr3lk28ckkmffsnu245296sqs61u&rid=giphy.gif",
    "https://media4.giphy.com/media/Nydo55HzhyGqI/giphy.gif?cid=ecf05e47szh4pioktxmkpr3lk28ckkmffsnu245296sqs61u&rid=giphy.gif",
    "https://media4.giphy.com/media/PFjXmKuwQsS9q/giphy.gif?cid=ecf05e47szh4pioktxmkpr3lk28ckkmffsnu245296sqs61u&rid=giphy.gif",
    "https://media3.giphy.com/media/3o7qDVQ2GrFAf1MVgc/giphy.gif?cid=ecf05e47szh4pioktxmkpr3lk28ckkmffsnu245296sqs61u&rid=giphy.gif",
    "https://media0.giphy.com/media/Ij1cbMbIWDKDK/giphy.gif?cid=ecf05e47szh4pioktxmkpr3lk28ckkmffsnu245296sqs61u&rid=giphy.gif",
    "https://media0.giphy.com/media/AIDv87fiokBva/giphy.gif?cid=ecf05e47kuml2nypxfq42u5bqwdw0w5r4bcu9rt1hbfg5emi&rid=giphy.gif",
    "https://media0.giphy.com/media/l0HU2EeywKGaMJCY8/giphy.gif?cid=ecf05e47kuml2nypxfq42u5bqwdw0w5r4bcu9rt1hbfg5emi&rid=giphy.gif",
    "https://media3.giphy.com/media/frHK797nhEUow/giphy.gif?cid=ecf05e47kuml2nypxfq42u5bqwdw0w5r4bcu9rt1hbfg5emi&rid=giphy.gif",
    "https://media2.giphy.com/media/fyM2loi1ZpOV2/giphy.gif?cid=ecf05e47kuml2nypxfq42u5bqwdw0w5r4bcu9rt1hbfg5emi&rid=giphy.gif",
    "https://media1.giphy.com/media/xT9IgFh732bmm00u1a/giphy.gif?cid=ecf05e47kuml2nypxfq42u5bqwdw0w5r4bcu9rt1hbfg5emi&rid=giphy.gif",
    "https://media4.giphy.com/media/KMuPz4KDkJuBq/giphy.gif?cid=ecf05e47szh4pioktxmkpr3lk28ckkmffsnu245296sqs61u&rid=giphy.gif",
    "https://media1.giphy.com/media/6uFetT0Kw9Isg/giphy.gif?cid=ecf05e47rukkjtkz20vg1dl6pk35vix9jo6sy2rx2httuv0q&rid=giphy.gif",
    "https://media2.giphy.com/media/l0MYEw4RMBirPQhHy/giphy.gif?cid=ecf05e47rukkjtkz20vg1dl6pk35vix9jo6sy2rx2httuv0q&rid=giphy.gif",
    "https://media1.giphy.com/media/l2Jedu4zTDKTk0khO/giphy.gif?cid=ecf05e476enlzcz3z86okfefaykdyfdvw81gt410e868ml7z&rid=giphy.gif",
    "https://media0.giphy.com/media/124oy5lEztKSI/giphy.gif?cid=ecf05e47c1dkq3jx1nb3wca5emgnvav0hkairumfeino014i&rid=giphy.gif",
    "https://media3.giphy.com/media/j1l1QRW2YMAec/giphy.gif?cid=ecf05e47rukkjtkz20vg1dl6pk35vix9jo6sy2rx2httuv0q&rid=giphy.gif",
    "https://media1.giphy.com/media/26CYzSwyz15mDjYdi/giphy.gif?cid=ecf05e47demkqy9dfbsrp58rvrts9vb7pubv2flo3ags1xqk&rid=giphy.gif",
    "https://media1.tenor.com/images/880f2769736057910c95ca45c92822a4/tenor.gif",
    "https://media1.tenor.com/images/9888a0dccd58a8f21d7535dbcf2aee9c/tenor.gif",
    "https://cdn.discordapp.com/attachments/829951518114840577/835494315505352724/43b7a7d85aa668b1a37358fa4995c181.gif",
    "https://cdn.discordapp.com/attachments/829951518114840577/835494316004212796/8c153af3b47b16d674968c004271d98a.gif",
    "https://media1.tenor.com/images/f5b905cfbb9e321f542441b99766cb85/tenor.gif",
    "https://media1.tenor.com/images/d307db89f181813e0d05937b5feb4254/tenor.gif"
]

skiss1 = [
    "https://media2.giphy.com/media/13R2R6io2ouk1jlv8f/giphy.gif?cid=ecf05e47kahckx6szy99jot741255zkcyoeswm55x1dg1emf&rid=giphy.gif",
    "https://media1.giphy.com/media/ToMjGpQu6ljfnlfWNHi/giphy.gif?cid=ecf05e47kahckx6szy99jot741255zkcyoeswm55x1dg1emf&rid=giphy.gif",
    "https://media1.giphy.com/media/l1J9AlzGcsIujy5TW/giphy.gif?cid=ecf05e47kahckx6szy99jot741255zkcyoeswm55x1dg1emf&rid=giphy.gif",
    "https://media0.giphy.com/media/dcicvkMIKwHRu/giphy.gif?cid=ecf05e47myh2qnmjrqxfn9w9zlwitxlyea0v5225qvsr9jz5&rid=giphy.gif",
    "https://media3.giphy.com/media/xTkcEQg6H8VgB9mGYg/giphy.gif?cid=ecf05e47amxfem8arwrvgj1n2lu0n1cipz4e16nbzooxhwbh&rid=giphy.gif",
    "https://media2.giphy.com/media/58Fr0AaHfMqwZSvYrS/giphy.gif?cid=ecf05e47kned0a5llcz0dm3doz70jt8f4el0zhvros8poofb&rid=giphy.gif"
]


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


hug1 = [
    "https://media2.giphy.com/media/3oEdv4hwWTzBhWvaU0/giphy.gif?cid=ecf05e47hecg9azz8ockpfh5kjqii08w0gat5buzaq68lgv5&rid=giphy.gif",
    "https://media2.giphy.com/media/EvYHHSntaIl5m/giphy.gif?cid=ecf05e47ow8xf6dv6upm32fb54fjk6ofbl9l7npwyykujqs7&rid=giphy.gif",
    "https://media4.giphy.com/media/42YlR8u9gV5Cw/giphy.gif?cid=ecf05e47ow8xf6dv6upm32fb54fjk6ofbl9l7npwyykujqs7&rid=giphy.gif",
    "https://media0.giphy.com/media/QTaesEFq1uxqEepIVI/giphy.gif?cid=ecf05e4777d2lmxqternriu4glbvrqufkui9wydloe6h992o&rid=giphy.gif",
    "https://media2.giphy.com/media/dQj2Cp0Gw8uLC/giphy.gif?cid=ecf05e477lv76wuk0tsok3uckw95q8ulh2hymisa0mgh8jn9&rid=giphy.gif",
    "https://media3.giphy.com/media/od5H3PmEG5EVq/giphy.gif?cid=ecf05e47t9i9gljc9v4lfda3xyuya65g6e5xi2sner8n69p7&rid=giphy.gif",
    "https://media1.giphy.com/media/wnsgren9NtITS/giphy.gif?cid=ecf05e47t9i9gljc9v4lfda3xyuya65g6e5xi2sner8n69p7&rid=giphy.gif",
    "https://media3.giphy.com/media/kvKFM3UWg2P04/giphy.gif?cid=ecf05e47t9i9gljc9v4lfda3xyuya65g6e5xi2sner8n69p7&rid=giphy.gif",
    "https://media2.giphy.com/media/sUIZWMnfd4Mb6/giphy.gif?cid=ecf05e47t9i9gljc9v4lfda3xyuya65g6e5xi2sner8n69p7&rid=giphy.gif",
    "https://media3.giphy.com/media/45Lg3ECIw25Fe/giphy.gif",
    "https://media4.giphy.com/media/l2QDM9Jnim1YVILXa/giphy.gif?cid=ecf05e47t9i9gljc9v4lfda3xyuya65g6e5xi2sner8n69p7&rid=giphy.gif",
    "https://media4.giphy.com/media/DjczAlIcyK1Co/giphy.gif?cid=ecf05e47ws1xpfdzvxja4bjprfprb5dsz5qzhqayg12a4ual&rid=giphy.gif",
    "https://media2.giphy.com/media/dZFwM99vVVlubq0S3R/giphy.gif?cid=ecf05e47648dh38lcz5e6hn5yia7l84wsw0p153o6ksdtpnl&rid=giphy.gif",
    "https://media1.giphy.com/media/YpueTEU32wnss/giphy.gif?cid=ecf05e47648dh38lcz5e6hn5yia7l84wsw0p153o6ksdtpnl&rid=giphy.gif",
    "https://media0.giphy.com/media/PHZ7v9tfQu0o0/giphy.gif?cid=ecf05e47ws1xpfdzvxja4bjprfprb5dsz5qzhqayg12a4ual&rid=giphy.gif",
    "https://media0.giphy.com/media/Y2bRsKceLPRaEm7Vgr/giphy.gif?cid=ecf05e470095e0001e31b95194adf275532c28e36664ca3e&rid=giphy.gif",
    "https://media1.tenor.com/images/95b41ae72f201a5389a78ccfdf2e6657/tenor.gif?itemid=4911454",
    "https://media1.tenor.com/images/68f16d787c2dfbf23a4783d4d048c78f/tenor.gif?itemid=9512793",
    "https://media1.tenor.com/images/29a2d3fc01c709ffb2f38cd9dfaf04d2/tenor.gif?itemid=3576907",
    "https://media1.tenor.com/images/f3ffd3669c13ee8d091a6b583976efe9/tenor.gif?itemid=9322908",
    "https://media1.tenor.com/images/bb9c0c56769afa3b58b9efe5c7bcaafb/tenor.gif?itemid=16831471",
    "https://media1.tenor.com/images/1506349f38bf33760d45bde9b9b263a4/tenor.gif?itemid=17266781",
    "https://media1.tenor.com/images/a71b123666e08bb6ad336cd1625c0cdb/tenor.gif?itemid=3525606",
    "https://media1.tenor.com/images/dd1b8fe694d7bfba2ae87e1ede030244/tenor.gif?itemid=15999080",
    "https://cdn.discordapp.com/attachments/790476204615925770/802624638990942238/osomatsu-san___Tumblr.gif",
    "https://cdn.zerotwo.dev/HUG/49ade704-4e3b-4fd6-a2d6-05ea6b8d9bf0.gif",
    "https://media1.tenor.com/images/8af307989eb713d2f3817f0e2fd1676d/tenor.gif"
]

shug1 = [
    "https://media0.giphy.com/media/l1J9E5yjPqaMM5M3K/giphy.gif",
    "https://media1.giphy.com/media/9xrrQ9UX8ImQWlHGwv/giphy.gif?cid=ecf05e47ow8xf6dv6upm32fb54fjk6ofbl9l7npwyykujqs7&rid=giphy.gif",
    "https://media2.giphy.com/media/Q5FpyePxey4EG4ek30/giphy.gif?cid=ecf05e47zy7rdsajv9ogc0howfqkzp07g3vm0fevkbh3xxud&rid=giphy.gif",
    "https://media1.tenor.com/images/5c65081368756873f7f8077d2a37d29f/tenor.gif?itemid=13902049",
    "https://media1.tenor.com/images/ece8e4aba023f8c487f4a8a83df280b0/tenor.gif?itemid=5612586",
    "https://media1.tenor.com/images/a1dfbc091c0bfb863a374cdd65f2b649/tenor.gif?itemid=3346668",
    "https://media1.tenor.com/images/9ab86529cd5dd5ed1c9ae615229745e9/tenor.gif?itemid=7518148",
    "https://media1.tenor.com/images/29b083641129892206ee041e4b0cac1b/tenor.gif?itemid=8301730",
    "https://media1.tenor.com/images/11607ef5c07a43207fc3e493f1ee59bc/tenor.gif?itemid=14258266",
    "https://media1.tenor.com/images/374c87c3441fb2ca2db721a9ca67b97d/tenor.gif?itemid=16957513",
    "https://media1.tenor.com/images/2fb9dd07c3355f9f7faae6d3e1dc94f2/tenor.gif?itemid=18670414"
]

hugal = [
    "https://images-ext-2.discordapp.net/external/iwNHwVgBKyhucRjR-_PuyvqZqVfzqjskA4OC3-0OhRc/https/cdn.zerotwo.dev/HUG/1f646518-d712-4a32-a3e1-0b7f75ec1257.gif",
    "https://media1.tenor.com/images/9486e539014596bbee9595ba91671982/tenor.gif",
    "https://media1.tenor.com/images/850294e5759ed8d17ac8a3bf4e13795c/tenor.gif",
    "https://media1.tenor.com/images/c32141ae982029beaf8db8d4ddf057bd/tenor.gif",
    "https://media1.tenor.com/images/c5c02e06814e2b6a14b7336ab57f115e/tenor.gif",
    "https://media1.tenor.com/images/4a5561b096946e67c3b80be463d2131d/tenor.gif",
    "https://media1.tenor.com/images/5aaa29c2af5f8fcd233d223c6027bb47/tenor.gif",
    "https://media1.tenor.com/images/45c9df7bc633cf80ba6201599f23373f/tenor.gif",
    "https://media1.tenor.com/images/06e9479bf42ed79021568ed086f1ed8d/tenor.gif",
    "https://cdn.discordapp.com/attachments/790476204615925770/802624633827229786/Yaoiland.gif",
    "https://media1.tenor.com/images/e1c4cb4c008e6b8de2addf22c72167e6/tenor.gif"
]

meme_l = ["https://cdn.discordapp.com/attachments/820309291197923339/820311542175760384/51em0y.png",
          "https://cdn.discordapp.com/attachments/813756241608310794/820296713226551316/yASAK_TAVUK_PILAV.png",
          "https://cdn.discordapp.com/attachments/813756241608310794/820301687393615883/MUHTESEM_UWU.png",
          "https://cdn.discordapp.com/attachments/813756241608310794/820304738247508008/zvall_psi.png",
          "https://cdn.discordapp.com/attachments/813756241608310794/820306683481686026/51kbye1.jpg",
          "https://cdn.discordapp.com/attachments/820309291197923339/820380477998497812/Snapchat-391032263.jpg",
          "https://cdn.discordapp.com/attachments/820309291197923339/820383082334257172/Snapchat-1720352703.jpg",
          "https://cdn.discordapp.com/attachments/820309291197923339/820387599704129536/Snapchat-1936584922.jpg",
          "https://cdn.discordapp.com/attachments/820309291197923339/820387599855386654/Snapchat-169194620.jpg",
          "https://cdn.discordapp.com/attachments/820309291197923339/820391180834832434/Snapchat-1387198496.jpg",
          "https://cdn.discordapp.com/attachments/820309291197923339/820391668670660668/su.jpg",
          "https://cdn.discordapp.com/attachments/820309291197923339/820395079952891954/b.png",
          "https://cdn.discordapp.com/attachments/820309291197923339/820395147001856000/Snapchat-1706959237.jpg",
          "https://cdn.discordapp.com/attachments/820309291197923339/820395492919476234/e3f6419b49b18c21c6ab2ea46fd23700.jpg",
          "https://cdn.discordapp.com/attachments/820309291197923339/820400403782303764/51lh03.png",
          "https://cdn.discordapp.com/attachments/820309291197923339/820533317082152960/51mu39.png",
          "https://cdn.discordapp.com/attachments/820309291197923339/820570258833539072/c0d73a71c69181987c21bff35bc19a95_1.jpeg",
          "https://cdn.discordapp.com/attachments/820309291197923339/820955539668205568/Snapchat-1887337141.jpg",
          "https://cdn.discordapp.com/attachments/820309291197923339/821049806558462043/dora_meme.jpg",
          "https://cdn.discordapp.com/attachments/820309291197923339/822490479865757716/meme_falan_1.png",
          "https://cdn.discordapp.com/attachments/820309291197923339/822491774290493450/bu_bir_meme.png",
          "https://cdn.discordapp.com/attachments/820309291197923339/822493882205995048/Dusunuyorum_oyleyse_insanlar_kolem_olmal.png",
          "https://cdn.discordapp.com/attachments/820309291197923339/823232899121283123/ttttt.gif",
          "https://cdn.discordapp.com/attachments/820309291197923339/825060904324300850/IMG_20210326_203618_720.jpg",
          "https://cdn.discordapp.com/attachments/820309291197923339/824355560447148052/IMG_20210324_214255_974.jpg",
          "https://cdn.discordapp.com/attachments/820309291197923339/824201926647218197/b780ea99e7ae27d13a88e50f651a466d.jpeg",
          "https://cdn.discordapp.com/attachments/820309291197923339/827413576859123722/ReisX_memei.mp4"]


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
@commands.has_role("Kayıtsız")
async def mulakat(ctx):
    if ctx.guild.id == 813756240286580789:
        if ctx.channel.id == 822377447227654195 or ctx.channel.id == 822377521491214377:

            for role in ctx.author.roles:
                if role == discord.utils.get(ctx.guild.roles, name="Susturuldu"):
                    await ctx.message.delete()
                    return
            await ctx.message.delete()

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.lower()

            role = discord.utils.get(ctx.guild.roles, name="Susturuldu")
            member = ctx.author

            inspire = client.get_channel(822381549696581633)

            sorular = ["**1.** Kendini nasıl tanımlarsın?",
                       "**2.** İnsanlarla hayvanların arasındaki en büyük fark nedir?",
                       "**3.** Bir süper güç edinme hakkın var diyelim; bu hakkı kullanır mısın, kullanırsan nasıl ve neden kullanırsın, kullanmazsan neden kullanmazsın?",
                       "**4.** Yaşamınızda şu anda bulunduğunuz noktada olmaktan memnun musunuz, neden?",
                       "**5.** Son 3 hafta içerisinde kendinizi geliştirmek için ne yaptınız?",
                       "**6.** Birini öldürmek zorundasınız ama hiç bir şart ve durum belli değil, nasıl öldürürsünüz?",
                       '**7.** Birisi gelip sana "Bir simülasyondasın. benimle gelirsen gerçekliğe ulaşacaksın." derse ne yaparsın, yaptığın şeyi neden yaparsın?',
                       "**8.** Sinirlendiğinde sakinleşmek için ne yaparsın?",
                       "**9.** Haksızlığa karşı tepkiniz ve tavrınız nasıl olur, bu tepki ve tavrın nedeni nedir?",
                       "**10.** Tütün, alkol ve benzeri maddelerin kullanımı, imalatı ve satışı yasalken eroin, kokain, metamfetamin ve benzeri maddelerin kullanımı, satışı ve imalatı yasadışıdır. Yani bazı uyuşturucular yasak değilken, bazıları yasaktır. Bu durum hakkında yorumunuz nedir?",
                       "**11.** Sizce en çok korkulması gereken şey nedir, neden?"]

            count = 0
            count1 = 0
            for i in sorular:
                count += 1

                await ctx.send(i, delete_after=180)
                try:
                    user_choice = (await client.wait_for('message', check=check, timeout=180))
                except:
                    await ctx.send(f"{ctx.author.mention}, **Soruya zamanında cevap veremdiğin için susturuldun!**",
                                   delete_after=15)
                    await member.add_roles(role)
                    break

                if user_choice.content == f"{prefix}mulakat":
                    await ctx.send(f"{ctx.author.mention}, **Sistemi bozmaya çalıştığın için susturuldun!**",
                                   delete_after=15)
                    await member.add_roles(role)
                    break

                if user_choice.content == user_choice.content:
                    await ctx.send("**Cevabın alındı!**", delete_after=3)
                    await user_choice.delete()

                    if len(user_choice.content) <= 15:
                        count1 += 1

                embed = discord.Embed(title=f"Mülakat| {ctx.author.name + '#' + ctx.author.discriminator}",
                                      color=0xc44cfc)
                embed.add_field(name=f"Soru: {count}", value=f"{i}")
                embed.add_field(name=f"Uyarı bilgisi", value=f"{ctx.author.mention}, uyarı sayısı **{count1}**")
                embed.add_field(name=f'{"-" * 98}', value=f"**Cevap:** {user_choice.content}\n", inline=False)
                embed.set_footer(text="ID: " + str(ctx.author.id))
                await inspire.send(embed=embed)

            await member.add_roles(role)


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

client.run("ODI1MjY1ODg4MjY5MzAzODI5.YF7awA.3w8gRTgtzp3YiNHaudFfpzoVtxU")
