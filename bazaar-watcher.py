import requests
import schedule 
import datetime
import time
import json
import sys
import os
from playsound import playsound
from colorama import init, Fore, Back, Style

init(autoreset=True)

def get_request(url):
    json_info = requests.get(url).json()
    
    while True:
            if json_info.get("error",True):
                break
            time.sleep(5)
            json_info = requests.get(url).json()
    return json_info



def cls(): #Clears console on linux and on windows
    os.system('cls' if os.name=='nt' else 'clear')

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

def scan_bazaar():

    cls()
    print("__________Update {}__________".format(datetime.datetime.now().time()))
    for watched in watch:
        data = get_request("https://api.torn.com/market/{}?selections=bazaar,itemmarket&key={}".format(watched["id"],API_key))
        bazaar = data.get("bazaar")
        itemmarket = data.get("itemmarket")
        for item in bazaar[0:3]: #Going only thru first 3 bazaars since they are the only ones that you can see (and the ones with lowest cost)
            if item.get("cost") <= watched.get("alert_bellow") and item.get("quantity") >= watched.get("if_amount_bigger"): 
                print("There is " + Fore.RED + "{} ".format(item.get("quantity")) + Fore.BLUE + "{} ".format(watched.get("name"))+ Fore.RESET + "on bazaar for " + Fore.GREEN + "${:,}".format(item.get("cost")))
        
        if itemmarket[0].get("cost") <= watched.get("alert_bellow") and watched.get("if_amount_bigger") == 0:
            print("There is " + Fore.RED + "{} ".format(itemmarket[0].get("quantity")) + Fore.BLUE + "{} ".format(watched.get("name"))+ Fore.RESET + "on item market for " + Fore.GREEN + "${:,}".format(itemmarket[0].get("cost")))

    pass



schedule.every(31).seconds.do(scan_bazaar)
schedule.run_all()

while 1:
    schedule.run_pending()
    time.sleep(1)