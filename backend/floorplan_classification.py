import open_clip
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile
import torchvision.transforms as T
from PIL import Image
from constants import CHECKPOINTS
import torch
import io


# Load the model
model_path = f"{CHECKPOINTS}/Best_EfficientNet_B0.pt"
model = torch.load(model_path, weights_only=False)
model.eval()

classes = ["other", "floor plan"]  # For all models except Roboflow2+random.pt
# classes = ["floor plan", "other"]  # for Roboflow2+random.pt


def transform_image(image_bytes):
    transform = T.Compose(
        [
            T.Resize((640, 640)),
            T.ToTensor(),
            T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return transform(image).unsqueeze(0)


def process_image(image_bytes, model):
    img = transform_image(image_bytes)
    output = model(img)
    _, predicted = torch.max(output, 1)
    return {"class": classes[predicted.item()]}


def ViT(image_bytes):
    model, _, preprocess = open_clip.create_model_and_transforms(
        "ViT-B-32", pretrained="laion2b_s34b_b79k"
    )
    model.eval()  # model in train mode by default, impacts some models with BatchNorm or stochastic depth active
    tokenizer = open_clip.get_tokenizer("ViT-B-32")

    image = preprocess(Image.open(io.BytesIO(image_bytes))).unsqueeze(0)
    text = tokenizer(classes)

    with torch.no_grad():
        image_features = model.encode_image(image)
        text_features = model.encode_text(text)
        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)

        text_probs = (100.0 * image_features @ text_features.T).softmax(dim=-1)
        _, predicted = torch.max(text_probs, 1)

    return {"class": classes[predicted.item()]}


def cocaViT(image_bytes):
    model, _, transform = open_clip.create_model_and_transforms(
        model_name="coca_ViT-L-14", pretrained="mscoco_finetuned_laion2B-s13B-b90k"
    )
    im = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    im = transform(im).unsqueeze(0)
    tokenizer = open_clip.get_tokenizer("coca_ViT-L-14")
    text = tokenizer(classes)
    with torch.no_grad():
        # generated = model.generate(im)
        image_features = model.encode_image(im)
        text_features = model.encode_text(text)
        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)
        text_probs = (100.0 * image_features @ text_features.T).softmax(dim=-1)
        _, predicted = torch.max(text_probs, 1)
        return {"class": classes[predicted.item()]}
