import folium
import geopandas as gpd

# Create map centered on LA County
m = folium.Map(
    location=[34.0522, -118.2437],
    zoom_start=9,
    tiles='OpenStreetMap'  # Original map style
)

# Get LA County boundary (not individual cities)
# Using Census County boundaries
url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"

gdf = gpd.read_file(url)
la_county = gdf[gdf['id'] == '06037']  # LA County FIPS code

# Add just the county outline
folium.GeoJson(
    la_county,
    style_function=lambda x: {
        'fillColor': 'none',
        'color': 'black',
        'weight': 3,
        'fillOpacity': 0
    }
).add_to(m)

m.save('la_county_map.html')