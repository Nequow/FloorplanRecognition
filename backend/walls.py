import trimesh
import numpy as np
from PIL import Image
from shapely.geometry import box, Polygon
from trimesh.creation import extrude_polygon


def generate_wall_polygon_from_bbox(wall_bbox):
    wall_polygon = Polygon()
    for i, (x_min, y_min, x_max, y_max) in enumerate(wall_bbox):

        bbox_width = x_max - x_min
        bbox_height = y_max - y_min
        walls = box(x_min, -y_min, (x_min + bbox_width + 2), -(y_min + bbox_height + 2))

        wall_polygon = wall_polygon.union(walls)

    return wall_polygon


def extrude_polygon(polygon, height):
    """Extrait un polygone 2D et l'extrude pour créer une forme 3D."""

    # Vérifier et réparer le polygone si nécessaire
    if not polygon.is_valid:
        polygon = polygon.buffer(0)  # Réparer les polygones invalides

    # # Convertir les coordonnées du polygone en un tableau NumPy
    # vertices = np.array(polygon.exterior.coords)

    # # Ajouter la coordonnée Z aux vertices pour créer une extrusion 3D
    # top_vertices = np.column_stack([vertices, np.full(len(vertices), height)])  # Ajout de la coordonnée Z

    # Créer la mesh 3D en utilisant les faces du haut et du bas
    mesh = trimesh.creation.extrude_polygon(polygon, height, engine="triangle")

    return mesh


def add_texture_to_mesh(mesh, texture_path):
    """
    Ajoute une texture à une mesh en projetant les coordonnées XY.
    """
    from PIL import Image

    texture_image = Image.open(texture_path)

    # UV mapping simple : projection XY (x -> u, y -> v)
    # Normalisation pour être dans [0,1]
    uv = mesh.vertices[:, :2].copy()
    uv -= uv.min(axis=0)
    uv /= uv.ptp(axis=0)  # peak-to-peak = max - min

    # Assignation du visuel
    material = trimesh.visual.material.SimpleMaterial(image=texture_image)
    mesh.visual = trimesh.visual.texture.TextureVisuals(
        uv=uv, image=texture_image, material=material
    )

    return mesh


def create_wall_meshes(polygons, wall_height, real_word_scale):
    """Extrude and merge wall polygons into a single mesh."""
    if not polygons:
        raise ValueError("Aucun polygone à traiter.")

    wall_meshes = []

    for idx, polygon in enumerate(polygons):
        try:
            mesh = extrude_polygon(polygon, height=wall_height)
            mesh.apply_scale(real_word_scale)
            mesh.visual.name = f"Wall_{idx}"
            wall_meshes.append(mesh)
        except Exception as e:
            print(f"Erreur lors de l'extrusion du polygone {idx}: {e}")

    return trimesh.util.concatenate(wall_meshes)
