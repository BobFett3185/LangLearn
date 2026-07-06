from .phrase_bank import lookup_phrase


def generate_question(question_type, phrase):
    entry = lookup_phrase(phrase)

    if question_type == "speaking":
        return {
            "mode": "speaking_question",
            "question_type": "speaking",
            "question": f"Say this in Hindi: {entry['english']}",
            "english": entry["english"],
            "expected_hindi": entry["hindi"],
            "answer": entry["hindi"],
            "next_tool_hint": "Use speak_phrase if the student should hear the model pronunciation first.",
        }

    if question_type == "listening":
        return {
            "mode": "listening_question",
            "question_type": "listening",
            "question": "Listen to the Hindi phrase and give the English meaning.",
            "phrase_to_play": entry["hindi"],
            "expected_english": entry["english"],
            "answer": entry["english"],
            "next_tool_hint": "Use speak_phrase with phrase_to_play before asking for the student's answer.",
        }

    raise ValueError("question_type must be either 'speaking' or 'listening'")
