import streamlit as st
import random

# --- 1. 페이지 및 스타일 설정 ---
st.set_page_config(page_title="Evolution Style Hi-Lo", layout="centered")

# CSS 스타일 주입
st.markdown("""
<style>
    .stApp { background-color: #1e1e1e; color: white; }
    
    /* 상단 로고 컨테이너 */
    .logo-container {
        display: flex; justify-content: center; margin-bottom: 20px;
    }
    
    /* 카드 박스 스타일 */
    .card-box {
        border: 2px solid #ddd; border-radius: 10px; padding: 10px;
        text-align: center; background-color: white; color: black;
        font-weight: bold; font-size: 24px; margin: 5px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.5);
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        height: 150px; /* 높이 고정 */
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
    
    /* 베팅 버튼 스타일 (네모난 카드 형태) */
    .bet-button {
        border: 2px solid #ffd700 !important; /* 금색 테두리 */
        border-radius: 10px !important; /* 약간 둥근 모서리 */
        background-color: #333 !important;
        color: white !important;
        padding: 10px !important;
        height: 100px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        transition: all 0.3s ease;
    }
    .bet-button:hover {
        background-color: #444 !important;
        border-color: white !important;
        cursor: pointer;
    }
    .bet-type { font-size: 20px; font-weight: bold; margin-bottom: 5px; }
    .bet-odds { font-size: 16px; color: #ffd700; }
    .bet-win { font-size: 14px; color: #aaa; }

    /* 스트림릿 기본 버튼 스타일 오버라이드 */
    .stButton > button {
        width: 100%;
        border-radius: 5px;
        font-weight: bold;
    }
    /* 칩 버튼 스타일 */
    div[data-testid="column"] > .stButton > button {
        background-color: #555 !important; color: white !important;
        border: 1px solid #777 !important; height: 50px !important;
        font-size: 14px !important;
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

# 세션 상태 초기화
if 'deck' not in st.session_state:
    st.session_state.deck = create_deck(2) # 2덱 사용
    st.session_state.current_card = st.session_state.deck.pop()
    st.session_state.history = []
    st.session_state.bet_amount = 0 # 초기 베팅금 0원
    st.session_state.game_message = "게임을 시작합니다. 칩을 눌러 베팅 금액을 추가하세요."

# 사이드바: 보유 머니 설정
with st.sidebar:
    st.header("게임 설정")
    initial_balance = st.number_input("초기 보유 머니 설정", min_value=10000, value=1000000, step=10000, format="%d")
    if 'balance' not in st.session_state:
        st.session_state.balance = initial_balance
    
    if st.button("설정된 머니로 게임 재시작"):
        st.session_state.balance = initial_balance
        st.session_state.deck = create_deck(2)
        st.session_state.current_card = st.session_state.deck.pop()
        st.session_state.history = []
        st.session_state.bet_amount = 0
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

    st.session_state.balance -= bet_amt
    current_card = st.session_state.current_card
    current_rank = current_card[0]
    
    odds_h, odds_l = calculate_odds(current_rank)
    odds_fixed = 1.95

    next_card = draw_card()
    next_rank = next_card[0]
    next_suit = next_card[1]
    
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

    cur_r_disp, cur_s_disp, _ = get_card_display(next_rank, next_suit)
    card_disp = f"{cur_s_disp}{cur_r_disp}"

    if win:
        payout = int(bet_amt * payout_mult)
        st.session_state.balance += payout
        st.session_state.game_message = f"승리! {card_disp} 당첨! (+{payout:,}원)"
    elif next_rank == current_rank:
        st.session_state.game_message = f"SNAP! (동일 숫자) - 패배. ({card_disp})"
    else:
        st.session_state.game_message = f"패배... 결과: {card_disp}"

    st.session_state.history.insert(0, current_card)
    if len(st.session_state.history) > 6:
        st.session_state.history.pop()
    
    st.session_state.current_card = next_card
    # st.session_state.bet_amount = 0 # 게임 후 베팅금 초기화 (선택사항)


# --- 3. 화면 구성 ---

# (0) 상단 로고
st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
st.image("image_4.png", width=300) # 로고 이미지 파일명 확인 필요
st.markdown("</div>", unsafe_allow_html=True)

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

# (3) 베팅 컨트롤 영역 (네모난 버튼 UI)
odds_h, odds_l = calculate_odds(st.session_state.current_card[0])
bet_amt = st.session_state.bet_amount
pot_h = int(bet_amt * odds_h)
pot_l = int(bet_amt * odds_l)
pot_rb = int(bet_amt * 1.95)

# 커스텀 버튼 생성 함수
def create_bet_button(col, type_str, label, odds_val, pot_val, color_class=""):
    with col:
        btn_html = f"""
        <button class='bet-button {color_class}'>
            <div class='bet-type'>{label}</div>
            <div class='bet-odds'>x{odds_val}</div>
            <div class='bet-win'>Win: {pot_val:,}</div>
        </button>
        """
        if st.button(label, key=f"btn_{type_str}", help=f"{label} 베팅"): # 실제 클릭 이벤트용 투명 버튼
            process_bet(type_str)
            st.rerun()
        # 위 st.button 위에 HTML 버튼을 덮어씌우는 방식으로 구현 (제한적)
        # Streamlit 한계로 완벽한 커스텀 HTML 버튼 이벤트 연결이 어려워, 
        # 시각적 요소는 HTML로, 클릭은 st.button으로 처리하는 타협안을 사용합니다.
        # 실제로는 st.button의 스타일을 CSS로 덮어쓰는 방식이 더 안정적입니다.
        # 아래는 CSS로 스타일링된 st.button을 사용하는 방식입니다.

# 2x2 그리드 베팅 버튼 (CSS 스타일 적용됨)
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

chip_cols = st.columns([1, 1, 1, 1, 1, 1, 1.5]) # 마지막 컬럼은 초기화 버튼용
chips = [1000, 5000, 10000, 50000, 100000, 500000]
for i, amount in enumerate(chips):
    with chip_cols[i]:
        if st.button(f"+{amount//1000}k", key=f"chip_{amount}"):
            st.session_state.bet_amount += amount # 금액 누적
            st.rerun()

# 베팅 금액 초기화 버튼
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
