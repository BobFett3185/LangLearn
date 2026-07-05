from .memory_store import upsert_progress


VALID_STATUSES = {"learned", "needs_review", "not_learned"}
VALID_MISTAKES = {"pronunciation", "meaning", "none"}


def save_progress(
    phrase,
    status,
    mistake_type="none",
    student_id="defaultstudent",
    feedback=None,
):
    if status not in VALID_STATUSES:
        raise ValueError(f"status must be one of {sorted(VALID_STATUSES)}")
    if mistake_type not in VALID_MISTAKES:
        raise ValueError(f"mistake_type must be one of {sorted(VALID_MISTAKES)}")

    memory = upsert_progress(student_id, phrase, status, mistake_type, feedback)
    return {
        "message": "Progress saved successfully",
        "phrase": phrase,
        "status": status,
        "mistake_type": mistake_type,
        "memory": memory,
    }
