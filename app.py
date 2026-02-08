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
    
    /* 카드 박스 (Deck & Current Card) */
    .card-box {
        border: 2px solid #ddd; border-radius: 10px; padding: 10px;
        text-align: center; background-color: white; color: black;
        font-weight: bold; font-size: 24px; margin: 5px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.5);
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        height: 160px; /* 높이 고정 */
    }
    .big-card-text { font-size: 56px; line-height: 1.1; }
    
    /* 히스토리 카드 */
    .history-card {
        border: 1px solid #888; border-radius: 5px; padding: 5px;
        text-align: center; background-color: #ddd; color: black;
        font-size: 12px; width: 40px; height: 50px; display: flex;
        justify-content: center; align-items: center; flex-direction: column;
    }
    
    /* [수정] 베팅 버튼 스타일 - 카드 박스와 유사한 크기/너비 */
    .bet-btn-style > button {
        width: 100% !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        border: 2px solid #ffd700 !important;
        background-color: #333 !important;
        color: white !important;
        padding: 10px !important;
        height: 100px !important; /* 높이 확대 */
        white-space: pre-wrap !important;
        font-size: 18px !important;
        transition: all 0.2s !important;
    }
    .bet-btn-style > button:hover {
        background-color: #555 !important;
        border-color: white !important;
        transform: scale(1.02);
    }

    /* [수정] 칩 버튼 스타일 - 확대 */
    .chip-btn-style > button {
        background-color: #555 !important;
        color: white !important;
        border: 2px solid #777 !important;
        height: 70px !important; /* 높이 확대 */
        width: 100% !important;
        border-radius: 50% !important; /* 원형 느낌 */
        font-size: 16px !important; /* 글자 확대 */
        font-weight: bold !important;
        padding: 0 !important;
    }
    .chip-btn-style > button:hover {
        background-color: #777 !important;
        border-color: white !important;
        color: #ffd700 !important;
    }

    /* [수정] 인출(Cash Out) 버튼 스타일 - 이전 '획득 금액' 디자인 적용 */
    .cashout-container {
        display: flex; justify-content: center; margin: 20px 0;
    }
    .cashout-btn-style > button {
        background-color: #222 !important; /* 검은 배경 */
        color: #ffd700 !important; /* 금색 글씨 */
        border: 3px solid #ffd700 !important; /* 금색 테두리 */
        border-radius: 15px !important;
        height: 100px !important;
        width: 100% !important;
        font-size: 24px !important;
        font-weight: bold !important;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.4) !important;
        transition: all 0.3s !important;
    }
    .cashout-btn-style > button:hover {
        background-color: #333 !important;
        box-shadow: 0 0 25px rgba(255, 215, 0, 0.7) !important;
        transform: scale(1.05);
    }
    
    /* 보유 머니 박스 */
    .balance-box {
        background-color:#333; padding:20px; border-radius:15px;
        text-align:center; margin-top:30px; border: 2px solid #555;
    }

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
    st.session_state.current_pot = 0 

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
    remaining = st.session_state.deck
    total = len(remaining)
    if total == 0: return 1.0, 1.0

    high_count = len([c for c in remaining if c[0] > current_rank])
    low_count = len([c for c in remaining if c[0] < current_rank])
    same_count = len([c for c in remaining if c[0] == current_rank])

    if current_rank == 14: # Ace
        prob_1 = same_count / total if total > 0 else 0
        prob_2 = low_count / total if total > 0 else 0
    else: # Normal
        prob_1 = (high_count + same_count) / total if total > 0 else 0
        prob_2 = (low_count + same_count) / total if total > 0 else 0

    odds_1 = round(1 / prob_1, 2) if prob_1 > 0 else 0.0
    odds_2 = round(1 / prob_2, 2) if prob_2 > 0 else 0.0
    
    return min(odds_1, 50.0), min(odds_2, 50.0)

def add_chip(amount):
    if st.session_state.balance >= amount:
        st.session_state.balance -= amount
        st.session_state.current_pot += amount
        st.session_state.game_message = "베팅 진행 중..."
    else:
        st.session_state.game_message = "잔액이 부족합니다!"

def cash_out():
    if st.session_state.current_pot > 0:
        win_amount = st.session_state.current_pot
        st.session_state.balance += win_amount
        st.session_state.game_message = f"인출 완료! (+{win_amount:,}원)"
        reset_game_state()
    else:
        st.session_state.game_message = "인출할 금액이 없습니다."

def process_bet(bet_type):
    if st.session_state.current_pot <= 0:
        st.session_state.game_message = "칩을 먼저 선택해 주세요!"
        return

    current_card = st.session_state.current_card
    current_rank = current_card[0]
    
    odds_1, odds_2 = calculate_odds(current_rank)
    odds_fixed = 1.95

    next_card = draw_card()
    next_rank = next_card[0]
    next_suit = next_card[1]
    
    win = False
    payout_mult = 0.0

    if current_rank == 14: # Ace
        if bet_type == "Hi": # Same
            payout_mult = odds_1
            if next_rank == 14: win = True
        elif bet_type == "Lo": # Under
            payout_mult = odds_2
            if next_rank < 14: win = True
    else: # Normal
        if bet_type == "Hi": # Over
            payout_mult = odds_1
            if next_rank >= current_rank: win = True
        elif bet_type == "Lo": # Under
            payout_mult = odds_2
            if next_rank <= current_rank: win = True

    if bet_type == "Red":
        payout_mult = odds_fixed
        if next_suit in RED_SUITS: win = True
    elif bet_type == "Black":
        payout_mult = odds_fixed
        if next_suit in BLACK_SUITS: win = True

    cur_r_disp, cur_s_disp, _ = get_card_display(next_rank, next_suit)
    card_disp = f"{cur_s_disp}{cur_r_disp}"

    if win:
        new_pot = int(st.session_state.current_pot * payout_mult)
        st.session_state.current_pot = new_pot
        st.session_state.game_message = f"적중! {card_disp} (현재 {new_pot:,}원)"
        
        st.session_state.history.insert(0, current_card)
        if len(st.session_state.history) > 6:
            st.session_state.history.pop()
        st.session_state.current_card = next_card
    else:
        st.session_state.game_message = f"버스트! ({card_disp})"
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

st.divider()

# (2) 메인 게임 영역 (Deck & Current Card)
c1, c2 = st.columns([1, 1]) # 1:1 비율
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

# 게임 메시지
st.markdown(f"<h4 style='text-align:center; color:#ffd700; margin: 15px 0;'>{st.session_state.game_message}</h4>", unsafe_allow_html=True)

# (3) 베팅 컨트롤 영역
# 배당률 계산
current_rank = st.session_state.current_card[0]
odds_1, odds_2 = calculate_odds(current_rank)
curr_pot = st.session_state.current_pot
next_pot_1 = int(curr_pot * odds_1)
next_pot_2 = int(curr_pot * odds_2)
next_pot_rb = int(curr_pot * 1.95)

if current_rank == 14: # Ace
    label_1 = "동일 (Same)"
    label_2 = "미만 (Under)"
else:
    label_1 = "초과 (Over)"
    label_2 = "미만 (Under)"

# [수정] 베팅 버튼 레이아웃 - 위 카드박스([1,1])와 동일한 그리드 사용
b_col1, b_col2 = st.columns([1, 1]) 

with b_col1:
    # 스타일 적용을 위해 컨테이너 사용
    st.markdown('<div class="bet-btn-style">', unsafe_allow_html=True)
    if st.button(f"{label_1}\nx{odds_1}\nGet: {next_pot_1:,}", key="bet_hi"): process_bet("Hi"); st.rerun()
    if st.button(f"Black (♠♣)\nx1.95\nGet: {next_pot_rb:,}", key="bet_black"): process_bet("Black"); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with b_col2:
    st.markdown('<div class="bet-btn-style">', unsafe_allow_html=True)
    if st.button(f"{label_2}\nx{odds_2}\nGet: {next_pot_2:,}", key="bet_lo"): process_bet("Lo"); st.rerun()
    if st.button(f"Red (♥♦)\nx1.95\nGet: {next_pot_rb:,}", key="bet_red"): process_bet("Red"); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# (4) 인출(Cash Out) 버튼 (이전 획득금액 표시창 스타일 적용 + 중앙 배치)
st.markdown('<div class="cashout-container"><div style="width: 50%;">', unsafe_allow_html=True) # 중앙 50% 너비
st.markdown('<div class="cashout-btn-style">', unsafe_allow_html=True)
# 버튼 내용: 현재 획득 금액 표시
cashout_label = f"₩ {st.session_state.current_pot:,}\nIN CHUL (인출)"
if st.button(cashout_label, key="cash_out"):
    cash_out()
    st.rerun()
st.markdown('</div></div></div>', unsafe_allow_html=True)

st.divider()

# (5) 칩 선택 영역 (버튼 확대)
st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
st.markdown(f"#### 칩을 눌러 금액 추가 (즉시 차감)", unsafe_allow_html=True)

chip_cols = st.columns(6)
chips = [1000, 5000, 10000, 50000, 100000, 500000]
for i, amount in enumerate(chips):
    with chip_cols[i]:
        st.markdown('<div class="chip-btn-style">', unsafe_allow_html=True)
        if st.button(f"+{amount//1000}k", key=f"chip_{amount}"):
            add_chip(amount)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# (6) 보유 머니
st.markdown(f"""
<div class='balance-box'>
    <span style='font-size:18px; color:#aaa;'>보유 머니 (Balance)</span><br>
    <span style='font-size:36px; color:#4CAF50; font-weight:bold;'>₩ {st.session_state.balance:,}</span>
</div>
""", unsafe_allow_html=True)
