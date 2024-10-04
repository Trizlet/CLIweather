import argparse

import requests

parser = argparse.ArgumentParser(
    prog=__file__,
    description="a simple CLI weather tool.",
    epilog="@Trizlet was here :P",
)
parser.add_argument(
    "-m",
    "--manual",
    action="store_true",
    help="Manually enter location (otherwise automatically found with http://ipinfo.io/json)",
)
parser.add_argument(
    "-w",
    "--week",
    action="store_true",
    help="Print weekly forecast instead of current day",
)
args = parser.parse_args()

if args.manual == True:
    print("Manual locating utilizes https://geocoding.geo.census.gov/geocoder/")

    address = input("Enter address (# and street)\n").strip().replace(" ", "+")
    city = input("Enter city\n").strip().replace(" ", "+")
    state = input("Enter state (abbreviated)\n").strip().upper()

    geocodeJSON = requests.get(
        "https://geocoding.geo.census.gov/geocoder/locations/address?street="
        + address
        + "&city="
        + city
        + "&state="
        + state
        + "&benchmark=2020&format=json"
    )
    if not geocodeJSON.status_code == 200:
        geocodeJSON = requests.get(
            "https://geocoding.geo.census.gov/geocoder/locations/address?street="
            + address
            + "&city="
            + city
            + "&state="
            + state
            + "&benchmark=2020&format=json"
        )
        if not geocodeJSON.status_code == 200:
            print(
                "Geocode API error! try again with different info, or try again later."
            )
            exit()
    geocode = geocodeJSON.json()
    long = str(geocode["result"]["addressMatches"][0]["coordinates"]["x"])[:-10]
    lat = str(geocode["result"]["addressMatches"][0]["coordinates"]["y"])[:-10]
else:
    ipJSON = requests.get("http://ipinfo.io/json")
    if not ipJSON.status_code == 200:
        ipJSON = requests.get("http://ipinfo.io/json")
        if not ipJSON.status_code == 200:
            print(
                "Geocode API error! try again with different info, or try again later."
            )
            exit()
    ip = ipJSON.json()
    lat = str(ip["loc"].split(",")[0])
    long = str(ip["loc"].split(",")[1])

metaJSON = requests.get("https://api.weather.gov/points/" + lat + "," + long)
if not metaJSON.status_code == 200:
    metaJSON = requests.get("https://api.weather.gov/points/" + lat + "," + long)
    if not metaJSON.status_code == 200:
        print(
            "NWS location data API error! try again with different info, or try again later."
        )
        exit()
meta = metaJSON.json()

forecastJSON = requests.get(meta["properties"]["forecast"])
if not forecastJSON.status_code == 200:
    forecastJSON = requests.get(meta["properties"]["forecast"])
    if not forecastJSON.status_code == 200:
        print("NWS API error! try again with different info, or try again later.")
        exit()
forecast = forecastJSON.json()

alertsJSON = requests.get(
    "https://api.weather.gov/alerts/active?point=" + lat + "," + long
)
if not alertsJSON.status_code == 200:
    alertsJSON = requests.get(
        "https://api.weather.gov/alerts/active?point=" + lat + "," + long
    )
    if not alertsJSON.status_code == 200:
        print(
            "NWS alerts API error! try again with different info, or try again later."
        )
        exit()
alerts = alertsJSON.json()

if len(alerts["features"]) > 0:
    print("\nCURRENT ALERTS:\n")
    for x in range(len(alerts["features"])):
        print(
            str(alerts["features"][x]["properties"]["severity"]).upper()
            + " "
            + alerts["features"][x]["properties"]["headline"]
        )
    print("\n")
    for x in range(len(alerts["features"])):
        print(alerts["features"][x]["properties"]["description"])

if args.week == True:
    print("\nStart of weekly forecast.\n")
    for x in forecast["properties"]["periods"]:
        print("========")
        print(
            "\n"
            + x["name"]
            + " "
            + str(x["temperature"])
            + chr(176)
            + " "
            + x["temperatureUnit"]
            + "\n"
            + str(x["detailedForecast"]).replace(". ", ".\n")
            + "\n"
        )
    print("========\n")
else:
    x = forecast["properties"]["periods"][0]
    print("\n" + "Current Forecast:")
    print(
        "\n"
        + x["name"]
        + ", "
        + str(x["temperature"])
        + chr(176)
        + " "
        + x["temperatureUnit"]
        + "\n"
        + str(x["detailedForecast"]).replace(". ", ".\n")
        + "\n"
    )
