import numpy as np
from noise import pnoise2
from panda3d.core import Geom, GeomNode, GeomTriangles, GeomVertexData, GeomVertexFormat
from panda3d.core import NodePath

def generate_heightmap(width, height, scale=100.0, octaves=6, persistence=0.5, lacunarity=2.0):
    heightmap = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            heightmap[y][x] = pnoise2(x / scale, y / scale, octaves=octaves, 
                                      persistence=persistence, lacunarity=lacunarity)
    heightmap = (heightmap - heightmap.min()) / (heightmap.max() - heightmap.min())
    return heightmap

def apply_terrain_features(heightmap, sand_threshold=0.3, rock_threshold=0.6):
    terrain = np.zeros_like(heightmap, dtype=str)
    for y in range(heightmap.shape[0]):
        for x in range(heightmap.shape[1]):
            h = heightmap[y, x]
            if h < sand_threshold:
                terrain[y, x] = 'sand'
            elif h < rock_threshold:
                terrain[y, x] = 'rock'
            else:
                terrain[y, x] = 'ruins'
    return terrain

def place_objects(terrain, object_density=0.01, ai_params=None, image_mask=None):
    objects = []
    height, width = terrain.shape
    for y in range(height):
        for x in range(width):
            if terrain[y, x] == 'ruins' and np.random.random() < object_density:
                objects.append((x, y, 'ruin'))
            elif terrain[y, x] == 'sand' and np.random.random() < object_density / 2:
                objects.append((x, y, 'crate'))
            if ai_params and ai_params.get("central_ruins") and abs(x - width//2) < 20 and abs(y - height//2) < 20:
                objects.append((x, y, 'large_ruin'))
            if image_mask is not None and image_mask[y, x]:
                objects.append((x, y, 'bunker'))
    return objects

def heightmap_to_geom(heightmap):
    format = GeomVertexFormat.getV3n3c4()
    vdata = GeomVertexData('terrain', format, Geom.UHStatic)
    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    color = GeomVertexWriter(vdata, 'color')

    height, width = heightmap.shape
    for y in range(height):
        for x in range(width):
            z = heightmap[y, x] * 10
            vertex.addData3(x, y, z)
            normal.addData3(0, 0, 1)
            color.addData4(1, 1, 1, 1)

    geom = Geom(vdata)
    tris = GeomTriangles(Geom.UHStatic)
    for y in range(height - 1):
        for x in range(width - 1):
            i = y * width + x
            tris.addVertices(i, i + 1, i + width)
            tris.addVertices(i + 1, i + width + 1, i + width)
    geom.addPrimitive(tris)

    node = GeomNode('terrain')
    node.addGeom(geom)
    return NodePath(node)
