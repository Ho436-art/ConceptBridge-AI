"""
Conversational Engine and Intent Router for ConceptBridge AI
Owner: Member 1 (Team Lead / AI & ML)

Responsibilities:
- Classifies user message intent (Greeting, Casual Chat, New Concept, Follow-up, Simpler, Another Example, Confused).
- Manages conversational memory without polluting context.
- Handles greetings like "hi" naturally and briefly instead of outputting an educational lecture.
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from models.schemas import ConceptExplanation, LearnerProfile
from ai.teaching_engine import explain_concept
from ai.feedback_handler import process_feedback
from ai.llm_client import query_llm_json

GREETING_PATTERNS = [
    r"^(hi|hello|hey|greetings|good\s+morning|good\s+afternoon|good\s+evening|howdy|sup|yo)[\s!.]*$"
]

CASUAL_PATTERNS = [
    r"^(how\s+are\s+you|who\s+are\s+you|what\s+can\s+you\s+do|thanks|thank\s+you|cool|awesome|ok|okay)[\s!.]*$"
]

SIMPLIFY_PATTERNS = [
    r"(make\s+it\s+simpler|explain\s+simpler|explain\s+like\s+i'?m\s+(5|10)|too\s+complex|too\s+hard|simplify)"
]

EXAMPLE_PATTERNS = [
    r"(give\s+(me\s+)?another\s+example|more\s+examples?|another\s+analogy|another\s+code\s+example)"
]

CONFUSED_PATTERNS = [
    r"(i\s+don'?t\s+understand|still\s+confused|explain\s+again|didn'?t\s+get\s+it|lost\s+me)"
]


class MessageIntent:
    GREETING = "greeting"
    CASUAL = "casual"
    SIMPLIFY = "simplify"
    ANOTHER_EXAMPLE = "another_example"
    STILL_CONFUSED = "still_confused"
    FOLLOW_UP = "follow_up"
    NEW_CONCEPT = "new_concept"


def classify_intent(message: str, active_concept: Optional[str] = None) -> str:
    """Classifies user intent from message text."""
    clean = message.strip().lower()

    for pattern in GREETING_PATTERNS:
        if re.search(pattern, clean):
            return MessageIntent.GREETING

    for pattern in CASUAL_PATTERNS:
        if re.search(pattern, clean):
            return MessageIntent.CASUAL

    for pattern in SIMPLIFY_PATTERNS:
        if re.search(pattern, clean):
            return MessageIntent.SIMPLIFY

    for pattern in EXAMPLE_PATTERNS:
        if re.search(pattern, clean):
            return MessageIntent.ANOTHER_EXAMPLE

    for pattern in CONFUSED_PATTERNS:
        if re.search(pattern, clean):
            return MessageIntent.STILL_CONFUSED

    # If there is an active concept and the question is short / contextual, treat as follow-up
    if active_concept and len(clean.split()) <= 15 and not clean.startswith(("explain", "what is", "teach me")):
        if any(w in clean for w in ["why", "how", "what if", "where", "can it", "difference", "complexity", "time"]):
            return MessageIntent.FOLLOW_UP

    return MessageIntent.NEW_CONCEPT


def handle_chat_message(
    user_message: str,
    active_concept: Optional[str] = None,
    learner_profile: Optional[LearnerProfile] = None,
    previous_explanation: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Main entry point for conversational learning messages.
    
    Returns structured payload:
    {
      "intent": str,
      "text_response": str,
      "explanation": Optional[Dict],  # if a full concept explanation was produced
      "active_concept": str
    }
    """
    intent = classify_intent(user_message, active_concept)

    # 1. GREETING
    if intent == MessageIntent.GREETING:
        concept_hint = f" We were discussing **{active_concept}** — want to continue with that or explore something new?" if active_concept else " What concept would you like to explore today?"
        return {
            "intent": intent,
            "text_response": f"Hi! 😊 I'm ConceptBridge AI, your personalized learning companion.{concept_hint}",
            "explanation": None,
            "active_concept": active_concept
        }

    # 2. CASUAL CHAT
    if intent == MessageIntent.CASUAL:
        clean = user_message.lower().strip()
        if "thank" in clean or "cool" in clean or "awesome" in clean or "ok" in clean:
            msg = "You're very welcome! Let me know if you want another example or ready for the next topic! 🚀"
        elif "who are you" in clean or "what can you do" in clean:
            msg = "I'm ConceptBridge AI! I bridge the gap from *'I don't understand'* to *'Oh, it's that easy!'* by teaching academic concepts through real-world analogies, multi-tier breakdowns, and interactive check questions."
        else:
            msg = "I'm doing great and excited to help you learn! What concept can we break down next?"
        return {
            "intent": intent,
            "text_response": msg,
            "explanation": None,
            "active_concept": active_concept
        }

    # 3. MAKE SIMPLER
    if intent == MessageIntent.SIMPLIFY:
        target_concept = active_concept or "Recursion"
        exp = explain_concept(target_concept, learner_profile=learner_profile, style_override="super_simple")
        return {
            "intent": intent,
            "text_response": f"Let's break down **{target_concept}** in super simple, plain English without jargon:",
            "explanation": exp.to_dict(),
            "active_concept": target_concept
        }

    # 4. ANOTHER EXAMPLE
    if intent == MessageIntent.ANOTHER_EXAMPLE:
        target_concept = active_concept or "Recursion"
        exp = explain_concept(target_concept, learner_profile=learner_profile, style_override="practical_code")
        return {
            "intent": intent,
            "text_response": f"Here is an alternative practical walk-through for **{target_concept}**:",
            "explanation": exp.to_dict(),
            "active_concept": target_concept
        }

    # 5. STILL CONFUSED
    if intent == MessageIntent.STILL_CONFUSED:
        target_concept = active_concept or "Recursion"
        pivot = process_feedback("still_confused", target_concept, learner_profile, previous_explanation)
        return {
            "intent": intent,
            "text_response": pivot.get("encouraging_message", f"Let's look at {target_concept} from another angle:"),
            "explanation": pivot.get("alternative_explanation"),
            "active_concept": target_concept
        }

    # 6. CONTEXTUAL FOLLOW-UP QUESTION
    if intent == MessageIntent.FOLLOW_UP and active_concept:
        # Generate targeted answer to the follow-up question in context of active concept
        prompt = (
            f"Concept in Context: '{active_concept}'\n"
            f"Student Follow-up Question: '{user_message}'\n\n"
            f"Answer the student's specific follow-up question concisely, accurately, and encouragingly in 2-3 short paragraphs."
        )
        llm_reply = query_llm_json(
            prompt=prompt,
            system_prompt="You are ConceptBridge AI. Answer the student's specific follow-up question concisely and accurately.",
            fallback_concept=active_concept
        )
        
        if llm_reply and isinstance(llm_reply, dict) and "simple_explanation" in llm_reply:
            ans_text = f"**Regarding {active_concept}:**\n\n" + llm_reply["simple_explanation"]
        else:
            ans_text = (
                f"**Regarding {active_concept}:**\n\n"
                f"To answer your question *'{user_message}'*: In {active_concept}, this mechanism ensures "
                f"proper state transitions and boundary control without exhausting system resources."
            )

        return {
            "intent": intent,
            "text_response": ans_text,
            "explanation": None,
            "active_concept": active_concept
        }

    # 7. NEW CONCEPT QUESTION
    exp = explain_concept(user_message, learner_profile=learner_profile)
    return {
        "intent": MessageIntent.NEW_CONCEPT,
        "text_response": f"Here is the conceptual breakdown for **{exp.concept}**:",
        "explanation": exp.to_dict(),
        "active_concept": exp.concept
    }
