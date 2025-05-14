from shapely.geometry import box as shapely_box
from shapely.geometry import Polygon
import supervision as sv
import numpy as np


def process_bbox(bounding_boxes: dict, iou_threshold: float = 0.3):
    """
    Applique NMS sur chaque type de boîte (murs, fenêtres, portes).

    Args:
        bounding_boxes (dict): {"wall_boxes": [...], "window_boxes": [...], "door_boxes": [...]}
        iou_threshold (float): Seuil d'IoU pour supprimer les boxes qui se chevauchent.

    Returns:
        dict: bounding_boxes filtré après NMS.
    """

    def nms(boxes, iou_threshold):
        if len(boxes) == 0:
            return []

        boxes = np.array(boxes)
        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]

        areas = (x2 - x1) * (y2 - y1)
        order = areas.argsort()[::-1]

        keep = []

        while order.size > 0:
            idx = order[0]
            keep.append(boxes[idx].tolist())

            xx1 = np.maximum(x1[idx], x1[order[1:]])
            yy1 = np.maximum(y1[idx], y1[order[1:]])
            xx2 = np.minimum(x2[idx], x2[order[1:]])
            yy2 = np.minimum(y2[idx], y2[order[1:]])

            w = np.maximum(0, xx2 - xx1)
            h = np.maximum(0, yy2 - yy1)

            inter = w * h
            iou = inter / (areas[idx] + areas[order[1:]] - inter)

            inds = np.where(iou <= iou_threshold)[0]
            order = order[inds + 1]

        return keep

    filtered_boxes = {}
    for key, boxes in bounding_boxes.items():
        filtered_boxes[key] = nms(boxes, iou_threshold)

    return filtered_boxes


def merge_boxes_dict(
    boxes_dict: dict, iou_threshold: float = 0.1, distance_threshold: int = 80
):

    import numpy as np

    def iou(boxA, boxB):
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])
        interArea = max(0, xB - xA) * max(0, yB - yA)

        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
        union = boxAArea + boxBArea - interArea
        return interArea / union if union > 0 else 0

    def same_orientation(box1, box2):
        w1, h1 = box1[2] - box1[0], box1[3] - box1[1]
        w2, h2 = box2[2] - box2[0], box2[3] - box2[1]
        return (w1 > h1 and w2 > h2) or (h1 >= w1 and h2 >= w2)

    def merge_class_boxes(boxes):
        boxes = [
            list(map(float, b)) for b in boxes
        ]  # Ensure all coordinates are floats
        merged = []

        while boxes:
            base = boxes.pop(0)
            to_merge = [base]

            i = 0
            while i < len(boxes):
                b = boxes[i]
                # Distance between centers
                center_dist = np.linalg.norm(
                    np.array([(base[0] + base[2]) / 2, (base[1] + base[3]) / 2])
                    - np.array([(b[0] + b[2]) / 2, (b[1] + b[3]) / 2])
                )
                if (
                    iou(base, b) > iou_threshold
                    or center_dist < distance_threshold
                    and same_orientation(base, b)
                ):
                    to_merge.append(boxes.pop(i))
                else:
                    i += 1

            to_merge = np.array(to_merge)
            x1 = np.min(to_merge[:, 0])
            y1 = np.min(to_merge[:, 1])
            x2 = np.max(to_merge[:, 2])
            y2 = np.max(to_merge[:, 3])
            merged.append([x1, y1, x2, y2])

        return merged

    # Apply merging to each category in the dictionary
    merged_dict = {}
    for key, box_list in boxes_dict.items():
        if key != "door_boxes" and key != "wall_boxes":
            merged_dict[key] = merge_class_boxes(box_list)
        else:
            merged_dict[key] = box_list
    return merged_dict


def bbox_to_polygon(bbox: list):
    """Convertit une bounding box [xmin, ymin, xmax, ymax] en polygon Shapely."""
    x0, y0, x1, y1 = bbox
    return Polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def remove_door_windows_overlapping(bbox_dict: dict):
    """Supprime les fenêtres et portes qui se chevauchent entre elles."""
    wall_bboxes = bbox_dict["wall_boxes"]
    window_bboxes = bbox_dict["window_boxes"]
    door_bboxes = bbox_dict["door_boxes"]

    # Convertir en Polygones
    wall_polygons = [bbox_to_polygon(wall) for wall in wall_bboxes]
    window_polygons = [bbox_to_polygon(window) for window in window_bboxes]
    door_polygons = [bbox_to_polygon(door) for door in door_bboxes]

    valid_windows = []
    valid_doors = []

    for i, win_poly in enumerate(window_polygons):
        overlap_with_door = any(
            win_poly.intersects(door_poly) for door_poly in door_polygons
        )
        if not overlap_with_door:
            valid_windows.append(window_bboxes[i])

    for i, door_poly in enumerate(door_polygons):
        overlap_with_window = any(
            door_poly.intersects(win_poly) for win_poly in window_polygons
        )
        if not overlap_with_window:
            valid_doors.append(door_bboxes[i])

    number_of_doors_remove = len(door_bboxes) - len(valid_doors)
    number_of_windows_remove = len(window_bboxes) - len(valid_windows)

    if number_of_doors_remove > 0:
        print(f"Removed {number_of_doors_remove} overlapping doors")
    if number_of_windows_remove > 0:
        print(f"Removed {number_of_windows_remove} overlapping windows")

    return {
        "wall_boxes": wall_bboxes,
        "window_boxes": valid_windows,
        "door_boxes": valid_doors,
    }


def remove_door_or_window_without_between_wall(bbox_dict: dict):
    """Supprime les portes ou fenêtres qui ne touchent aucun mur."""
    wall_bboxes = bbox_dict["wall_boxes"]
    door_bboxes = bbox_dict["door_boxes"]
    window_bboxes = bbox_dict["window_boxes"]

    wall_polygons = [bbox_to_polygon(wall) for wall in wall_bboxes]
    door_polygons = [bbox_to_polygon(door) for door in door_bboxes]
    window_polygons = [bbox_to_polygon(win) for win in window_bboxes]

    valid_doors = []
    for i, door_poly in enumerate(door_polygons):
        touches_wall = any(
            door_poly.intersects(wall_poly) for wall_poly in wall_polygons
        )
        if touches_wall:
            valid_doors.append(door_bboxes[i])

    valid_windows = []
    for i, win_poly in enumerate(window_polygons):
        touches_wall = any(
            win_poly.intersects(wall_poly) for wall_poly in wall_polygons
        )
        if touches_wall:
            valid_windows.append(window_bboxes[i])

    number_of_doors_remove = len(door_bboxes) - len(valid_doors)
    number_of_windows_remove = len(window_bboxes) - len(valid_windows)

    if number_of_doors_remove > 0:
        print(f"Removed {number_of_doors_remove} doors not touching walls")

    if number_of_windows_remove > 0:
        print(f"Removed {number_of_windows_remove} windows not touching walls")

    return {
        "wall_boxes": wall_bboxes,
        "door_boxes": valid_doors,
        "window_boxes": valid_windows,
    }


from shapely.geometry import box as shapely_box


def remove_door_windows_not_in_wall(bbox: dict, iou_threshold: float = 1e-2):
    """
    Supprime les portes et fenêtres qui ne sont pas du tout placées sur un mur
    en vérifiant l'intersection (IOU) entre leurs bounding boxes et les murs.

    Paramètres :
        bbox (dict) : Dictionnaire contenant les clés "wall_boxes", "door_boxes", "window_boxes"
        iou_threshold (float) : Seuil minimum d'intersection pour considérer une porte/fenêtre comme valide.

    Retour :
        dict : bbox mis à jour
    """

    def has_overlap(candidate_bbox, wall_bboxes):
        c_box = shapely_box(*candidate_bbox)
        for wall_bbox in wall_bboxes:
            w_box = shapely_box(*wall_bbox)
            inter_area = c_box.intersection(w_box).area
            union_area = c_box.union(w_box).area
            if union_area > 0 and (inter_area / union_area) > iou_threshold:
                return True
        return False

    wall_bboxes = bbox.get("wall_boxes", [])
    original_door_count = len(bbox.get("door_boxes", []))
    original_window_count = len(bbox.get("window_boxes", []))

    bbox["door_boxes"] = [
        door for door in bbox.get("door_boxes", []) if has_overlap(door, wall_bboxes)
    ]

    bbox["window_boxes"] = [
        window
        for window in bbox.get("window_boxes", [])
        if has_overlap(window, wall_bboxes)
    ]

    print(
        f"Removed {original_door_count - len(bbox['door_boxes'])} doors and {original_window_count - len(bbox['window_boxes'])} windows not placed on walls."
    )

    return bbox


def remove_alone_walls_not_attached_to_another_wall(
    bbox: dict, distance_threshold: int = 5
):
    """
    Supprime les murs qui ne sont pas connectés (ou proches) d'au moins un autre mur.
    :param bbox: dictionnaire contenant bbox["wall_boxes"]
    :param distance_threshold: distance max (en pixels ou mètres selon ton unité) pour considérer un mur comme attaché
    :return: bbox mis à jour avec les murs seuls supprimés
    """
    wall_boxes = bbox["wall_boxes"]
    kept_walls = []

    for i, box_i in enumerate(wall_boxes):
        poly_i = shapely_box(*box_i)
        attached = False

        for j, box_j in enumerate(wall_boxes):
            if i == j:
                continue
            poly_j = shapely_box(*box_j)
            if (
                poly_i.intersects(poly_j)
                or poly_i.distance(poly_j) < distance_threshold
            ):
                attached = True
                break

        if attached:
            kept_walls.append(box_i)
        else:
            print(f"Removed isolated wall: {box_i}")

    bbox["wall_boxes"] = kept_walls
    return bbox


def apply_bbox_pipeline(bbox: list, steps: list):
    for func in steps:
        bbox = func(bbox)
    return bbox


def bbox_pipeline(detections: sv.Detections):
    pipeline = [
        # process_bbox,
        merge_boxes_dict,
        remove_door_windows_overlapping,
        remove_door_or_window_without_between_wall,
        remove_door_windows_not_in_wall,
        remove_alone_walls_not_attached_to_another_wall,
    ]

    bbox = {
        "door_boxes": detections.xyxy[detections.class_id == 1].tolist(),
        "wall_boxes": detections.xyxy[detections.class_id == 2].tolist(),
        "window_boxes": detections.xyxy[detections.class_id == 3].tolist(),
    }

    bbox = apply_bbox_pipeline(bbox, pipeline)

    # bbox = scale_bbox(bbox, scale)

    # Combine all bounding boxes into a single NumPy array
    all_boxes = bbox["door_boxes"] + bbox["window_boxes"] + bbox["wall_boxes"]
    all_boxes_class_id = (
        [0] * len(bbox["door_boxes"])
        + [1] * len(bbox["window_boxes"])
        + [2] * len(bbox["wall_boxes"])
    )
    all_boxes_labels = (
        ["Door"] * len(bbox["door_boxes"])
        + ["Window"] * len(bbox["window_boxes"])
        + ["Wall"] * len(bbox["wall_boxes"])
    )

    windows_doors_bbox = bbox["window_boxes"] + bbox["door_boxes"]
    windows_doors_class_id = [0] * len(bbox["window_boxes"]) + [1] * len(
        bbox["door_boxes"]
    )
    windows_doors_labels = ["Window"] * len(bbox["window_boxes"]) + ["Door"] * len(
        bbox["door_boxes"]
    )

    window_bbox = bbox["window_boxes"]
    window_class_id = [0] * len(bbox["window_boxes"])
    window_labels = ["Window"] * len(bbox["window_boxes"])

    door_bbox = bbox["door_boxes"]
    door_class_id = [1] * len(bbox["door_boxes"])
    door_labels = ["Door"] * len(bbox["door_boxes"])

    detr_detections = sv.Detections(
        xyxy=np.array(all_boxes),
        class_id=np.array(all_boxes_class_id),
    )

    box_annotator = sv.BoxAnnotator(color_lookup=sv.ColorLookup.INDEX)
    label_annotator = sv.RichLabelAnnotator()

    # annotated_image = box_annotator.annotate(
    #     scene=image.copy(), detections=detr_detections
    # )
    # annotated_image = label_annotator.annotate(
    #     scene=annotated_image, detections=detr_detections, labels=all_boxes_labels
    # )

    # sv.plot_images_grid(
    #     images=[image, annotated_image],
    #     grid_size=(1, 2),
    #     size=(40, 40),
    #     titles=["Original image", "Annotated image"],
    # )

    return bbox
