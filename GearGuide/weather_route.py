from flask import Flask, request, jsonify
import app 

@app.route("/weather", method=["GET"])
def weather():
  #/ latitude and longitude requests
  lat = requests.args.ge("Lat", type=float)
  lon = requests.args.get("Lon", type=float)

  if lat is None or lon is None:
    return jsonify({"error": "lat and lon query parameters are required"}), 400

try:
  points_url = f"https://api.weather.gov/points/{lat},{lon}"
  points_res = requests.get(points_url, headers=NWS_HEADERS, timeout=10)

  if points_res.status_code != 200:
  return jsonify({
      "error": "NWS points lookup failed",
      "details": points_res.text
    }), points_res.status.code

  points_data = points_res.json()
  forecast_url = points_data["properties"]["forecast"]

  forecast_res = requests.get(forecast_url, headers=NWS_HEADERS, timeout=10)
  if forecast_res.status_code != 200:
      return jsonify({
          "error": "NWS forecast fetch failed",
          "details": forecast_res.text
      }), forecast_res

  forecast_data = forecast_res.json()
  periods = forecast_data["properties"]["periods"]

  simplified = [
      {
          "name": p["name"],
          "startTime": p["startTime"],
          "endTime": p["endTime"],
          "isDaytime": p["isDaytime"],
          "isNighttime": p["isNighttime"],
          "temperature": p["temperature"],
          "temperatureUnit": p["temperatureUnit"],
          "windSpeed": p["windSpeed"],
          "windDirection": p["windDirection"],
          "shortForecast": p["shortForecast"],
          "detailedForecast": p["detailedForecast"],
    }
    for p in periods
  ]

  return jsonify({
      "Lat": lat,
      "Lon": lon,
      "forecast": simplified
  })

  except KeyError:
      return jsonify({"error": "Unexpected NWS response format"}), 500
  except requests.RequestException as e:
      return jsonify({"error": f"Error contacting NWS API: {e}"}), 502

if __name__ == "__main__":
    app.run(debug=True)
