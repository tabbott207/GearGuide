// ---------- DATE CONSTRAINTS ----------
const todayISO = new Date().toISOString().split("T")[0];
const startEl = document.getElementById("start_date");
const endEl = document.getElementById("end_date");

if (startEl && endEl) {
  startEl.min = todayISO;
  endEl.min = todayISO;

  startEl.addEventListener("change", () => {
    const s = startEl.value || todayISO;
    endEl.min = s;
    if (endEl.value && endEl.value < s) endEl.value = s;
  });
}

// ---------- LOCATION AUTOCOMPLETE ----------
const destInput = document.getElementById("destination");
const list = document.getElementById("dest-suggestions");
let debounce;

if (destInput && list) {
  destInput.addEventListener("input", () => {
    const q = destInput.value.trim();
    destInput.setAttribute("aria-expanded", q ? "true" : "false");
    clearTimeout(debounce);
    if (!q) {
      list.style.display = "none";
      list.innerHTML = "";
      return;
    }
    debounce = setTimeout(() => searchPlaces(q), 400);
  });

  destInput.addEventListener("blur", () =>
    setTimeout(() => {
      list.style.display = "none";
    }, 150)
  );

  async function searchPlaces(q) {
    try {
      const url = `https://nominatim.openstreetmap.org/search?format=json&addressdetails=1&limit=6&q=${encodeURIComponent(q)}`;
      const res = await fetch(url, { headers: { Accept: "application/json" } });
      const data = await res.json();

      if (!Array.isArray(data) || data.length === 0) {
        list.style.display = "none";
        list.innerHTML = "";
        return;
      }

      list.innerHTML = data
        .map((item) => {
          const a = item.address || {};
          const city =
            a.city ||
            a.town ||
            a.village ||
            a.hamlet ||
            a.suburb ||
            a.municipality ||
            "";
          const region = a.state || a.county || "";
          const country = a.country || "";
          const pretty =
            [city, region, country].filter(Boolean).join(", ") ||
            item.display_name;
          return `<li data-val="${escapeHtml(pretty)}" role="option">${escapeHtml(pretty)}</li>`;
        })
        .join("");

      list.style.display = "block";

      Array.from(list.querySelectorAll("li")).forEach((li) => {
        li.addEventListener("mousedown", () => {
          destInput.value = li.getAttribute("data-val");
          list.style.display = "none";
          destInput.setAttribute("aria-expanded", "false");
        });
      });
    } catch {
      list.style.display = "none";
      list.innerHTML = "";
    }
  }

  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, (c) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      }[c])
    );
  }
}