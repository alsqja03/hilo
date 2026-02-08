import streamlit as st
import random

# --- 1. 페이지 및 스타일 설정 ---
st.set_page_config(page_title="Evolution Style Hi-Lo", layout="centered")

# CSS 스타일 주입
st.markdown("""
<style>
    .stApp { background-color: #1e1e1e; color: white; }
    
    /* 상단 타이틀 */
    .title-container {
        display: flex; justify-content: center; margin-bottom: 20px;
        border-bottom: 2px solid #333; padding-bottom: 10px;
    }
    
    /* 카드 박스 */
    .card-box {
        border: 2px solid #ddd; border-radius: 10px; padding: 10px;
        text-align: center; background-color: white; color: black;
        font-weight: bold; font-size: 24px; margin: 5px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.5);
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        height: 150px;
    }
    .big-card-text { font-size: 48px; line-height: 1.1; }
    
    /* 히스토리 카드 */
    .history-card {
        border: 1px solid #888; border-radius: 5px; padding: 5px;
        text-align: center; background-color: #ddd; color: black;
        font-size: 12px; width: 40px; height: 50px; display: flex;
        justify-content: center; align-items: center; flex-direction: column;
    }
    
    /* 현재 획득 금액 표시 영역 */
    .pot-display {
        background-color: #222; border: 2px solid #ffd700; border-radius: 10px;
        padding: 15px; text-align: center; margin: 20px 0;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
    }
    
    /* 베팅 버튼 공통 스타일 */
    .stButton > button {
        width: 100%; border-radius: 10px; font-weight: bold;
        border: 2px solid #ffd700; background-color: #333; color: white;
        padding: 10px; height: auto; white-space: pre-wrap;
    }
    .stButton > button:hover { background-color: #444; border-color: white; }

    /* 칩 버튼 */
    div[data-testid="column"] > .stButton > button {
        background-color: #555 !important; color: white !important;
        border: 1px solid #777 !important; height: 50px !important;
        font-size: 14px !important; padding: 0 !important;
    }
    div[data-testid="column"] > .stButton > button:hover {
        background-color: #777 !important; border-color: white !important;
    }

    /* 인출(Cash Out) 버튼 스타일 - 크고 초록색 */
    .cashout-btn > button {
        background-color: #2e7d32 !important; /* Green */
        color: white !important; font-size: 20px !important;
        border: 2px solid #4caf50 !important;
        height: 80px !important;
    }
    .cashout-btn > button:hover { background-color: #1b5e20 !important; }
    
</style>
""", unsafe_allow_html=True)

# --- 2. 게임 데이터 및 함수 정의 ---

SUITS = ['♠', '♣', '♥', '♦']
RED_SUITS = ['♥', '♦']
BLACK_SUITS = ['♠', '♣']
RANKS = list(range(2, 15)) # 2~14 (Ace=14)
RANK_MAP = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}

def get_card_display(rank, suit):
    r_str = RANK_MAP.get(rank, str(rank))
    color = "red" if suit in RED_SUITS else "black"
    return r_str, suit, color

def create_deck(num_decks=2):
    deck = []
    for _ in range(num_decks):
        for r in RANKS:
            for s in SUITS:
                deck.append((r, s))
    random.shuffle(deck)
    return deck

def reset_game_state():
    """게임을 재시작 (덱, 현재 카드 리셋). 보유머니는 유지."""
    st.session_state.deck = create_deck(2)
    st.session_state.current_card = st.session_state.deck.pop()
    st.session_state.history = []
    st.session_state.current_pot = 0 # 테이블 위 판돈 초기화

# 세션 상태 초기화
if 'deck' not in st.session_state:
    st.session_state.balance = 1000000
    st.session_state.current_pot = 0 
    reset_game_state()
    st.session_state.game_message = "게임을 시작합니다. 칩을 눌러 베팅하세요."

# 사이드바 설정
with st.sidebar:
    st.header("게임 설정")
    initial_balance = st.number_input("초기 보유 머니", min_value=10000, value=1000000, step=10000)
    if st.button("설정된 머니로 완전 초기화"):
        st.session_state.balance = initial_balance
        reset_game_state()
        st.session_state.game_message = "초기화 되었습니다."
        st.rerun()

def draw_card():
    if len(st.session_state.deck) == 0:
        st.session_state.deck = create_deck(2)
        st.session_state.game_message = "덱 셔플 완료 (2 Decks)"
    return st.session_state.deck.pop()

def calculate_odds(current_rank):
    """
    배당률 계산 로직 변경:
    - 일반: 동률(Tie)도 승리로 간주하므로 확률 분모에 포함.
    - Ace: '동일'과 '미만'으로 나뉨.
    """
    remaining = st.session_state.deck
    total = len(remaining)
    if total == 0: return 1.0, 1.0

    high_count = len([c for c in remaining if c[0] > current_rank])
    low_count = len([c for c in remaining if c[0] < current_rank])
    same_count = len([c for c in remaining if c[0] == current_rank])

    if current_rank == 14: # Ace일 경우 (특수 룰)
        # 버튼 1: 동일 (Same)
        prob_1 = same_count / total if total > 0 else 0
        # 버튼 2: 미만 (Under)
        prob_2 = low_count / total if total > 0 else 0
    else: # 일반 경우 (Snap도 승리)
        # 버튼 1: 초과 (Over) + 동일 (Tie)
        prob_1 = (high_count + same_count) / total if total > 0 else 0
        # 버튼 2: 미만 (Under) + 동일 (Tie)
        prob_2 = (low_count + same_count) / total if total > 0 else 0

    # 배당률 계산 (최소 1.01배, 최대 20배 제한)
    odds_1 = round(1 / prob_1, 2) if prob_1 > 0 else 0.0
    odds_2 = round(1 / prob_2, 2) if prob_2 > 0 else 0.0
    
    return min(odds_1, 50.0), min(odds_2, 50.0)

def add_chip(amount):
    if st.session_state.balance >= amount:
        st.session_state.balance -= amount
        st.session_state.current_pot += amount
        st.session_state.game_message = "베팅 진행 중..."
    else:
        st.session_state.game_message = "잔액이 부족합니다."

def cash_out():
    if st.session_state.current_pot > 0:
        win_amount = st.session_state.current_pot
        st.session_state.balance += win_amount
        st.session_state.game_message = f"이기셨습니다. ({win_amount:,}원)"
        reset_game_state()
    else:
        st.session_state.game_message = "인출할 금액이 없습니다."

def process_bet(bet_type):
    if st.session_state.current_pot <= 0:
        st.session_state.game_message = "칩을 먼저 선택해 주세요."
        return

    current_card = st.session_state.current_card
    current_rank = current_card[0]
    
    odds_1, odds_2 = calculate_odds(current_rank) # odds_1: Hi/Same, odds_2: Lo
    odds_fixed = 1.95

    next_card = draw_card()
    next_rank = next_card[0]
    next_suit = next_card[1]
    
    win = False
    payout_mult = 0.0

    # 승리 조건 로직
    if current_rank == 14: # 현재 카드가 ACE일 때
        if bet_type == "Hi": # "동일" 버튼 역할
            payout_mult = odds_1
            if next_rank == 14: win = True # A -> A 만 승리
        elif bet_type == "Lo": # "미만" 버튼 역할
            payout_mult = odds_2
            if next_rank < 14: win = True # A -> ~K 승리
    else: # 일반적인 경우
        if bet_type == "Hi": # "초과" 버튼 역할
            payout_mult = odds_1
            if next_rank >= current_rank: win = True # 초과 OR 동일 승리
        elif bet_type == "Lo": # "미만" 버튼 역할
            payout_mult = odds_2
            if next_rank <= current_rank: win = True # 미만 OR 동일 승리

    # Red/Black (항상 고정)
    if bet_type == "Red":
        payout_mult = odds_fixed
        if next_suit in RED_SUITS: win = True
    elif bet_type == "Black":
        payout_mult = odds_fixed
        if next_suit in BLACK_SUITS: win = True

    # 결과 처리
    cur_r_disp, cur_s_disp, _ = get_card_display(next_rank, next_suit)
    card_disp = f"{cur_s_disp}{cur_r_disp}"

    if win:
        prev_pot = st.session_state.current_pot
        new_pot = int(prev_pot * payout_mult)
        st.session_state.current_pot = new_pot
        st.session_state.game_message = f" "
        
        st.session_state.history.insert(0, current_card)
        if len(st.session_state.history) > 6:
            st.session_state.history.pop()
        st.session_state.current_card = next_card
    else:
        reason = "패배"
        # 상세 패배 사유
        if current_rank == 14 and bet_type == "Lo" and next_rank == 14:
            reason = "A-A 동일 (미만 패배)"
        
        st.session_state.game_message = f"버스트(Bust)! ({reason}: {card_disp})"
        reset_game_state()


# --- 3. 화면 구성 ---

# (0) 상단 타이틀
st.markdown("""
<div class='title-container'>
    <h1 style='font-size: 48px; font-weight: bold; margin: 0; color: #ffd700; text-shadow: 2px 2px 4px #000000;'>HI-LO</h1>
</div>
""", unsafe_allow_html=True)

# (1) 히스토리 영역
st.markdown("### Previous Cards")
hist_cols = st.columns(7)
cur_r, cur_s, cur_c = get_card_display(st.session_state.current_card[0], st.session_state.current_card[1])
with hist_cols[0]:
    st.markdown(f"<div class='history-card' style='border: 2px solid gold; background: white; color:{cur_c}'><span>{cur_s}</span><span>{cur_r}</span></div>", unsafe_allow_html=True)
    st.caption("Current")

for i, card in enumerate(st.session_state.history[:6]):
    hr, hs, hc = get_card_display(card[0], card[1])
    with hist_cols[i+1]:
        st.markdown(f"<div class='history-card' style='color:{hc}'><span>{hs}</span><span>{hr}</span></div>", unsafe_allow_html=True)

# (2) 현재 획득 금액 표시
pot_value = st.session_state.current_pot
st.markdown(f"""
<div class='pot-display'>
    <div style='color:#aaa; font-size:16px;'>현재 획득 금액 (Current Pot)</div>
    <div style='color:#ffd700; font-size:32px; font-weight:bold;'>₩ {pot_value:,}</div>
</div>
""", unsafe_allow_html=True)

# (3) 메인 게임 영역
c1, c2 = st.columns([1, 1])
with c1:
    st.markdown(f"""
    <div class='card-box' style='background: repeating-linear-gradient(45deg, #606dbc, #606dbc 10px, #465298 10px, #465298 20px); color: white;'>
        <div style='font-size:36px; font-weight:bold;'>Deck</div>
        <div style='font-size: 20px; margin-top: 10px;'>{len(st.session_state.deck)} left</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class='card-box' style='color: {cur_c};'>
        <div class='big-card-text'>{cur_s}<br>{cur_r}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"<h4 style='text-align:center; color:#ffd700; margin: 20px 0;'>{st.session_state.game_message}</h4>", unsafe_allow_html=True)

# (4) 베팅 컨트롤 영역
# 배당률 및 라벨 결정 로직
current_rank = st.session_state.current_card[0]
odds_1, odds_2 = calculate_odds(current_rank)
curr_pot = st.session_state.current_pot
next_pot_1 = int(curr_pot * odds_1)
next_pot_2 = int(curr_pot * odds_2)
next_pot_rb = int(curr_pot * 1.95)

# 버튼 라벨 동적 생성
if current_rank == 14: # Ace
    label_1 = "동일 (Same)"
    label_2 = "미만 (Under)"
else:
    label_1 = "초과 (Over)"
    label_2 = "미만 (Under)"

b_col1, b_col2 = st.columns(2)
with b_col1:
    # Button 1 (Hi/Same)
    if st.button(f"{label_1}\nx{odds_1}\nGet: {next_pot_1:,}", key="bet_hi"): process_bet("Hi"); st.rerun()
    if st.button(f"Black (♠♣)\nx1.95\nGet: {next_pot_rb:,}", key="bet_black"): process_bet("Black"); st.rerun()
with b_col2:
    # Button 2 (Lo)
    if st.button(f"{label_2}\nx{odds_2}\nGet: {next_pot_2:,}", key="bet_lo"): process_bet("Lo"); st.rerun()
    if st.button(f"Red (♥♦)\nx1.95\nGet: {next_pot_rb:,}", key="bet_red"): process_bet("Red"); st.rerun()

st.divider()

# (5) 인출(Cash Out) 버튼 (획득 금액 포함)
st.markdown("<div style='display:flex; justify-content:center; margin-bottom:20px;'>", unsafe_allow_html=True)
c_btn_col1, c_btn_col2, c_btn_col3 = st.columns([1, 2, 1])
with c_btn_col2:
    st.markdown("<div class='cashout-btn'>", unsafe_allow_html=True)
    # 인출 버튼 속에 현재 금액 표시
    btn_text = f"IN CHUL (인출)\n₩ {st.session_state.current_pot:,}"
    if st.button(btn_text, key="cash_out"):
        cash_out()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# (6) 칩 선택 영역
st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
st.markdown(f"#### 칩을 눌러 금액 추가 (즉시 차감)", unsafe_allow_html=True)
chip_cols = st.columns(6)
chips = [1000, 5000, 10000, 50000, 100000, 500000]
for i, amount in enumerate(chips):
    with chip_cols[i]:
        if st.button(f"+{amount//1000}k", key=f"chip_{amount}"):
            add_chip(amount)
            st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# (7) 보유 머니
st.markdown(f"""
<div style='background-color:#333; padding:20px; border-radius:15px; text-align:center; margin-top:30px; border: 2px solid #555;'>
    <span style='font-size:18px; color:#aaa;'>보유 머니 (Balance)</span><br>
    <span style='font-size:36px; color:#4CAF50; font-weight:bold;'>₩ {st.session_state.balance:,}</span>
</div>
""", unsafe_allow_html=True)
