from rfdetr_detection import rfdetr_locally_detection
from constants import OBJ_MODELS, TEXTURES_FOLDER
from bounding_boxes import bbox_pipeline
from walls import generate_wall_polygon_from_bbox
from utils import process_polygons
from generate_model import generate_3d_model_from_polygons
from my_logger import my_logger


def detect_and_generate_3d(image_path: str, scale: float):
    my_logger.info(f"Image path: {image_path}")

    detections, _ = rfdetr_locally_detection(image_path)
    bbox = bbox_pipeline(detections)

    door_path = f"{OBJ_MODELS}/Door.obj"
    window_path = f"{OBJ_MODELS}/Window.obj"
    textures = [f"{TEXTURES_FOLDER}/WoodFloor039.jpg"]
    # textures = [f"{TEXTURES_FOLDER}/carpet.jpg", f"{TEXTURES_FOLDER}/woodFloor.jpg", f"{TEXTURES_FOLDER}/WoodFloor039.jpg"]

    wall_polygon = generate_wall_polygon_from_bbox(bbox["wall_boxes"])
    polygons = process_polygons(wall_polygon)

    output_path = f"outputs/{image_path.split('/')[-1].split('.')[0]}.glb"
    mesh = generate_3d_model_from_polygons(
        polygons=polygons,
        wall_bboxes=bbox["wall_boxes"],
        door_data=(door_path, bbox["door_boxes"], scale * 0.6),
        window_data=(window_path, bbox["window_boxes"], scale * 0.6),
        floor_textures=textures,
        output_path=output_path,
        real_world_scale=scale,
        wall_height=240,
        image_path=image_path,
    )
    return output_path, mesh
