import trimesh
import numpy as np
import os
from walls import create_wall_meshes
from rooms import extract_room_polygons, create_floor_meshes_with_texture
from doors import cut_and_place_doors
from windows import cut_and_place_windows


def generate_3d_model_from_polygons(
    wall_polygons,
    wall_bboxes,
    door_data,
    window_data,
    real_world_scale,
    wall_height,
    floor_textures,
    image_path,
    output_path="floorplan.glb",
    print_output=True,
):
    # print(f"🗞️ Real world scale: {real_world_scale}")
    # # Créer la mesh des murs
    wall_mesh = create_wall_meshes(wall_polygons, wall_height, real_world_scale)

    # Extraire les pièces
    rooms_polygons = extract_room_polygons(wall_polygons)

    # Créer les sols avec les textures
    floor_meshes = create_floor_meshes_with_texture(
        rooms_polygons, wall_mesh, floor_textures, real_world_scale
    )

    # Placer les portes et les fenêtres
    # def cut_and_place_doors(wall_mesh, door_path, doors_bbox, wall_bboxes, door_scale, real_world_scale, image_path):
    if door_data is not None:
        door_path, doors_bbox, door_scale = door_data
        wall_mesh, placed_doors = cut_and_place_doors(
            wall_mesh,
            door_path,
            doors_bbox,
            wall_bboxes.copy(),
            door_scale,
            real_world_scale,
            image_path,
        )
        # wall_mesh, placed_doors = cut_and_place_doors_bbox(
        #     wall_mesh,
        #     doors_bbox,
        #     wall_bboxes.copy(),
        #     real_world_scale,
        #     image_path,
        # )

    else:
        placed_doors = None

    # Placer les fenêtres
    # def cut_and_place_windows(wall_mesh, window_path, windows_bbox, wall_bboxes, wall_height, window_scale, real_world_scale, image_path):
    if window_data is not None:
        window_path, windows_bbox, window_scale = window_data
        wall_mesh, placed_windows = cut_and_place_windows(
            wall_mesh,
            window_path,
            windows_bbox,
            wall_bboxes.copy(),
            wall_height,
            window_scale,
            real_world_scale,
            image_path,
        )
    else:
        placed_windows = None

    meshes = [wall_mesh]

    if floor_meshes is not None:
        meshes.extend(floor_meshes)

    if placed_doors is not None:
        meshes.extend(placed_doors)

    if placed_windows is not None:
        meshes.extend(placed_windows)

    # rotate by 90 degrees all the meshes
    for mesh in meshes:
        mesh.apply_transform(
            trimesh.transformations.rotation_matrix(np.pi / 2, [-1, 0, 0], [0, 0, 0])
        )

    # mesh.apply_transform(
    # # Add texture to the wall mesh
    # texture_path = f"{TEXTURES_FOLDER}/wall.jpg"
    # wall_mesh = meshes[0] = add_texture_to_mesh(wall_mesh, texture_path)

    # On ajoute murs + sols + portes
    scene = trimesh.Scene(meshes)

    # check path
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    scene.export(output_path)

    if print_output:
        print(f"📌 Fichier GLB avec {len(meshes)} objets enregistré : {output_path}")

    return scene
