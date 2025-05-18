import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from terrain import generate_heightmap, apply_terrain_features, place_objects, heightmap_to_geom

st.title("Echoes of a Wasteland Map Generator")

# User inputs
width = st.slider("Map Width", 128, 512, 256)
height = st.slider("Map Height", 128, 512, 256)
scale = st.slider("Terrain Scale", 50.0, 200.0, 100.0)
object_density = st.slider("Object Density", 0.001, 0.1, 0.01)

if st.button("Generate Map"):
    # Generate heightmap and features
    heightmap = generate_heightmap(width, height, scale)
    terrain = apply_terrain_features(heightmap)
    objects = place_objects(terrain, object_density)

    # Visualize heightmap
    fig, ax = plt.subplots()
    ax.imshow(heightmap, cmap='terrain')
    st.pyplot(fig)

    # Save Panda3D terrain
    terrain_node = heightmap_to_geom(heightmap)
    terrain_node.writeToBamFile('terrain.bam')

    # Provide download link
    with open('terrain.bam', 'rb') as f:
        st.download_button("Download Map (.bam)", f, file_name="terrain.bam")

    # Display object placements
    st.write("Objects Placed:", objects)
