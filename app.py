import ee
import geemap.foliumap as geemap
import streamlit as st

# === INIT ===
try:
    ee.Initialize(project='ee-fragotyron')
except Exception as e:
    st.error(f"Earth Engine initialization failed: {e}")
    st.stop()

# === Load datasets ===
five_year = ee.ImageCollection("projects/sat-io/open-datasets/GLC-FCS30D/five-years-map")
annual = ee.ImageCollection("projects/sat-io/open-datasets/GLC-FCS30D/annual")

# === Indonesia boundary ===
indonesia = ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017") \
    .filter(ee.Filter.eq('country_na', 'Indonesia')).geometry()

# === Load land cover images and clip ===
lc_1985 = five_year.mosaic().select("b1").clip(indonesia)
lc_2022 = annual.mosaic().select("b23").clip(indonesia)

# === Class remapping: Fine class to Basic class values ===
# Map basic classes to integer IDs
basic_class_ids = {
    'Cropland': 1, 'Forest': 2, 'Shrubland': 3, 'Grassland': 4, 'Tundra': 5,
    'Wetland': 6, 'Impervious surface': 7, 'Bare areas': 8,
    'Water body': 9, 'Permanent snow and ice': 10
}

# Original fine class to basic class name
fine_to_basic_name = {
    10: 'Cropland', 11: 'Cropland', 12: 'Cropland', 20: 'Cropland',
    51: 'Forest', 52: 'Forest', 61: 'Forest', 62: 'Forest',
    71: 'Forest', 72: 'Forest', 81: 'Forest', 82: 'Forest',
    91: 'Forest', 92: 'Forest',
    120: 'Shrubland', 121: 'Shrubland', 122: 'Shrubland',
    130: 'Grassland', 140: 'Tundra',
    181: 'Wetland', 182: 'Wetland', 183: 'Wetland', 184: 'Wetland',
    185: 'Wetland', 186: 'Wetland', 187: 'Wetland',
    190: 'Impervious surface',
    150: 'Bare areas', 152: 'Bare areas', 153: 'Bare areas',
    200: 'Bare areas', 201: 'Bare areas', 202: 'Bare areas',
    210: 'Water body', 220: 'Permanent snow and ice'
}

# Build remap lists
from_classes = list(fine_to_basic_name.keys())
to_classes = [basic_class_ids[fine_to_basic_name[c]] for c in from_classes]

# Remap images to basic classes
lc_1985_basic = lc_1985.remap(from_classes, to_classes)
lc_2022_basic = lc_2022.remap(from_classes, to_classes)

# === Define color palette for 10 basic classes ===
basic_palette = [
    '#ffff64',  # Cropland
    '#4c7300',  # Forest
    '#a0b432',  # Shrubland
    '#788200',  # Grassland
    '#f57ab6',  # Tundra
    '#00a884',  # Wetland
    '#ffffff',  # Impervious
    '#828282',  # Bare areas
    '#0046c8',  # Water body
    '#dcdcdc'   # Snow/Ice
]

# === Visualization parameters ===
basic_vis_params = {'min': 1, 'max': 10, 'palette': basic_palette}

# === Create and display map ===
st.subheader("Land Cover Change in Indonesia (1985 vs 2022)")

# Create a geemap.Map object centered over Indonesia
Map = geemap.Map(center=[-2.5, 118], zoom=5, basemap='HYBRID')

# Split map for 1985 and 2022 basic land cover
Map.split_map(
    geemap.ee_tile_layer(lc_1985_basic, basic_vis_params, 'LC 1985 (Basic)'),
    geemap.ee_tile_layer(lc_2022_basic, basic_vis_params, 'LC 2022 (Basic)')
)

# Add legend
legend_dict = {
    'Cropland': '#ffff64',
    'Forest': '#4c7300',
    'Shrubland': '#a0b432',
    'Grassland': '#788200',
    'Tundra': '#f57ab6',
    'Wetland': '#00a884',
    'Impervious surface': '#ffffff',
    'Bare areas': '#828282',
    'Water body': '#0046c8',
    'Permanent snow and ice': '#dcdcdc'
}
Map.add_legend(title="Basic Land Cover Classes", legend_dict=legend_dict)

# Display the map in Streamlit
Map.to_streamlit()

# === Application Title and Description ===
st.title("Land Cover Change in Indonesia")
st.markdown("""
This application visualizes the basic land cover change in Indonesia between 1985 and 2022
using data from the GLC-FCS30-2020 dataset on Google Earth Engine.
Use the split map to compare land cover between the two years.
""")
