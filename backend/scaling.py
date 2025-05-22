from math import sqrt
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from constants import DATASET
import numpy as np


def show_scale_points_on_image(image_path, point1, point2):
    """Affiche deux points sur une image pour vérifier la distance utilisée comme référence d'échelle."""
    # Charger l'image
    img = mpimg.imread(image_path)
    print(img.shape)

    fig, ax = plt.subplots()
    ax.imshow(img)

    # Tracer les points
    ax.plot(point1[0], point1[1], "ro", label="Point 1")
    ax.plot(point2[0], point2[1], "bo", label="Point 2")

    # Tracer la ligne entre les deux
    ax.plot(
        [point1[0], point2[0]],
        [point1[1], point2[1]],
        "g-",  # label="Distance de référence",
        label="Reference distance",
        linewidth=3,
    )

    # ax.set_title("Vérification des points d'échelle")
    ax.legend(bbox_to_anchor=(-0.2, -0.12), loc="lower left")
    plt.axis("off")
    # plt.axis("equal")
    # plt.grid(True)
    plt.show()


def compute_scale(image_path, point1, point2, real_distance_m):
    """Calcule l'échelle en mètres par pixel."""
    # Charger l'image
    img = mpimg.imread(image_path)

    print(f"Image shape: {img.shape}")
    print("Points:", point1, point2)

    # Calculer la distance en pixels entre les deux points
    pixel_distance = np.linalg.norm(np.array(point2) - np.array(point1))
    print(f"Distance en pixels : {pixel_distance:.2f}")
    # Calculer l'échelle (mètres/pixel)
    scale = real_distance_m / pixel_distance
    print(f"✅ Échelle estimée : {scale:.6f} m/pixel")
    return scale


# image_path = f"{DATASET}/10.png"
# if image_path.endswith("10.png"):
#     point1 = (670, 927)
#     point2 = (920, 927)

#     real_distance_m = 5.0

# elif image_path.endswith("12.png"):
#     point1 = (130, 1200)
#     point2 = (1560, 1200)
#     real_distance_m = 14.33


# # show_scale_points_on_image(image_path, point1, point2)
# scale = compute_scale(image_path, point1, point2, real_distance_m)
