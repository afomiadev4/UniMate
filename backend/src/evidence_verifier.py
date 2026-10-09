import re


FALLBACK_MESSAGE = (
    "I couldn't find a verified answer for that yet. "
    "I don't want to guess about university information."
)


# ==========================================
# 1. IDENTIFY QUESTION TOPIC
# ==========================================

TOPIC_KEYWORDS = {
    "exams": [
        "exam", "exams", "examination",
        "finals", "midterm"
    ],

    "registration": [
        "registration", "register",
        "enrollment", "enroll"
    ],

    "calendar": [
        "semester", "academic calendar",
        "classes", "school start"
    ],

    "location": [
        "where", "located", "location",
        "building", "room", "office"
    ],

    "library": [
        "library", "libraries"
    ]
}


def detect_topic(question):

    question = question.lower()

    # Specific topics take priority
    if "library" in question:
        return "library"

    for topic, keywords in TOPIC_KEYWORDS.items():

        if any(keyword in question for keyword in keywords):
            return topic

    return None


# ==========================================
# 2. CHECK DOCUMENT RELEVANCE
# ==========================================

def is_relevant(question, document):

    text = document.get("text", "").lower()

    if not text.strip():
        return False

    topic = detect_topic(question)

    if topic is None:
        return False

    # Library questions
    if topic == "library":

        return bool(
            re.search(r"\blibrar(?:y|ies)\b", text)
        )

    # Location questions
    if topic == "location":

        location_terms = [
            "located", "location",
            "building", "room",
            "floor", "address"
        ]

        return any(
            term in text
            for term in location_terms
        )

    # Examination questions
    if topic == "exams":

        return bool(
            re.search(
                r"\b(exam|exams|examination|finals|midterm)\b",
                text
            )
        )

    # Registration questions
    if topic == "registration":

        return any(
            term in text
            for term in ["registration", "register", "enrollment"]
        )

    # Calendar questions
    if topic == "calendar":

        return any(
            term in text
            for term in ["semester", "classes", "academic"]
        )

    return False


# ==========================================
# 3. VERIFY RETRIEVED DOCUMENTS
# ==========================================

def verify_evidence(question, documents):

    verified_documents = []

    for document in documents:

        if not is_relevant(question, document):
            continue

        verified_documents.append({
            "text": document.get("text", ""),
            "source": document.get("source"),
            "page": document.get("page"),
            "distance": document.get("distance")
        })

    return verified_documents


# ==========================================
# 4. TEST EVIDENCE VERIFICATION
# ==========================================

if __name__ == "__main__":

    test_documents = [
        {
            "text": "First Semester Exam Period for All Students",
            "source": "aau_academic_calendar.pdf",
            "page": 2,
            "distance": 0.4
        },
        {
            "text": "Registration of Year II Undergraduate Students",
            "source": "aau_academic_calendar.pdf",
            "page": 1,
            "distance": 0.5
        },
        {
            "text": "Addis Ababa University Research Week",
            "source": "aau_academic_calendar.pdf",
            "page": 4,
            "distance": 0.7
        }
    ]

    questions = [
        "When are exams?",
        "When is registration?",
        "Where is the library?",
        "What is the president's phone number?"
    ]

    for question in questions:

        print("\n" + "=" * 50)
        print("QUESTION:", question)

        results = verify_evidence(
            question,
            test_documents
        )

        if results:

            print("Status: evidence_found")

            for result in results:
                print("Source:", result["source"])
                print("Page:", result["page"])
                print("Text:", result["text"])

        else:

            print("Status: not_found")
            print("Answer:", FALLBACK_MESSAGE)