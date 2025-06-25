import argparse
import sys

import requests


def parse_args():
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
    return parser.parse_args()


def fetch_json(url, desc, retries=1):
    for _ in range(retries + 1):
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    print(f"{desc} error! Status {r.status_code}.")
    sys.exit(1)


def get_coords_manual():
    print("Manual locating uses https://geocoding.geo.census.gov/geocoder/")
    street = input("Enter street (# and name): ").strip().replace(" ", "+")
    city = input("Enter city: ").strip().replace(" ", "+")
    state = input("Enter state (abbrev): ").strip().upper()
    url = (
        "https://geocoding.geo.census.gov/geocoder/locations/address"
        f"?street={street}&city={city}&state={state}"
        "&benchmark=2020&format=json"
    )
    data = fetch_json(url, "Geocode API", retries=1)
    coords = data["result"]["addressMatches"][0]["coordinates"]
    return str(coords["y"]), str(coords["x"])


def get_coords_auto():
    data = fetch_json("http://ipinfo.io/json", "IP geolocation", retries=1)
    lat, lon = data["loc"].split(",")
    return lat, lon


def get_point_metadata(lat, lon):
    url = f"https://api.weather.gov/points/{lat},{lon}"
    return fetch_json(url, "NWS location data")


def get_forecast(forecast_url):
    return fetch_json(forecast_url, "NWS forecast")


def get_alerts(lat, lon):
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


def main():
    args = parse_args()
    if args.manual:
        lat, lon = get_coords_manual()
    else:
        lat, lon = get_coords_auto()

    meta = get_point_metadata(lat, lon)
    forecast = get_forecast(meta["properties"]["forecast"])
    alerts = get_alerts(lat, lon)

    display_alerts(alerts)
    periods = forecast["properties"]["periods"]
    if args.week:
        display_weekly(periods)
    else:
        display_current(periods[0])


if __name__ == "__main__":
    main()
