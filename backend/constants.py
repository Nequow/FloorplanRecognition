import os
from my_logger import my_logger

paths = []
DATASET = "./Floor plan dataset"
CHECKPOINTS = "./checkpoints"
TEXTURES_FOLDER = "./Textures"
OBJ_MODELS = "./3D Models"

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
