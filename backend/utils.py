import trimesh
import matplotlib.pyplot as plt
from shapely.geometry import (
    box as shapely_box,
    MultiPolygon,
    GeometryCollection,
    Polygon,
)
import matplotlib.patches as patches
import matplotlib.image as mpimg


def process_polygons(polygons):
    if isinstance(polygons, MultiPolygon):
        return list(polygons.geoms)
    elif isinstance(polygons, GeometryCollection):
        return [geom for geom in polygons.geoms if isinstance(geom, Polygon)]
    else:
        return [polygons]


def load_mesh_safe(path):
    mesh = trimesh.load(path)
    if isinstance(mesh, trimesh.Scene):
        mesh = trimesh.util.concatenate([geom for geom in mesh.geometry.values()])
    return mesh


def bbox_intersection_area(bbox1, bbox2):
    """Calcule l'aire de l'intersection entre deux bounding boxes."""
    if len(bbox1) > 5 or len(bbox2) > 5:
        raise ValueError(
            f"Bounding boxes must be in the format [x0, y0, x1, y1] but got {bbox1} and {bbox2}"
        )

    poly1 = shapely_box(*bbox1)
    poly2 = shapely_box(*bbox2)
    return poly1.intersection(poly2).area


def find_best_wall_by_intersection(
    element_bbox,
    wall_bboxes,
    image_path=None,
    element_type="door",
    show_all_walls=True,
    visualize=True,
):
    """
    Trouve le mur qui a le plus grand chevauchement avec un élément (porte ou fenêtre).
    Peut afficher les résultats si visualize=True.
    """
    max_intersection = 0
    best_idx = None
    for idx, wall_bbox in enumerate(wall_bboxes):
        area = bbox_intersection_area(element_bbox, wall_bbox)
        if area > max_intersection:
            max_intersection = area
            best_idx = idx

    if best_idx is None:
        print("Aucune intersection trouvée.")
        return None

    best_wall_bbox = wall_bboxes[best_idx]

    if visualize:
        print(
            f"Best wall index: {best_idx} with area: {max_intersection} and bbox {best_wall_bbox} for {element_type} {element_bbox}"
        )

    if not visualize:
        return best_idx

    # Plot
    fig, ax = plt.subplots()

    # Show background image if given
    if image_path is not None:
        img = mpimg.imread(image_path)
        ax.imshow(img, origin="upper")

    # Optionally show all wall bboxes
    if show_all_walls:
        for wall_bbox in wall_bboxes:
            x0, y0, x1, y1 = wall_bbox
            rect = patches.Rectangle(
                (x0, y0),
                x1 - x0,
                y1 - y0,
                linewidth=1,
                edgecolor="gray",
                facecolor="none",
                alpha=0.3,
            )
            ax.add_patch(rect)

    # Element bbox (red or blue)
    x0_e, y0_e, x1_e, y1_e = element_bbox
    element_color = "red" if element_type == "door" else "blue"
    element_label = "Door" if element_type == "door" else "Window"

    element_rect = patches.Rectangle(
        (x0_e, y0_e),
        x1_e - x0_e,
        y1_e - y0_e,
        edgecolor=element_color,
        facecolor="none",
        linewidth=2,
        label=element_label,
    )
    ax.add_patch(element_rect)

    # Best wall bbox (green)
    x0_w, y0_w, x1_w, y1_w = best_wall_bbox
    wall_rect = patches.Rectangle(
        (x0_w, y0_w),
        x1_w - x0_w,
        y1_w - y0_w,
        edgecolor="green",
        facecolor="none",
        linewidth=2,
        label="Best Wall",
    )
    ax.add_patch(wall_rect)

    # Zoom on area
    margin = 50
    x_min = min(x0_e, x0_w) - margin
    x_max = max(x1_e, x1_w) + margin
    y_min = min(y0_e, y0_w) - margin
    y_max = max(y1_e, y1_w) + margin
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_max, y_min)  # origin='upper' image

    ax.set_aspect("equal")
    ax.legend()
    ax.set_title(f"{element_label} and Best Matching Wall")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return best_idx
