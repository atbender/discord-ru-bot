# bot.py
import datetime
import os
from typing import Optional

import discord
from discord.ext import commands
from dotenv import load_dotenv

import scrap

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())


@bot.event
async def on_ready() -> None:
    print(f"{bot.user.name} has connected to Discord!")


@bot.command(name="ru")
async def get_ru(ctx):
    day_formatted = datetime.date.today()
    meal_type = scrap.MealType.LUNCH
    response = scrap.get_menus(day_formatted, meal_type)
    await ctx.send(response)


@bot.command(name="ru-tomorrow")
async def get_ru_tomorrow(ctx):
    day_formatted = datetime.date.today() + datetime.timedelta(days=1)
    meal_type = scrap.MealType.LUNCH
    response = scrap.get_menus(day_formatted, meal_type)
    await ctx.send(response)


def validate_meal(meal: Optional[str]) -> scrap.MealType:
    if not meal:
        return scrap.MealType.LUNCH
    if meal.lower not in ("lunch", "dinner"):
        return scrap.MealType.LUNCH
    return scrap.MealType.LUNCH if meal.lower() == "lunch" else scrap.MealType.DINNER


def validate_day(day: Optional[str]) -> datetime.date:
    if not day:
        return datetime.date.today()
    if day == "tomorrow":
        return datetime.date.today() + datetime.timedelta(days=1)

    return datetime.datetime.strptime(day, "%d/%m/%Y")


@bot.command(name="ru-meal")
async def get_ru_meal(ctx, meal=None, day=None):

    meal_type: scrap.MealType = validate_meal(meal)

    try:
        day_formatted: datetime.date = validate_day(day)
    except ValueError:
        response = "Incorrect data format, should be DD/MM/YYYY"
        await ctx.send(response)
        return

    response = scrap.get_menus(day_formatted, meal_type)
    await ctx.send(response)


bot.run(TOKEN)
