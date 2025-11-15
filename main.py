import folium
from folium.plugins import HeatMap
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

def main():
    csv_path = "water_data.csv"

    # ------------------------------------------------------------
    # 1. LOAD DATA
    # ------------------------------------------------------------
    df = pd.read_csv(csv_path)

    url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
    gdf = gpd.read_file(url)
    la_county = gdf[gdf['id'] == '06037']
    la_polygon = la_county.geometry.values[0]
    df = df[df.apply(lambda r: la_polygon.contains(Point(r["Longitude"], r["Latitude"])), axis=1)]
    df["geometry"] = df.apply(lambda r: Point(r["Longitude"], r["Latitude"]), axis=1)

    # Clean missing coords
    df = df.dropna(subset=["Latitude", "Longitude"])
    df["Latitude"] = df["Latitude"].astype(float)
    df["Longitude"] = df["Longitude"].astype(float)

    # ------------------------------------------------------------
    # 2. SELECT METRIC FOR HEATMAP
    # ------------------------------------------------------------
    # Options include:
    # "Drinking Water", "Lead", "Pollution Burden Score",
    # "Ozone", "PM2.5", "Traffic", etc.
    metric = "Lead Pctl"   # <-- change if needed

    df[metric] = pd.to_numeric(df[metric], errors="coerce").fillna(0)

    # ------------------------------------------------------------
    # 3. CREATE BASE MAP
    # ------------------------------------------------------------
    m = folium.Map(location=[34.0522, -118.2437], zoom_start=10, tiles="OpenStreetMap", control_scale=True, name="LA County Disparity Map")

    # Enable rectangle drawing on the map
    draw_plugin = folium.plugins.Draw(
        draw_options={
            'polyline': False,
            'polygon': False,
            'circle': False,
            'marker': False,
            'circlemarker': False,
            'rectangle': True
        },
        edit_options={'edit': False, 'remove': True}
    )
    draw_plugin.add_to(m)

    la_border_group = folium.FeatureGroup(name="LA County Borders", show=True, control=False)
    folium.GeoJson(
        la_county,
        style_function=lambda x: {
            'fillColor': 'none',
            'color': 'black',
            'weight': 3,
            'fillOpacity': 0
        }
    ).add_to(la_border_group)
    la_border_group.add_to(m)

    # Small black dots for measurement locations
    measurement_layer = folium.FeatureGroup(name="Measurement Locations", show=True)
    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=4,
            color="#cccccc",
            fill=True,
            fill_color="#eeeeee",
            fill_opacity=0.5,
            weight=1,
            tooltip=(
                f"<b>Lead Pctl:</b> {round(float(row.get('Lead Pctl', 0)), 2)}<br>"
                f"<b>PM2.5 Pctl:</b> {round(float(row.get('PM2.5 Pctl', 0)), 2)}<br>"
                f"<b>Asthma Pctl:</b> {round(float(row.get('Asthma Pctl', 0)), 2)}<br>"
                f"<b>Education:</b> {round(float(row.get('Education', 0)), 2)}<br>"
                f"<b>Poverty:</b> {round(float(row.get('Poverty', 0)), 2)}<br>"
                f"<b>Haz. Waste Pctl:</b> {round(float(row.get('Haz. Waste Pctl', 0)), 2)}<br>"
                f"<b>Traffic Pctl:</b> {round(float(row.get('Traffic Pctl', 0)), 2)}"
            )
        ).add_to(measurement_layer)
    measurement_layer.add_to(m)

    # ------------------------------------------------------------
    # 4. ADD HEATMAP LAYER
    # ------------------------------------------------------------
    df["intensity"] = df[metric] / df[metric].max()
    heat_data = df[["Latitude", "Longitude", "intensity"]].values.tolist()

    water_layer = folium.FeatureGroup(name="Water Quality", show=False)

    HeatMap(
        heat_data,
        radius=30,
        blur=40,
        max_zoom=12,
        min_opacity=0.02,
        gradient={
            0.00: "rgba(0, 0, 255, 0.00)",    # Transparent low
            0.10: "rgba(135, 206, 250, 0.25)",# Light sky blue
            0.25: "rgba(173, 216, 230, 0.35)",# Soft blue
            0.40: "rgba(255, 255, 102, 0.50)",# Yellow
            0.60: "rgba(255, 165, 0, 0.60)",  # Orange
            0.80: "rgba(255, 69, 0, 0.75)",   # Strong orange-red
            1.00: "rgba(255, 0, 0, 0.95)"     # Deep red
        }
    ).add_to(water_layer)

    water_layer.add_to(m)

    # ---- PM2.5 Layer ----
    pm = "PM2.5 Pctl"
    df[pm] = df[pm].fillna(0)
    df["pm_intensity"] = df[pm] / df[pm].max()
    pm_data = df[["Latitude", "Longitude", "pm_intensity"]].values.tolist()

    pm_layer = folium.FeatureGroup(name="PM2.5 Pctl", show=False)
    HeatMap(
        pm_data,
        radius=30,
        blur=40,
        max_zoom=12,
        min_opacity=0.02,
        gradient={
            0.00: "rgba(0, 0, 255, 0.00)",    # Transparent low
            0.10: "rgba(135, 206, 250, 0.25)",# Light sky blue
            0.25: "rgba(173, 216, 230, 0.35)",# Soft blue
            0.40: "rgba(255, 255, 102, 0.50)",# Yellow
            0.60: "rgba(255, 165, 0, 0.60)",  # Orange
            0.80: "rgba(255, 69, 0, 0.75)",   # Strong orange-red
            1.00: "rgba(255, 0, 0, 0.95)"     # Deep red
        }
    ).add_to(pm_layer)
    pm_layer.add_to(m)

    # ---- Asthma Layer ----
    asth = "Asthma Pctl"
    df[asth] = df[asth].fillna(0)
    df["asthma_intensity"] = df[asth] / df[asth].max()
    asthma_data = df[["Latitude", "Longitude", "asthma_intensity"]].values.tolist()

    asthma_layer = folium.FeatureGroup(name="Asthma Pctl", show=False)
    HeatMap(
        asthma_data,
        radius=30,
        blur=40,
        max_zoom=12,
        min_opacity=0.02,
        gradient={
            0.00: "rgba(0, 0, 255, 0.00)",    # Transparent low
            0.10: "rgba(135, 206, 250, 0.25)",# Light sky blue
            0.25: "rgba(173, 216, 230, 0.35)",# Soft blue
            0.40: "rgba(255, 255, 102, 0.50)",# Yellow
            0.60: "rgba(255, 165, 0, 0.60)",  # Orange
            0.80: "rgba(255, 69, 0, 0.75)",   # Strong orange-red
            1.00: "rgba(255, 0, 0, 0.95)"     # Deep red
        }
    ).add_to(asthma_layer)
    asthma_layer.add_to(m)

    # ---- Education Layer ----
    edu = "Education"
    df[edu] = df[edu].fillna(0)
    df["edu_intensity"] = df[edu] / df[edu].max()
    edu_data = df[["Latitude", "Longitude", "edu_intensity"]].values.tolist()

    education_layer = folium.FeatureGroup(name="Education", show=False)
    HeatMap(
        edu_data,
        radius=30,
        blur=40,
        max_zoom=12,
        min_opacity=0.02,
        gradient={
            0.00: "rgba(0, 0, 255, 0.00)",
            0.10: "rgba(135, 206, 250, 0.25)",
            0.25: "rgba(173, 216, 230, 0.35)",
            0.40: "rgba(255, 255, 102, 0.50)",
            0.60: "rgba(255, 165, 0, 0.60)",
            0.80: "rgba(255, 69, 0, 0.75)",
            1.00: "rgba(255, 0, 0, 0.95)"
        }
    ).add_to(education_layer)
    education_layer.add_to(m)

    # ---- Poverty Layer ----
    pov = "Poverty"
    df[pov] = df[pov].fillna(0)
    df["pov_intensity"] = df[pov] / df[pov].max()
    pov_data = df[["Latitude", "Longitude", "pov_intensity"]].values.tolist()

    poverty_layer = folium.FeatureGroup(name="Poverty", show=False)
    HeatMap(
        pov_data,
        radius=30,
        blur=40,
        max_zoom=12,
        min_opacity=0.02,
        gradient={
            0.00: "rgba(0, 0, 255, 0.00)",
            0.10: "rgba(135, 206, 250, 0.25)",
            0.25: "rgba(173, 216, 230, 0.35)",
            0.40: "rgba(255, 255, 102, 0.50)",
            0.60: "rgba(255, 165, 0, 0.60)",
            0.80: "rgba(255, 69, 0, 0.75)",
            1.00: "rgba(255, 0, 0, 0.95)"
        }
    ).add_to(poverty_layer)
    poverty_layer.add_to(m)

    # ---- Haz. Waste Layer ----
    hw = "Haz. Waste Pctl"
    df[hw] = df[hw].fillna(0)
    df["hw_intensity"] = df[hw] / df[hw].max()
    hw_data = df[["Latitude", "Longitude", "hw_intensity"]].values.tolist()

    hazw_layer = folium.FeatureGroup(name="Haz. Waste Pctl", show=False)
    HeatMap(
        hw_data,
        radius=30,
        blur=40,
        max_zoom=12,
        min_opacity=0.02,
        gradient={
            0.00: "rgba(0, 0, 255, 0.00)",
            0.10: "rgba(135, 206, 250, 0.25)",
            0.25: "rgba(173, 216, 230, 0.35)",
            0.40: "rgba(255, 255, 102, 0.50)",
            0.60: "rgba(255, 165, 0, 0.60)",
            0.80: "rgba(255, 69, 0, 0.75)",
            1.00: "rgba(255, 0, 0, 0.95)"
        }
    ).add_to(hazw_layer)
    hazw_layer.add_to(m)

    # ---- Traffic Layer ----
    traffic = "Traffic Pctl"
    df[traffic] = df[traffic].fillna(0)
    df["traffic_intensity"] = df[traffic] / df[traffic].max()
    traffic_data = df[["Latitude", "Longitude", "traffic_intensity"]].values.tolist()

    traffic_layer = folium.FeatureGroup(name="Traffic Pctl", show=False)
    HeatMap(
        traffic_data,
        radius=30,
        blur=40,
        max_zoom=12,
        min_opacity=0.02,
        gradient={
            0.00: "rgba(0, 0, 255, 0.00)",
            0.10: "rgba(135, 206, 250, 0.25)",
            0.25: "rgba(173, 216, 230, 0.35)",
            0.40: "rgba(255, 255, 102, 0.50)",
            0.60: "rgba(255, 165, 0, 0.60)",
            0.80: "rgba(255, 69, 0, 0.75)",
            1.00: "rgba(255, 0, 0, 0.95)"
        }
    ).add_to(traffic_layer)
    traffic_layer.add_to(m)

    # Inject JavaScript to force global heatmap scaling (disable local extrema)
    custom_js = folium.Element("""
    <script>
    document.addEventListener("DOMContentLoaded", function () {
        // Find the heatmap layer
        for (var i in window._layers) {
            var layer = window._layers[i];
            if (layer && layer._heat) {
                // Override options to disable viewport-based scaling
                layer._heat._config.useLocalExtrema = false;
                layer._heat._config.scaleRadius = false;
                layer._heat._config.maxOpacity = 0.6;
            }
        }
    });
    </script>
    """)
    m.get_root().html.add_child(custom_js)

    combined_ui_html = """
    <style>
    .ui-box {
        position: fixed;
        top: 200px;
        left: 20px;
        width: 210px;
        background-color: white;
        border: 1.5px solid #444;
        border-radius: 12px;
        font-size: 13px;
        padding: 12px;
        z-index: 9999;
        box-shadow: 0 0 8px rgba(0,0,0,0.25);
    }
    .ui-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        font-weight: bold;
        cursor: pointer;
    }
    summary::before {
        content: "▸ ";
        font-size: 12px;
        margin-right: 4px;
    }

    details[open] summary::before {
        content: "▾ ";
    }
    </style>

    <div class="ui-box">
<details style="margin-bottom:12px;">
  <summary style="cursor:pointer; font-size:13px; font-weight:bold; color:#000; display:flex; justify-content:space-between; align-items:center;">
    <span>Water Quality</span>
    <input type="checkbox" id="water-toggle">
  </summary>
  <div style="padding:8px 0 0 10px; font-size:12px;">
    Represents percentile ranking of drinking water contaminant levels affecting communities.
  </div>
</details>

<details style="margin-bottom:12px;">
  <summary style="cursor:pointer; font-size:13px; font-weight:bold; color:#000; display:flex; justify-content:space-between; align-items:center;">
    <span>PM2.5 Pctl Heatmap</span>
    <input type="checkbox" id="pm25-toggle">
  </summary>
  <div style="padding:8px 0 0 10px; font-size:12px;">
    Percentile ranking of annual average PM2.5 concentrations (fine particulate matter).
  </div>
</details>

<details style="margin-bottom:12px;">
  <summary style="cursor:pointer; font-size:13px; font-weight:bold; color:#000; display:flex; justify-content:space-between; align-items:center;">
    <span>Asthma Pctl Heatmap</span>
    <input type="checkbox" id="asthma-toggle">
  </summary>
  <div style="padding:8px 0 0 10px; font-size:12px;">
    Percentile ranking of age‑adjusted emergency department visits for asthma.
  </div>
</details>

<details style="margin-bottom:12px;">
  <summary style="cursor:pointer; font-size:13px; font-weight:bold; color:#000; display:flex; justify-content:space-between; align-items:center;">
    <span>Education Heatmap</span>
    <input type="checkbox" id="education-toggle">
  </summary>
  <div style="padding:8px 0 0 10px; font-size:12px;">
    Percent of population over age 25 without a high school diploma, expressed as a percentile.
  </div>
</details>

<details style="margin-bottom:12px;">
  <summary style="cursor:pointer; font-size:13px; font-weight:bold; color:#000; display:flex; justify-content:space-between; align-items:center;">
    <span>Poverty Heatmap</span>
    <input type="checkbox" id="poverty-toggle">
  </summary>
  <div style="padding:8px 0 0 10px; font-size:12px;">
    Percentile ranking of population living below twice the federal poverty level.
  </div>
</details>

<details style="margin-bottom:12px;">
  <summary style="cursor:pointer; font-size:13px; font-weight:bold; color:#000; display:flex; justify-content:space-between; align-items:center;">
    <span>Haz. Waste Pctl</span>
    <input type="checkbox" id="hazw-toggle">
  </summary>
  <div style="padding:8px 0 0 10px; font-size:12px;">
    Percentile ranking of hazardous waste facility proximity and quantity.
  </div>
</details>

<details style="margin-bottom:12px;">
  <summary style="cursor:pointer; font-size:13px; font-weight:bold; color:#000; display:flex; justify-content:space-between; align-items:center;">
    <span>Traffic Pctl</span>
    <input type="checkbox" id="traffic-toggle">
  </summary>
  <div style="padding:8px 0 0 10px; font-size:12px;">
    Percentile ranking of traffic density and vehicle-related pollution burden.
  </div>
</details>
    </div>

    <script>
    function toggleLayer(layerName, checked) {
        var selectors = document.querySelectorAll('.leaflet-control-layers-selector');
        selectors.forEach(function(sel) {
            var label = sel.nextSibling.textContent.trim();

            // Normalize layer name for matching
            var cleanLabel = label.replace(/\s+/g, ' ').trim().toLowerCase();
            var cleanTarget = layerName.replace(/\s+/g, ' ').trim().toLowerCase();

            if (cleanLabel.includes(cleanTarget)) {
                if (sel.checked !== checked) {
                    sel.click();
                }
            }
        });
    }

    document.getElementById('water-toggle').addEventListener('change', function() {
        toggleLayer("Water Quality", this.checked);
    });

    document.getElementById('pm25-toggle').addEventListener('change', function() {
        toggleLayer("PM2.5 Pctl", this.checked);
    });

    document.getElementById('asthma-toggle').addEventListener('change', function() {
        toggleLayer("Asthma Pctl", this.checked);
    });

    document.getElementById('education-toggle').addEventListener('change', function() {
        toggleLayer("Education", this.checked);
    });

    document.getElementById('poverty-toggle').addEventListener('change', function() {
        toggleLayer("Poverty", this.checked);
    });

    document.getElementById('hazw-toggle').addEventListener('change', function() {
        toggleLayer("Haz. Waste Pctl", this.checked);
    });

    document.getElementById('traffic-toggle').addEventListener('change', function() {
        toggleLayer("Traffic Pctl", this.checked);
    });

    // Global selection tracking
    window.savedRegions = [];
    window.activeLayers = [];

    // When a rectangle is created
    map.on(folium.Draw.Event.CREATED, function(e) {
        var layer = e.layer;
        window._pendingLayer = layer; // store temporary layer
        map.addLayer(layer);
    });

    // When user clicks "Clear All"
    map.on('draw:deleted', function() {
        window.savedRegions = [];
        window.activeLayers = [];
        console.log("Selections cleared.");
    });
    </script>
    """
    # Re-enable hidden LayerControl so custom toggles work
    folium.LayerControl(collapsed=True).add_to(m)

    # Hide LayerControl with CSS
    hidden_layercontrol_css = """
    <style>
    .leaflet-control-layers {
        display: none !important;
    }
    </style>
    """
    m.get_root().html.add_child(folium.Element(hidden_layercontrol_css))

    m.get_root().html.add_child(folium.Element(combined_ui_html))


    # ------------------------------------------------------------
    # 7. SAVE OUTPUT
    # ------------------------------------------------------------
    # Prepare measurement site coordinates for JS
    measurement_js_array = ",\n        ".join(
        f"[{row['Latitude']}, {row['Longitude']}]" for _, row in df.iterrows()
    )
    capture_js = folium.Element(f"""
<script>
document.addEventListener("DOMContentLoaded", function () {{
    var map = window._map || window.map;

    // Inject measurement site coordinates into JS
    var measurementSites = [
        {measurement_js_array}
    ];

    map.on(folium.Draw.Event.CREATED, function (e) {{
        var layer = e.layer;

        if (e.layerType === 'rectangle') {{
            var bounds = layer.getBounds();

            // Find included measurement points
            var inside = measurementSites.filter(function(pt) {{
                return pt[0] <= bounds.getNorth() &&
                       pt[0] >= bounds.getSouth() &&
                       pt[1] <= bounds.getEast() &&
                       pt[1] >= bounds.getWest();
            }});

            window.savedRegions = [{{
                north: bounds.getNorth(),
                south: bounds.getSouth(),
                east: bounds.getEast(),
                west: bounds.getWest(),
                count: inside.length
            }}];

            window.activeLayers = [layer];

            console.log("Region selected:", window.savedRegions[0]);
        }}

        map.addLayer(layer);
    }});
}});
</script>
""")
    m.get_root().html.add_child(capture_js)
    m.save("water_quality_map.html")
    print("✓ Saved: water_quality_map.html")

if __name__ == "__main__":
    main()