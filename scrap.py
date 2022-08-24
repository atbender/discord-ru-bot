import datetime
from dataclasses import dataclass
from enum import Enum
from typing import List

import requests
from temporalcache import interval


class MealType(Enum):
    LUNCH = "ALMOÇO"
    DINNER = "JANTA"


@dataclass
class Meal:
    meal_type: MealType
    meal_day: datetime.date
    dishes: dict
    has_lactose: bool

    def parse_meals(self, meal_json):
        self.dishes = {}

        for item in meal_json["rows"]:
            if item["refeicao"] != self.meal_type.value:
                continue
            if item["nome"] not in self.dishes:
                self.dishes[item["nome"]] = None
            self.dishes[item["nome"]] = item["descricao"]

            lactose: List[str] = ["leite", "queijo"]
            lactose_items: List[str] = [
                ele for ele in lactose if ele in item["descricao"].lower()
            ]
            self.has_lactose = bool(lactose_items)

        return self.dishes

    def format_meal(self) -> str:
        txt = f"{self.meal_type.value}"
        txt += f" --- {self.meal_day.day}/{self.meal_day.month}/{self.meal_day.year}\n"

        for item, description in self.dishes.items():
            txt += f"\t{item.lower()} \t ||{description.lower()}|| \n"
        txt += "\n\n"
        if self.has_lactose:
            txt += "**Attention: **One or more items may contain lactose elements.\n\n"

        return txt


def get_query_string(date: str) -> str:
    query = (
        f"https://cobalto.ufpel.edu.br/portal/cardapios/cardapioPublico/"
        f"listaCardapios?null&txtData={date}&cmbRestaurante=8&_search=false"
        f"&nd=1656779148361&rows=20&page=1&sidx=refeicao+asc%2C+id&sord=asc"
    )
    return query


@interval(seconds=3600)
def get_menus(meal_date: datetime.date, meal_type: MealType):
    date_formatted: str = f"{meal_date.day}/{meal_date.month}/{meal_date.year}"

    query_string: str = get_query_string(date_formatted)
    meal_json = requests.get(query_string).json()

    message: str

    if "rows" not in meal_json:
        message = "No meals listed today."
        return message

    new_meal: Meal = Meal(meal_type, meal_date, {}, False)
    new_meal.parse_meals(meal_json)
    message = new_meal.format_meal()

    return message
