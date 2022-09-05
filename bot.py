import datetime
import logging
import os
from typing import Optional

import pytz
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from dotenv import load_dotenv

import discord
import scrap

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

timezone = pytz.timezone("Etc/GMT-3")
os.system("mkdir logs")

discord.VoiceClient.warn_nacl = False

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename="logs/users.log",
    filemode="a+",
)


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.event
async def on_ready() -> None:
    print(f"{bot.user.name} has connected to Discord!")


def validate_meal(args) -> scrap.MealType:
    if "dinner" in args:
        return scrap.MealType.DINNER
    return scrap.MealType.LUNCH


def has_digits(string):
    return any(character.isdigit() for character in string)


def check_number(args):
    digits = [element for element in args if has_digits(element)]
    if digits is None:
        return None
    if any(digits):
        return digits[0]
    return None


def validate_day(args) -> datetime.date:
    datetime_timezone: datetime.datetime = datetime.datetime.now(timezone)
    today_date: datetime.date = datetime_timezone.today()

    if args is None:
        return today_date

    if "tomorrow" in args:
        tomorrow_date = today_date + datetime.timedelta(days=1)
        return tomorrow_date

    date = check_number(args)
    if date is None:
        return today_date

    return datetime.datetime.strptime(date, "%d/%m/%Y")


def log_command(ctx):
    log_message: str = (
        f"author:   {ctx.author}\t"
        f"guild:    {ctx.guild}\t"
        f"message:  {ctx.message.content}"
    )
    logging.info(log_message)


def generate_embed(response):
    embed = discord.Embed(
        title="menu!", description=response, color=discord.Color.red()
    )
    return embed


def handle_input(*args):
    datetime_timezone: datetime.datetime = datetime.datetime.now(timezone)
    today_date: datetime.date = datetime_timezone.today()

    if args is None:
        return today_date, scrap.MealType.LUNCH

    args_lower = [element.lower() for element in args]
    meal_type: scrap.MealType = validate_meal(args_lower)

    day_formatted: datetime.date = validate_day(args_lower).date()  # type: ignore

    return meal_type, day_formatted


def is_input_correct(*args):
    try:
        input_formatted = handle_input(*args)
    except ValueError:
        return None
    return input_formatted


@bot.command(name="ru")
async def get_ru_meal(ctx, *args):
    log_command(ctx)

    input_formatted = is_input_correct(*args)
    if input_formatted is None:
        response = "Incorrect data format, should be DD/MM/YYYY"
        await ctx.send(response)
        return

    response = scrap.get_menus(*input_formatted)

    embed = generate_embed(response)

    await ctx.send(embed=embed)


@bot.event
async def on_command_error(ctx, error) -> None:
    if isinstance(error, CommandNotFound):
        embed = discord.Embed(
            title="Error!",
            description="Command not found.",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)
        return
    raise error


bot.run(TOKEN)
