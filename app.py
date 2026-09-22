import streamlit as st
import chess
import chess.svg
import chess.engine
import shutil
import os

st.set_page_config(page_title="Play vs Stockfish", page_icon="♟️")
st.title("Streamlit Chess vs AI 🤖")

st.sidebar.title("AI Settings")
ai_skill = st.sidebar.slider("Stockfish Skill Level", 0, 20, 2)
ai_think_time = st.sidebar.slider("AI Think Time (seconds)", 0.1, 2.0, 0.5)

if "board" not in st.session_state:
    st.session_state.board = chess.Board()

board = st.session_state.board

board_svg = chess.svg.board(
    board,
    size=400,
    lastmove=board.peek() if board.move_stack else None,
    check=board.king(board.turn) if board.is_check() else None
)
st.write(f"<div style='display: flex; justify-content: center;'>{board_svg}</div>", unsafe_allow_html=True)
st.divider()

if board.is_game_over():
    st.success(f"Game Over! Result: {board.result()}")
    if st.button("Play Again"):
        st.session_state.board = chess.Board()
        st.rerun()
else:
    with st.form("move_form", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            move_input = st.text_input("Enter your move (e.g., 'e4' or 'Nf3'):")
        with col2:
            st.write("") 
            st.write("") 
            submitted = st.form_submit_button("Submit Move", use_container_width=True)

    if submitted and move_input:
        try:
            # 1. Player makes their move
            board.push_san(move_input)
            
            # 2. AI makes its move
            if not board.is_game_over():
                engine_path = shutil.which("stockfish") 
                
                # --- STREAMLIT CLOUD FIX ---
                # If Python can't find it normally, explicitly check the Linux games folder
                if engine_path is None and os.path.exists("/usr/games/stockfish"):
                    engine_path = "/usr/games/stockfish"
                elif engine_path is None and os.path.exists("/usr/bin/stockfish"):
                    engine_path = "/usr/bin/stockfish"
                # ---------------------------
                
                if engine_path is None:
                    st.error("Stockfish engine not found! Ensure packages.txt is spelled correctly.")
                else:
                    with st.spinner("AI is thinking..."):
                        with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
                            engine.configure({"Skill Level": ai_skill})
                            result = engine.play(board, chess.engine.Limit(time=ai_think_time))
                            board.push(result.move)
                    
            st.rerun()
        
        except ValueError:
            st.error(f"'{move_input}' is an invalid or illegal move.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

    if st.button("Undo Last Move") and len(board.move_stack) >= 2:
        board.pop() 
        board.pop()
        st.rerun()
