import os
from groq import Groq
import moondream as md
from PIL import Image

# 🔹 SETUP API KEY (Make sure to use your actual API key)
GROQ_API_KEY = "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"  # Replace with your API key

# 🔹 Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# 🔹 Load Moondream model (Ensure correct path)
MODEL_PATH = "F://GAT\MARK//moondream-0_5b-int8.mf"
IMAGE_PATH = "F://GAT\MARK//n.jpeg"

try:
    moondream_model = md.vl(model=MODEL_PATH)
    print("✅ Moondream model loaded successfully!")
except Exception as e:
    print("❌ Error loading Moondream model:", e)
    exit()

# 🔹 Load and process image
try:
    image = Image.open(IMAGE_PATH).resize((224, 224))
    encoded_image = moondream_model.encode_image(image)

    # Generate Caption
    caption = moondream_model.caption(encoded_image)["caption"]
    print("\n🖼️ Caption:", caption)

    # Generate Image Description
    image_description = moondream_model.query(encoded_image, "What's in this image?")["answer"]
    print("\n📸 Image Description:", image_description)
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
        response = moondream_model.query(encoded_image, user_query)["answer"]
        print("🤖 Answer:", response)
    except Exception as e:
        print("❌ Error processing question:", e)
