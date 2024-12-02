import asyncio

import discord
from discord import app_commands
from env import TOKEN
import logging

from time_manager import read_time_left, write_time_left
from mathproblems import generate_problem_answer

log_handler = logging.StreamHandler()

OPUS_LIBS = [
    "/usr/local/lib/libopus.0.dylib",
    "libopus.so.0",
    "libopus.0.dylib",
]


def load_opus_lib(opus_libs=OPUS_LIBS):
    if discord.opus.is_loaded():
        return True

    for opus_lib in opus_libs:
        try:
            discord.opus.load_opus(opus_lib)
            return
        except OSError:
            pass

        raise RuntimeError(
            "Could not load an opus lib. Tried %s" % (", ".join(opus_libs))
        )


load_opus_lib()

intents = discord.Intents.default()
intents.voice_states, intents.guild_messages, intents.guilds = True, True, True
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

DEBUG = True
USER = 341638922809507841 if DEBUG else 547114856252178433
CHANNEL = 1312364194582233132 if DEBUG else 1253267777830260858
SERVER = 1312364194036715560 if DEBUG else 1205191226354303056

is_connected: bool = False


async def time_check():
    guild = client.get_guild(SERVER)
    member = guild.get_member(USER)

    while True:
        global is_connected
        time_left = read_time_left()
        if is_connected:
            if time_left <= 0:
                if not member.voice.mute:
                    await member.send(
                        embed=discord.Embed(
                            title="Time is up!",
                            description="Run `/givemetime` in the ICT Auditorium to get more time to speak.",
                        )
                    )
                    await member.edit(mute=True)
            else:
                if member.voice.mute:
                    await member.edit(mute=False)
                time_left -= 1
                write_time_left(time_left)

        await asyncio.sleep(1)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}!")
    await tree.sync(guild=discord.Object(id=SERVER))
    global is_connected
    channel = client.get_channel(CHANNEL)
    for member in channel.members:
        if member.id == USER:
            is_connected = True
            break
    client.loop.create_task(time_check())


@client.event
async def on_voice_state_update(member, before, after):
    if member.id == USER:
        global is_connected
        if before.channel is None and after.channel is not None:
            is_connected = True
        elif before.channel is not None and after.channel is None:
            is_connected = False


@tree.command(
    name="givemetime",
    description="Solve a maths problem, and get more speaking time!",
    guild=discord.Object(id=SERVER),
)
async def givemetime(interaction):
    view = discord.ui.View()

    async def button_callback(interaction: discord.Interaction):
        data = interaction.data
        difficulty = data["custom_id"]

        if difficulty == "easy":
            timeToAdd = 10
        elif difficulty == "medium":
            timeToAdd = 20
        elif difficulty == "hard":
            timeToAdd = 30
        elif difficulty == "impossible":
            timeToAdd = 60
        else:
            return

        question, answer = generate_problem_answer(difficulty)
        answer = round(answer, 2)

        timeouts = {
            "easy": 10,
            "medium": 60 * 10,
            "hard": 60 * 15,
            "impossible": 100000000,
        }

        import datetime

        # from seconds to HH:MM:SS
        formatted_time = datetime.datetime.strftime(
            datetime.datetime.utcfromtimestamp(timeouts[difficulty]), "%H:%M:%S"
        )

        embed = discord.Embed(title="Solve this problem to get more time!")
        embed.set_image(url=question)
        embed.set_thumbnail(
            url="https://scontent.xx.fbcdn.net/v/t1.15752-9/462579919_874269258162528_8710530634644707577_n.jpg?_nc_cat=100&ccb=1-7&_nc_sid=0024fc&_nc_ohc=3GHVadbZ5u4Q7kNvgGYbeln&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent.xx&oh=03_Q7cD1QG18wr_Ms2nhXMLwGiDSXUW1iSgh9yee-wAhz9xISvnGw&oe=677454C4"
        )
        embed.set_footer(
            text=f"You have {formatted_time} to solve this problem. Type your answer in the chat, rounded to 2 decimal places."
        )

        logging.info(
            f"User {interaction.user} requested a problem of difficulty {difficulty} with answer {answer}"
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        try:
            message = await client.wait_for(
                "message", check=check, timeout=timeouts[difficulty]
            )
        except asyncio.TimeoutError:
            await interaction.followup.send(
                "You took too long to answer the question.\n Better luck next time 😋",
                ephemeral=True,
            )
            return

        try:
            provided_answer = float(message.content)
        except ValueError:
            await interaction.followup.send(
                "MElA MA TAFX TIKTEB NUMRU, MELA NUMRU, MELA NUMRU! 😡",
            )
            return

        print(answer)

        if provided_answer == answer and not message.author.bot and not answer is None:
            time_left = read_time_left()
            time_left += timeToAdd
            write_time_left(time_left)

            await interaction.followup.send(
                f"Welcome to the team AYYY. You now have {time_left} seconds before you're muted. *Again.*\nType `/givemetime` to get more time.",
            )

            voice_channel = interaction.user.voice.channel

            vclient = await voice_channel.connect()

            vclient.play(discord.FFmpegPCMAudio("assets/wlcm.m4a"))

            while vclient.is_playing():
                await asyncio.sleep(1)

            await vclient.disconnect()

        else:
            await interaction.followup.send(
                interaction.user.mention
                + " what the fuck ah, you should know this 🤫🧏"
            )

            voice_channel = interaction.user.voice.channel
            vclient = await voice_channel.connect()
            vclient.play(
                discord.FFmpegPCMAudio("assets/shldknowthis.m4a"),
            )

            while vclient.is_playing():
                await asyncio.sleep(1)

            await vclient.disconnect()

    for difficulty, colour in [
        ("easy", discord.ButtonStyle.green),
        ("medium", discord.ButtonStyle.blurple),
        ("hard", discord.ButtonStyle.red),
        ("impossible", discord.ButtonStyle.secondary),
    ]:
        button = discord.ui.Button(label=difficulty.capitalize())
        button.custom_id = difficulty
        button.style = colour
        button.callback = button_callback
        view.add_item(button)

    await interaction.response.send_message(
        "Choose a difficulty: \n\n", view=view, ephemeral=True
    )


client.run(TOKEN, log_handler=log_handler)
