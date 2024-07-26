import traceback

from foundry_api.standard_library import *

# import required modules for time
from datetime import datetime, timezone, timedelta

timezone_offset = +2.0
tzinfo = timezone(timedelta(hours=timezone_offset))

# import required modules for API request
import requests, json

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

# Enter your KNMI API key here
api_key = "knmi_api_key" # Create an account and put the API key here
weerlive_url = "https://weerlive.nl/api/weerlive_api_v2.php?"

# buienradar: https://gadgets.buienradar.nl/data/raintext/?lat=52.03&lon=4.34
buienradar_url = "https://gadgets.buienradar.nl/data/raintext/?"

# Give city location in latitude and longitude
lat =  "52.0355505"
lon = "4.3480274"

# complete url addresses
complete_weerlive_url = weerlive_url + "key=" + api_key + "&locatie=" + lat + "," + lon
complete_buienradar_url = buienradar_url + "lat=" + lat + "&lon=" + lon

# print(complete_weerlive_url)
# print(complete_buienradar_url)

# digits are defined as bits on in a 3x5 grid, 0,0 =bottomleft
digitAll = [ (0,0), (0,1), (0,2), (1,0), (1,1), (1,2), (2,0), (2,1), (2,2), (3,0), (3,1), (3,2), (4,0), (4,1), (4,2)]
digit =   [[ (0,0), (0,1), (0,2), (1,0),        (1,2), (2,0),        (2,2), (3,0),        (3,2), (4,0), (4,1), (4,2)],
           [        (0,1),               (1,1),               (2,1),               (3,1),               (4,1)       ],
           [ (0,0), (0,1), (0,2), (1,0),               (2,0), (2,1), (2,2),               (3,2), (4,0), (4,1), (4,2)],
           [ (0,0), (0,1), (0,2),               (1,2), (2,0), (2,1), (2,2),               (3,2), (4,0), (4,1), (4,2)],
           [               (0,2),               (1,2), (2,0), (2,1), (2,2), (3,0),        (3,2), (4,0),        (4,2)],
           [ (0,0), (0,1), (0,2),               (1,2), (2,0), (2,1), (2,2), (3,0),               (4,0), (4,1), (4,2)],
           [ (0,0), (0,1), (0,2), (1,0),        (1,2), (2,0), (2,1), (2,2), (3,0),               (4,0)              ],
           [               (0,2),               (1,2),               (2,2),               (3,2), (4,0), (4,1), (4,2)],
           [ (0,0), (0,1), (0,2), (1,0),        (1,2), (2,0), (2,1), (2,2), (3,0),        (3,2), (4,0), (4,1), (4,2)],
           [               (0,2),               (1,2), (2,0), (2,1), (2,2), (3,0),        (3,2), (4,0), (4,1), (4,2)]]
# x and y from bottom left
leftOnesLeds = [[(4,1),(5,1),(6,1)],[(4,2),(5,2),(6,2)],[(4,3),(5,3),(6,3)],[(4,4),(5,4),(6,4)],[(4,5),(5,5),(6,5)]]
leftTensLeds = [[(0,1),(1,1),(2,1)],[(0,2),(1,2),(2,2)],[(0,3),(1,3),(2,3)],[(0,4),(1,4),(2,4)],[(0,5),(1,5),(2,5)]]
# z and y from bottom left
rightOnesLeds = [[(2,1),(1,1),(0,1)],[(2,2),(1,2),(0,2)],[(2,3),(1,3),(0,3)],[(2,4),(1,4),(0,4)],[(2,5),(1,5),(0,5)]]
rightTensLeds = [[(6,1),(5,1),(4,1)],[(6,2),(5,2),(4,2)],[(6,3),(5,3),(4,3)],[(6,4),(5,4),(4,4)],[(6,5),(5,5),(4,5)]]

def clear_left(all_leds, background_color):
    for x in range(9):
        for y in range(9):
            all_leds[(x,y,8)] = background_color

def clear_right(all_leds, background_color):
    for y in range(9):
        for z in range(9):
            all_leds[(8,y,z)] = background_color

def set_left(all_leds, value_leds, value_color, background_color, clear=False):
    if clear:
        clear_left(all_leds, background_color)
    for v in value_leds:
        all_leds[(v[0],v[1],v[2])] = value_color

def set_right(all_leds, value_leds, value_color, background_color, clear=False):
    if clear:
        clear_right(all_leds, background_color)
    for v in value_leds:
        all_leds[(v[0],v[1],v[2])] = value_color

def clear_digits(all_leds, side, background):
    if side == 'right':
        clear_right(all_leds, background)
    else:
        clear_left(all_leds, background)

def set_digits(all_leds, side, total, color, background, float_temp=0, show_plus=0):
    clear_digits(all_leds, side, background)
    if total == None:
        return

    ones = total % 10
    tens = total // 10
    shift = 0
    if tens == 0:
        shift = 1

    # special setup for display floating point temperature
    if float_temp == 1:
        shift = 3
        all_leds[(8,1,7)] = color

    # special setup for display day indicator
    if show_plus == 1:
        all_leds[(8,2,6)] = color
        all_leds[(8,3,5)] = color
        all_leds[(8,3,6)] = color
        all_leds[(8,3,7)] = color
        all_leds[(8,4,6)] = color

    if side == 'right':
        onesLeds = rightOnesLeds
        tensLeds = rightTensLeds
    else:
        onesLeds = leftOnesLeds
        tensLeds = leftTensLeds

    for point in range(len(digit[ones])):
        pair = onesLeds[digit[ones][point][0]][digit[ones][point][1]]
        h = pair[0]
        v = pair[1]
        if side == 'right':
            all_leds[(8,v,h+shift)] = color
        else:
            all_leds[(h-shift,v,8)] = color

    if tens > 0:
        for point in range(len(digit[tens])):
            pair = tensLeds[digit[tens][point][0]][digit[tens][point][1]]
            h = pair[0]
            v = pair[1]
            if side == 'right':
                all_leds[(8,v,h+shift)] = color
            else:
                all_leds[(h-shift,v,8)] = color


def initalize_left_right_leds():
    for x in range(9):
        for y in range(9):
            for z in range(9):
                leds[(x,0,z)] = black


def fetchdata():
    # get method of requests module
    # return response object
    response = requests.get(complete_weerlive_url)

    if response.ok:
        # json method of response object
        # convert json format data into python format data
        data = response.json()
        print (data)
    else:
        print('Invalid request')

    # insert dummy data
    # json_data = '{"liveweer": [{"image": "halfbewolkt_regen", "plaats": "Rijswijk", "timestamp": 1721546885, "time": "21-07-2024 09:28:05", "temp": 18.9, "gtemp": 16.9, "samenv": "Regen", "lv": 92, "windr": "W", "windrgr": 270.2, "windms": 3.87, "windbft": 3, "windknp": 7.5, "windkmh": 13.9, "luchtd": 1007.27, "ldmmhg": 756, "dauwp": 17.7, "zicht": 4650, "gr": 27, "verw": "Eerst nog enkele (onweers)buien, vanaf vanavond droog", "sup": "05:47", "sunder": "21:50", "alarm": 0, "lkop": "Er zijn geen waarschuwingen", "ltekst": " Er zijn momenteel geen waarschuwingen van kracht.", "wrschklr": "groen", "wrsch_g": "-", "wrsch_gts": 0, "wrsch_gc": "-"}], "wk_verw": [{"dag": "21-07-2024", "image": "halfbewolkt", "max_temp": 23, "min_temp": 17, "windbft": 3, "windkmh": 14, "windknp": 8, "windms": 4, "windrgr": 310, "windr": "NW", "neersl_perc_dag": 60, "zond_perc_dag": 78}, {"dag": "22-07-2024", "image": "halfbewolkt", "max_temp": 21, "min_temp": 15, "windbft": 3, "windkmh": 14, "windknp": 8, "windms": 4, "windrgr": 289, "windr": "W", "neersl_perc_dag": 30, "zond_perc_dag": 77}, {"dag": "23-07-2024", "image": "regen", "max_temp": 21, "min_temp": 16, "windbft": 3, "windkmh": 14, "windknp": 8, "windms": 4, "windrgr": 283, "windr": "W", "neersl_perc_dag": 80, "zond_perc_dag": 70}, {"dag": "24-07-2024", "image": "halfbewolkt", "max_temp": 18, "min_temp": 14, "windbft": 3, "windkmh": 18, "windknp": 10, "windms": 5, "windrgr": 298, "windr": "W", "neersl_perc_dag": 50, "zond_perc_dag": 74}, {"dag": "25-07-2024", "image": "halfbewolkt", "max_temp": 21, "min_temp": 13, "windbft": 3, "windkmh": 14, "windknp": 8, "windms": 4, "windrgr": 291, "windr": "W", "neersl_perc_dag": 0, "zond_perc_dag": 68}], "uur_verw": [{"uur": "21-07-2024 10:00", "timestamp": 1721548800, "image": "halfbewolkt", "temp": 22, "windbft": 2, "windkmh": 10, "windknp": 6, "windms": 3, "windrgr": 296, "windr": "W", "neersl": 1, "gr": 579}, {"uur": "21-07-2024 11:00", "timestamp": 1721552400, "image": "bewolkt", "temp": 24, "windbft": 2, "windkmh": 10, "windknp": 6, "windms": 3, "windrgr": 298, "windr": "W", "neersl": 2, "gr": 662}, {"uur": "21-07-2024 12:00", "timestamp": 1721556000, "image": "zonnig", "temp": 25, "windbft": 3, "windkmh": 14, "windknp": 8, "windms": 4, "windrgr": 304, "windr": "NW", "neersl": 2, "gr": 620}, {"uur": "21-07-2024 13:00", "timestamp": 1721559600, "image": "zonnig", "temp": 25, "windbft": 3, "windkmh": 14, "windknp": 8, "windms": 4, "windrgr": 302, "windr": "W", "neersl": 1, "gr": 814}, {"uur": "21-07-2024 14:00", "timestamp": 1721563200, "image": "lichtbewolkt", "temp": 25, "windbft": 3, "windkmh": 18, "windknp": 10, "windms": 5, "windrgr": 301, "windr": "W", "neersl": 0, "gr": 781}, {"uur": "21-07-2024 15:00", "timestamp": 1721566800, "image": "zonnig", "temp": 25, "windbft": 3, "windkmh": 14, "windknp": 8, "windms": 4, "windrgr": 300, "windr": "W", "neersl": 0, "gr": 737}, {"uur": "21-07-2024 16:00", "timestamp": 1721570400, "image": "lichtbewolkt", "temp": 24, "windbft": 3, "windkmh": 18, "windknp": 10, "windms": 5, "windrgr": 301, "windr": "W", "neersl": 0, "gr": 662}, {"uur": "21-07-2024 17:00", "timestamp": 1721574000, "image": "zonnig", "temp": 24, "windbft": 3, "windkmh": 14, "windknp": 8, "windms": 4, "windrgr": 308, "windr": "NW", "neersl": 0, "gr": 476}, {"uur": "21-07-2024 18:00", "timestamp": 1721577600, "image": "halfbewolkt", "temp": 23, "windbft": 3, "windkmh": 18, "windknp": 10, "windms": 5, "windrgr": 313, "windr": "NW", "neersl": 0, "gr": 391}, {"uur": "21-07-2024 19:00", "timestamp": 1721581200, "image": "wolkennacht", "temp": 22, "windbft": 3, "windkmh": 14, "windknp": 8, "windms": 4, "windrgr": 328, "windr": "NW", "neersl": 1, "gr": 216}, {"uur": "21-07-2024 20:00", "timestamp": 1721584800, "image": "halfbewolkt", "temp": 21, "windbft": 3, "windkmh": 14, "windknp": 8, "windms": 4, "windrgr": 333, "windr": "NW", "neersl": 2, "gr": 86}, {"uur": "21-07-2024 21:00", "timestamp": 1721588400, "image": "halfbewolkt", "temp": 20, "windbft": 2, "windkmh": 10, "windknp": 6, "windms": 3, "windrgr": 328, "windr": "NW", "neersl": 0, "gr": 14}, {"uur": "21-07-2024 22:00", "timestamp": 1721592000, "image": "nachtbewolkt", "temp": 19, "windbft": 2, "windkmh": 10, "windknp": 6, "windms": 3, "windrgr": 314, "windr": "NW", "neersl": 1, "gr": 0}, {"uur": "21-07-2024 23:00", "timestamp": 1721595600, "image": "nachtbewolkt", "temp": 19, "windbft": 2, "windkmh": 10, "windknp": 6, "windms": 3, "windrgr": 301, "windr": "W", "neersl": 2, "gr": 0}, {"uur": "22-07-2024 00:00", "timestamp": 1721599200, "image": "nachtbewolkt", "temp": 19, "windbft": 2, "windkmh": 10, "windknp": 6, "windms": 3, "windrgr": 297, "windr": "W", "neersl": 3, "gr": 0}, {"uur": "22-07-2024 01:00", "timestamp": 1721602800, "image": "helderenacht", "temp": 18, "windbft": 2, "windkmh": 10, "windknp": 6, "windms": 3, "windrgr": 299, "windr": "W", "neersl": 0, "gr": 0}, {"uur": "22-07-2024 02:00", "timestamp": 1721606400, "image": "helderenacht", "temp": 18, "windbft": 2, "windkmh": 7, "windknp": 4, "windms": 2, "windrgr": 301, "windr": "W", "neersl": 0, "gr": 0}, {"uur": "22-07-2024 03:00", "timestamp": 1721610000, "image": "helderenacht", "temp": 17, "windbft": 2, "windkmh": 7, "windknp": 4, "windms": 2, "windrgr": 310, "windr": "NW", "neersl": 0, "gr": 0}, {"uur": "22-07-2024 04:00", "timestamp": 1721613600, "image": "helderenacht", "temp": 17, "windbft": 2, "windkmh": 7, "windknp": 4, "windms": 2, "windrgr": 297, "windr": "W", "neersl": 0, "gr": 0}, {"uur": "22-07-2024 05:00", "timestamp": 1721617200, "image": "helderenacht", "temp": 16, "windbft": 2, "windkmh": 7, "windknp": 4, "windms": 2, "windrgr": 279, "windr": "W", "neersl": 0, "gr": 0}, {"uur": "22-07-2024 06:00", "timestamp": 1721620800, "image": "zonnig", "temp": 16, "windbft": 2, "windkmh": 7, "windknp": 4, "windms": 2, "windrgr": 272, "windr": "W", "neersl": 0, "gr": 47}, {"uur": "22-07-2024 07:00", "timestamp": 1721624400, "image": "zonnig", "temp": 17, "windbft": 2, "windkmh": 7, "windknp": 4, "windms": 2, "windrgr": 282, "windr": "W", "neersl": 0, "gr": 166}, {"uur": "22-07-2024 08:00", "timestamp": 1721628000, "image": "zonnig", "temp": 18, "windbft": 2, "windkmh": 7, "windknp": 4, "windms": 2, "windrgr": 286, "windr": "W", "neersl": 0, "gr": 316}, {"uur": "22-07-2024 09:00", "timestamp": 1721631600, "image": "halfbewolkt", "temp": 19, "windbft": 2, "windkmh": 7, "windknp": 4, "windms": 2, "windrgr": 276, "windr": "W", "neersl": 0, "gr": 457}], "api": [{"bron": "Bron: Weerdata KNMI/NOAA via Weerlive.nl", "max_verz": 300, "rest_verz": 296}]}'
    # data = json.loads(json_data)

    global liveweather
    liveweather = data.get("liveweer")

    global week_forecast
    week_forecast = data.get("wk_verw")

    global hour_forecast
    hour_forecast = data.get("uur_verw")


def fetchraindata():
    # get method of requests module
    # return response object
    response = requests.get(complete_buienradar_url)

    if response.ok:
        # print(response.headers)
        # print(response.text)
        # print(response.status_code)
        # json_content = json.loads(response)
        lines = response.text.splitlines()
        global totalrain
        global max_rainfall_two_hours
        global five_minute_rain
        totalrain = 0
        max_rainfall_two_hours = 0
        five_minute_rain = []
        # looping through lines of forecasted precipitation data and
        for line in lines:
            (val, key) = line.split("|")
            # See buienradar documentation for this api, attribution
            # https://www.buienradar.nl/overbuienradar/gratis-weerdata
            #
            # Op basis van de door u gewenste coordinaten (latitude en longitude)
            # kunt u de neerslag tot twee uur vooruit ophalen in tekstvorm. De
            # data wordt iedere 5 minuten geupdatet. Op deze pagina kunt u de
            # neerslag in tekst vinden. De waarde 0 geeft geen neerslag aan (droog)
            # de waarde 255 geeft zware neerslag aan. Gebruik de volgende formule
            # voor het omrekenen naar de neerslagintensiteit in de eenheid
            # millimeter per uur (mm/u):
            #
            # Neerslagintensiteit = 10^((waarde-109)/32)
            #
            # Ter controle: een waarde van 77 is gelijk aan een neerslagintensiteit
            # van 0,1 mm/u.
            val = float(val.replace(',', '.'))
            mmu = 10**((val - 109) / 32)
            totalrain += round(mmu,2)
            if mmu > max_rainfall_two_hours:
                max_rainfall_two_hours = mmu
            five_minute_rain.append(round(mmu,2))

        # print(five_minute_rain)
        # print("maximum rain in the next two hours =" + round(max_rainfall_two_hours,2) + " mm/u")
        # print("total rain in the next two hours = " + round(totalrain,2) + " mm")
    else:
        print('Invalid request')

    # testdata setup
    # five_minute_rain = []
    # for i in range(0,24):
    #     testvalue = i*3/10
    #     five_minute_rain.append(testvalue)
    #     if testvalue > max_rainfall_two_hours:
    #         max_rainfall_two_hours = testvalue


def show_weather_icon(image):
    icon_sun = [ [0,0,y,0,0,y,0,0], [0,0,0,0,0,0,0,0], [y,0,y,y,y,y,0,y], [0,0,y,y,y,y,0,0], [0,0,y,y,y,y,0,0], [y,0,y,y,y,y,0,y], [0,0,0,0,0,0,0,0], [0,0,y,0,0,y,0,0] ]
    icon_thunder = [ [0,0,0,D,D,D,0,0], [0,0,D,G,y,G,D,0], [0,D,G,y,G,G,G,D], [D,G,y,G,G,G,G,D], [0,D,y,y,y,D,D,0], [0,0,0,0,y,0,0,0], [0,0,0,y,0,0,0,0], [0,0,y,0,0,0,0,0] ]
    icon_rain = [ [0,0,b,0,0,b,0,0], [b,0,0,b,0,0,b,0], [0,b,0,0,b,0,0,b], [0,0,b,0,0,b,0,0], [b,0,0,b,0,0,b,0], [0,b,0,0,b,0,0,b], [0,0,b,0,0,b,0,0], [b,0,0,b,0,0,b,0] ]
    icon_rainshowers = [ [0,0,0,0,0,b,0,0], [0,0,0,0,0,0,b,0], [b,0,0,0,0,0,0,b], [0,b,0,0,0,b,0,0], [0,0,b,0,0,0,b,0], [b,0,0,0,0,0,0,b], [0,b,0,0,0,0,0,0], [0,0,0,0,0,0,0,0] ]
    icon_hail = [ [0,0,0,G,G,G,0,0], [0,0,G,w,w,w,G,0], [0,G,w,w,w,w,w,G], [G,w,w,w,w,w,w,G], [0,G,G,G,G,G,G,0], [0,0,0,0,0,0,0,0], [0,0,w,0,0,w,0,0], [0,0,0,w,0,0,w,0] ]
    icon_fog = [ [0,0,0,0,0,0,0,0], [0,w,w,w,0,0,0,0], [0,0,0,0,0,0,0,0], [w,w,0,w,w,w,w,0], [0,0,0,0,0,0,0,0], [w,w,w,w,0,w,w,w], [0,0,0,0,0,0,0,0], [0,0,w,w,w,w,0,0] ]
    icon_clouds = [ [0,0,G,G,G,0,0,0], [0,G,w,w,w,G,0,0], [G,w,w,w,G,G,G,0], [G,w,w,G,w,w,w,G], [w,w,w,w,G,G,w,w], [w,w,G,G,w,w,G,G], [w,G,w,w,w,w,w,w], [G,w,w,w,w,w,w,w ] ]
    icon_clear_day = [ [0,0,y,0,0,y,0,0], [0,0,0,0,0,0,0,0], [y,0,y,y,y,y,0,y], [0,0,y,y,y,y,0,0], [0,0,y,y,y,y,0,0], [y,0,y,y,y,y,0,y], [0,0,0,0,0,0,0,0], [0,0,y,0,0,y,0,0] ]
    icon_light_clouds = [ [0,0,o,o,o,0,0,0], [0,o,y,y,y,o,0,0], [o,y,y,y,G,G,G,0], [o,y,y,G,w,w,w,G], [o,y,y,G,w,w,w,w], [0,o,G,w,w,w,w,w], [0,G,w,w,w,w,w,w], [G,w,w,w,w,w,w,w] ]
    icon_half_clouds = [ [0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0], [0,0,0,G,G,G,0,0], [0,0,G,w,w,w,G,0], [0,G,w,w,w,w,w,G], [G,w,w,w,w,w,w,G], [0,G,G,G,G,G,G,0], [0,0,0,0,0,0,0,0] ]
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


def display_two_numbers(number_left, number_right, colour_left, colour_right):
    if number_left >= 100:
        number_left = 99
    if number_right >= 100:
        number_left = 99
    display.set_3d(leds)
    set_digits(leds,'left',number_left,colour_left,black)
    set_digits(leds,'right',number_right,colour_right,black)
    display.set_3d(leds)


def displaytemperature(temp):
    result = str(temp).split('.')
     # colour of the text based on temperature
    celsius_temperature = int(result[0])
    if celsius_temperature >= 30: colour = red
    elif celsius_temperature >= 25 and celsius_temperature < 30: colour = orange
    elif celsius_temperature >= 20 and celsius_temperature < 25: colour = yellow
    elif celsius_temperature >= 10 and celsius_temperature < 20: colour = green
    elif celsius_temperature >= 0 and celsius_temperature < 10: colour = cyan
    elif celsius_temperature >= -10 and celsius_temperature < 0: colour = blue
    else: colour = white

    display.set_3d(leds)
    set_digits(leds,'left',celsius_temperature,colour,black)
    set_digits(leds,'right',int(result[1]),colour,black,1)
    display.set_3d(leds)


def displaywind(wind):
    result = str(wind).split('.')

    display.set_3d(leds)
    set_digits(leds,'left',int(result[0]),blue,black,0)
    set_digits(leds,'right',int(result[1]),blue,black,1)
    display.set_3d(leds)


def display_predicted_temperature(from_temp,to_temp):
     # colour of the text based on to_temp
    if to_temp >= 30: colour = red
    elif to_temp >= 25 and to_temp < 30: colour = orange
    elif to_temp >= 20 and to_temp < 25: colour = yellow
    elif to_temp >= 10 and to_temp < 20: colour = green
    elif to_temp >= 0 and to_temp < 10: colour = cyan
    elif to_temp >= -10 and to_temp < 0: colour = blue
    else: colour = white

    display_two_numbers(from_temp,to_temp,colour, colour)


def display_day(index):
    display.set_3d(leds)
    clear_left(leds, black)
    set_digits(leds,'right',index,white,black,0,1)
    display.set_3d(leds)


def show_week_forecast():
    counter = 0
    for day in week_forecast:
        counter+=1
        show_weather_icon(day["image"])
        display_day(counter)
        time.sleep(1)
        display_two_numbers(day["zond_perc_dag"], day["neersl_perc_dag"], yellow, blue)
        time.sleep(5)
        display_predicted_temperature(day["min_temp"], day["max_temp"])
        time.sleep(5)


def show_hour_rain_forecast():
    counter = 0
    for hour in hour_forecast:
        if counter <= 15:
            rain = int(hour["neersl"]+1)
            for i in range(1,7):
                display.set_led(counter,i,black)
            for i in range(0,rain):
                if i == 0:
                    display.set_led(counter,i,white)
                else:
                    display.set_led(counter,i,blue)
            counter+=1
    time.sleep(5)


def show_five_minute_rain_forecast():
    counter = 0
    for mmu in five_minute_rain:
        if counter <= 15:
            # show the rain, relative to the max value in the next 2 hours
            rain = round(mmu/max_rainfall_two_hours*8)
            for i in range(1,7):
                display.set_led(counter,i,black)
            for i in range(0,rain):
                display.set_led(counter,i,blue)
            counter+=1
    time.sleep(5)


def displaydata():
    display.set_all(black)

    show_weather_icon(liveweather[0]["image"])

    show_five_minute_rain_forecast()

    if liveweather[0]["alarm"] > 0:
        for frequency in range(500, 2000, 100):
            speaker.tone(frequency, 0.01)
        speaker.say("Weather alert for {0}".format(locatie))
        display.scroll_text(liveweather[0]["plaats"] + ": " + liveweather[0]["lkop"] + " " + liveweather[0]["ltekst"], red)

    if show_full_msg:
        print("scrolling forecast message")
        # display.scroll_text(timeknmi + " ", orange)
        display.scroll_text(liveweather[0]["plaats"] + ": " + liveweather[0]["samenv"], yellow)
        display.scroll_text(str(liveweather[0]["temp"]) + " graden", yellow)
        display.scroll_text(liveweather[0]["windr"] + " " + str(liveweather[0]["windkmh"]) + " km/h", blue)
        # display.scroll_text(verw, yellow)
    else:
        print("no scrolling forecast message")

    # Scroll the time across the cube.
    time_text = datetime.now(tzinfo).strftime("%H:%M")
    # display.scroll_text(time_text, green)

    displaytemperature(liveweather[0]["temp"])
    time.sleep(5)
    displaywind(liveweather[0]["windkmh"])
    time.sleep(5)
    displaytemperature(liveweather[0]["temp"])
    time.sleep(5)

    if show_forecast:
        print("5 day forecast")
        show_week_forecast()
    else:
        print("no 5 day forecast")
    if (totalrain > 0):
        print("rain incoming show 5 minute forecast")
        show_five_minute_rain_forecast()
    if show_rain:
        print("16 hour rain forecast")
        show_hour_rain_forecast()
    else:
        print("no 16 hour rain forecast")


def wait_on_buttons(delay):
    global button_warned
    action = None
    try:
        action = buttons.get_next_action(delay)
    except:
        if not button_warned:
            print('This lumicube does not appear to have buttons?')
            button_warned = True
        time.sleep(delay)

    return action


show_rain = True
show_full_msg = True
show_forecast = True
refresh_rate = 120
# initialize our led dictionary
leds = {}
initalize_left_right_leds()

display.set_all(black)

try:
    while True:
        fetchdata()
        fetchraindata()
        displaydata()

        waiting = True
        while waiting:
            button = wait_on_buttons(120)

            if button == None:
                print('no selection')
                waiting = False
            elif button == 'top':
                show_rain = not show_rain
            elif button == 'bottom':
                show_full_msg = not show_full_msg
            elif button == 'middle':
                show_forecast = not show_forecast
            else:
                print('no change')
            waiting = False

except Exception:
    print(traceback.format_exc())
    screen.draw_rectangle(0, 0, 320, 240, black)
    screen.write_text(0, 0, traceback.format_exc(), 1, black, white)
