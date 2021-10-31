import requests
import json
import sys
from colorama import init, Fore, Back, Style

init(autoreset=True)

def get_request(url):
    json_info = requests.get(url).json()
    
    while True:
            if json_info.get("error") == None:
                break
            time.sleep(5)
            json_info = requests.get(url).json()
    return json_info


with open("setting.json") as json_data: #loads data from file.
    data = json.load(json_data)


API_key = data.get("API_key") #Get user API_key.
watch = data.get("watch") #Get list of items to be watched. 

items = get_request("https://api.torn.com/torn/?selections=items&key={}".format(API_key)).get("items")

#finds Id to item name and sets alert_bellow if user want's to use x% under market value.  
for watched in watch:
    for item in items:
       if watched.get("name") == items.get(item).get("name"):
           watched["id"] = item
           if watched["alert_bellow"] <= 1: watched["alert_bellow"] *= items.get(item).get("market_value")

def scan_bazar():

    for watched in watch:
        data = get_request("https://api.torn.com/market/{}?selections=bazaar,itemmarket&key={}".format(watched["id"],API_key))
        bazaar = data.get("bazaar")
        itemmarket = data.get("itemmarket")
        for item in bazaar[0:3]: #Going only thru first 3 bazaars since they are the only ones that you can see (and the ones with lowest cost)
            if item.get("cost") <= watched.get("alert_bellow") and item.get("quantity") >= watched.get("if_amount_bigger"): 
                print("There is " + Fore.RED + "{} ".format(item.get("quantity")) + Fore.BLUE + "{} ".format(watched.get("name"))+ Fore.RESET + "for " + Fore.GREEN + "${:,}".format(item.get("cost")))


    pass

scan_bazar()