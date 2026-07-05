TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_memory",
            "description": "Check the student's current language-learning memory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "The ID of the student.",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_progress",
            "description": "Save a student's progress for a phrase.",
            "parameters": {
                "type": "object",
                "properties": {
                    "phrase": {
                        "type": "string",
                        "description": "The phrase being evaluated or saved.",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["learned", "needs_review", "not_learned"],
                        "description": "The learning status of the phrase.",
                    },
                    "mistake_type": {
                        "type": "string",
                        "enum": ["pronunciation", "meaning", "none"],
                        "description": "The type of mistake the student made, if any.",
                    },
                    "student_id": {
                        "type": "string",
                        "description": "The ID of the student.",
                    },
                    "feedback": {
                        "type": "string",
                        "description": "Short feedback to store with this progress event.",
                    },
                },
                "required": ["phrase", "status"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "teach_phrase",
            "description": "Teach a Hindi phrase with a beginner-friendly breakdown.",
            "parameters": {
                "type": "object",
                "properties": {
                    "phrase": {
                        "type": "string",
                        "description": "The English or Hindi phrase being taught.",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["learned", "needs_review", "not_learned"],
                        "description": "The student's current status for this phrase.",
                    },
                },
                "required": ["phrase"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "speak_phrase",
            "description": "Generate and optionally play audio for a Hindi phrase.",
            "parameters": {
                "type": "object",
                "properties": {
                    "phrase": {
                        "type": "string",
                        "description": "The phrase to speak aloud.",
                    },
                    "play_audio": {
                        "type": "boolean",
                        "description": "Whether to open the generated audio file for playback.",
                    },
                },
                "required": ["phrase"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_question",
            "description": "Generate a speaking or listening practice question.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question_type": {
                        "type": "string",
                        "enum": ["speaking", "listening"],
                        "description": "Use speaking for English-to-Hindi speaking practice, listening for Hindi-to-English comprehension.",
                    },
                    "phrase": {
                        "type": "string",
                        "description": "The phrase to practice.",
                    },
                },
                "required": ["question_type", "phrase"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "evaluate_question",
            "description": "Evaluate a speaking or listening question response.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question_type": {
                        "type": "string",
                        "enum": ["speaking", "listening"],
                        "description": "The type of question being evaluated.",
                    },
                    "phrase": {
                        "type": "string",
                        "description": "The target phrase from the question.",
                    },
                    "user_response": {
                        "type": "string",
                        "description": "The student's English response. Required for listening questions.",
                    },
                    "file": {
                        "type": "string",
                        "description": "Path to the student's recorded audio file. Required for speaking questions.",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["learned", "needs_review", "not_learned"],
                        "description": "Optional current learning status.",
                    },
                },
                "required": ["question_type", "phrase"],
            },
        },
    },
]
