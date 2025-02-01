import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
from groq import Groq

# 🔹 SETUP API KEY (Replace with your actual API key)
GROQ_API_KEY = "key"

# 🔹 Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# 🔹 Load Hugging Face BLIP model (Image Captioning)
device = "cuda" if torch.cuda.is_available() else "cpu"
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)

# 🔹 Load and process image
IMAGE_PATH = "image_path.jpeg"
try:
    image = Image.open(IMAGE_PATH).convert("RGB")
    inputs = processor(image, return_tensors="pt").to(device)

    # Generate Caption
    with torch.no_grad():
        caption_ids = model.generate(**inputs)
        caption = processor.decode(caption_ids[0], skip_special_tokens=True)
    
    print("\n🖼️ Caption:", caption)
except Exception as e:
    print("❌ Error processing image:", e)
    exit()

# 🔹 Ask Groq AI: Is the image safe for a blind person?
prompt = f"Caption: {caption}. Based on this, is this image okay for a blind person to navigate safely?"
try:
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    print("\n🤖 Groq AI Response:", chat_completion.choices[0].message.content)
except Exception as e:
    print("❌ Error querying Groq model:", e)

# 🔹 Chatbot: Ask more questions about the image
while True:
    user_query = input("\n❓ Ask a question about the image (or type 'exit' to quit): ")
    if user_query.lower() == "exit":
        print("👋 Exiting chatbot. Have a great day!")
        break

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": f"Based on this caption: '{caption}', {user_query}"}],
            model="llama-3.3-70b-versatile",
        )
        print("🤖 Answer:", response.choices[0].message.content)
    except Exception as e:
        print("❌ Error processing question:", e)
