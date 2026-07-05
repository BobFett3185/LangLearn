PHRASE_BANK = {
    "hello": {
        "hindi": "namaste",
        "devanagari": "नमस्ते",
        "english": "hello",
        "breakdown": [
            "namaste means hello and is useful in almost any greeting.",
            "Say it as nuh-muh-stay, with an even rhythm.",
        ],
    },
    "how are you": {
        "hindi": "aap kaise hain",
        "devanagari": "आप कैसे हैं",
        "english": "how are you",
        "breakdown": [
            "aap means you, politely.",
            "kaise hain means how are.",
            "Say it as aap kai-say hain.",
        ],
    },
    "i am fine": {
        "hindi": "main theek hoon",
        "devanagari": "मैं ठीक हूँ",
        "english": "i am fine",
        "breakdown": [
            "main means I.",
            "theek means fine or okay.",
            "hoon means am.",
        ],
    },
    "thank you": {
        "hindi": "dhanyavaad",
        "devanagari": "धन्यवाद",
        "english": "thank you",
        "breakdown": [
            "dhanyavaad means thank you.",
            "Break it into dhun-yuh-vaad.",
        ],
    },
    "what is your name": {
        "hindi": "aapka naam kya hai",
        "devanagari": "आपका नाम क्या है",
        "english": "what is your name",
        "breakdown": [
            "aapka means your.",
            "naam means name.",
            "kya hai means what is.",
        ],
    },
}


def normalize_phrase(phrase):
    return " ".join(str(phrase or "").strip().lower().split())


def lookup_phrase(phrase):
    normalized = normalize_phrase(phrase)
    if normalized in PHRASE_BANK:
        return PHRASE_BANK[normalized]

    for item in PHRASE_BANK.values():
        if normalized in {
            normalize_phrase(item["hindi"]),
            normalize_phrase(item["devanagari"]),
            normalize_phrase(item["english"]),
        }:
            return item

    return {
        "hindi": phrase,
        "devanagari": "",
        "english": phrase,
        "breakdown": [
            "Practice the phrase slowly first.",
            "Then say it again at normal speaking speed.",
        ],
    }


def phrase_matches(expected, actual):
    expected_norm = normalize_phrase(expected)
    actual_norm = normalize_phrase(actual)
    if not expected_norm or not actual_norm:
        return False
    return expected_norm in actual_norm or actual_norm in expected_norm
