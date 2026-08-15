"""
Smart Refresh Page View
Owner: Member 2 (UI/UX) & Member 4 (AI/ML + Smart Refresh)

Features:
- Maximum 5-minute mental micro-break activities.
- Persistent 30-minute cooldown calculation with database audit.
- Real-time timestamp-based countdown timer.
- Working Memory Cards state, 15-20+ question pools across all 9 games, and zero negative scoring/stress.
"""

import streamlit as st
import time
import random
import database.queries as queries
from frontend.components.timer import render_refresh_timer

# Game Modules
import smart_refresh.memory_game as memory_game
import smart_refresh.guess_concept as guess_concept
import smart_refresh.gk as gk
import smart_refresh.math_games as math_games
import smart_refresh.english_games as english_games
import smart_refresh.tongue_twisters as tongue_twisters
import smart_refresh.riddles as riddles
import smart_refresh.relaxation as relaxation
import smart_refresh.friendly_chat as friendly_chat


def show():
    user_id = st.session_state.get("current_user_id")
    if not user_id:
        st.warning("🔒 Please log in or sign up first.")
        return

    st.markdown("<h2>⚡ Smart Refresh Hub</h2>", unsafe_allow_html=True)
    st.caption("Restore mental clarity with a non-addictive 5-minute micro-break. When the timer ends, we return smoothly to learning.")

    # Initialize Phase States
    if "refresh_phase" not in st.session_state:
        st.session_state.refresh_phase = "menu"
    if "active_activity" not in st.session_state:
        st.session_state.active_activity = None
    if "game_state" not in st.session_state:
        st.session_state.game_state = {}

    # Check 30-minute Cooldown
    bypass_cooldown = st.sidebar.checkbox("⚡ Bypass Cooldown (for Testing)", value=False)
    cooldown_seconds_left = _calculate_cooldown_remaining(user_id)

    if cooldown_seconds_left > 0 and st.session_state.refresh_phase == "menu" and not bypass_cooldown:
        _render_cooldown_screen(cooldown_seconds_left)
        return

    # Phase Routing
    if st.session_state.refresh_phase == "playing":
        _render_playing_phase(user_id)
    elif st.session_state.refresh_phase == "complete":
        _render_complete_screen()
    else:
        _render_menu()


def _calculate_cooldown_remaining(user_id: str) -> int:
    """Calculates remaining seconds in 30-minute (1800s) cooldown window."""
    last_ts = st.session_state.get("last_refresh_end_time")
    if not last_ts:
        # Check DB history
        try:
            history = queries.get_smart_refresh_history(user_id)
            if history:
                # Latest session
                latest = history[0]
                created_str = latest.get("created_at") or latest.get("started_at")
                if created_str:
                    import datetime
                    # Parse timestamp
                    dt = datetime.datetime.fromisoformat(created_str.replace("Z", "+00:00").split(".")[0])
                    last_ts = dt.timestamp()
        except Exception:
            last_ts = None

    if not last_ts:
        return 0

    elapsed = time.time() - last_ts
    remaining = int(1800 - elapsed)
    return max(0, remaining)


def _render_cooldown_screen(cooldown_seconds: int):
    """Renders informative cooldown notification and learning redirection."""
    mins, secs = divmod(cooldown_seconds, 60)
    st.markdown(f"""
    <div class='glass-card' style='text-align: center; padding: 30px; margin-top: 20px;'>
        <h3 style='color: #F59E0B;'>⏳ Smart Refresh Cooldown Active</h3>
        <p style='color: #ddd; font-size: 1.05rem;'>
            To prevent distraction and preserve study momentum, breaks are available once every 30 minutes.<br>
            Smart Refresh will be available again in <strong>{mins} minutes, {secs} seconds</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
    with col_b2:
        if st.button("📖 Continue to Learning Hub", type="primary", use_container_width=True):
            st.session_state.navigation_selection = "📖 Learning Hub"
            st.rerun()


def _render_menu():
    st.markdown("### 🌿 Select a 5-Minute Recharge Activity")
    st.write("All sessions are strictly capped at 5 minutes to prevent endless scrolling and build concentration.")
    
    activities = [
        ("🃏 Memory Cards", "memory_game", "Match technical terms and definitions in a card flip grid."),
        ("🕵️ Guess Concept", "guess_concept", "Decode an academic concept from 3 progressive clues."),
        ("🌍 GK Trivia", "gk", "Challenge your general knowledge with rapid-fire trivia."),
        ("➗ Fun Math", "math", "Engage your logical mind with rapid pattern puzzles."),
        ("📚 Word Anagrams", "english", "Rearrange scrambled letters to find key computer science terms."),
        ("😄 Tongue Twister", "tongue_twister", "Warm up your articulation with fun pronunciation challenges."),
        ("🧩 Riddle", "riddle", "Tease your brain with playful textual riddles."),
        ("🌿 Deep Breathing", "relaxation", "Rest your eyes, neck, and shoulders with 20-20-20 and box breathing."),
        ("☕ Coffee Chat", "friendly_chat", "Have a friendly, lightweight conversation with AI companion.")
    ]
    
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    
    for idx, (label, name, desc) in enumerate(activities):
        target_col = cols[idx % 3]
        with target_col:
            st.markdown(f"""
            <div class='glass-card' style='padding: 16px; margin-bottom: 14px; min-height: 140px;'>
                <h4 style='margin: 0 0 8px 0;'>{label}</h4>
                <p style='font-size: 0.85rem; color: #aaa; margin: 0;'>{desc}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Start {label.split(None, 1)[1]}", key=f"btn_start_{name}", use_container_width=True):
                st.session_state.refresh_phase = "playing"
                st.session_state.active_activity = name
                st.session_state.break_start_time = time.time()
                st.session_state.game_state = {}
                st.rerun()


def _render_playing_phase(user_id: str):
    # Render countdown timer
    time_expired = render_refresh_timer(300)
    
    if time_expired:
        elapsed = int(time.time() - st.session_state.break_start_time)
        try:
            queries.save_refresh_session(user_id, st.session_state.active_activity, duration=elapsed, completed=True)
        except Exception:
            pass
        st.session_state.last_refresh_end_time = time.time()
        st.session_state.refresh_phase = "complete"
        st.rerun()
        
    st.markdown("---")
    _render_game_interface()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🚪 End Break Early & Return to Learning", use_container_width=True):
        elapsed = int(time.time() - st.session_state.break_start_time)
        try:
            queries.save_refresh_session(user_id, st.session_state.active_activity, duration=elapsed, completed=True)
        except Exception:
            pass
        st.session_state.last_refresh_end_time = time.time()
        st.session_state.refresh_phase = "complete"
        st.rerun()


def _render_complete_screen():
    st.markdown("""
    <div class='glass-card' style='text-align: center; padding: 30px;'>
        <h2>✨ Refresh Session Complete!</h2>
        <p style='font-size: 1.1rem; color: #ddd;'>
            Awesome job giving your mind a healthy recharge. Ready to dive back into your concepts?
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
    with col_b2:
        if st.button("📚 Return to Learning Hub", type="primary", use_container_width=True):
            st.session_state.refresh_phase = "menu"
            st.session_state.active_activity = None
            st.session_state.game_state = {}
            if "break_start_time" in st.session_state:
                del st.session_state.break_start_time
            st.session_state.navigation_selection = "📖 Learning Hub"
            st.rerun()


def _render_game_interface():
    activity = st.session_state.active_activity
    state = st.session_state.game_state
    
    # 1. MEMORY CARDS
    if activity == "memory_game":
        st.subheader("🃏 Memory Cards - Match the Pairs")
        
        if "cards" not in state:
            deck = memory_game.get_memory_card_deck(limit=3)
            cards = []
            for item in deck:
                cards.append({"id": f"{item['id']}_a", "text": item["card_a"], "pair_id": item["id"], "flipped": False, "matched": False})
                cards.append({"id": f"{item['id']}_b", "text": item["card_b"], "pair_id": item["id"], "flipped": False, "matched": False})
            random.shuffle(cards)
            state["cards"] = cards
            state["selected_indices"] = []
            state["match_count"] = 0
            
        cards = state["cards"]
        selected = state["selected_indices"]
        
        col_c1, col_c2, col_c3 = st.columns(3)
        cols = [col_c1, col_c2, col_c3]
        
        for i, card in enumerate(cards):
            card_col = cols[i % 3]
            with card_col:
                if card["matched"]:
                    st.markdown(f"""
                    <div style='background: rgba(16, 185, 129, 0.2); border: 2px solid #10B981; border-radius: 10px; height: 90px; display:flex; align-items:center; justify-content:center; text-align:center; padding:8px;'>
                        <strong style='color:#10B981;'>✓ Matched<br>{card['text']}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                elif card["flipped"]:
                    st.markdown(f"""
                    <div style='background: #1E40AF; border: 2px solid #3B82F6; border-radius: 10px; height: 90px; display:flex; align-items:center; justify-content:center; text-align:center; padding:8px; color:white;'>
                        <strong>{card['text']}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Hide", key=f"btn_hide_{i}", use_container_width=True):
                        card["flipped"] = False
                        if i in selected:
                            selected.remove(i)
                        st.rerun()
                else:
                    st.markdown("""
                    <div style='background: #1E293B; border: 1px solid rgba(255,255,255,0.15); border-radius: 10px; height: 90px; display:flex; align-items:center; justify-content:center;'>
                        <span style='font-size:1.5rem;'>❓</span>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Reveal", key=f"btn_reveal_{i}", use_container_width=True):
                        card["flipped"] = True
                        selected.append(i)
                        
                        if len(selected) == 2:
                            c1 = cards[selected[0]]
                            c2 = cards[selected[1]]
                            if c1["pair_id"] == c2["pair_id"] and c1["id"] != c2["id"]:
                                c1["matched"] = True
                                c2["matched"] = True
                                state["match_count"] += 1
                                st.toast("🎉 Correct Match!", icon="✅")
                            else:
                                st.toast("❌ No match. Try another pair!", icon="⚠️")
                            state["selected_indices"] = []
                        st.rerun()
                        
        if state.get("match_count", 0) >= 3:
            st.success("🎉 You matched all card pairs! Outstanding memory.")
            if st.button("Shuffle New Deck", use_container_width=True):
                del state["cards"]
                st.rerun()

    # 2. GUESS THE CONCEPT
    elif activity == "guess_concept":
        st.subheader("🕵️ Guess the Concept")
        if "challenge" not in state:
            state["challenge"] = guess_concept.get_guess_challenge(
                exclude_keys=state.get("shown_concepts", [])
            )
            state["revealed_hints"] = 1
            state["guess_correct"] = False
            state.setdefault("shown_concepts", []).append(state["challenge"].get("pool_key", ""))

        challenge = state["challenge"]
        hints = challenge["hints"]
        
        st.markdown("<div class='glass-card' style='padding: 20px;'>", unsafe_allow_html=True)
        st.write("Analyze the clues below and guess the concept:")
        for k in range(state["revealed_hints"]):
            st.info(hints[k])
            
        if state["revealed_hints"] < len(hints) and not state["guess_correct"]:
            if st.button("🔍 Show Next Clue", use_container_width=True):
                state["revealed_hints"] += 1
                st.rerun()
                
        user_guess = st.text_input("Enter your guess:", placeholder="e.g. Graph Coloring, Recursion", key="guess_input").strip()
        if st.button("Submit Guess", type="primary", use_container_width=True):
            if guess_concept.verify_guess(user_guess, challenge):
                state["guess_correct"] = True
            else:
                st.warning("❌ Not quite! Check the clues or reveal another clue.")
                
        if state["guess_correct"]:
            st.success(f"🎉 **Correct!** The concept is **{challenge['answer']}**.")
            if st.button("Play Next Concept", use_container_width=True):
                del state["challenge"]
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # 3. GK TRIVIA
    elif activity == "gk":
        st.subheader("🌍 GK Trivia")
        if "question_data" not in state:
            q_list = gk.get_gk_trivia(limit=1, exclude_indices=state.get("shown_gk", []))
            state["question_data"] = q_list[0]
            state["answered"] = False
            state["user_ans"] = None
            state.setdefault("shown_gk", []).append(state["question_data"].get("question_index", 0))

        q_data = state["question_data"]
        st.markdown("<div class='glass-card' style='padding: 20px;'>", unsafe_allow_html=True)
        st.markdown(f"**Question:** {q_data['question']}")
        
        ans = st.radio("Choose an option:", q_data["options"], key=f"gk_rad_{q_data.get('question_index')}")
        if st.button("Submit Answer", type="primary", use_container_width=True):
            state["answered"] = True
            state["user_ans"] = ans
            
        if state["answered"]:
            if state["user_ans"] == q_data["answer"]:
                st.success("🎉 **Correct!** Great general knowledge.")
            else:
                st.error(f"❌ Correct answer was: **{q_data['answer']}**.")
            if st.button("Next Trivia Question", use_container_width=True):
                del state["question_data"]
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # 4. FUN MATH
    elif activity == "math":
        st.subheader("➗ Fun Math Pattern Puzzle")
        if "puzzle_data" not in state:
            state["puzzle_data"] = math_games.get_math_puzzle(
                exclude_indices=state.get("shown_math", [])
            )
            state["answered"] = False
            state["user_ans"] = None
            state.setdefault("shown_math", []).append(state["puzzle_data"].get("puzzle_index", 0))

        p_data = state["puzzle_data"]
        st.markdown("<div class='glass-card' style='padding: 20px;'>", unsafe_allow_html=True)
        st.markdown(f"**Puzzle:** {p_data['puzzle']}")
        
        ans = st.radio("Select the correct value:", p_data["options"], key=f"math_rad_{p_data.get('puzzle_index')}")
        if st.button("Verify Answer", type="primary", use_container_width=True):
            state["answered"] = True
            state["user_ans"] = ans
            
        if state["answered"]:
            if state["user_ans"] == p_data["answer"]:
                st.success(f"🎉 **Correct!** {p_data['explanation']}")
            else:
                st.error(f"❌ Incorrect. {p_data['explanation']}")
            if st.button("New Math Puzzle", use_container_width=True):
                del state["puzzle_data"]
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # 5. WORD ANAGRAMS
    elif activity == "english":
        st.subheader("📚 Computer Science Word Anagrams")
        if "puzzle" not in state:
            state["puzzle"] = english_games.get_word_puzzle(
                exclude_indices=state.get("shown_english", [])
            )
            state["solved"] = False
            state.setdefault("shown_english", []).append(state["puzzle"].get("puzzle_index", 0))

        p_data = state["puzzle"]
        st.markdown("<div class='glass-card' style='padding: 20px;'>", unsafe_allow_html=True)
        st.write("Unscramble the letters to reveal a computer science term:")
        st.markdown(f"<h2 style='text-align:center; color:#38BDF8; letter-spacing: 4px;'>{p_data['scrambled']}</h2>", unsafe_allow_html=True)
        st.info(f"💡 **Hint:** {p_data['hint']}")
        
        guess = st.text_input("Your answer:", placeholder="Type word here...", key="anagram_input").strip()
        if st.button("Verify Word", type="primary", use_container_width=True):
            if guess.upper() == p_data["answer"].upper():
                state["solved"] = True
            else:
                st.error("❌ Not quite. Check the hint and try another arrangement.")
                
        if state["solved"]:
            st.success(f"🎉 **Brilliant!** You solved it. The word is **{p_data['answer']}**.")
            if st.button("Play Next Anagram", use_container_width=True):
                del state["puzzle"]
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # 6. TONGUE TWISTERS
    elif activity == "tongue_twister":
        st.subheader("😄 Tongue Twister Challenge")
        if "twister" not in state:
            state["twister"] = tongue_twisters.get_tongue_twister()
            
        st.markdown("<div class='glass-card' style='text-align:center; padding: 25px;'>", unsafe_allow_html=True)
        st.write("Try saying this twister out loud 3 times fast:")
        st.markdown(f"<h3 style='color:#10B981; margin: 15px 0;'>\"{state['twister']}\"</h3>", unsafe_allow_html=True)
        st.caption("Stretches your facial articulation muscles and resets cognitive fatigue!")
        
        if st.button("✅ I said it 3 times cleanly!", type="primary", use_container_width=True):
            st.balloons()
            st.toast("Fabulous articulation! Break recorded.", icon="🎉")
        if st.button("Next Tongue Twister", use_container_width=True):
            state["twister"] = tongue_twisters.get_tongue_twister()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # 7. RIDDLES
    elif activity == "riddle":
        st.subheader("🧩 Playful Riddle")
        if "riddle_data" not in state:
            state["riddle_data"] = riddles.get_riddle(
                exclude_indices=state.get("shown_riddles", [])
            )
            state["show_hint"] = False
            state["show_ans"] = False
            state.setdefault("shown_riddles", []).append(state["riddle_data"].get("riddle_index", 0))

        r_data = state["riddle_data"]
        st.markdown("<div class='glass-card' style='padding: 20px;'>", unsafe_allow_html=True)
        st.markdown(f"**Riddle:** *{r_data['riddle']}*")
        
        if state["show_hint"]:
            st.info(f"💡 **Hint:** {r_data['hint']}")
        else:
            if st.button("Reveal Hint", use_container_width=True):
                state["show_hint"] = True
                st.rerun()
                
        if state["show_ans"]:
            st.success(f"🎯 **Answer:** {r_data['answer']}\n\n*{r_data['explanation']}*")
            if st.button("Next Riddle", use_container_width=True):
                del state["riddle_data"]
                st.rerun()
        else:
            if st.button("Reveal Answer", type="primary", use_container_width=True):
                state["show_ans"] = True
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # 8. RELAXATION (No Quiz!)
    elif activity == "relaxation":
        st.subheader("🌿 Guided Relaxation & Eye Rest")
        if "current_step" not in state:
            state["current_step"] = 0
            state["breathing_activity"] = relaxation.get_relaxation_activity()

        step_data = state["breathing_activity"]
        steps = step_data["steps"]
        
        st.markdown("<div class='glass-card' style='padding: 25px;'>", unsafe_allow_html=True)
        st.markdown(f"#### 🧘 Routine: {step_data['title']}")
        
        current_step_text = steps[state["current_step"]]
        st.info(f"**Step {state['current_step'] + 1} of {len(steps)}:**\n\n{current_step_text}")
        
        col_prev, col_next = st.columns(2)
        with col_prev:
            if st.button("⏮️ Previous Step", disabled=state["current_step"] == 0, use_container_width=True):
                state["current_step"] -= 1
                st.rerun()
        with col_next:
            if state["current_step"] < len(steps) - 1:
                if st.button("⏭️ Next Step", type="primary", use_container_width=True):
                    state["current_step"] += 1
                    st.rerun()
            else:
                if st.button("🧘 Finish Relaxation", type="primary", use_container_width=True):
                    st.balloons()
                    st.success("Routine complete. Your focus is refreshed!")
        st.markdown("</div>", unsafe_allow_html=True)

    # 9. FRIENDLY COFFEE CHAT
    elif activity == "friendly_chat":
        st.subheader("☕ Casual Coffee Chat")
        st.caption("A short, friendly chat to unwind. (Not for full lectures).")
        
        if "chat_history" not in state:
            user_name = st.session_state.get("current_user_name", "Student")
            state["chat_history"] = [
                ("assistant", f"Hey {user_name}! ☕ Taking a short break from coding? How is your day going so far?")
            ]
            
        for role, text in state["chat_history"]:
            with st.chat_message(role):
                st.write(text)
                
        if q := st.chat_input("Say something casual...", key="coffee_chat_input"):
            state["chat_history"].append(("user", q))
            
            replies = [
                "That's great! By the way, make sure to drink a glass of water and stretch your shoulders.",
                "Haha, totally relatable! Did you know the first computer bug was an actual moth trapped inside a Mark II relay in 1947?",
                "Taking short micro-breaks is scientifically proven to improve long-term memory consolidation!",
                "Awesome! Remember: great programmers aren't the ones who never get stuck, but the ones who take a breather and try again.",
                "Sounds fun! Whenever you feel ready, we can return to the Learning Hub and tackle your next topic!"
            ]
            reply = random.choice(replies)
            state["chat_history"].append(("assistant", reply))
            st.rerun()
