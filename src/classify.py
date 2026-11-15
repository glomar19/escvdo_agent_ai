import torch #motor que ejecuta RNN
from PIL import Image
from transformers import CLIPModel, CLIPProcessor


MODEL = "openai/clip-vit-base-patch32"
#MODEL = "patrickjohncyh/fashion-clip"
model = CLIPModel.from_pretrained(MODEL)
processor = CLIPProcessor.from_pretrained(MODEL)

GARMENTS = {
    "tops": "a simple top, t-shirt, blouse or shirt",
    "bottoms": "trousers, pants, shorts or a skirt",
    "dresses": "a dress",
    "knitwear": "a knitted sweater, cardigan or knit top",
    "outerwear": "a jacket, coat or blazer",
}

def classify_garment(image_path):
    image = Image.open(image_path).convert("RGB")
    texts = [f"a photo of {d}" for d in GARMENTS.values()]
    inputs = processor(text=texts, images=image, return_tensors="pt", padding=True)
    with torch.no_grad():
        probs = model(**inputs).logits_per_image.softmax(dim=1)[0]
    best = probs.argmax().item()
    return list(GARMENTS)[best], round(probs[best].item(), 2)

def get_embedding(image_path):
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        emb = model.get_image_features(**inputs)
    if hasattr(emb, "pooler_output"):
        emb = emb.pooler_output
    emb = emb / emb.norm(dim=-1, keepdim=True)
    return emb[0].numpy()

PATTERNS = {
    "solid": "a plain solid color garment",
    "striped": "a striped garment",
    "checked": "a checked or plaid garment",
    "floral": "a floral print garment",
    "animal print": "an animal print garment",
    "polka dots": "a polka dot garment",
}

def classify_pattern(image_path):
    image = Image.open(image_path).convert("RGB")
    texts = [f"a photo of {d}" for d in PATTERNS.values()]
    inputs = processor(text=texts, images=image, return_tensors="pt", padding=True)
    with torch.no_grad():
        probs = model(**inputs).logits_per_image.softmax(dim=1)[0]
    best = probs.argmax().item()
    return list(PATTERNS)[best], round(probs[best].item(), 2)