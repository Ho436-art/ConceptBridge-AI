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
    r"(make\s+(it|that|this)\s+simpler|explain\s+(it|that|this)\s+simpler|explain\s+simpler|explain\s+like\s+i'?m\s+(5|10)|too\s+complex|too\s+hard|simplify\s+(it|that|this)?|in\s+simpler\s+words)"
]

EXAMPLE_PATTERNS = [
    r"(give\s+(me\s+)?another\s+example|more\s+examples?|another\s+analogy|another\s+code\s+example|show\s+me\s+code\s+for\s+(it|this|that))"
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
    """
    Classifies user intent from natural language message.
    Accurately distinguishes between new topics, clarifications, and contextual follow-ups.
    """
    clean = message.strip().lower()

    # 1. Greetings
    for pattern in GREETING_PATTERNS:
        if re.search(pattern, clean):
            return MessageIntent.GREETING

    # 2. Casual Chat
    for pattern in CASUAL_PATTERNS:
        if re.search(pattern, clean):
            return MessageIntent.CASUAL

    # 3. Simplify active concept
    for pattern in SIMPLIFY_PATTERNS:
        if re.search(pattern, clean):
            return MessageIntent.SIMPLIFY

    # 4. Another example for active concept
    for pattern in EXAMPLE_PATTERNS:
        if re.search(pattern, clean):
            return MessageIntent.ANOTHER_EXAMPLE

    # 5. Still confused about active concept
    for pattern in CONFUSED_PATTERNS:
        if re.search(pattern, clean):
            return MessageIntent.STILL_CONFUSED

    # 6. Follow-up Question on Active Concept vs New Concept
    if active_concept:
        # If query has demonstratives / pronouns pointing to active concept:
        # e.g. "what is its time complexity?", "why does it call itself?", "how does it work?"
        has_pronoun_ref = bool(re.search(r"\b(its?|itself|this|that|these|those)\b", clean))
        
        # Explicit new topic introduction (e.g. "what is a transistor?", "explain binary search", "why does a refrigerator...")
        introduces_new_topic = bool(re.search(
            r"^(explain\s+(?!that|this|it)\w+|what\s+is\s+(a\s+|an\s+|the\s+(?!time\s+|space\s+|drawback|advantage|difference|best\s+|worst\s+))\w+|why\s+does\s+(a\s+|an\s+)\w+|how\s+does\s+(a\s+|an\s+)\w+)",
            clean
        ))

        if has_pronoun_ref and not introduces_new_topic:
            return MessageIntent.FOLLOW_UP

        # Common short follow-up questions (e.g. "time complexity?", "worst case?")
        short_followup_patterns = [
            r"^(what\s+is\s+(the\s+)?)?(time|space)\s+complexity\??$",
            r"^(what\s+about\s+(the\s+)?)?(worst|best|average)\s+case\??$",
            r"^(show\s+me\s+)?(code|pseudocode|implementation)\??$"
        ]
        if any(re.search(pat, clean) for pat in short_followup_patterns):
            return MessageIntent.FOLLOW_UP

    return MessageIntent.NEW_CONCEPT


def handle_chat_message(
    user_message: str,
    active_concept: Optional[str] = None,
    learner_profile: Optional[LearnerProfile] = None,
    previous_explanation: Optional[Dict[str, Any]] = None,
    context_document: Optional[str] = None
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
    intent = classify_intent(user_message, active_concept) if not context_document else MessageIntent.NEW_CONCEPT

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
            msg = "You're very welcome! Let me know if you want another example or are ready for the next topic! 🚀"
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
        exp = explain_concept(
            f"Explain {target_concept} in very simple words",
            learner_profile=learner_profile,
            style_override="super_simple",
            context_document=context_document
        )
        return {
            "intent": intent,
            "text_response": f"Let's break down **{exp.concept}** in super simple, plain English without jargon:",
            "explanation": exp.to_dict(),
            "active_concept": exp.concept
        }

    # 4. ANOTHER EXAMPLE
    if intent == MessageIntent.ANOTHER_EXAMPLE:
        target_concept = active_concept or "Recursion"
        exp = explain_concept(
            f"Give another practical example of {target_concept}",
            learner_profile=learner_profile,
            style_override="practical_code",
            context_document=context_document
        )
        return {
            "intent": intent,
            "text_response": f"Here is an alternative practical walk-through for **{exp.concept}**:",
            "explanation": exp.to_dict(),
            "active_concept": exp.concept
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
    if intent == MessageIntent.FOLLOW_UP and active_concept and not context_document:
        from ai.llm_client import query_llm_text
        
        system_prompt = (
            f"You are ConceptBridge AI, a helpful, empathetic learning companion. "
            f"The student is currently learning about '{active_concept}' and is asking a specific follow-up question. "
            f"Answer the student's follow-up question directly, clearly, and concisely in 2-3 friendly paragraphs. "
            f"Do not output robotic boilerplate. Answer specifically for {active_concept}."
        )
        prompt = (
            f"Active Topic: '{active_concept}'\n"
            f"Student's Follow-up Question: '{user_message}'\n\n"
            f"Please answer the student's question specifically in relation to '{active_concept}'."
        )
        ai_reply = query_llm_text(prompt=prompt, system_prompt=system_prompt)
        
        if ai_reply and len(ai_reply) > 20:
            ans_text = ai_reply
        else:
            ans_text = (
                f"Regarding **{active_concept}**: In response to *'{user_message}'*, "
                f"this mechanism operates according to the fundamental invariants and constraints of {active_concept}."
            )

        return {
            "intent": intent,
            "text_response": ans_text,
            "explanation": None,
            "active_concept": active_concept
        }

    # 7. NEW CONCEPT QUESTION
    exp = explain_concept(user_message, learner_profile=learner_profile, context_document=context_document)
    return {
        "intent": MessageIntent.NEW_CONCEPT,
        "text_response": f"Here is the conceptual breakdown for **{exp.concept}**:",
        "explanation": exp.to_dict(),
        "active_concept": exp.concept
    }
