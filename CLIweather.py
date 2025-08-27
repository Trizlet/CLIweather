import argparse
import sys
import time
import requests


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog=__file__,
        description="A simple CLI weather tool.",
        epilog="@Trizlet was here :P",
    )
    parser.add_argument(
        "-m",
        "--manual",
        action="store_true",
        help="Manually enter location (otherwise auto-located via ipinfo.io)",
    )
    parser.add_argument(
        "-w",
        "--week",
        action="store_true",
        help="Print weekly forecast instead of current day",
    )
    parser.add_argument(
        "-a",
        "--alerts-only",
        action="store_true",
        help="Only print alerts",
    )
    return parser.parse_args(argv)

def fetch_json(url, desc, retries=1):
    headers = {
    "User-Agent": "CLIweather (@Trizlet)",
    "Accept": "application/json"
    }
    for _ in range(retries + 1):
        r = requests.get(url,headers=headers)
        if r.status_code == 200:
            return r.json()
        time.sleep(1)
    print(f"{desc} error! Status {r.status_code}.")
    sys.exit(1)


def get_coords_manual():
    print("Manual locating uses https://nominatim.openstreetmap.org")
    locsearch = input("Enter location query (city, region/state, or postal code. country recommended for clarity): ").strip().replace(" ", "+")
    url = (
        "https://nominatim.openstreetmap.org/search?"
        f"q={locsearch}&format=json&limit=1"
    )
    data = fetch_json(url, "Geocode API", retries=1)
    return str(data[0]["lat"]), str(data[0]["lon"])


def get_coords_auto():
    data = fetch_json("http://ipinfo.io/json", "IP geolocation", retries=1)
    lat, lon = data["loc"].split(",")
    return lat, lon


def get_point_metadata_NWS(lat, lon):
    url = f"https://api.weather.gov/points/{lat},{lon}"
    return fetch_json(url, "NWS location data")


def get_forecast(forecast_url):
    return fetch_json(forecast_url, "NWS forecast")


def get_alerts_NWS(lat, lon):
    url = f"https://api.weather.gov/alerts/active?point={lat},{lon}"
    return fetch_json(url, "NWS alerts")


def display_alerts(alerts):
    features = alerts.get("features", [])
    if not features:
        return
    print("\nCURRENT ALERTS:\n")
    for feat in features:
        p = feat["properties"]
        print(f"{p['severity'].upper()} {p['headline']}\n{p['description']}\n")


def display_current(period):
    print("\nCurrent Forecast:\n")
    print(
        f"{period['name']}, {period['temperature']}{chr(176)} {period['temperatureUnit']}"
    )
    print(period["detailedForecast"].replace(". ", ".\n") + "\n")


def display_weekly(periods):
    print("\nWeekly Forecast:")
    for p in periods:
        print(
            f"============\n{p['name']} {p['temperature']}{chr(176)} {p['temperatureUnit']}"
        )
        print(p["detailedForecast"].replace(". ", ".\n"))
    print("============\n")


def main(argv=None):
    args = parse_args(argv)

    if args.manual:
        lat,lon = get_coords_manual()
    else:
        lat, lon = get_coords_auto()

    alerts = get_alerts_NWS(lat, lon)
    display_alerts(alerts)

    if args.alerts_only:
        return

    meta = get_point_metadata_NWS(lat, lon)
    forecast = get_forecast(meta["properties"]["forecast"])

    periods = forecast["properties"]["periods"]
    
    if args.week:
        display_weekly(periods)
    else:
        display_current(periods[0])


if __name__ == "__main__":
    main()
