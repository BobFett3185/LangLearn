import os

import dotenv
from httpx import stream

from groq import Groq
from dotenv import load_dotenv
load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)
'''
query = input("Enter your query: ")

stream = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": query,
        }
    ],
    model="llama-3.3-70b-versatile",

    #optional parameters
    temperature=0.7,
    stream=True,

)
# Print the incremental deltas returned by the LLM.
for chunk in stream:
    print(chunk.choices[0].delta.content, end="")
#print(chat_completion.choices[0].message.content)
'''


# we need to load in an audio file 

filename = os.path.dirname(__file__) + "/test2.m4a"

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


print(f"Transcription: {transcription.text}")
print(f"Translation: {translation.text}")

