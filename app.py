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
    
    /* 베팅 버튼 */
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

    /* 인출(Cash Out) 버튼 스타일 */
    .cashout-btn > button {
        background-color: #2e7d32 !important; /* Green */
        color: white !important; font-size: 20px !important;
        border: 2px solid #4caf50 !important;
        height: 60px !important;
    }
    .cashout-btn > button:hover { background-color: #1b5e20 !important; }
    
    /* 초기화 버튼 */
    .reset-btn > button {
        background-color: #d32f2f !important; color: white !important; border: none !important;
    }

</style>
""", unsafe_allow_html=True)

# --- 2. 게임 데이터 및 함수 정의 ---

SUITS = ['♠', '♣', '♥', '♦']
RED_SUITS = ['♥', '♦']
BLACK_SUITS = ['♠', '♣']
RANKS = list(range(2, 15))
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

def reset_game_state(keep_balance=True):
    """게임을 재시작 (덱, 현재 카드 리셋). 보유머니는 유지."""
    st.session_state.deck = create_deck(2)
    st.session_state.current_card = st.session_state.deck.pop()
    st.session_state.history = []
    st.session_state.current_pot = 0 # 테이블 위 판돈 초기화

# 세션 상태 초기화
if 'deck' not in st.session_state:
    st.session_state.balance = 1000000
    st.session_state.current_pot = 0 # 현재 베팅/누적된 금액 (아직 인출 안한 돈)
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
    odds_high = round(1 / (high_count / total), 2) if high_count > 0 else 1.01
    odds_low = round(1 / (low_count / total), 2) if low_count > 0 else 1.01
    return min(odds_high, 20.0), min(odds_low, 20.0)

def add_chip(amount):
    """칩 클릭 시 즉시 차감 및 판돈 추가"""
    if st.session_state.balance >= amount:
        st.session_state.balance -= amount
        st.session_state.current_pot += amount
        st.session_state.game_message = "베팅 진행 중..."
    else:
        st.session_state.game_message = "잔액이 부족합니다!"

def cash_out():
    """인출 버튼 클릭 시"""
    if st.session_state.current_pot > 0:
        win_amount = st.session_state.current_pot
        st.session_state.balance += win_amount
        st.session_state.game_message = f"이기셨습니다. ({win_amount:,}원)"
        reset_game_state() # 인출 후 게임 재시작
    else:
        st.session_state.game_message = "인출할 금액이 없습니다."

def process_bet(bet_type):
    # 판돈이 걸려있지 않으면 베팅 불가
    if st.session_state.current_pot <= 0:
        st.session_state.game_message = "칩을 먼저 선택해 주세요!"
        return

    current_card = st.session_state.current_card
    current_rank = current_card[0]
    
    odds_h, odds_l = calculate_odds(current_rank)
    odds_fixed = 1.95

    next_card = draw_card()
    next_rank = next_card[0]
    next_suit = next_card[1]
    
    win = False
    payout_mult = 0.0

    if bet_type == "Hi":
        payout_mult = odds_h
        if next_rank > current_rank: win = True
    elif bet_type == "Lo":
        payout_mult = odds_l
        if next_rank < current_rank: win = True
    elif bet_type == "Red":
        payout_mult = odds_fixed
        if next_suit in RED_SUITS: win = True
    elif bet_type == "Black":
        payout_mult = odds_fixed
        if next_suit in BLACK_SUITS: win = True

    # 결과 카드 표시용
    cur_r_disp, cur_s_disp, _ = get_card_display(next_rank, next_suit)
    card_disp = f"{cur_s_disp}{cur_r_disp}"

    if win:
        # 승리 시: 축하 메시지 없이 금액만 불어남
        prev_pot = st.session_state.current_pot
        new_pot = int(prev_pot * payout_mult)
        st.session_state.current_pot = new_pot
        st.session_state.game_message = f"적중! {card_disp} (현재 {new_pot:,}원)"
        
        # 히스토리 업데이트 및 게임 계속 진행
        st.session_state.history.insert(0, current_card)
        if len(st.session_state.history) > 6:
            st.session_state.history.pop()
        st.session_state.current_card = next_card
        
    else:
        # 패배 시: 버스트 처리 및 리셋
        reason = "SNAP" if next_rank == current_rank else "예측 실패"
        st.session_state.game_message = f"버스트(Bust)! ({reason}: {card_disp})"
        reset_game_state() # 즉시 리셋 (판돈 0원 됨)


# --- 3. 화면 구성 ---

# (0) 상단 타이틀
st.markdown("""
<div class='title-container'>
    <h1 style='font-size: 48px; font-weight: bold; margin: 0; color: #ffd700; text-shadow: 2px 2px 4px #000000;'>HI-LO</h1>
</div>
""", unsafe_allow_html=True)

# (1) 히스토리 영역 (이전 카드)
st.markdown("### Previous Cards")
hist_cols = st.columns(7)
cur_r, cur_s, cur_c = get_card_display(st.session_state.current_card[0], st.session_state.current_card[1])
# 현재 카드는 여기서 보여주지 않고 메인 영역에서 보여줌. 히스토리만 표시.
# 그래도 배열상 0번을 Current라고 명시하는게 사용자가 헷갈리지 않음
with hist_cols[0]:
    st.markdown(f"<div class='history-card' style='border: 2px solid gold; background: white; color:{cur_c}'><span>{cur_s}</span><span>{cur_r}</span></div>", unsafe_allow_html=True)
    st.caption("Current")

for i, card in enumerate(st.session_state.history[:6]):
    hr, hs, hc = get_card_display(card[0], card[1])
    with hist_cols[i+1]:
        st.markdown(f"<div class='history-card' style='color:{hc}'><span>{hs}</span><span>{hr}</span></div>", unsafe_allow_html=True)

# (2) 현재 획득 금액 표시 (중간 영역)
pot_value = st.session_state.current_pot
st.markdown(f"""
<div class='pot-display'>
    <div style='color:#aaa; font-size:16px;'>현재 획득 금액 (Current Pot)</div>
    <div style='color:#ffd700; font-size:32px; font-weight:bold;'>₩ {pot_value:,}</div>
</div>
""", unsafe_allow_html=True)

# (3) 메인 게임 영역 (Deck & Current Card)
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

# 게임 상태 메시지
st.markdown(f"<h4 style='text-align:center; color:#ffd700; margin: 20px 0;'>{st.session_state.game_message}</h4>", unsafe_allow_html=True)

# (4) 베팅 컨트롤 영역
# 배당률 계산
odds_h, odds_l = calculate_odds(st.session_state.current_card[0])
# 현재 판돈 기준으로 예상 획득 금액 계산 (판돈이 0이면 0으로 표시됨)
curr_pot = st.session_state.current_pot
next_pot_h = int(curr_pot * odds_h)
next_pot_l = int(curr_pot * odds_l)
next_pot_rb = int(curr_pot * 1.95)

b_col1, b_col2 = st.columns(2)
with b_col1:
    if st.button(f"Hi (▲)\nx{odds_h}\nGet: {next_pot_h:,}", key="bet_hi"): process_bet("Hi"); st.rerun()
    if st.button(f"Black (♠♣)\nx1.95\nGet: {next_pot_rb:,}", key="bet_black"): process_bet("Black"); st.rerun()
with b_col2:
    if st.button(f"Lo (▼)\nx{odds_l}\nGet: {next_pot_l:,}", key="bet_lo"): process_bet("Lo"); st.rerun()
    if st.button(f"Red (♥♦)\nx1.95\nGet: {next_pot_rb:,}", key="bet_red"): process_bet("Red"); st.rerun()

st.divider()

# (5) 인출(Cash Out) 버튼 (베팅과 칩 사이)
st.markdown("<div style='display:flex; justify-content:center; margin-bottom:20px;'>", unsafe_allow_html=True)
c_btn_col1, c_btn_col2, c_btn_col3 = st.columns([1, 2, 1])
with c_btn_col2:
    # 스타일이 적용된 인출 버튼
    st.markdown("<div class='cashout-btn'>", unsafe_allow_html=True)
    if st.button(f"IN CHUL (인출)\n₩ {st.session_state.current_pot:,} 가져가기", key="cash_out"):
        cash_out()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# (6) 칩 선택 영역 (즉시 차감)
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

# (7) 보유 머니 (Balance)
st.markdown(f"""
<div style='background-color:#333; padding:20px; border-radius:15px; text-align:center; margin-top:30px; border: 2px solid #555;'>
    <span style='font-size:18px; color:#aaa;'>보유 머니 (Balance)</span><br>
    <span style='font-size:36px; color:#4CAF50; font-weight:bold;'>₩ {st.session_state.balance:,}</span>
</div>
""", unsafe_allow_html=True)
