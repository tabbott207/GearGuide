from flask import Blueprint, request, jsonify
import requests

# National Weather Service requires a User-Agent
NWS_HEADERS = {
    "User-Agent": "GearGuideApp (contact@example.com)",
    "Accept": "application/geo+json",
}

# Blueprint so it can be registered in create_app()
bp = Blueprint("weather", __name__)


@bp.route("/weather", methods=["GET"])
def weather():
    """
    Example: /weather?lat=35.2271&lon=-80.8431
    """

    # latitude and longitude from query parameters
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)

    if lat is None or lon is None:
        return jsonify({"error": "lat and lon query parameters are required"}), 400

    try:
        # 1) Look up the grid point from NWS
        points_url = f"https://api.weather.gov/points/{lat},{lon}"
        points_res = requests.get(points_url, headers=NWS_HEADERS, timeout=10)

        if points_res.status_code != 200:
            return jsonify(
                {
                    "error": "NWS points lookup failed",
                    "details": points_res.text,
                }
            ), points_res.status_code

        points_data = points_res.json()
        forecast_url = points_data["properties"]["forecast"]

        # 2) Fetch forecast for that gridpoint
        forecast_res = requests.get(forecast_url, headers=NWS_HEADERS, timeout=10)
        if forecast_res.status_code != 200:
            return jsonify(
                {
                    "error": "NWS forecast fetch failed",
                    "details": forecast_res.text,
                }
            ), forecast_res.status_code

        forecast_data = forecast_res.json()
        periods = forecast_data["properties"]["periods"]

        # 3) Simplify periods down to fields you care about
        simplified = [
            {
                "name": p.get("name"),
                "startTime": p.get("startTime"),
                "endTime": p.get("endTime"),
                "isDaytime": p.get("isDaytime"),
                "temperature": p.get("temperature"),
                "temperatureUnit": p.get("temperatureUnit"),
                "windSpeed": p.get("windSpeed"),
                "windDirection": p.get("windDirection"),
                "shortForecast": p.get("shortForecast"),
                "detailedForecast": p.get("detailedForecast"),
            }
            for p in periods
        ]

        return jsonify(
            {
                "lat": lat,
                "lon": lon,
                "forecast": simplified,
            }
        )

    except KeyError:
        # If NWS changes their response format or something is missing
        return jsonify({"error": "Unexpected NWS response format"}), 500
    except requests.RequestException as e:
        # Network / HTTP errors
        return jsonify({"error": f"Error contacting NWS API: {e}"}), 502
