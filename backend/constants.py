import os
from my_logger import my_logger

paths = []
DATASET = "./floorplan_dataset"
CHECKPOINTS = "./checkpoints"
TEXTURES_FOLDER = "./textures"
OBJ_MODELS = "./3D_models"

paths.extend([DATASET, CHECKPOINTS, TEXTURES_FOLDER, OBJ_MODELS])

for path in paths:
    if os.path.exists(path):
        # print(f"✅ {path} exist")
        my_logger.info(f"✅ {path} exist")
    else:
        raise RuntimeError(f"{path} does not exist")
# print(DATASET, CHECKPOINTS, TEXTURES_FOLDER)
# print("✅ Code executed with success")
# my_logger.info("✅ Code executed with success")
