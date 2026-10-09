import json
import re
from pathlib import Path

# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

CALENDAR_FILE = (
    BASE_DIR / "data" / "structured" / "calendar_events.json"
)

FALLBACK_MESSAGE = (
    "I couldn't find a verified answer for that yet. "
    "I don't want to guess about university information."
)


# ==========================================
# 2. LOAD CALENDAR DATA
# ==========================================

def load_calendar():
    if not CALENDAR_FILE.exists():
        return []

    try:
        with open(CALENDAR_FILE, "r", encoding="utf-8") as file:
            events = json.load(file)

        if not isinstance(events, list):
            return []

        return events

    except (json.JSONDecodeError, OSError):
        return []


# ==========================================
# 3. QUESTION INTENTS
# ==========================================

INTENT_KEYWORDS = {
    "semester_start": [
        "semester start",
        "semester begin",
        "school start",
        "school begin",
        "classes start",
        "classes begin",
        "class start",
        "class begin",
        "students start",
        "students begin",
        "student start",
        "student begin",
        "university start",
        "university begin",
        "start of semester",
        "start of classes",
        "when does school start",
        "when do classes start",
        "when do students start",
        "when does the semester start"
    ],

    "registration": [
        "register",
        "registration",
        "enroll",
        "enrollment"
    ],

    "exams": [
        "exam",
        "examination",
        "finals",
        "final exam",
        "exam period"
    ]
}


# ==========================================
# 4. DETECT QUESTION INTENT
# ==========================================

def detect_intent(question):
    question = question.lower()

    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in question for keyword in keywords):
            return intent

    return None


# ==========================================
# 5. DETECT STUDENT YEAR
# ==========================================

def detect_student_year(question):
    question = question.lower()

    year_patterns = {
        1: r"\b(first[\s-]*year|1st[\s-]*year|year\s*(i|1))\b",
        2: r"\b(second[\s-]*year|2nd[\s-]*year|year\s*(ii|2))\b",
        3: r"\b(third[\s-]*year|3rd[\s-]*year|year\s*(iii|3))\b",
        4: r"\b(fourth[\s-]*year|4th[\s-]*year|year\s*(iv|4))\b"
    }

    for year, pattern in year_patterns.items():
        if re.search(pattern, question):
            return year

    return None


# ==========================================
# 6. DETECT SEMESTER
# ==========================================

def detect_semester(question):
    question = question.lower()

    first_semester = [
        "first semester",
        "1st semester",
        "semester 1",
        "semester one"
    ]

    second_semester = [
        "second semester",
        "2nd semester",
        "semester 2",
        "semester two"
    ]

    if any(term in question for term in first_semester):
        return 1

    if any(term in question for term in second_semester):
        return 2

    return None


# ==========================================
# 7. MATCH STUDENT YEAR
# ==========================================

def match_student_year(event, student_year):

    if student_year is None:
        return True

    event_year = str(event.get("year", "")).lower().strip()

    category = str(
        event.get("student_category", "")
    ).lower().strip()

    # General events
    if event_year == "all":
        return True

    # Specific structured categories
    if category == f"undergraduate_year{student_year}":
        return True

    # Year II and above
    if "year ii and above" in event_year:
        return student_year >= 2

    # Normalize Roman numerals
    roman_years = {
        1: "i",
        2: "ii",
        3: "iii",
        4: "iv"
    }

    expected_roman = roman_years.get(student_year)

    if event_year == f"year {expected_roman}":
        return True

    if event_year == f"year {student_year}":
        return True

    # Explicitly reject unmatched years
    return False


# ==========================================
# 8. EVENT PRIORITY
# ==========================================

def event_priority(event, student_year):

    category = str(
        event.get("student_category", "")
    ).lower().strip()

    event_year = str(
        event.get("year", "")
    ).lower().strip()

    if student_year is not None:

        if category == f"undergraduate_year{student_year}":
            return 0

        roman_years = {
            1: "i",
            2: "ii",
            3: "iii",
            4: "iv"
        }

        if event_year == f"year {roman_years.get(student_year)}":
            return 0

    if category == "all":
        return 2

    return 1


# ==========================================
# 9. SEARCH CALENDAR EVENTS
# ==========================================

def search_calendar(question):

    events = load_calendar()

    intent = detect_intent(question)
    student_year = detect_student_year(question)
    semester = detect_semester(question)

    # Unknown question: do not guess
    if intent is None:
        return []

    matches = []

    for event in events:

        if not isinstance(event, dict):
            continue

        event_name = str(
            event.get("event", "")
        ).lower()

        # ------------------------------
        # Filter by intent
        # ------------------------------

        if intent == "semester_start":

            if not any(
                phrase in event_name
                for phrase in [
                    "classes begin",
                    "classes start",
                    "semester begins",
                    "semester starts"
                ]
            ):
                continue

        elif intent == "registration":

            if not any(
                phrase in event_name
                for phrase in [
                    "registration",
                    "enrollment"
                ]
            ):
                continue

        elif intent == "exams":

            if not any(
                phrase in event_name
                for phrase in [
                    "exam",
                    "examination",
                    "finals"
                ]
            ):
                continue

        # ------------------------------
        # Filter by semester
        # ------------------------------

        if semester is not None:

            if event.get("semester") != semester:
                continue

        # ------------------------------
        # Filter by student year
        # ------------------------------

        if not match_student_year(event, student_year):
            continue

        matches.append(event)

    # ==========================================
    # Rank and filter results
    # ==========================================
    matches.sort(
        key=lambda event: (
            event_priority(event, student_year),
            event.get("semester") or 0,
            event.get("date_start", "")
        )
    )

    # Prefer the most specific events when a student year is given.
    if student_year is not None and matches:
        best_priority = min(
            event_priority(event, student_year) for event in matches
        )
        matches = [
            event for event in matches
            if event_priority(event, student_year) == best_priority
        ]

    return matches


# ==========================================
# 10. BUILD SOURCE INFORMATION
# ==========================================

def build_sources(events):

    sources = []
    seen = set()

    for event in events:

        source = event.get("source")
        page = event.get("page")

        if not source:
            continue

        key = (source, page)

        if key in seen:
            continue

        seen.add(key)

        sources.append({
            "document": source,
            "page": page
        })

    return sources


# ==========================================
# 11. GENERATE CALENDAR RESPONSE
# ==========================================

def get_calendar_answer(question):

    intent = detect_intent(question)

    # CASE 1: Unsupported question
    if intent is None:

        return {
            "status": "not_found",
            "answer": FALLBACK_MESSAGE,
            "events": [],
            "sources": [],
            "suggested_questions": []
        }

    results = search_calendar(question)

    # CASE 2: No verified information
    if not results:

        return {
            "status": "not_found",
            "answer": FALLBACK_MESSAGE,
            "events": [],
            "sources": [],
            "suggested_questions": []
        }

    semester = detect_semester(question)

    # CASE 3: Ambiguous semester
    if semester is None and intent == "semester_start":

        semesters = {
            event.get("semester")
            for event in results
            if event.get("semester") is not None
        }

        if len(semesters) > 1:

            return {
                "status": "needs_clarification",
                "answer": (
                    "Are you asking about the "
                    "first or second semester?"
                ),
                "events": [],
                "sources": [],
                "suggested_questions": [
                    "When does the first semester start?",
                    "When does the second semester start?"
                ]
            }

    # CASE 4: Verified information found
    sources = build_sources(results)

    return {
        "status": "answered",
        "answer": "I found the following academic calendar information.",
        "events": results,
        "sources": sources,
        "suggested_questions": []
    }


# ==========================================
# 12. TEST UNIGUIDE CALENDAR
# ==========================================

if __name__ == "__main__":

    questions = [
        "When do second-year students start?",
        "When do second-year students start their first semester?",
        "When does the second semester start?",
        "When do first-year students register?",
        "When is registration?",
        "When are exams?",
        "Where is the registrar office?",
        "What is the university president's phone number?",
        "Does AAU have a swimming pool?"
    ]

    for question in questions:

        print("\n" + "=" * 55)
        print("QUESTION:", question)
        print("=" * 55)

        result = get_calendar_answer(question)

        print("Status:", result["status"])
        print("Answer:", result["answer"])

        if result["status"] == "answered":

            for event in result["events"]:

                print("\nEvent:", event.get("event"))
                print("Start Date:", event.get("date_start"))
                print("End Date:", event.get("date_end"))
                print("Student Category:", event.get("student_category"))
                print("Academic Year:", event.get("academic_year"))
                print("Semester:", event.get("semester"))
                print("Source:", event.get("source"))
                print("Page:", event.get("page"))

        elif result["status"] == "needs_clarification":

            print(
                "Suggested questions:",
                result["suggested_questions"]
            )