import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import speech_recognition as sr
import pyttsx3
import os
import moondream as md
from groq import Groq
import threading
import time

# Load API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("API key missing! Set 'GROQ_API_KEY' as an environment variable.")

# Initialize Groq AI client
groq_client = Groq(api_key=GROQ_API_KEY)

# Load Moondream model directly (ensure correct path)
MODEL_PATH = "path/to/your/model.xx.mf"  # Replace with the actual model path
moondream_model = md.vl(model=MODEL_PATH)

# Initialize speech recognizer and text-to-speech engine
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Multimedia Assistant")
        self.root.geometry("800x600")
        self.root.configure(bg="#ADD8E6")

        self.speaking = False
        self.conversation_active = False
        self.image_save_path = "images/"
        os.makedirs(self.image_save_path, exist_ok=True)
        self.image_counter = 1

        # Layout
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.video_label = ttk.Label(self.left_frame)
        self.video_label.pack()

        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.text_display = tk.Text(self.right_frame, height=10, width=50, font=("Arial", 12))
        self.text_display.pack(pady=10, fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(self.right_frame)
        button_frame.pack()

        self.caption_button = ttk.Button(button_frame, text="Generate Caption", command=self.generate_caption)
        self.caption_button.grid(row=0, column=0, padx=5)

        self.speak_button = ttk.Button(button_frame, text="Start Conversation", command=self.start_conversation)
        self.speak_button.grid(row=0, column=1, padx=5)

        self.stop_speech_button = ttk.Button(button_frame, text="Stop Speech", command=self.stop_speech)
        self.stop_speech_button.grid(row=0, column=2, padx=5)

        self.save_image_button = ttk.Button(button_frame, text="Save Image", command=self.save_image)
        self.save_image_button.grid(row=0, column=3, padx=5)

        # Start video capture
        self.cap = cv2.VideoCapture(0)
        self.update_video()

    def update_video(self):
        """Updates video feed in Tkinter window"""
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame).resize((240, 160))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        self.root.after(10, self.update_video)

    def save_image(self):
        """Saves the current video frame"""
        if hasattr(self, "current_frame"):
            file_path = os.path.join(self.image_save_path, f"{self.image_counter}.png")
            img = Image.fromarray(cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB))
            img.save(file_path)
            self.image_counter += 1

    def generate_caption(self):
        """Generates and speaks an image caption using the direct Moondream model"""
        ret, frame = self.cap.read()
        if ret:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            encoded_image = moondream_model.encode_image(img)
            caption = moondream_model.caption(encoded_image)["caption"]
            formatted_caption = f"\n📸 **Image Description:**\n{caption}\n"
            self.display_and_speak(formatted_caption)

    def start_conversation(self):
        """Starts a conversation with Groq AI"""
        if self.conversation_active:
            return
        self.conversation_active = True
        self.display_text("🗣️ **Conversation started. Say 'stop' to exit.**")
        threading.Thread(target=self.conversational_loop, daemon=True).start()

    def conversational_loop(self):
        """Handles continuous conversation"""
        conversation_history = []

        while self.conversation_active:
            prompt = self.get_audio_input_with_delay("Speak now or say 'stop' to exit.")
            if not prompt:
                continue
            if prompt.lower() == "stop":
                self.display_text("🛑 **Conversation ended.**")
                self.speak_text("Conversation ended.")
                self.conversation_active = False
                break

            conversation_history.append({"role": "user", "content": prompt})
            try:
                response = groq_client.chat.completions.create(
                    messages=conversation_history, model="llama3-8b-8192", max_tokens=50
                )
                result = response.choices[0].message.content
                conversation_history.append({"role": "assistant", "content": result})
            except Exception as e:
                result = f"Error: {e}"

            self.display_and_speak(f"🗣️ **You:** {prompt}\n🤖 **AI:** {result}")

    def get_audio_input_with_delay(self, prompt_text):
        """Captures audio input and waits for completion"""
        self.speak_text(prompt_text)
        with sr.Microphone() as source:
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = recognizer.recognize_google(audio)
                time.sleep(1)
                return text
            except sr.UnknownValueError:
                return ""
            except sr.RequestError:
                return "Network error."

    def display_and_speak(self, text):
        """Displays text in UI and speaks it"""
        self.text_display.insert(tk.END, text + "\n")
        self.text_display.see(tk.END)
        threading.Thread(target=self.speak_text, args=(text,)).start()

    def speak_text(self, text):
        """Handles speech output asynchronously"""
        if self.speaking:
            return
        self.speaking = True
        def speak():
            tts_engine.say(text)
            try:
                tts_engine.runAndWait()
            except RuntimeError:
                pass
            self.speaking = False
        threading.Thread(target=speak, daemon=True).start()

    def stop_speech(self):
        """Stops speech and conversation"""
        self.speaking = False
        self.conversation_active = False
        tts_engine.stop()
        self.display_text("🛑 **Speech Stopped.**")

    def display_text(self, text):
        """Displays text in UI"""
        self.text_display.insert(tk.END, text + "\n")
        self.text_display.see(tk.END)

    def on_closing(self):
        """Handles cleanup on exit"""
        self.cap.release()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
