from .phrase_bank import lookup_phrase, phrase_matches
from .transcribe import transcribe_user_response


def _evaluate_listening(entry, phrase, user_response):
    expected = entry["english"]
    correct = phrase_matches(expected, user_response)
    status = "learned" if correct else "needs_review"
    feedback = (
        "Great job. You understood the Hindi phrase."
        if correct
        else f"Close practice target: '{entry['hindi']}' means '{expected}'."
    )
    return {
        "mode": "question_evaluation",
        "question_type": "listening",
        "correct": correct,
        "status": status,
        "mistake_type": "none" if correct else "meaning",
        "phrase": phrase,
        "expected_english": expected,
        "user_response": user_response,
        "feedback": feedback,
    }


def _evaluate_speaking(entry, phrase, file, status):
    transcript = transcribe_user_response(file)

    if not transcript["ok"]:
        return {
            "mode": "question_evaluation",
            "question_type": "speaking",
            "correct": False,
            "status": status or "needs_review",
            "mistake_type": "pronunciation",
            "phrase": phrase,
            "expected_hindi": entry["hindi"],
            "feedback": (
                "I could not transcribe the audio yet. Check the audio path/API key, "
                "then try this speaking question again."
            ),
            "transcription": transcript,
        }

    heard_hindi = transcript["transcription"]
    heard_english = transcript["translation"]
    correct = phrase_matches(entry["hindi"], heard_hindi) or phrase_matches(
        entry["english"], heard_english
    )
    final_status = "learned" if correct else "needs_review"
    feedback = (
        "Nice work. The response matched the target phrase."
        if correct
        else (
            f"I heard '{heard_hindi}'. Target phrase: '{entry['hindi']}' "
            f"for '{entry['english']}'. Try it more slowly once."
        )
    )
    return {
        "mode": "question_evaluation",
        "question_type": "speaking",
        "correct": correct,
        "status": final_status,
        "mistake_type": "none" if correct else "pronunciation",
        "phrase": phrase,
        "expected_hindi": entry["hindi"],
        "expected_english": entry["english"],
        "heard_hindi": heard_hindi,
        "heard_english": heard_english,
        "feedback": feedback,
        "transcription": transcript,
    }


def evaluate_question(question_type, phrase, user_response=None, file=None, status=None):
    entry = lookup_phrase(phrase)

    if question_type == "listening":
        if not user_response:
            raise ValueError("user_response is required for listening questions")
        return _evaluate_listening(entry, phrase, user_response)

    if question_type == "speaking":
        if not file:
            raise ValueError("file is required for speaking questions")
        return _evaluate_speaking(entry, phrase, file, status)

    raise ValueError("question_type must be either 'speaking' or 'listening'")
