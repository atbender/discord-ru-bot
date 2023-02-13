import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import List

import requests
from temporalcache import interval


class MealType(Enum):
    LUNCH = "ALMOÇO"
    DINNER = "JANTA"

class Restaurant(Enum):
    ANGLO = 8
    SANTA_CRUZ = 6


@dataclass
class Meal:
    meal_type: MealType
    meal_day: datetime.date
    dishes: dict
    has_lactose: bool

    def check_lactose(self, description):
        lactose: List[str] = ["leite,", "leite.", "queijo"]
        lactose_items: List[str] = [
            ele for ele in lactose if ele in description.lower()
        ]
        if not self.has_lactose:
            self.has_lactose = bool(lactose_items)
        return bool(lactose_items)

    def parse_meals(self, meal_json):
        self.dishes = {}

        for item in meal_json["rows"]:
            if item["refeicao"] != self.meal_type.value:
                continue
            if item["nome"] not in self.dishes:
                self.dishes[item["nome"]] = None

            self.dishes[item["nome"]] = item["descricao"], self.check_lactose(
                item["descricao"]
            )
        return self.dishes

    def format_meal(self) -> str:
        txt = f"{self.meal_type.value}"
        txt += f" --- {self.meal_day.day}/{self.meal_day.month}/{self.meal_day.year}\n"

        for item, description in self.dishes.items():
            if description[1]:
                txt += f"**\t{item.lower()}** \t ||{description[0].lower()}|| \n"
            else:
                txt += f"\t{item.lower()} \t ||{description[0].lower()}|| \n"
        txt += "\n"
        if self.has_lactose:
            txt += "**Attention: **One or more items may contain lactose elements.\n\n"

        return txt


def get_query_string(date: str, restaurant) -> str:
    query = f"https://cobalto.ufpel.edu.br/portal/cardapios/cardapioPublico/listaCardapios?null&txtData={date}&cmbRestaurante={restaurant.value}&_search=false&nd=1676208086850&rows=20&page=1&sidx=refeicao+asc%2C+id&sord=asc"
    return query


@interval(seconds=3600)
def get_menus(meal_type: MealType, meal_date: datetime.date, restaurant):
    logging.warning("Cobalto was requested.")

    date_formatted: str = f"{meal_date.day}/{meal_date.month}/{meal_date.year}"

    query_string: str = get_query_string(date_formatted, restaurant)
    # print("Cobalto was requestedd.")
    meal_json = requests.get(query_string, timeout=3).json()

    # print("Request received.")
    message: str

    if "rows" not in meal_json:
        message = "No meals listed."
        return message

    new_meal: Meal = Meal(meal_type, meal_date, {}, False)
    new_meal.parse_meals(meal_json)
    message = new_meal.format_meal()

    return message
