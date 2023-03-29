import datetime
import json
import os
import time

import requests
import schedule
from colorama import init, Fore

from sets import sets

init(autoreset=True)

"""
    This function is used to get data from torn api. 
    It will keep trying to get data until it gets it.
"""


def get_request(url):
    while True:
        json_info = requests.get(url).json()
        if not json_info.get("error"):
            return json_info
        time.sleep(5)


# Clears console.
def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


with open("setting.json") as json_data:  # loads data from file.
    data = json.load(json_data)

API_key = data.get("API_key")  # Get user API_key.
watch = data.get("watch")  # Get list of items to be watched.

items = get_request(f"https://api.torn.com/torn/?selections=items&key={API_key}").get("items")

for watched in watch:
    if watched.get("name") in sets.keys():
        for set_item in sets[watched.get("name")]:
            watch.append({"name": set_item, "alert_bellow": watched.get("alert_bellow"),
                          "if_amount_bigger": watched.get("if_amount_bigger")})

        watch.remove(watched)

# finds ID to item name and sets alert_bellow if user want's to use x% under market value.
for watched in watch:
    for item in items:
        if watched.get("name") == items.get(item).get("name"):
            watched["id"] = item
            if watched["alert_bellow"] <= 1: watched["alert_bellow"] *= items.get(item).get("market_value")

for watched in watch:
    print(watched)


#
def scan_bazaar():
    cls()
    print("__________Update {}__________".format(datetime.datetime.now().time()))
    for watched in watch:
        data = get_request("https://api.torn.com/market/{}?selections=bazaar,itemmarket&key={}".format(watched["id"], API_key))
        bazaar = data.get("bazaar")
        itemmarket = data.get("itemmarket")
        for item in bazaar[0:3]:
            if item.get("cost") <= watched.get("alert_bellow") and item.get("quantity") >= watched.get("if_amount_bigger"):
                print(f"There is {Fore.RED}{item.get('quantity')} {Fore.BLUE}{watched.get('name')} {Fore.RESET}on bazaar for {Fore.GREEN}${item.get('cost'):,}")
        if itemmarket[0].get("cost") <= watched.get("alert_bellow") and watched.get("if_amount_bigger") == 0:
            print(f"There is {Fore.RED}{itemmarket[0].get('quantity')} {Fore.BLUE}{watched.get('name')} {Fore.RESET}on item market for {Fore.GREEN}${itemmarket[0].get('cost'):,}")

if __name__ == "__main__":
    scan_bazaar()
    schedule.every(31).seconds.do(scan_bazaar)
    while True:
        schedule.run_pending()
        time.sleep(1)
