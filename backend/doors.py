import trimesh
from utils import load_mesh_safe, find_best_wall_by_intersection
import numpy as np


def generate_door_cut_or_instance(
    x_min,
    y_min,
    x_max,
    y_max,
    door_model,
    door_scale,
    real_world_scale,
    mode,
    wall_bbox,
):
    """Génère un box pour découper ou une instance de porte à placer."""
    door_model = door_model.copy()

    # Calculs de base
    x_center = ((x_min + x_max) / 2) * real_world_scale
    y_center = ((y_min + y_max) / 2) * real_world_scale
    width_bbox = x_max - x_min
    height_bbox = y_max - y_min
    is_vertical = height_bbox > width_bbox

    if mode == "cut":
        # Taille du modèle porte
        door_size = door_model.bounds[1] - door_model.bounds[0]
        door_height = door_size[2] * door_scale
        door_width = door_size[0] * door_scale

        # Calcul dynamique de l'épaisseur du mur à cet endroit
        if wall_bbox is not None:
            wxmin, wymin, wxmax, wymax = wall_bbox
            depth = (
                abs(wxmax - wxmin) * real_world_scale
                if is_vertical
                else abs(wymax - wymin) * real_world_scale
            )
            depth += 15 * real_world_scale  # Ajout d'une marges
        else:
            depth = 40 * real_world_scale  # fallback

        # Créer la box pour la découpe
        box = trimesh.creation.box(extents=(door_width, depth, door_height))
        if is_vertical:
            box.apply_transform(
                trimesh.transformations.rotation_matrix(np.radians(90), [0, 0, 1])
            )
        box.apply_translation((x_center, -y_center, door_height / 2))
        return box

    elif mode == "instance":
        door_instance = door_model.copy()
        door_instance.apply_scale(door_scale)
        if is_vertical:
            door_instance.apply_transform(
                trimesh.transformations.rotation_matrix(np.radians(90), [0, 0, 1])
            )
        door_instance.apply_translation((x_center, -y_center, 0.01))
        return door_instance


def cut_and_place_doors(
    wall_mesh,
    door_path,
    doors_bbox,
    wall_bboxes,
    door_scale,
    real_world_scale,
    image_path,
):
    """Découpe les murs et place les portes à partir des bbox de portes et murs."""
    door_model = load_mesh_safe(door_path)

    cut_boxes = []
    placed_doors = []

    for i, door_bbox in enumerate(doors_bbox):
        # wall_idx = find_corresponding_wall_bbox(door_bbox, wall_bboxes)
        wall_idx = find_best_wall_by_intersection(
            door_bbox,
            wall_bboxes,
            element_type="door",
            image_path=image_path,
            visualize=False,
        )
        wall_bbox = wall_bboxes[wall_idx] if wall_idx is not None else None

        # Générer la box de découpe
        box_cut = generate_door_cut_or_instance(
            *door_bbox,
            door_model,
            door_scale,
            real_world_scale,
            mode="cut",
            wall_bbox=wall_bbox,
        )
        cut_boxes.append(box_cut)

        # Générer l'instance porte
        door_instance = generate_door_cut_or_instance(
            *door_bbox,
            door_model,
            door_scale,
            real_world_scale,
            mode="instance",
            wall_bbox=wall_bbox,
        )
        door_instance.visual.name = f"Door_{i}"
        placed_doors.append(door_instance)

    if cut_boxes:
        cut_union = trimesh.util.concatenate(cut_boxes)
        wall_mesh = trimesh.boolean.boolean_manifold(
            [wall_mesh, cut_union], operation="difference", check_volume=False
        )

    return wall_mesh, placed_doors
