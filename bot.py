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
# GUILD = os.getenv("DISCORD_GUILD")

timezone = pytz.timezone("Etc/GMT-3")

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename="logs/users.log",
    filemode="a+",
)


bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())


@bot.event
async def on_ready() -> None:
    print(f"{bot.user.name} has connected to Discord!")


def validate_meal(meal: Optional[str]) -> scrap.MealType:
    if meal is None:
        return scrap.MealType.LUNCH
    if meal.lower not in ("lunch", "dinner"):
        return scrap.MealType.LUNCH
    return scrap.MealType.LUNCH if meal.lower() == "lunch" else scrap.MealType.DINNER


def validate_day(day: Optional[str]) -> datetime.date:
    datetime_timezone: datetime.datetime = datetime.datetime.now(timezone)
    today_date: datetime.date = datetime_timezone.today()

    if day is None:
        return today_date

    if day == "tomorrow":
        return today_date + datetime.timedelta(days=1)

    return datetime.datetime.strptime(day, "%d/%m/%Y")


@bot.command(name="ru")
async def get_ru_meal(ctx, day=None, meal=None):

    logging.info(
        f"author: {ctx.author}\t guild: {ctx.guild}\t message: {ctx.message.content}"
    )

    meal_type: scrap.MealType = validate_meal(meal)

    try:
        day_formatted: datetime.date = validate_day(day)
    except ValueError:
        response = "Incorrect data format, should be DD/MM/YYYY"
        await ctx.send(response)
        return

    response = scrap.get_menus(day_formatted, meal_type)
    await ctx.send(response)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        em = discord.Embed(
            title=f"Error!!!", description=f"Command not found.", color=ctx.author.color
        )
        await ctx.send(embed=em)
        return
    raise error


bot.run(TOKEN)
