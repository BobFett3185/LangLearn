import os
import dotenv
from httpx import stream
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)



query = input("Say hi to start the conversation with your Hindi tutor! ")

def run_conversation(query):
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

                    "Other relevant intructions:"
                
                    "The FIRST tool you must ALWAYS call is get_memory.Never call any other tool before get_memory. RIGHT AFTER you call get_memory you MUST call another tool to continue the learning"

                    "When you call get_memory, use the returned information to decide what to teach or ask next. If the student's memory shows they are a beginner with no learned phrases, start with teaching a simple phrase. If they have some learned phrases, use that information to either teach a new phrase at the right level or generate an appropriate question. Always tailor your teaching and questions to the student's current knowledge as shown in their memory."
                    "When evaluating responses, use the information in memory about the student's status on that word to provide feedback. For example, if memory shows the student struggles with saying phrase xyz, focus your feedback on that phrase(s) and consider reteaching with speak_phrase before asking them to try again."
                    "You are either going to call a tool or return some information to the user and wait for their input before calling another tool. "
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
                        "required": []
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
                            
                        },
                        "required": ["phrase"]
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
                            
                            
                        },
                        "required": ["phrase"]
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
                            
                        },
                        "required": ["phrase"]
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
        temperature=0.1, # keep it low for testing...
       # tool_choice = "required", # require the model to call a tool at every step, no plain text responses allowed
    # stream=True,

    )

    ''' Print the incremental deltas returned by the LLM.
    for chunk in stream:

        print(chunk.choices[0].delta.content, end="")

        dont print in stream just do all at once lol

    '''

    from tools import(get_memory, save_progress, teach_phrase, speak_phrase, generate_speaking_question, 
                    generate_listening_question, evaluate_speaking_question, evaluate_listening_question)

    # Map function names to implementations
    available_functions = {
        "get_memory": get_memory,
        "save_progress": save_progress,
        "teach_phrase": teach_phrase,
        "speak_phrase": speak_phrase,
        "generate_speaking_question": generate_speaking_question,
        "generate_listening_question": generate_listening_question,
        "evaluate_speaking_question": evaluate_speaking_question,
        "evaluate_listening_question": evaluate_listening_question
    }
    import json

    def execute_tool_call(tool_call):
        """Parse and execute a single tool call"""
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
        function_args = json.loads(tool_call.function.arguments)
        
        print(f"Executing tool call: {function_name} with arguments {function_args}")

        # Call the function 
        return function_to_call(**function_args)



    tools_called = response.choices[0].message.tool_calls
    #print(tools_called)
    result = execute_tool_call(tools_called[0]) # for now just execute the first tool call, but could loop through if multiple
    print(result )
    print("Done executing tool call, now testing all the tools called\n")

    for tool in tools_called:
        print(f"tool call: {tool.function.name} with arguments {tool.function.arguments}")
        result = execute_tool_call(tool)
        print(result)

while True:
    query = input("You: ")

    resultOfPreviousToolCall = run_conversation(query)
    
    

    run_conversation(f"This is either the result of your previous tool call or a response to you. {query}")




'''
def handle_tool_call(tool_name, tool_args):
    if tool_name == "get_memory":
        return get_memory(**tool_args)
    elif tool_name == "save_progress":
        return save_progress(**tool_args)
    elif tool_name == "teach_phrase":
        return teach_phrase(**tool_args)
    elif tool_name == "speak_phrase":
        return speak_phrase(**tool_args)
    elif tool_name == "generate_speaking_question":
        return generate_speaking_question(**tool_args)
    elif tool_name == "generate_listening_question":
        return generate_listening_question(**tool_args)
    elif tool_name == "evaluate_speaking_question":
        return evaluate_speaking_question(**tool_args)
    elif tool_name == "evaluate_listening_question":
        return evaluate_listening_question(**tool_args)

    

'''