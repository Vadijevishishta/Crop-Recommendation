// =============================
// GLOBAL CHART INSTANCE
// =============================
let chartInstance = null;

// =============================
// PREDICT FUNCTION
// =============================
async function predict() {

  const data = {
    N: +document.getElementById("N").value,
    P: +document.getElementById("P").value,
    K: +document.getElementById("K").value,
    SOIL_PH: +document.getElementById("SOIL_PH").value,
    lat: +document.getElementById("lat").value,
    lon: +document.getElementById("lon").value
  };

  const res = await fetch("/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });

  const r = await res.json();
  console.log("Response:", r);

  document.getElementById("result").innerHTML = `
    <h3>🌾 Crop: ${r.recommended_crop}</h3>

    <p>🌡 Avg Temperature (7 days): ${r.avg_7day_temp} °C</p>
    <p>💧 Avg Humidity (7 days): ${r.avg_7day_humidity} %</p>

    <h4>🔍 XAI – Why this crop?</h4>
    <ul>
      ${r.xai_reasons.map(x => `<li>${x}</li>`).join("")}
    </ul>

    <h4>🐛 Organic Pest Control</h4>
    <ul>
      ${r.organic_pest_control.map(p => `<li>${p}</li>`).join("")}
    </ul>
  `;

  // ✅ VERY IMPORTANT
  drawChart(r.feature_importance);
  console.log("Feature importance:", r.feature_importance);

}


// =============================
// DRAW CHART FUNCTION (OUTSIDE)
// =============================
function drawChart(importance) {

  const canvas = document.getElementById("xaiChart");
  if (!canvas) {
    console.error("Canvas not found");
    return;
  }

  // ✅ canvas height compulsory
  canvas.height = 300;

  const ctx = canvas.getContext("2d");

  if (chartInstance) {
    chartInstance.destroy();
  }

  const labels = [
    "N",
    "P",
    "K",
    "TEMP",
    "RELATIVE_HUMIDITY",
    "SOIL_PH"
  ];

  const values = labels.map(l => Number(importance[l] || 0));
  console.log("Chart values:", values);

  chartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Feature Importance (XAI)",
        data: values,
        backgroundColor: [
          "#2e7d32",
          "#2e7d32",
          "#2e7d32",
          "#2e7d32",
          "#2e7d32",
          "#2e7d32"
        ],
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        title: {
          display: true,
          text: "XAI – Feature Influence"
        }
      },
      scales: {
        y: { beginAtZero: true }
      }
    }
  });
}
