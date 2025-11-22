document.addEventListener("DOMContentLoaded", () => {
  const meta = document.getElementById("weather-data");
  if (!meta) return; // Not on a trip-detail page with weather

  // --- Toggle weather suggestions section ---
const toggleBtn = document.getElementById("toggle-weather-suggestions");
const suggestionsWrapper = document.getElementById("weather-suggestions-wrapper");

if (toggleBtn && suggestionsWrapper) {
  toggleBtn.addEventListener("click", () => {
    const isHidden = suggestionsWrapper.style.display === "none";
    suggestionsWrapper.style.display = isHidden ? "block" : "none";
    toggleBtn.textContent = isHidden
      ? "Hide Suggestions ▲"
      : "Show Suggestions ▼";
  });
}

  const loadingEl = document.getElementById("weather-loading");
  const errorEl = document.getElementById("weather-error");
  const containerEl = document.getElementById("weather-container");

  if (!loadingEl || !errorEl || !containerEl) return;

  // Elements for weather-based packing suggestions (optional card)
  const suggestListEl = document.getElementById("weather-pack-list");
  const suggestEmptyEl = document.getElementById("weather-pack-empty");

  // Read data attributes from the hidden meta div
  const lat = parseFloat(meta.dataset.lat);
  const lon = parseFloat(meta.dataset.lon);
  const tripStartStr = meta.dataset.start || null; // "YYYY-MM-DD"
  const tripEndStr = meta.dataset.end || null;     // "YYYY-MM-DD"

  /* -------- Helper functions -------- */

  // Turn an ISO datetime into a normalized date key "YYYY-MM-DD" using UTC
  function toDateKeyFromISO(isoString) {
    if (!isoString) return null;
    const d = new Date(isoString);
    if (isNaN(d)) return null;
    return d.toISOString().slice(0, 10);
  }

  // Turn a "YYYY-MM-DD" (or ISO datetime) into "MM/DD" for display
  function formatDateMMDD(dateStrOrIso) {
    if (!dateStrOrIso) return "";
    let d;
    if (dateStrOrIso.length === 10) {
      // Assume YYYY-MM-DD, treat as UTC
      d = new Date(dateStrOrIso + "T00:00:00Z");
    } else {
      d = new Date(dateStrOrIso);
    }
    if (isNaN(d)) return "";
    return `${d.getUTCMonth() + 1}/${d.getUTCDate()}`;
  }

  // Emoji icon from forecast text
  function getWeatherIcon(shortForecast, isDaytime) {
    if (!shortForecast) return isDaytime ? "🌤️" : "🌙";
    const s = shortForecast.toLowerCase();

    if (s.includes("thunder")) return "⛈️";
    if (s.includes("snow") || s.includes("sleet") || s.includes("flurries")) return "❄️";
    if (s.includes("rain") || s.includes("shower") || s.includes("drizzle")) return "🌧️";
    if (s.includes("fog") || s.includes("haze") || s.includes("mist")) return "🌫️";
    if (s.includes("cloud")) return isDaytime ? "⛅" : "☁️";
    if (s.includes("sun") || s.includes("clear")) return isDaytime ? "☀️" : "🌙";
    return isDaytime ? "🌤️" : "🌙";
  }

  // Color for temp bar
  function getTempColor(tempF) {
    if (tempF == null || isNaN(tempF)) return "#9ca3af"; // gray
    if (tempF <= 40) return "#3b82f6"; // blue
    if (tempF <= 60) return "#10b981"; // green
    if (tempF <= 80) return "#f59e0b"; // orange
    return "#ef4444";                 // red
  }

  // Little horizontal bar that visually encodes temp
  function buildTempBar(tempF) {
    const clamped = Math.max(0, Math.min(100, tempF || 0));
    const width = clamped + "%";
    const color = getTempColor(tempF);

    return `
      <div style="margin-top:0.25rem; background:#e5e7eb; border-radius:999px; height:6px; overflow:hidden;">
        <div style="width:${width}; height:100%; background:${color};"></div>
      </div>
    `;
  }

  // Build array of date keys from trip start → end as "YYYY-MM-DD" (UTC-normalized)
  function getTripDateKeys(startStr, endStr) {
    if (!startStr || !endStr) return [];
    const dates = [];
    const start = new Date(startStr + "T00:00:00Z");
    const end = new Date(endStr + "T00:00:00Z");
    if (isNaN(start) || isNaN(end)) return [];

    let cur = new Date(start);
    while (cur <= end) {
      dates.push(cur.toISOString().slice(0, 10)); // YYYY-MM-DD
      cur.setUTCDate(cur.getUTCDate() + 1);
    }
    return dates;
  }

  /* -------- Fetch Weather from backend /weather route -------- */

  if (!Number.isFinite(lat) || !Number.isFinite(lon)) {
    loadingEl.textContent =
      "No geographic coordinates available for this destination.";
    return;
  }

  fetch(`/weather?lat=${lat}&lon=${lon}`)
    .then((res) => res.json())
    .then((data) => {
      loadingEl.style.display = "none";

      if (data.error || !data.forecast) {
        errorEl.textContent = "Weather data unavailable.";
        errorEl.style.display = "block";
        return;
      }

      const forecast = data.forecast || [];

      // Group periods by normalized date key
      const periodsByDate = {};
      forecast.forEach((p) => {
        const key = toDateKeyFromISO(p.startTime);
        if (!key) return;
        if (!periodsByDate[key]) periodsByDate[key] = [];
        periodsByDate[key].push(p);
      });

      containerEl.innerHTML = "";
      containerEl.style.display = "block";

      const tripDateKeys = getTripDateKeys(tripStartStr, tripEndStr);
      let itemsRendered = 0;

      /* -------- Weather-based packing suggestions -------- */

      if (suggestListEl) {
        let willRain = false;
        let willSnow = false;
        let veryCold = false; // <= 40°F
        let veryHot = false;  // >= 85°F

        if (tripDateKeys.length) {
          tripDateKeys.forEach((dateKey) => {
            const dayPeriods = periodsByDate[dateKey] || [];
            dayPeriods.forEach((p) => {
              const short = (p.shortForecast || "").toLowerCase();
              const temp = p.temperature;

              if (short.includes("rain") || short.includes("shower") || short.includes("drizzle")) {
                willRain = true;
              }
              if (short.includes("snow") || short.includes("sleet") || short.includes("flurries")) {
                willSnow = true;
              }
              if (typeof temp === "number") {
                if (temp <= 40) veryCold = true;
                if (temp >= 85) veryHot = true;
              }
            });
          });
        }

        const suggestions = new Set();

        if (willRain || willSnow) {
          suggestions.add("Rain jacket");
          suggestions.add("Waterproof boots or shoes");
          suggestions.add("Extra warm socks");
          suggestions.add("Dry bag or pack liner");
        }
        if (veryCold) {
          suggestions.add("Insulated jacket");
          suggestions.add("Gloves");
          suggestions.add("Beanie or warm hat");
          suggestions.add("Thermal base layers");
        }
        if (veryHot) {
          suggestions.add("Sun hat");
          suggestions.add("Sunscreen");
          suggestions.add("Lightweight, breathable clothing");
          suggestions.add("Electrolyte packets");
        }

        if (suggestions.size > 0) {
          if (suggestEmptyEl) {
            suggestEmptyEl.remove();
          }
          suggestions.forEach((item) => {
            const li = document.createElement("li");
            li.textContent = item;
            suggestListEl.appendChild(li);
          });
        }
      }

      /* -------- Render per-day forecast for trip dates -------- */

      if (tripDateKeys.length) {
        tripDateKeys.forEach((dateKey) => {
          const dayPeriods = periodsByDate[dateKey] || [];

          if (!dayPeriods.length) {
            // No forecast yet for this date (e.g., trip >7 days out)
            const block = document.createElement("div");
            block.style.marginBottom = "1rem";
            block.innerHTML = `
              <div style="display:flex; align-items:flex-start; gap:0.75rem;">
                <div style="font-size:1.5rem;">🌤️</div>
                <div style="flex:1;">
                  <strong>${formatDateMMDD(dateKey)}</strong><br>
                  <span>No forecast available for this date yet.</span>
                </div>
              </div>
            `;
            containerEl.appendChild(block);
            return;
          }

          // Prefer a daytime period; fallback to the first one
          const best =
            dayPeriods.find((p) => p.isDaytime === true) || dayPeriods[0];

          const icon = getWeatherIcon(best.shortForecast, best.isDaytime);
          const temp = best.temperature;
          const unit = best.temperatureUnit || "F";

          const block = document.createElement("div");
          block.style.marginBottom = "1rem";
          block.innerHTML = `
            <div style="display:flex; align-items:flex-start; gap:0.75rem;">
              <div style="font-size:1.5rem;">${icon}</div>
              <div style="flex:1;">
                <strong>${best.name || "Forecast"} (${formatDateMMDD(
            dateKey
          )})</strong><br>
                <span>${temp != null ? temp + "°" + unit : "—"} · ${
            best.shortForecast || ""
          }</span>
                ${buildTempBar(temp)}
                <br>
                <small class="muted">Wind: ${
                  best.windSpeed || "—"
                } ${best.windDirection || ""}</small>
              </div>
            </div>
          `;
          containerEl.appendChild(block);
          itemsRendered++;
        });
      }

      // If trip is out of range and nothing rendered, show first few raw periods as a fallback
      if (!itemsRendered && forecast.length) {
        const fallback = forecast.slice(0, 5);
        fallback.forEach((period) => {
          const icon = getWeatherIcon(period.shortForecast, period.isDaytime);
          const temp = period.temperature;
          const unit = period.temperatureUnit || "F";

          const block = document.createElement("div");
          block.style.marginBottom = "1rem";
          block.innerHTML = `
            <div style="display:flex; align-items:flex-start; gap:0.75rem;">
              <div style="font-size:1.5rem;">${icon}</div>
              <div style="flex:1;">
                <strong>${period.name || "Forecast"} (${formatDateMMDD(
            period.startTime
          )})</strong><br>
                <span>${temp != null ? temp + "°" + unit : "—"} · ${
            period.shortForecast || ""
          }</span>
                ${buildTempBar(temp)}
                <br>
                <small class="muted">Wind: ${
                  period.windSpeed || "—"
                } ${period.windDirection || ""}</small>
              </div>
            </div>
          `;
          containerEl.appendChild(block);
        });
      }
    })
    .catch((err) => {
      loadingEl.style.display = "none";
      errorEl.textContent = "Failed to load weather.";
      errorEl.style.display = "block";
      console.error("Weather fetch error:", err);
    });
});