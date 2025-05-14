from rfdetr import RFDETRBase
from rfdetr.util.coco_classes import COCO_CLASSES
import supervision as sv
import numpy as np
from PIL import Image
import cv2
from my_logger import my_logger

from constants import CHECKPOINTS

my_logger.info("Importation de RFDETR pour la détection d'objets.")


def rfdetr_locally_detection(image_path):
    """Détection d'objets avec RFDETR localement."""
    image = Image.open(image_path).convert("RGB")  # Convertir en format RGB
    # image = cv2.imread(image_path)

    # Définir les classes COCO
    COCO_CLASSES = {
        1: "door",
        2: "wall",
        3: "window",
    }

    # Charger le modèle pré-entraîné
    model = RFDETRBase(
        pretrain_weights=f"{CHECKPOINTS}/cubicasa5k-rfdetr-wall-window-door-v3.pt",
        num_classes=3,
    )

    # Effectuer la prédiction
    detections = model.predict(image, threshold=0.4)

    # Préparer les annotateurs pour dessiner les boîtes et les labels
    color = sv.ColorPalette.from_hex(
        [
            "#ffff00",
            "#ff9b00",
            "#ff8080",
            "#ff66b2",
            "#ff66ff",
            "#b266ff",
            "#9999ff",
            "#3399ff",
            "#66ffff",
            "#33ff99",
            "#66ff66",
            "#99ff00",
        ]
    )

    text_scale = sv.calculate_optimal_text_scale(resolution_wh=image.size)
    thickness = sv.calculate_optimal_line_thickness(resolution_wh=image.size)

    bbox_annotator = sv.BoxAnnotator(color=color, thickness=thickness)
    label_annotator = sv.LabelAnnotator(
        color=color, text_color=sv.Color.BLACK, text_scale=0.5, smart_position=True
    )

    # Créer les labels pour les détections
    labels = [
        f"{COCO_CLASSES[class_id]} {confidence:.2f}"
        for class_id, confidence in zip(detections.class_id, detections.confidence)
    ]

    # Créer une copie de l'image pour l'annotation
    annotated_image = image.copy()

    # Annoter l'image avec les boîtes et les labels
    annotated_image = bbox_annotator.annotate(annotated_image, detections)
    annotated_image = label_annotator.annotate(annotated_image, detections, labels)

    # Afficher l'image annotée
    return detections, annotated_image
