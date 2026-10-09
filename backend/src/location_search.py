import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

LOCATION_FILE = (
    BASE_DIR / "data" / "university_info" / "locations.json"
)


def load_locations():
    with open(LOCATION_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def search_location(question):

    question = question.lower().strip()

    locations = load_locations()

    for location in locations:

        keywords = location.get("keywords", [])

        if any(keyword in question for keyword in keywords):

            return {
                "status": "answered",
                "answer": location["description"],
                "source": "University location information",
                "location": location
            }

    return {
        "status": "not_found",
        "answer": (
            "I couldn't find a verified answer for that yet. "
            "I don't want to guess about university information."
        ),
        "source": None
    }


if __name__ == "__main__":

    questions = [
        "Where is the registrar office?",
        "Where can I find the registrar?",
        "Where is the registration office?",
        "Where is the library?"
    ]

    for question in questions:

        print("\n================================")
        print("QUESTION:", question)
        print("================================")

        result = search_location(question)

        print("Status:", result["status"])
        print("Answer:", result["answer"])