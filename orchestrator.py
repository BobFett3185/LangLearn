import os
import dotenv
from httpx import stream
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)



query = input("Enter your query: ")

response = client.chat.completions.create(
    messages=[
        {   
            
            "role": "system",
            "content": "You are an expert Hindi language tutor focused on spoken language learning. You operate in three modes: "
                "Teach Mode — call get_memory to check what the student knows, then call teach_phrase to introduce a new phrase appropriate for their level, then call speak_phrase so they can hear correct pronunciation."
                "Question Mode — two question types. Type 1: call generate_speaking_question to give the student an English phrase to speak back in Hindi, then call speak_phrase so they hear it first. Type 2: call generate_listening_question then call speak_phrase to play a Hindi phrase, student types the english translation"
                "Evaluate Mode — after every attempt call the appropriate evaluation tool to grade the response. If correct call save_progress and move on. If close retry by calling speak_phrase again. If completely wrong call teach_phrase to reteach with a full breakdown, then retry. Use the grade_pronunciation tool to evaluate pronunciation and correctness of the user's spoken response to a question."
                "Rules you must always follow:  Always call a tool, never respond with plain text , Always call get_memory before deciding what to teach or ask, Always call save_progress after every evaluation"
                "Focus entirely on spoken language, never ask the student to type in Hindi. Assume the student is an absolute beginner unless memory says otherwise. Be encouraging, patient, and specific in feedback"
        },

        {
            "role": "user",
            "content": query,
        }
    ],
    tools =[
        {
            "type": "function", # tool for checking the student's current knowledge
            "function": {
                "name": "get_memory",
                "description": "Check the student's current knowledge",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "student_id": {
                            "type": "string",
                            "description": "The ID of the student"
                        }
                    },
                    "required": ["student_id"]
                }
            }
        },

    #------------------------------------------------------------

        {
            "type": "function", # tool schema for saving progress after a step 
            "function": {
                "name": "save_progress",
                "description": "Save the student's progress after an evaluation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phrase": {
                            "type": "string",
                            "description": "The phrase being evaluated"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["learned", "needs_review", "not_learned"],
                            "description": "The learning status of the phrase"
                        },
                        "mistake_type": {
                            "type": "string",
                            "enum": ["pronunciation", "meaning", "none"],
                            "description": "Type of mistake the student made if any"
                        }
                    },
                    "required": ["phrase", "status"]
                }
            }
        }, 

        #------------------------------------------------------------

        {
            "type": "function", # tool schema for teaching a phrase to the student
            "function": {
                "name": "teach_phrase",
                "description": "Teach a phrase to the student",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phrase": {
                            "type": "string",
                            "description": "The phrase being taught"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["learned", "needs_review", "not_learned"],
                            "description": "The learning status of the phrase"
                        }
                    },
                    "required": ["phrase", "status"]
                }
            }
        }, #------------------------------------------------------------

        {
            # tool schema for speaking a phrase for the user to hear
            "type": "function", 
            "function": {
                "name": "speak_phrase",
                "description": "Speak a phrase for the user to hear",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phrase": {
                            "type": "string",
                            "description": "The phrase being spoken for the user to hear"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["learned", "needs_review", "not_learned"],
                            "description": "The learning status of the phrase"
                        }
                    },
                    "required": ["phrase", "status"]
                }
            }
        }, #------------------------------------------------------------

        {
            # tool schema for generating a speaking question for the user to answer
            "type": "function", 
            "function": {
                "name": "generate_speaking_question",
                "description": "Generate a speaking question for the user to answer",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phrase": {
                            "type": "string",
                            "description": "The phrase which the user will be asked to speak back in Hindi"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["learned", "needs_review", "not_learned"],
                            "description": "The learning status of the phrase"
                        },
                        
                    },
                    "required": ["phrase", "status"]
                }
            }
        }, #------------------------------------------------------------

        {
            # tool schema for generating a listening question for the user to answer
            "type": "function", 
            "function": {
                "name": "generate_listening_question",
                "description": "Generate a listening question for the user to answer. It will be spoken in hindi and user responds in english",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phrase": {
                            "type": "string",
                            "description": "The Hindi phrase being spoken for the user to listen to and respond in English"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["learned", "needs_review", "not_learned"],
                            "description": "The learning status of the phrase"
                        },
                    },
                    "required": ["phrase", "status"]
                }
            }
        }, #------------------------------------------------------------

        {
            # tool schema for evaluating the user's spoken response to a question
            "type": "function", 
            "function": {
                "name": "evaluate_speaking_question",
                "description": "Evaluate the user's spoken response to a question",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phrase": {
                            "type": "string",
                            "description": "The english phrase the user was asked to speak in Hindi"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["learned", "needs_review", "not_learned"],
                            "description": "The learning status of the phrase"
                        },
                        "file": {
                            "type": "string",
                            "description": "Path to the audio file containing the user's spoken response"
                        }
                    },
                    "required": ["phrase", "file"]
                }
            }
        }, #------------------------------------------------------------

        {
            # tool schema for evaluating the user's translation of a spoken hindi phrase
            "type": "function", 
            "function": {
                "name": "evaluate_listening_question",
                "description": "Evaluate the user's translation of a spoken Hindi phrase",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phrase": {
                            "type": "string",
                            "description": "The Hindi phrase being spoken for the user to listen to and translate in English"
                        },
                        "user_response": {
                            "type": "string",
                            "description": "The user's translation of the spoken Hindi phrase"
                        }
                    },
                    "required": ["phrase", "user_response"]
                }
            }
        }, #------------------------------------------------------------

        {
            #grade response tool schema for evalution of pronunciation and correctness of a user's spoken response to a question
            "type": "function", 
            "function": {
                "name": "grade_pronunciation",
                "description": "Evaluate the pronunciation and correctness of the user's spoken response to a question",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phrase": {
                            "type": "string",
                            "description": "The english phrase being evaluated "
                        },
                        "file": {
                            "type": "string",
                            "description": "Path to the audio file containing the user's spoken response"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["learned", "needs_review", "not_learned"],
                            "description": "The learning status of the phrase"
                        },
                        
                    },
                    "required": ["phrase", "file", "status"]
                }
            }
        }, 

    
    ],
    model="llama-3.3-70b-versatile", # calling our LLM

    #optional parameters
    temperature=0.7,
    stream=True,

)
''' Print the incremental deltas returned by the LLM.
for chunk in stream:

    print(chunk.choices[0].delta.content, end="")

    dont print in stream just do all at once lol

'''
print(response.choices[0].message.content)

