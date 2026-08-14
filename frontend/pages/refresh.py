"""
Smart Refresh Page View
Owner: Member 2 (UI/UX) & Member 4 (AI/ML + Smart Refresh)
"""

import streamlit as st
import time
import database.queries as queries
from frontend.components.timer import render_refresh_timer

# Game imports
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
    st.write("Restore your focus with a non-addictive 5-minute micro-break. When the timer ends, we return to study mode.")

    # Initialize states
    if "refresh_phase" not in st.session_state:
        st.session_state.refresh_phase = "menu"
    if "active_activity" not in st.session_state:
        st.session_state.active_activity = None
    if "game_state" not in st.session_state:
        st.session_state.game_state = {}

    # Check if timer is running and active
    if st.session_state.refresh_phase == "playing":
        # Render the timer bar
        time_expired = render_refresh_timer(300)
        
        if time_expired:
            # Save break session in database
            elapsed = int(time.time() - st.session_state.break_start_time)
            queries.log_smart_refresh(user_id, st.session_state.active_activity, elapsed)
            
            # Switch phase to complete
            st.session_state.refresh_phase = "complete"
            st.rerun()
            
        # Draw active game interface
        st.markdown("---")
        render_game_interface()
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        # End break early button
        if st.button("🚪 End Break Early", use_container_width=True):
            elapsed = int(time.time() - st.session_state.break_start_time)
            queries.log_smart_refresh(user_id, st.session_state.active_activity, elapsed)
            st.session_state.refresh_phase = "complete"
            st.rerun()
            
    elif st.session_state.refresh_phase == "complete":
        render_complete_screen()
        
    else:
        render_menu()

def render_menu():
    st.markdown("### 🌿 Select a 5-Minute Recharge Activity")
    st.write("All sessions are capped at 5 minutes to prevent endless scrolling and build concentration.")
    
    # 9 Micro break cards in 3x3 layout
    activities = [
        ("🃏 Memory Cards", "memory_game", "Match terms and definitions in a card flip grid."),
        ("🕵️ Guess Concept", "guess_concept", "Decode a concept from progressive hints."),
        ("🌍 GK Trivia", "gk", "Challenge yourself with rapid-fire general trivia."),
        ("➗ Fun Math", "math", "Engage your logical mind with rapid math puzzles."),
        ("📚 Word Anagrams", "english", "Rearrange scrambled letters to find key programming terms."),
        ("😄 Tongue Twister", "tongue_twister", "Warm up your speech with pronunciation challenges."),
        ("🧩 Riddle", "riddle", "Tease your brain with playful textual riddles."),
        ("🌿 Deep Breathing", "relaxation", "Relax your eyes, neck, and shoulders with box breathing."),
        ("☕ Coffee Chat", "friendly_chat", "Have a friendly, lightweight chat with AI companion.")
    ]
    
    # Render cards in grid
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    
    for idx, (label, name, desc) in enumerate(activities):
        target_col = cols[idx % 3]
        with target_col:
            st.markdown(f"""
            <div class='activity-card'>
                <div class='activity-icon'>{label.split()[0]}</div>
                <h4>{label.split(None, 1)[1]}</h4>
                <p style='font-size:0.85rem; color:#888; height: 50px;'>{desc}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Start {label.split(None, 1)[1]}", key=f"start_{name}", use_container_width=True):
                # Setup session states
                st.session_state.refresh_phase = "playing"
                st.session_state.active_activity = name
                st.session_state.break_start_time = time.time()
                st.session_state.game_state = {}
                st.rerun()

def render_complete_screen():
    st.markdown("<div class='glass-card' style='text-align: center;'>", unsafe_allow_html=True)
    st.markdown("<h2>✨ Refresh Session Complete!</h2>", unsafe_allow_html=True)
    st.write("Awesome job giving your brain a productive break. Ready to resume learning?")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    if st.button("📚 Return to Learning Point", type="primary", use_container_width=True):
        # Reset state and redirect user to Hub
        st.session_state.refresh_phase = "menu"
        st.session_state.active_activity = None
        st.session_state.game_state = {}
        if "break_start_time" in st.session_state:
            del st.session_state.break_start_time
            
        st.session_state.navigation_selection = "📖 Learning Hub"
        st.rerun()
        
    st.markdown("</div>", unsafe_allow_html=True)

def render_game_interface():
    activity = st.session_state.active_activity
    state = st.session_state.game_state
    
    # Render individual game based on selection
    if activity == "memory_game":
        st.subheader("🃏 Memory Cards - Match the Pairs")
        
        # Load deck if not initialized
        if "deck" not in state:
            deck = memory_game.get_memory_card_deck()
            # Construct card states (ids, flipped states, values)
            cards = []
            for item in deck:
                cards.append({"id": f"{item['id']}_a", "text": item["card_a"], "pair_id": item["id"], "type": "term", "flipped": False, "matched": False})
                cards.append({"id": f"{item['id']}_b", "text": item["card_b"], "pair_id": item["id"], "type": "def", "flipped": False, "matched": False})
            
            # Shuffle mock cards
            import random
            random.seed(42)  # consistent shuffle for prototype stability
            random.shuffle(cards)
            
            state["cards"] = cards
            state["selected_card_indices"] = []
            state["match_count"] = 0
            
        cards = state["cards"]
        selected_indices = state["selected_card_indices"]
        
        # Grid display
        col_c1, col_c2, col_c3 = st.columns(3)
        cols = [col_c1, col_c2, col_c3]
        
        for i, card in enumerate(cards):
            card_col = cols[i % 3]
            with card_col:
                # Custom flip container representation
                if card["matched"]:
                    st.markdown(f"""
                    <div style='background: rgba(16, 185, 129, 0.2); border: 2px solid #10B981; border-radius: 10px; height: 100px; display:flex; align-items:center; justify-content:center; text-align:center; padding:10px;'>
                        <strong style='color:#10B981;'>✓ Matched<br>{card['text']}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    st.button("Matched", key=f"matched_btn_{i}", disabled=True)
                elif card["flipped"]:
                    st.markdown(f"""
                    <div style='background: #3B82F6; border: 1px solid rgba(255,255,255,0.2); border-radius: 10px; height: 100px; display:flex; align-items:center; justify-content:center; text-align:center; padding:10px; color:white;'>
                        <strong>{card['text']}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Hide", key=f"hide_btn_{i}", use_container_width=True):
                        card["flipped"] = False
                        if i in selected_indices:
                            selected_indices.remove(i)
                        st.rerun()
                else:
                    st.markdown("""
                    <div style='background: #1E293B; border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; height: 100px; display:flex; align-items:center; justify-content:center;'>
                        <span style='font-size:1.5rem;'>❓</span>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Reveal", key=f"reveal_btn_{i}", use_container_width=True):
                        # Flip card
                        card["flipped"] = True
                        selected_indices.append(i)
                        
                        # If two cards are flipped, compare them
                        if len(selected_indices) == 2:
                            c1 = cards[selected_indices[0]]
                            c2 = cards[selected_indices[1]]
                            
                            if c1["pair_id"] == c2["pair_id"] and c1["id"] != c2["id"]:
                                # Match
                                c1["matched"] = True
                                c2["matched"] = True
                                state["match_count"] += 1
                                st.toast("🎉 Correct Match!", icon="✅")
                            else:
                                # Not matching - user will see them and they can hide or we show error toast
                                st.toast("❌ No Match. Try again!", icon="⚠️")
                                
                            # Reset selection list but keep cards flipped momentarily
                            state["selected_card_indices"] = []
                        st.rerun()
                        
        if state["match_count"] == 3:
            st.success("🎉 You matched all cards! You can return to study or restart the game.")
            if st.button("Play Again", use_container_width=True):
                del state["deck"]
                st.rerun()
                
    elif activity == "guess_concept":
        st.subheader("🕵️ Guess the Concept")
        
        if "challenge" not in state:
            state["challenge"] = guess_concept.get_guess_challenge()
            state["revealed_hints"] = 1
            state["guess_correct"] = False
            
        challenge = state["challenge"]
        hints = challenge["hints"]
        
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.write("Analyze the clues below and guess the concept:")
        
        for k in range(state["revealed_hints"]):
            st.info(hints[k])
            
        if state["revealed_hints"] < len(hints) and not state["guess_correct"]:
            if st.button("Show Next Hint", use_container_width=True):
                state["revealed_hints"] += 1
                st.rerun()
                
        user_guess = st.text_input("Enter your guess:", placeholder="e.g. Recursion").strip()
        
        if st.button("Submit Guess", type="primary", use_container_width=True):
            if user_guess.lower() == challenge["answer"].lower():
                state["guess_correct"] = True
            else:
                st.error("❌ Not quite! Review the hints and try again.")
                
        if state["guess_correct"]:
            st.success(f"🎉 Correct! The concept is indeed **{challenge['answer']}**.")
            if st.button("New Challenge", use_container_width=True):
                del state["challenge"]
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    elif activity == "gk":
        st.subheader("🌍 GK Trivia")
        
        if "questions" not in state:
            state["questions"] = gk.get_gk_trivia()
            state["answered"] = False
            state["user_ans"] = None
            
        q_data = state["questions"][0] # single trivia for break
        
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown(f"**Question:** {q_data['question']}")
        
        ans = st.radio("Choose an option:", q_data["options"], index=None)
        
        if st.button("Submit Answer", type="primary", use_container_width=True):
            state["answered"] = True
            state["user_ans"] = ans
            
        if state["answered"]:
            if state["user_ans"] == q_data["answer"]:
                st.success("🎉 Correct Answer! Good job.")
            else:
                st.error(f"❌ Wrong answer. Correct answer was: **{q_data['answer']}**.")
                
            if st.button("Next Question", use_container_width=True):
                del state["questions"]
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    elif activity == "math":
        st.subheader("➗ Fun Math Puzzle")
        
        if "puzzle_data" not in state:
            state["puzzle_data"] = math_games.get_math_puzzle()
            state["answered"] = False
            state["user_ans"] = None
            
        p_data = state["puzzle_data"]
        
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown(f"**Puzzle:** {p_data['puzzle']}")
        
        ans = st.radio("Select the correct value:", p_data["options"], index=None)
        
        if st.button("Verify Answer", type="primary", use_container_width=True):
            state["answered"] = True
            state["user_ans"] = ans
            
        if state["answered"]:
            if state["user_ans"] == p_data["answer"]:
                st.success(f"🎉 Correct! Explanation: {p_data['explanation']}")
            else:
                st.error(f"❌ Incorrect. Explanation: {p_data['explanation']}")
                
            if st.button("New Puzzle", use_container_width=True):
                del state["puzzle_data"]
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    elif activity == "english":
        st.subheader("📚 Word Anagrams")
        
        if "puzzle" not in state:
            state["puzzle"] = english_games.get_word_puzzle()
            state["solved"] = False
            
        p_data = state["puzzle"]
        
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.write(f"Rearrange these scrambled letters to find a word:")
        st.markdown(f"<h3 style='text-align:center; color:#FF6B6B;'>{p_data['scrambled']}</h3>", unsafe_allow_html=True)
        
        st.info(f"💡 **Hint:** {p_data['hint']}")
        
        guess = st.text_input("Your answer:", placeholder="e.g. PYTHON").strip()
        
        if st.button("Verify Word", type="primary", use_container_width=True):
            if guess.lower() == p_data["answer"].lower():
                state["solved"] = True
            else:
                st.error("❌ That's not correct. Try another arrangement.")
                
        if state["solved"]:
            st.success(f"🎉 Excellent! You solved it. The word is **{p_data['answer']}**.")
            if st.button("Play Again", use_container_width=True):
                del state["puzzle"]
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    elif activity == "tongue_twister":
        st.subheader("😄 Tongue Twister Challenge")
        
        twister = tongue_twisters.get_tongue_twister()
        
        st.markdown("<div class='glass-card' style='text-align:center;'>", unsafe_allow_html=True)
        st.write("Try saying this twister out loud 3 times fast:")
        st.markdown(f"<h4 style='color:#6BCB77;'>\"{twister}\"</h4>", unsafe_allow_html=True)
        
        st.write("This exercise stretches your focus and vocal muscle state!")
        if st.button("✅ I said it successfully!", type="primary", use_container_width=True):
            st.balloons()
            st.toast("Fabulous articulation! Break logged.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    elif activity == "riddle":
        st.subheader("🧩 Playful Riddle")
        
        if "riddle_data" not in state:
            state["riddle_data"] = riddles.get_riddle()
            state["show_hint"] = False
            state["show_ans"] = False
            
        r_data = state["riddle_data"]
        
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown(f"**Riddle:** *{r_data['riddle']}*")
        
        if state["show_hint"]:
            st.info(f"💡 **Hint:** {r_data['hint']}")
        else:
            if st.button("Reveal Hint", use_container_width=True):
                state["show_hint"] = True
                st.rerun()
                
        if state["show_ans"]:
            st.success(f"🎯 **Answer:** {r_data['answer']}")
        else:
            if st.button("Reveal Answer", type="primary", use_container_width=True):
                state["show_ans"] = True
                st.rerun()
                
        if state["show_ans"]:
            if st.button("New Riddle", use_container_width=True):
                del state["riddle_data"]
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    elif activity == "relaxation":
        st.subheader("🌿 Guided Breathing Break")
        
        if "current_step" not in state:
            state["current_step"] = 0
            state["breathing_activity"] = relaxation.get_relaxation_activity()
            
        step_data = state["breathing_activity"]
        steps = step_data["steps"]
        
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown(f"#### 🧘 Activity: {step_data['title']}")
        st.write("Box breathing calms the nervous system and refreshes cognition:")
        
        # Pulse Circle with instructions
        current_step_text = steps[state["current_step"]]
        circle_text = "Inhale" if "Inhale" in current_step_text else \
                      "Hold" if "Hold" in current_step_text else \
                      "Exhale" if "Exhale" in current_step_text else "Relax"
                      
        st.markdown(f"<div class='breathing-circle'>{circle_text}</div>", unsafe_allow_html=True)
        st.info(f"**Current Instruction:** {current_step_text}")
        
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
                if st.button("🧘 Complete Routine", type="primary", use_container_width=True):
                    st.success("Breathing routine complete. You look calmer!")
                    st.balloons()
        st.markdown("</div>", unsafe_allow_html=True)
        
    elif activity == "friendly_chat":
        st.subheader("☕ Light Coffee Chat")
        
        if "chat_history" not in state:
            state["chat_history"] = [
                ("assistant", friendly_chat.get_friendly_chat_prompt(st.session_state.current_user_name))
            ]
            
        for role, text in state["chat_history"]:
            with st.chat_message(role):
                st.write(text)
                
        if q := st.chat_input("Say something casual..."):
            with st.chat_message("user"):
                st.write(q)
            state["chat_history"].append(("user", q))
            
            # Simple list of mock lighthearted break replies
            import random
            replies = [
                "That's interesting! By the way, did you know that the first computer bug was an actual moth found in a relay in 1947?",
                "Haha, nice! Take a sip of water, relax your shoulders, and keep doing great work.",
                "I hear you! Sometimes code just needs a quick walk in the garden. Let's make sure we stretch our wrists.",
                "Awesome. Let's take a deep breath. Learning is a marathon, not a sprint!",
                "Great! I am here to keep you company. Tell me, what got you excited about programming originally?"
            ]
            
            reply = random.choice(replies)
            with st.chat_message("assistant"):
                st.write(reply)
            state["chat_history"].append(("assistant", reply))
            st.rerun()
