import os
import dotenv
from httpx import stream
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

def transcribe_user_response(filename):
    # load an audio file for testing
    filename = r"C:\Users\kdfer\Desktop\CSProjects\LangLearn\LangLearn\audiofiles\test2.m4a"
    #filename = os.path.dirname(__file__) + "/audiofiles/test2.m4a"
    print(f"Using audio file: {filename}")


    # function for transrbing and translating audio using the Groq API
    def transcribe_and_translate_audio(filename):
        with open(filename, "rb") as f:
            translation = client.audio.translations.create(
            
                model="whisper-large-v3",
                file=(filename, f.read()), # Required audio file
                prompt="this is a hindi phrase, translate it to english, and critique on pronunciation and correctness.",  # Optional
            # language="hi", # Optional ('en' only)
                response_format="json",  # Optional
            # temperature=0.0  # Optiona

            )

        with open(filename, "rb") as f:
            transcription = client.audio.transcriptions.create(
            
                model="whisper-large-v3",
                file=(filename, f.read()), # Required audio file
                prompt="transcribe this users response from hindi to english, and critique on pronunciation and correctness.",  # Optional
                #language="en", # Optional ('en' only)
                response_format="json",  # Optional
            # temperature=0.0  # Optional

            )
        return translation.text, transcription.text
    ''' 
    translation, transcription = transcribe_and_translate_audio(filename)
    print(f"Transcription: {transcription}")
    print(f"Translation: {translation}")

    '''