import streamlit as st
import random

# --- 1. 페이지 및 스타일 설정 ---
st.set_page_config(page_title="Evolution Style Hi-Lo", layout="centered")

# CSS 스타일 주입
st.markdown("""
<style>
    .stApp { background-color: #1e1e1e; color: white; }
    
    /* 상단 타이틀 컨테이너 */
    .title-container {
        display: flex; justify-content: center; margin-bottom: 20px;
        border-bottom: 2px solid #333; padding-bottom: 10px;
    }
    
    /* 카드 박스 스타일 */
    .card-box {
        border: 2px solid #ddd; border-radius: 10px; padding: 10px;
        text-align: center; background-color: white; color: black;
        font-weight: bold; font-size: 24px; margin: 5px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.5);
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        height: 150px;
    }
    .big-card-text { font-size: 48px; line-height: 1.1; }
    .deck-text { font-size: 36px; font-weight: bold; }
    
    /* 히스토리 카드 스타일 */
    .history-card {
        border: 1px solid #888; border-radius: 5px; padding: 5px;
        text-align: center; background-color: #ddd; color: black;
        font-size: 12px; width: 40px; height: 50px; display: flex;
        justify-content: center; align-items: center; flex-direction: column;
    }
    
    /* 베팅 버튼 스타일 */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
        border: 2px solid #ffd700;
        background-color: #333;
        color: white;
        padding: 10px;
        height: auto;
        white-space: pre-wrap;
    }
    .stButton > button:hover {
        background-color: #444;
        border-color: white;
    }

    /* 칩 버튼 스타일 */
    div[data-testid="column"] > .stButton > button {
        background-color: #555 !important; color: white !important;
        border: 1px solid #777 !important; height: 50px !important;
        font-size: 14px !important; padding: 0 !important;
    }
    div[data-testid="column"] > .stButton > button:hover {
        background-color: #777 !important; border-color: white !important;
    }
    /* 초기화 버튼 스타일 */
    .reset-btn > button {
        background-color: #d32f2f !important; color: white !important;
        border: none !important;
    }
    .reset-btn > button:hover { background-color: #b71c1c !important; }

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
    """지정된 수만큼의 덱을 생성하고 셔플"""
    deck = []
    for _ in range(num_decks):
        for r in RANKS:
            for s in SUITS:
                deck.append((r, s))
    random.shuffle(deck)
    return deck

def reset_game_state():
    """보유 머니를 제외한 게임 상태 초기화"""
    st.session_state.deck = create_deck(2)
    st.session_state.current_card = st.session_state.deck.pop()
    st.session_state.history = []
    st.session_state.bet_amount = 0

# 세션 상태 초기화
if 'deck' not in st.session_state:
    st.session_state.balance = 1000000 # Default
    reset_game_state()
    st.session_state.game_message = "게임을 시작합니다. 칩을 눌러 베팅 금액을 추가하세요."

# 사이드바: 보유 머니 설정
with st.sidebar:
    st.header("게임 설정")
    initial_balance = st.number_input("초기 보유 머니 설정", min_value=10000, value=1000000, step=10000, format="%d")
    if st.button("설정된 머니로 완전 초기화"):
        st.session_state.balance = initial_balance
        reset_game_state()
        st.session_state.game_message = "새로운 게임이 시작되었습니다."
        st.rerun()

def draw_card():
    if len(st.session_state.deck) == 0:
        st.session_state.deck = create_deck(2)
        st.session_state.game_message = "덱을 새로 셔플했습니다! (2 Decks)"
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

def process_bet(bet_type):
    bet_amt = st.session_state.bet_amount
    if bet_amt <= 0:
        st.session_state.game_message = "베팅 금액을 설정해주세요!"
        return
    if st.session_state.balance < bet_amt:
        st.session_state.game_message = "잔액이 부족합니다!"
        return

    # 1. 베팅금 차감
    st.session_state.balance -= bet_amt
    current_card = st.session_state.current_card
    current_rank = current_card[0]
    
    # 2. 배당 계산
    odds_h, odds_l = calculate_odds(current_rank)
    odds_fixed = 1.95

    # 3. 결과 카드 오픈
    next_card = draw_card()
    next_rank = next_card[0]
    next_suit = next_card[1]
    
    # 4. 승패 판정
    win = False
    payout_mult = 0

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

    # 결과 표시용 문자열
    cur_r_disp, cur_s_disp, _ = get_card_display(next_rank, next_suit)
    card_disp = f"{cur_s_disp}{cur_r_disp}"

    # 5. 결과 처리 분기
    if win:
        # [승리] -> 게임 계속 진행 (History 쌓임)
        payout = int(bet_amt * payout_mult)
        st.session_state.balance += payout
        st.session_state.game_message = f"승리! {card_disp} 당첨! (+{payout:,}원)"
        
        # 히스토리 업데이트
        st.session_state.history.insert(0, current_card)
        if len(st.session_state.history) > 6:
            st.session_state.history.pop()
        
        # 현재 카드 갱신
        st.session_state.current_card = next_card
        
    else:
        # [패배] -> 보유 머니 제외하고 모두 초기화
        loss_reason = "예측 실패"
        if next_rank == current_rank:
            loss_reason = "SNAP(동일 숫자)"
            
        st.session_state.game_message = f"패배 ({loss_reason})! 결과: {card_disp} -> 게임이 초기화되었습니다."
        
        # --- 초기화 로직 수행 ---
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

# (2) 메인 게임 영역
c1, c2 = st.columns([1, 1])
with c1:
    st.markdown(f"""
    <div class='card-box' style='background: repeating-linear-gradient(45deg, #606dbc, #606dbc 10px, #465298 10px, #465298 20px); color: white;'>
        <div class='deck-text'>Deck</div>
        <div style='font-size: 24px; margin-top: 10px;'>{len(st.session_state.deck)} left</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class='card-box' style='color: {cur_c};'>
        <div class='big-card-text'>{cur_s}<br>{cur_r}</div>
    </div>
    """, unsafe_allow_html=True)

# 게임 메시지
st.markdown(f"<h4 style='text-align:center; color:#ffd700; margin: 20px 0;'>{st.session_state.game_message}</h4>", unsafe_allow_html=True)

# (3) 베팅 컨트롤 영역
odds_h, odds_l = calculate_odds(st.session_state.current_card[0])
bet_amt = st.session_state.bet_amount
pot_h = int(bet_amt * odds_h)
pot_l = int(bet_amt * odds_l)
pot_rb = int(bet_amt * 1.95)

b_col1, b_col2 = st.columns(2)
with b_col1:
    if st.button(f"Hi (▲)\nx{odds_h}\nWin: {pot_h:,}", key="bet_hi"): process_bet("Hi"); st.rerun()
    if st.button(f"Black (♠♣)\nx1.95\nWin: {pot_rb:,}", key="bet_black"): process_bet("Black"); st.rerun()
with b_col2:
    if st.button(f"Lo (▼)\nx{odds_l}\nWin: {pot_l:,}", key="bet_lo"): process_bet("Lo"); st.rerun()
    if st.button(f"Red (♥♦)\nx1.95\nWin: {pot_rb:,}", key="bet_red"): process_bet("Red"); st.rerun()

st.divider()

# (4) 칩 선택 및 초기화 영역
st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
st.markdown(f"#### 총 베팅 금액: <span style='color:#ffd700; font-size:24px;'>{st.session_state.bet_amount:,} 원</span>", unsafe_allow_html=True)

chip_cols = st.columns([1, 1, 1, 1, 1, 1, 1.5])
chips = [1000, 5000, 10000, 50000, 100000, 500000]
for i, amount in enumerate(chips):
    with chip_cols[i]:
        if st.button(f"+{amount//1000}k", key=f"chip_{amount}"):
            st.session_state.bet_amount += amount
            st.rerun()

with chip_cols[-1]:
    st.markdown("<div class='reset-btn'>", unsafe_allow_html=True)
    if st.button("Reset ↺", key="reset_bet"):
        st.session_state.bet_amount = 0
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# (5) 보유 머니
st.markdown(f"""
<div style='background-color:#333; padding:20px; border-radius:15px; text-align:center; margin-top:30px; border: 2px solid #555;'>
    <span style='font-size:18px; color:#aaa;'>보유 머니 (Balance)</span><br>
    <span style='font-size:36px; color:#4CAF50; font-weight:bold;'>₩ {st.session_state.balance:,}</span>
</div>
""", unsafe_allow_html=True)
