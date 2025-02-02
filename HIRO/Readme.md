HIRO is an AI-powered image captioning and chatbot that uses: ✅ Groq's Llama model to answer questions about the image. ✅ Works on CPU-friendly devices like Raspberry Pi 5.

🛠️ Installation 1️⃣ Install Required Dependencies Run the following commands:

pip install torch transformers pillow groq numpy<2 "tokenizers>=0.14,<0.19"

🚀 Usage 1️⃣ Run the Script python boti.py

The script loads an image, generates a caption, and analyzes it. You can ask questions about the image via chatbot. 📷 How It Works 1️⃣ Loads the Image: Reads and preprocesses the image using PIL. 2️⃣ Generates Caption: Uses BLIP from Hugging Face for image-to-text conversion. 3️⃣ Analyzes with AI: Uses Groq's Llama model to check if the image is safe for blind people. 4️⃣ Chatbot Mode: Users can ask follow-up questions about the image.