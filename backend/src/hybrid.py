from calendar_search import get_calendar_answer
from retrieve import search_documents
from location_search import search_location
from evidence_verifier import verify_evidence

import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai


# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")

MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.1-flash-lite"
)

client = genai.Client(api_key=API_KEY) if API_KEY else None

FALLBACK_MESSAGE = (
    "I couldn't find a verified answer for that yet. "
    "I don't want to guess about university information."
)


# ==========================================
# 2. STANDARDIZE RESPONSES
# ==========================================

def format_response(
    status,
    answer,
    events=None,
    sources=None,
    evidence=None,
    suggested_questions=None
):

    return {
        "status": status,
        "answer": answer,
        "events": events if events is not None else [],
        "sources": sources if sources is not None else [],
        "evidence": evidence if evidence is not None else [],
        "suggested_questions": (
            suggested_questions
            if suggested_questions is not None
            else []
        )
    }


# ==========================================
# 3. GEMINI ANSWER GENERATION
# ==========================================

def generate_answer(question, context):

    if not client:
        return None

    prompt = f"""
You are UniGuide AI, an assistant for Addis Ababa
University students.

Your job is to answer student questions using ONLY
the university information provided below.

STRICT RULES:

1. Never invent university information.
2. Never invent dates, locations, phone numbers,
   deadlines, or university policies.
3. Use only the provided context.
4. If the context does not answer the question,
   respond exactly with:

{FALLBACK_MESSAGE}

5. Give short, clear, friendly answers.
6. Do not add information that is not in the context.
7. Do not claim information is officially verified
   unless the supplied evidence supports that claim.

UNIVERSITY INFORMATION:

{context}

STUDENT QUESTION:

{question}

ANSWER:
"""

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        answer = (response.text or "").strip()

        if not answer:
            return None

        return answer

    except Exception as error:

        print("Gemini API error:", error)

        return None


# ==========================================
# 4. HYBRID SEARCH
# ==========================================

def hybrid_search(question):

    question = question.strip()

    if not question:

        return format_response(
            status="not_found",
            answer="Please enter a question."
        )

    # ======================================
    # STEP 1: LOCATION SEARCH
    # ======================================

    location_result = search_location(question)

    if location_result["status"] == "answered":

        original_answer = location_result["answer"]

        answer = generate_answer(
            question,
            original_answer
        )

        return format_response(
            status="answered",
            answer=answer or original_answer,
            sources=[
                {
                    "source": location_result.get(
                        "source",
                        "University location information"
                    ),
                    "type": "location",
                    "verification": "user_provided"
                }
            ]
        )

    # ======================================
    # STEP 2: CALENDAR SEARCH
    # ======================================

    calendar_result = get_calendar_answer(question)

    if calendar_result["status"] == "needs_clarification":

        return format_response(
            status="needs_clarification",
            answer=calendar_result["answer"],
            suggested_questions=calendar_result.get(
                "suggested_questions", []
            )
        )

    if calendar_result["status"] == "answered":

        events = calendar_result.get("events", [])

        context_parts = []

        for event in events:

            context_parts.append(
                f"""
Event: {event.get('event')}
Start Date: {event.get('date_start')}
End Date: {event.get('date_end')}
Student Category: {event.get('student_category')}
Academic Year: {event.get('academic_year')}
Semester: {event.get('semester')}
Source: {event.get('source')}
Page: {event.get('page')}
"""
            )

        context = "\n".join(context_parts)

        original_answer = calendar_result["answer"]

        if context.strip():

            answer = generate_answer(
                question,
                context
            )

        else:

            answer = None

        return format_response(
            status="answered",
            answer=answer or original_answer,
            events=events,
            sources=calendar_result.get("sources", [])
        )

    # ======================================
    # STEP 3: CHROMADB RETRIEVAL
    # ======================================

    documents = search_documents(
        question,
        top_k=3
    )

    # ======================================
    # STEP 4: EVIDENCE VERIFICATION
    # ======================================

    documents = verify_evidence(
        question,
        documents
    )

    evidence = []

    for document in documents:

        text = document.get("text", "").strip()

        if not text:
            continue

        evidence.append({
            "text": text,
            "source": document.get("source"),
            "page": document.get("page"),
            "distance": document.get("distance")
        })

    # ======================================
    # STEP 5: GEMINI DOCUMENT ANSWER
    # ======================================

    if evidence:

        context_parts = []

        for document in evidence:

            context_parts.append(
                f"""
Source: {document['source']}
Page: {document['page']}
Information:
{document['text']}
"""
            )

        context = "\n\n".join(context_parts)

        answer = generate_answer(
            question,
            context
        )

        if answer and answer != FALLBACK_MESSAGE:

            return format_response(
                status="answered",
                answer=answer,
                evidence=evidence,
                sources=[
                    {
                        "document": doc["source"],
                        "page": doc["page"]
                    }
                    for doc in evidence
                ]
            )

    # ======================================
    # STEP 6: FALLBACK
    # ======================================

    return format_response(
        status="not_found",
        answer=FALLBACK_MESSAGE
    )


# ==========================================
# 5. TEST
# ==========================================

if __name__ == "__main__":

    questions = [
        "Where is the registrar office?",
        "When do second-year students start?",
        "When are first semester exams?",
        "When does the second semester start?",
        "When do first-year students register?",
        "Where is the library?",
        "What is the university president's phone number?"
    ]

    for question in questions:

        print("\n" + "=" * 60)
        print("QUESTION:", question)

        result = hybrid_search(question)

        print("Status:", result["status"])
        print("Answer:", result["answer"])
        print("Sources:", result["sources"])