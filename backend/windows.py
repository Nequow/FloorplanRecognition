import trimesh
import numpy as np
from utils import load_mesh_safe, find_best_wall_by_intersection


def generate_window_cut_or_instance(
    x_min,
    y_min,
    x_max,
    y_max,
    window_model,
    window_scale,
    window_offset,
    wall_height,
    real_world_scale,
    mode,
    wall_bbox,
):
    """Génère un box pour découper ou une instance de porte à placer."""
    window_model = window_model.copy()

    x_center = ((x_min + x_max) / 2) * real_world_scale
    y_center = ((y_min + y_max) / 2) * real_world_scale

    width_bbox = x_max - x_min
    height_bbox = y_max - y_min

    is_vertical = height_bbox > width_bbox

    up = (wall_height / 2) * real_world_scale

    window_size = window_model.bounds[1] - window_model.bounds[0]
    window_height = window_size[2] * window_scale
    window_width = window_size[0] * window_scale

    if mode == "cut":
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

        # print(f"Depth: {depth}")
        box = trimesh.creation.box(extents=(window_width, depth, window_height))
        if is_vertical:
            box.apply_transform(
                trimesh.transformations.rotation_matrix(np.radians(90), [0, 0, 1])
            )
        box.apply_translation((x_center, -y_center, up))
        return box

    elif mode == "instance":
        window_instance = window_model.copy()
        # change size of the door based on real_world_scale
        window_instance.apply_scale(window_scale)
        if is_vertical:
            window_instance.apply_transform(
                trimesh.transformations.rotation_matrix(np.radians(90), [0, 0, 1])
            )
        window_instance.apply_translation((x_center, -y_center, up + window_offset))
        return window_instance


def cut_and_place_windows(
    wall_mesh,
    window_path,
    windows_bbox,
    wall_bboxes,
    wall_height,
    window_scale,
    real_world_scale,
    image_path,
):
    """Découpe les murs et place les portes."""
    window_model = load_mesh_safe(window_path)

    if "small" in window_path.lower():
        window_offset = 0.1
    else:
        window_offset = -0.02

    cut_boxes = []
    placed_window = []

    for i, bbox in enumerate(windows_bbox):
        wall_idx = find_best_wall_by_intersection(
            bbox,
            wall_bboxes,
            element_type="window",
            image_path=image_path,
            visualize=False,
        )
        wall_bbox = wall_bboxes[wall_idx] if wall_idx is not None else None

        # Générer le trou
        box_cut = generate_window_cut_or_instance(
            *bbox,
            window_model,
            window_scale,
            window_offset,
            wall_height,
            real_world_scale,
            mode="cut",
            wall_bbox=wall_bbox,
        )
        cut_boxes.append(box_cut)

        # # Générer l'instance
        window_instance = generate_window_cut_or_instance(
            *bbox,
            window_model,
            window_scale,
            window_offset,
            wall_height,
            real_world_scale,
            mode="instance",
            wall_bbox=wall_bbox,
        )

        window_instance.visual.name = f"Window_{i}"
        placed_window.append(window_instance)

    if cut_boxes:
        cut_union = trimesh.util.concatenate(cut_boxes)
        wall_mesh = trimesh.boolean.boolean_manifold(
            [wall_mesh, cut_union], operation="difference", check_volume=False
        )
    return wall_mesh, placed_window
