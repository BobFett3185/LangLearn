'''
This has all the logic for taking an audio file, transcribing it and translating it using groq api. 

this result will be given back to the orchstrator to be used as part of the evaluation of the speaking question.

This was the tricky part of evaluation because the model needs to listen to the users response and then translate and transcribe to 
compare with the original phrase and critique pronunciation and correctness. 

'''

def evaluate_speaking_question(audio_file):
    
    import os
    import dotenv
    from httpx import stream
    from groq import Groq
    from dotenv import load_dotenv
    load_dotenv()

    client = Groq(
        api_key=os.getenv("GROQ_API_KEY"),
    )


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




def generate_speaking_question(phrase):
    #stub - return fake question for now
    return {
        "question": f"Please say the following phrase in Hindi: '{phrase}'",
        "answer": phrase
    }