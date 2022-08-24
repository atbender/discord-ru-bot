# bot.py
import datetime
import os

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


@bot.command(name="ru-meal")
async def get_ru_meal(ctx, meal=None, day=None):
    day_formatted: datetime.date
    meal_type: scrap.MealType

    if not day:
        day_formatted = datetime.date.today()
    elif day == "tomorrow":
        day_formatted = datetime.date.today() + datetime.timedelta(days=1)
    else:
        try:
            day_formatted = datetime.datetime.strptime(day, "%d/%m/%Y")
        except ValueError:
            response = "Incorrect data format, should be DD/MM/YYYY"
            await ctx.send(response)
            return

    meal_type = scrap.MealType.LUNCH
    if not meal:
        meal_type = scrap.MealType.LUNCH
    elif meal.lower() not in ("lunch", "dinner"):
        meal_type = scrap.MealType.LUNCH

    if meal == "dinner":
        meal_type = scrap.MealType.DINNER

    response = scrap.get_menus(day_formatted, meal_type)
    await ctx.send(response)


bot.run(TOKEN)
