import zipfile
import io
import traceback

from foundry_api.standard_library import *

# import required modules for time
from datetime import datetime, timezone, timedelta

timezone_offset = +2.0 
tzinfo = timezone(timedelta(hours=timezone_offset))

# import required modules for API request
import requests, json

# Enter your KNMI API key here
api_key = "knmi_api_key" # Create an account and put the API key here
# base_url variable to store url
base_url = "https://weerlive.nl/api/weerlive_api_v2.php?"
# Give city location in latitude and longitude
lat =  "52.0355505"
lon = "4.3480274"

# complete_url variable to store
# complete url address
complete_url = base_url + "key=" + api_key + "&locatie=" + lat + "," + lon
print(complete_url)

# buienradar: https://gadgets.buienradar.nl/data/raintext/?lat=52.03&lon=4.34

# Neerslagintensiteit = 10^((waarde-109)/32)

# Ter controle: een waarde van 77 is gelijk aan een neerslagintensiteit van 0,1 mm/u. 

# 112|09:45
# 120|09:50
# 122|09:55
# 116|10:00
# 112|10:05
# 112|10:10
# 096|10:15
# 087|10:20
# 000|10:25
# 000|10:30
# 000|10:35
# 000|10:40
# 000|10:45
# 000|10:50
# 000|10:55
# 000|11:00
# 000|11:05
# 000|11:10
# 000|11:15
# 000|11:20
# 000|11:25
# 000|11:30
# 000|11:35
# 000|11:40


def fetchdata():
    global image
    global locatie
    global timeknmi
    global temp
    global samenv
    global verw
    global windr
    global windkmh
    global alarm
    global lkop
    global ltekst

    # get method of requests module
    # return response object
    response = requests.get(complete_url)
    
    if response.ok:
        # json method of response object
        # convert json format data into python format data
        data = response.json()
        print (data)
    else:
        print('Invalid request')

    # insert dummy data
    # json_data = '{"liveweer": [{"image": "halfbewolkt_regen", "plaats": "Rijswijk", "timestamp": 1721546885, "time": "21-07-2024 09:28:05", "temp": 18.9, "gtemp": 16.9, "samenv": "Regen", "lv": 92, "windr": "W", "windrgr": 270.2, "windms": 3.87, "windbft": 3, "windknp": 7.5, "windkmh": 13.9, "luchtd": 1007.27, "ldmmhg": 756, "dauwp": 17.7, "zicht": 4650, "gr": 27, "verw": "Eerst nog enkele (onweers)buien, vanaf vanavond droog", "sup": "05:47", "sunder": "21:50", "alarm": 0, "lkop": "Er zijn geen waarschuwingen", "ltekst": " Er zijn momenteel geen waarschuwingen van kracht.", "wrschklr": "groen", "wrsch_g": "-", "wrsch_gts": 0, "wrsch_gc": "-"}], "wk_verw": [{"dag": "21-07-2024", "image": "halfbewolkt", "max_temp": 23, "min_temp": 17, "windbft": 3, "windkmh": 14, "windknp": 8, "windms": 4, "windrgr": 310, "windr": "NW", "neersl_perc_dag": 60, "zond_perc_dag": 78}, {"dag": "22-07-2024", "image": "halfbewolkt", "max_temp": 21, "min_temp": 15, "windbft": 3, "windkmh": 14, "windknp": 8, "windms": 4, "windrgr": 289, "windr": "W", "neersl_perc_dag": 30, "zond_perc_dag": 77}, {"dag": "23-07-2024", "image": "regen", "max_temp": 21, "min_temp": 16, "windbft": 3, "windkmh": 14, "windknp": 8, "windms": 4, "windrgr": 283, "windr": "W", "neersl_perc_dag": 80, "zond_perc_dag": 70}, {"dag": "24-07-2024", "image": "halfbewolkt", "max_temp": 18, "min_temp": 14, "windbft": 3, "windkmh": 18, "windknp": 10, "windms": 5, "windrgr": 298, "windr": "W", "neersl_perc_dag": 50, "zond_perc_dag": 74}, {"dag": "25-07-2024", "image": "halfbewolkt", "max_temp": 21, "min_temp": 13, "windbft": 3, "windkmh": 14, "windknp": 8, "windms": 4, "windrgr": 291, "windr": "W", "neersl_perc_dag": 0, "zond_perc_dag": 68}], "uur_verw": [{"uur": "21-07-2024 10:00", "timestamp": 1721548800, "image": "halfbewolkt", "temp": 22, "windbft": 2, "windkmh": 10, "windknp": 6, "windms": 3, "windrgr": 296, "windr": "W", "neersl": 0, "gr": 579}, {"uur": "21-07-2024 11:00", "timestamp": 1721552400, "image": "bewolkt", "temp": 24, "windbft": 2, "windkmh": 10, "windknp": 6, "windms": 3, "windrgr": 298, "windr": "W", "neersl": 0, "gr": 662}, {"uur": "21-07-2024 12:00", "timestamp": 1721556000, "image": "zonnig", "temp": 25, "windbft": 3, "windkmh": 14, "windknp": 8, "windms": 4, "windrgr": 304, "windr": "NW", "neersl": 0, "gr": 620}, {"uur": "21-07-2024 13:00", "timestamp": 1721559600, "image": "zonnig", "temp": 25, "windbft": 3, "windkmh": 14, "windknp": 8, "windms": 4, "windrgr": 302, "windr": "W", "neersl": 0, "gr": 814}, {"uur": "21-07-2024 14:00", "timestamp": 1721563200, "image": "lichtbewolkt", "temp": 25, "windbft": 3, "windkmh": 18, "windknp": 10, "windms": 5, "windrgr": 301, "windr": "W", "neersl": 0, "gr": 781}, {"uur": "21-07-2024 15:00", "timestamp": 1721566800, "image": "zonnig", "temp": 25, "windbft": 3, "windkmh": 14, "windknp": 8, "windms": 4, "windrgr": 300, "windr": "W", "neersl": 0, "gr": 737}, {"uur": "21-07-2024 16:00", "timestamp": 1721570400, "image": "lichtbewolkt", "temp": 24, "windbft": 3, "windkmh": 18, "windknp": 10, "windms": 5, "windrgr": 301, "windr": "W", "neersl": 0, "gr": 662}, {"uur": "21-07-2024 17:00", "timestamp": 1721574000, "image": "zonnig", "temp": 24, "windbft": 3, "windkmh": 14, "windknp": 8, "windms": 4, "windrgr": 308, "windr": "NW", "neersl": 0, "gr": 476}, {"uur": "21-07-2024 18:00", "timestamp": 1721577600, "image": "halfbewolkt", "temp": 23, "windbft": 3, "windkmh": 18, "windknp": 10, "windms": 5, "windrgr": 313, "windr": "NW", "neersl": 0, "gr": 391}, {"uur": "21-07-2024 19:00", "timestamp": 1721581200, "image": "wolkennacht", "temp": 22, "windbft": 3, "windkmh": 14, "windknp": 8, "windms": 4, "windrgr": 328, "windr": "NW", "neersl": 0, "gr": 216}, {"uur": "21-07-2024 20:00", "timestamp": 1721584800, "image": "halfbewolkt", "temp": 21, "windbft": 3, "windkmh": 14, "windknp": 8, "windms": 4, "windrgr": 333, "windr": "NW", "neersl": 0, "gr": 86}, {"uur": "21-07-2024 21:00", "timestamp": 1721588400, "image": "halfbewolkt", "temp": 20, "windbft": 2, "windkmh": 10, "windknp": 6, "windms": 3, "windrgr": 328, "windr": "NW", "neersl": 0, "gr": 14}, {"uur": "21-07-2024 22:00", "timestamp": 1721592000, "image": "nachtbewolkt", "temp": 19, "windbft": 2, "windkmh": 10, "windknp": 6, "windms": 3, "windrgr": 314, "windr": "NW", "neersl": 0, "gr": 0}, {"uur": "21-07-2024 23:00", "timestamp": 1721595600, "image": "nachtbewolkt", "temp": 19, "windbft": 2, "windkmh": 10, "windknp": 6, "windms": 3, "windrgr": 301, "windr": "W", "neersl": 0, "gr": 0}, {"uur": "22-07-2024 00:00", "timestamp": 1721599200, "image": "nachtbewolkt", "temp": 19, "windbft": 2, "windkmh": 10, "windknp": 6, "windms": 3, "windrgr": 297, "windr": "W", "neersl": 0, "gr": 0}, {"uur": "22-07-2024 01:00", "timestamp": 1721602800, "image": "helderenacht", "temp": 18, "windbft": 2, "windkmh": 10, "windknp": 6, "windms": 3, "windrgr": 299, "windr": "W", "neersl": 0, "gr": 0}, {"uur": "22-07-2024 02:00", "timestamp": 1721606400, "image": "helderenacht", "temp": 18, "windbft": 2, "windkmh": 7, "windknp": 4, "windms": 2, "windrgr": 301, "windr": "W", "neersl": 0, "gr": 0}, {"uur": "22-07-2024 03:00", "timestamp": 1721610000, "image": "helderenacht", "temp": 17, "windbft": 2, "windkmh": 7, "windknp": 4, "windms": 2, "windrgr": 310, "windr": "NW", "neersl": 0, "gr": 0}, {"uur": "22-07-2024 04:00", "timestamp": 1721613600, "image": "helderenacht", "temp": 17, "windbft": 2, "windkmh": 7, "windknp": 4, "windms": 2, "windrgr": 297, "windr": "W", "neersl": 0, "gr": 0}, {"uur": "22-07-2024 05:00", "timestamp": 1721617200, "image": "helderenacht", "temp": 16, "windbft": 2, "windkmh": 7, "windknp": 4, "windms": 2, "windrgr": 279, "windr": "W", "neersl": 0, "gr": 0}, {"uur": "22-07-2024 06:00", "timestamp": 1721620800, "image": "zonnig", "temp": 16, "windbft": 2, "windkmh": 7, "windknp": 4, "windms": 2, "windrgr": 272, "windr": "W", "neersl": 0, "gr": 47}, {"uur": "22-07-2024 07:00", "timestamp": 1721624400, "image": "zonnig", "temp": 17, "windbft": 2, "windkmh": 7, "windknp": 4, "windms": 2, "windrgr": 282, "windr": "W", "neersl": 0, "gr": 166}, {"uur": "22-07-2024 08:00", "timestamp": 1721628000, "image": "zonnig", "temp": 18, "windbft": 2, "windkmh": 7, "windknp": 4, "windms": 2, "windrgr": 286, "windr": "W", "neersl": 0, "gr": 316}, {"uur": "22-07-2024 09:00", "timestamp": 1721631600, "image": "halfbewolkt", "temp": 19, "windbft": 2, "windkmh": 7, "windknp": 4, "windms": 2, "windrgr": 276, "windr": "W", "neersl": 0, "gr": 457}], "api": [{"bron": "Bron: Weerdata KNMI/NOAA via Weerlive.nl", "max_verz": 300, "rest_verz": 296}]}'
    # data = json.loads(json_data) 

    for item in data.get("liveweer"):
        image = item["image"]
        locatie = item["plaats"]
        timeknmi = item["time"]
        samenv = item["samenv"]
        verw = item["verw"]
        windr = item["windr"]
        windkmh = item["windkmh"]
        temp = item["temp"]
        alarm = item["alarm"]
        lkop = item["lkop"]
        ltekst = item["ltekst"]
    
def show_weather_icon():
    # Predefined colors

    D = 0x5A5A5A # dark grey
    G = grey
    w = white
    r = red
    o = orange
    y = yellow
    g = green
    c = cyan
    b = blue
    m = magenta
    p = pink
    P = purple
    
    icon_sun = [ [0,0,y,0,0,y,0,0], [0,0,0,0,0,0,0,0], [y,0,y,y,y,y,0,y], [0,0,y,y,y,y,0,0], [0,0,y,y,y,y,0,0], [y,0,y,y,y,y,0,y], [0,0,0,0,0,0,0,0], [0,0,y,0,0,y,0,0] ]
    icon_thunder = [ [0,0,0,D,D,D,0,0], [0,0,D,G,y,G,D,0], [0,D,G,y,G,G,G,D], [D,G,y,G,G,G,G,D], [0,D,y,y,y,D,D,0], [0,0,0,0,y,0,0,0], [0,0,0,y,0,0,0,0], [0,0,y,0,0,0,0,0] ]
    icon_rain = [ [0,0,b,0,0,b,0,0], [b,0,0,b,0,0,b,0], [0,b,0,0,b,0,0,b], [0,0,b,0,0,b,0,0], [b,0,0,b,0,0,b,0], [0,b,0,0,b,0,0,b], [0,0,b,0,0,b,0,0], [b,0,0,b,0,0,b,0] ]
    icon_rainshowers = [ [0,0,0,0,0,b,0,0], [0,0,0,0,0,0,b,0], [b,0,0,0,0,0,0,b], [0,b,0,0,0,b,0,0], [0,0,b,0,0,0,b,0], [b,0,0,0,0,0,0,b], [0,b,0,0,0,0,0,0], [0,0,0,0,0,0,0,0] ]
    icon_hail = [ [0,0,0,G,G,G,0,0], [0,0,G,w,w,w,G,0], [0,G,w,w,w,w,w,G], [G,w,w,w,w,w,w,G], [0,G,G,G,G,G,G,0], [0,0,0,0,0,0,0,0], [0,0,w,0,0,w,0,0], [0,0,0,w,0,0,w,0] ]
    icon_fog = [ [0,0,0,0,0,0,0,0], [0,w,w,w,0,0,0,0], [0,0,0,0,0,0,0,0], [w,w,0,w,w,w,w,0], [0,0,0,0,0,0,0,0], [w,w,w,w,0,w,w,w], [0,0,0,0,0,0,0,0], [0,0,w,w,w,w,0,0] ]
    icon_clouds = [ [0,0,G,G,G,0,0,0], [0,G,w,w,w,G,0,0], [G,w,w,w,G,G,G,0], [G,w,w,G,w,w,w,G], [w,w,w,w,G,G,w,w], [w,w,G,G,w,w,G,G], [w,G,w,w,w,w,w,w], [G,w,w,w,w,w,w,w ] ]
    icon_clear_day = [ [0,0,y,0,0,y,0,0], [0,0,0,0,0,0,0,0], [y,0,y,y,y,y,0,y], [0,0,y,y,y,y,0,0], [0,0,y,y,y,y,0,0], [y,0,y,y,y,y,0,y], [0,0,0,0,0,0,0,0], [0,0,y,0,0,y,0,0] ]
    icon_light_clouds = [ [0,0,o,o,o,0,0,0], [0,o,y,y,y,o,0,0], [o,y,y,y,G,G,G,0], [o,y,y,G,w,w,w,G], [o,y,y,G,w,w,w,w], [0,o,G,w,w,w,w,w], [0,G,w,w,w,w,w,w], [G,w,w,w,w,w,w,w] ]
    icon_half_clouds = [ [0,0,0,G,G,G,0,0], [0,0,G,w,w,w,G,0], [0,G,w,w,w,w,w,G], [G,w,w,w,w,w,w,G], [0,G,G,G,G,G,G,0], [0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0] ]
    icon_half_clouds_rain = [ [0,0,0,G,G,G,0,0], [0,0,G,w,w,w,G,0], [0,G,w,w,w,w,w,G], [G,w,w,w,w,w,w,G], [0,G,G,G,G,G,G,0], [0,b,0,0,b,0,0,b], [0,0,b,0,0,b,0,0], [b,0,0,b,0,0,b,0] ]
    icon_heavy_clouds = [ [0,0,D,D,D,0,0,0], [0,D,G,G,G,D,0,0], [D,G,G,G,D,D,D,0], [D,G,G,D,G,G,G,D], [G,G,G,G,D,D,G,G], [G,G,D,D,G,G,D,D], [G,D,G,G,G,G,G,G], [D,G,G,G,G,G,G,G] ]
    icon_night_fog = [ [0,0,0,y,y,0,0,0], [0,w,w,w,0,0,0,0], [0,y,y,0,0,0,0,0], [w,w,y,w,w,w,w,0], [0,y,y,0,0,0,0,0], [w,w,w,w,0,w,w,w], [0,0,0,y,y,0,0,0], [0,0,w,w,w,w,0,0] ]
    icon_moon = [ [0,0,0,0,y,y,0,0], [0,0,0,y,y,0,0,0], [0,0,y,y,0,0,0,0], [0,0,y,y,0,0,0,0], [0,0,y,y,0,0,0,0], [0,0,0,y,y,0,0,0], [0,0,0,0,y,y,0,0], [0,0,0,0,0,0,0,0] ]
    icon_night_cloud = [ [0,0,0,y,y,0,0,0], [0,0,y,y,0,0,0,0], [0,y,y,0,G,G,G,0], [0,y,y,G,w,w,w,G], [0,y,y,G,w,w,w,w], [0,0,G,w,w,w,w,w], [0,G,w,w,w,w,w,w], [G,w,w,w,w,w,w,w] ]
    icon_snow = [ [0,0,0,w,0,0,0,0], [0,0,w,w,w,0,0,0], [0,0,0,w,0,0,w,0], [0,w,0,w,w,w,w,w], [w,w,w,w,w,0,w,0], [0,w,0,0,w,0,0,0], [0,0,0,w,w,w,0,0], [0,0,0,0,w,0,0,0] ]
    icon_question_mark = [ [0,r,r,r,r,r,r,0], [r,r,r,r,r,r,r,r], [r,r,0,0,0,0,r,r], [0,0,0,0,0,0,r,r], [0,0,0,r,r,r,r,0], [0,0,0,r,r,0,0,0], [0,0,0,0,0,0,0,0], [0,0,0,r,r,0,0,0] ]
    
    weather_icon = image
    
    if weather_icon == "zonnig": icon = icon_sun
    elif weather_icon == "bliksem": icon = icon_thunder
    elif weather_icon == "regen": icon = icon_rain
    elif weather_icon == "buien": icon = icon_rainshowers
    elif weather_icon == "hagel": icon = icon_hail
    elif weather_icon == "mist": icon = icon_fog
    elif weather_icon == "bewolkt": icon = icon_clouds
    elif weather_icon == "lichtbewolkt": icon = icon_light_clouds
    elif weather_icon == "halfbewolkt": icon = icon_half_clouds
    elif weather_icon == "halfbewolkt_regen": icon = icon_half_clouds_rain
    elif weather_icon == "zwaarbewolkt": icon = icon_heavy_clouds
    elif weather_icon == "nachtmist": icon = icon_night_fog
    elif weather_icon == "helderenacht": icon = icon_moon
    elif weather_icon == "nachtbewolkt": icon = icon_night_cloud
    elif weather_icon == "sneeuw": icon = icon_snow
    
    else: icon = icon_question_mark

    display.set_panel("top", icon)


def displaydata():
    display.set_all(black)
    
    show_weather_icon()
    
    if alarm > 0:
        for frequency in range(500, 2000, 100):
            speaker.tone(frequency, 0.01)
        speaker.say("Weather alert for {0}".format(locatie))
        display.scroll_text(locatie + ": " + lkop + " " + ltekst, red)

    display.scroll_text(samenv, yellow)
    # display.scroll_text(timeknmi + " ", orange)
    # display.scroll_text(str(temp) + " graden", yellow)
    display.scroll_text(windr + " " + str(windkmh) + " km/h", purple)
    display.scroll_text(verw, yellow)
    # Scroll the time across the cube.
    time_text = datetime.now(tzinfo).strftime("%H:%M")
    display.scroll_text(time_text, green)
    


show_rain = True
show_full_msg = False
refresh_rate = 60
display.set_all(black)

try:
    while True:
        if buttons.top_pressed:
            show_full_msg = not show_full_msg
        if buttons.middle_pressed:
            show_rain = not show_rain
            
        fetchdata()
        displaydata()
        
        time.sleep(refresh_rate)
        
except Exception:
    print(traceback.format_exc())
    screen.draw_rectangle(0, 0, 320, 240, black)
    screen.write_text(0, 0, traceback.format_exc(), 1, black, white)
