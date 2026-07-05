from .memory_store import get_memory_snapshot


def get_memory(student_id="defaultstudent"):
    memory = get_memory_snapshot(student_id)
    memory["message"] = "Memory retrieved successfully"
    return memory
