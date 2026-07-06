from .phrase_bank import lookup_phrase


def teach_phrase(phrase, status="not_learned"):
    entry = lookup_phrase(phrase)
    return {
        "mode": "teach",
        "status": status,
        "english": entry["english"],
        "hindi": entry["hindi"],
        "pronunciation_tip": f"Practice saying: {entry['hindi']}",
        "breakdown": entry["breakdown"],
        "student_prompt": (
            f"Listen to '{entry['hindi']}', then try saying it back out loud."
        ),
    }

