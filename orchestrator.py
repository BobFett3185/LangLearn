import json
import os

from dotenv import load_dotenv
from groq import Groq

from tools import (
    evaluate_question,
    generate_question,
    get_memory,
    save_progress,
    speak_phrase,
    teach_phrase,
)
from tools.schemas import TOOL_SCHEMAS


load_dotenv()

MODEL = os.getenv("GROQ_CHAT_MODEL", "llama-3.3-70b-versatile")
DEFAULT_STUDENT_ID = os.getenv("LANGLEARN_STUDENT_ID", "defaultstudent")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are an expert Hindi language tutor focused on spoken language learning.

Core loop:
- First inspect memory with get_memory before choosing what to teach or ask.
- Teach useful spoken Hindi phrases with teach_phrase.
- Play Hindi audio with speak_phrase whenever introducing or drilling a phrase. Only pass exact Hindi text returned by teach_phrase or generate_question; never invent a new Hindi phrase for speak_phrase.
- Generate questions with generate_question. Use question_type='speaking' when the student should say Hindi from English, and question_type='listening' when the student should translate heard Hindi into English.
- Evaluate attempts with evaluate_question. Speaking evaluations use an audio file and listening evaluations use the student's English response.

Important rules:
- The first tool call in a fresh conversation should be get_memory.
- Use memory to choose beginner-friendly phrases and review weak areas.
- The orchestrator automatically saves evaluation results, so do not call save_progress after evaluate_question.
- Use save_progress only when you intentionally want to record a non-evaluation teaching milestone.
- After tool calls are complete, respond to the student with a short, encouraging next step.
- For speaking questions, ask the student to record themselves and paste the audio file path. When the next user message looks like a file path, call evaluate_question with question_type='speaking', the target phrase, and file set to that path.
- For listening questions, ask the student for the English meaning. When the next user message is an English answer, call evaluate_question with question_type='listening', the target phrase, and user_response set to their answer.
- Focus on spoken language. Use romanized Hindi only, such as "namaste" or "aap kaise hain". Do not show Devanagari or any non-Latin script. Never require the student to type in Hindi.
""".strip()

AVAILABLE_FUNCTIONS = {
    "get_memory": get_memory,
    "save_progress": save_progress,
    "teach_phrase": teach_phrase,
    "speak_phrase": speak_phrase,
    "generate_question": generate_question,
    "evaluate_question": evaluate_question,
}

EVALUATION_TOOLS = {
    "evaluate_question",
}


def assistant_message_to_dict(message):
    message_dict = {
        "role": "assistant",
        "content": message.content,
    }
    if message.tool_calls:
        message_dict["tool_calls"] = [
            {
                "id": tool_call.id,
                "type": tool_call.type,
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                },
            }
            for tool_call in message.tool_calls
        ]
    return message_dict


def execute_tool_call(tool_call):
    function_name = tool_call.function.name
    if function_name not in AVAILABLE_FUNCTIONS:
        raise ValueError(f"Unknown tool call: {function_name}")

    function_args = json.loads(tool_call.function.arguments or "{}")
    print(f"\n[tool] {function_name}({function_args})")
    result = AVAILABLE_FUNCTIONS[function_name](**function_args)
    print(f"[result] {result}")
    return function_name, result


def maybe_save_evaluation(function_name, result):
    if function_name not in EVALUATION_TOOLS or not isinstance(result, dict):
        return None

    phrase = result.get("phrase")
    status = result.get("status")
    if not phrase or not status:
        return None

    return save_progress(
        phrase=phrase,
        status=status,
        mistake_type=result.get("mistake_type", "none"),
        student_id=DEFAULT_STUDENT_ID,
        feedback=result.get("feedback"),
    )


def append_tool_result(messages, tool_call, result):
    messages.append(
        {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call.function.name,
            "content": json.dumps(result, ensure_ascii=False),
        }
    )


def run_conversation(messages, user_input, max_tool_rounds=6):
    messages.append({"role": "user", "content": user_input})

    for _ in range(max_tool_rounds):
        response = client.chat.completions.create(
            messages=messages,
            tools=TOOL_SCHEMAS,
            model=MODEL,
            temperature=0.1,
        )
        assistant_message = response.choices[0].message
        messages.append(assistant_message_to_dict(assistant_message))

        if not assistant_message.tool_calls:
            content = assistant_message.content or ""
            if content:
                print(f"\nTutor: {content}")
            return content

        for tool_call in assistant_message.tool_calls:
            function_name, result = execute_tool_call(tool_call)
            auto_save_result = maybe_save_evaluation(function_name, result)
            if auto_save_result:
                result = {
                    "tool_result": result,
                    "auto_save_result": auto_save_result,
                }
                print(f"[auto-save] {auto_save_result}")
            append_tool_result(messages, tool_call, result)

    message = "I hit the tool-call limit for this turn. Try one smaller step."
    messages.append({"role": "assistant", "content": message})
    print(f"\nTutor: {message}")
    return message


def main():
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("Say hi to start the conversation with your Hindi tutor.")
    while True:
        query = input("\nYou: ").strip()
        if query.lower() in {"quit", "exit"}:
            break
        if not query:
            continue
        run_conversation(messages, query)


if __name__ == "__main__":
    main()
