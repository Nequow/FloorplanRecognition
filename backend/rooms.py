from shapely.geometry import Polygon, MultiPolygon, box
from shapely.ops import unary_union


def extract_room_polygons(wall_polygons):
    """Retourne les polygones des pièces (zones libres)."""
    walls_union = unary_union(wall_polygons)

    # Créer un gros rectangle englobant tout le plan
    minx, miny, maxx, maxy = walls_union.bounds
    marge = 0
    envelope = box(minx - marge, miny - marge, maxx + marge, maxy + marge)  # marge

    # Les pièces sont les zones libres à l'intérieur des murs
    free_space = envelope.difference(walls_union)

    if isinstance(free_space, Polygon):
        return [free_space]
    elif isinstance(free_space, MultiPolygon):
        return list(free_space.geoms)
    else:
        return []


import trimesh
import numpy as np
import random
from PIL import Image


def create_floor_meshes_with_texture(
    rooms_polygons, wall_mesh, textures_paths, real_word_scale
):
    floor_meshes = []

    # Créer un rectangle englobant pour le sol
    min_x, min_y, min_z = wall_mesh.bounds[0]
    max_x, max_y, max_z = wall_mesh.bounds[1]

    floor_bounds = box(min_x, min_y, max_x, max_y)
    mesh = trimesh.creation.extrude_polygon(floor_bounds, height=-0.03)

    mesh.apply_translation((0, 0, -0.02))  # Légèrement en dessous des sols

    floor_meshes.append(mesh)

    # Créer un mesh pour chaque pièce
    for idx, room_polygon in enumerate(rooms_polygons):
        if not room_polygon.is_valid:
            room_polygon = room_polygon.buffer(0)

        # Créer le mesh du sol
        mesh = trimesh.creation.extrude_polygon(room_polygon, height=5)
        mesh.apply_translation((0, 0, 0))  # Légèrement en dessous des murs

        # Générer les coordonnées UV (simple mapping XY -> UV [0,1])
        vertices = mesh.vertices[:, :2]  # On prend X et Y
        min_xy = vertices.min(axis=0)
        max_xy = vertices.max(axis=0)
        uv = (vertices - min_xy) / (max_xy - min_xy + 1e-8)  # UV entre 0 et 1

        # Choisir une texture aléatoire et la charger avec PIL
        texture_path = random.choice(textures_paths)
        # texture_path = textures_paths[2]
        image = Image.open(texture_path)

        material = trimesh.visual.texture.SimpleMaterial(image=image)
        visual = trimesh.visual.TextureVisuals(uv=uv, image=image, material=material)

        mesh.visual = visual
        mesh.visual.name = f"Floor_{idx}"
        mesh.apply_scale(real_word_scale)

        floor_meshes.append(mesh)

    return floor_meshes
