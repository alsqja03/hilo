import streamlit as st
import random
import time

# --- 1. 게임 설정 및 초기화 ---
st.set_page_config(page_title="Evolution Style Hi-Lo", layout="centered")

# 카드 문양 및 색상 정의
SUITS = ['♠', '♣', '♥', '♦']
RED_SUITS = ['♥', '♦']
BLACK_SUITS = ['♠', '♣']

# 카드 숫자 및 표시 문자
RANKS = list(range(2, 15)) # 2 ~ 14 (Ace)
RANK_MAP = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}

def get_card_display(rank, suit):
    """숫자와 문양을 받아 표시용 문자열과 색상을 반환"""
    r_str = RANK_MAP.get(rank, str(rank))
    color = "red" if suit in RED_SUITS else "black"
    return r_str, suit, color

# 세션 상태 초기화 (새로고침 해도 데이터 유지)
if 'deck' not in st.session_state:
    st.session_state.deck = []
    st.session_state.current_card = None
    st.session_state.history = [] # [바로 전, 전전, ...]
    st.session_state.balance = 1000000 # 시작 자금
    st.session_state.bet_amount = 10000 # 기본 베팅금
    st.session_state.game_message = "게임을 시작합니다. 칩을 선택하고 베팅하세요."
    
    # 덱 생성 함수
    def create_deck():
        deck = []
        for r in RANKS:
            for s in SUITS:
                deck.append((r, s))
        random.shuffle(deck)
        return deck
    
    st.session_state.deck = create_deck()
    st.session_state.current_card = st.session_state.deck.pop()

# --- 2. 게임 로직 함수 ---

def draw_card():
    """카드를 뽑고 덱이 비면 섞음"""
    if len(st.session_state.deck) == 0:
        st.session_state.deck = [] # create_deck 로직 재사용 필요하나 간단히 처리
        for r in RANKS:
            for s in SUITS:
                st.session_state.deck.append((r, s))
        random.shuffle(st.session_state.deck)
        st.session_state.game_message = "덱을 새로 셔플했습니다!"
    return st.session_state.deck.pop()

def calculate_odds(current_rank):
    """현재 카드를 기준으로 Hi/Lo 배당률 계산"""
    remaining = st.session_state.deck
    total = len(remaining)
    if total == 0: return 1.0, 1.0

    high_count = len([c for c in remaining if c[0] > current_rank])
    low_count = len([c for c in remaining if c[0] < current_rank])

    # 배당 계산 (하우스 엣지 없이 순수 확률 역수, 최소 1.01배)
    odds_high = round(1 / (high_count / total), 2) if high_count > 0 else 1.01
    odds_low = round(1 / (low_count / total), 2) if low_count > 0 else 1.01
    
    # 극단적인 배당 제한 (UI 깨짐 방지)
    return min(odds_high, 20.0), min(odds_low, 20.0)

def process_bet(bet_type):
    """베팅 처리 로직"""
    bet_amt = st.session_state.bet_amount
    
    if st.session_state.balance < bet_amt:
        st.session_state.game_message = "잔액이 부족합니다!"
        return

    st.session_state.balance -= bet_amt
    current_card = st.session_state.current_card
    current_rank = current_card[0]
    
    # 배당률 확정 (베팅 시점 기준)
    odds_h, odds_l = calculate_odds(current_rank)
    odds_fixed = 1.95 # Red/Black 고정 배당

    # 다음 카드 뽑기
    next_card = draw_card()
    next_rank = next_card[0]
    next_suit = next_card[1]
    
    # 승패 판정
    win = False
    payout = 0
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

    # 결과 처리
    if win:
        payout = int(bet_amt * payout_mult)
        st.session_state.balance += payout
        st.session_state.game_message = f"승리! {next_card[1]}{RANK_MAP.get(next_rank, next_rank)} 당첨! (+{payout:,}원)"
    elif next_rank == current_rank:
        st.session_state.game_message = f"SNAP! (동일 숫자) - 패배. ({next_card[1]}{RANK_MAP.get(next_rank, next_rank)})"
    else:
        st.session_state.game_message = f"패배... 결과: {next_card[1]}{RANK_MAP.get(next_rank, next_rank)}"

    # 히스토리 업데이트 (최신이 앞으로)
    st.session_state.history.insert(0, current_card)
    if len(st.session_state.history) > 5:
        st.session_state.history.pop()
    
    # 현재 카드 갱신
    st.session_state.current_card = next_card


# --- 3. UI 스타일링 (CSS Injection) ---
st.markdown("""
<style>
    .stApp { background-color: #1e1e1e; color: white; }
    .card-box {
        border: 2px solid #ddd; border-radius: 10px; padding: 20px;
        text-align: center; background-color: white; color: black;
        font-weight: bold; font-size: 24px; margin: 5px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.5);
    }
    .history-card {
        border: 1px solid #888; border-radius: 5px; padding: 10px;
        text-align: center; background-color: #ddd; color: black;
        font-size: 14px; width: 50px; display: inline-block; margin-right: 5px;
    }
    .big-card {
        font-size: 60px; height: 180px; line-height: 140px;
    }
    .bet-btn-area {
        border: 2px solid #ffd700; border-radius: 15px; padding: 10px;
        margin-top: 10px; text-align: center;
    }
    .stat-text { font-size: 18px; color: #ccc; }
    .highlight-text { color: #ffd700; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 4. 화면 구성 ---

# (1) 히스토리 영역 (스케치 상단)
st.markdown("### Previous Cards")
hist_cols = st.columns(6)
# 현재 카드를 가장 왼쪽에 표시 (스케치: '현재')
cur_r, cur_s, cur_c = get_card_display(st.session_state.current_card[0], st.session_state.current_card[1])
with hist_cols[0]:
    st.markdown(f"<div class='history-card' style='border: 2px solid gold; background: white; color:{cur_c}'>{cur_s}<br>{cur_r}</div>", unsafe_allow_html=True)
    st.caption("Current")

# 과거 기록 표시 (스케치: '바로 전', '바로 전 전')
for i, card in enumerate(st.session_state.history[:5]):
    hr, hs, hc = get_card_display(card[0], card[1])
    with hist_cols[i+1]:
        st.markdown(f"<div class='history-card' style='color:{hc}'>{hs}<br>{hr}</div>", unsafe_allow_html=True)


st.divider()

# (2) 메인 게임 영역 (스케치 중간: 카드 뭉치 vs 현재 카드)
c1, c2 = st.columns([1, 1])

with c1:
    st.markdown("<div style='text-align:center; padding-top:40px;'>", unsafe_allow_html=True)
    # 카드 뒷면 이미지 대신 텍스트/박스로 표현
    st.markdown(f"""
    <div class='card-box big-card' style='background: repeating-linear-gradient(45deg, #606dbc, #606dbc 10px, #465298 10px, #465298 20px); color: white;'>
        Deck<br><span style='font-size:20px'>{len(st.session_state.deck)} left</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div style='text-align:center; padding-top:40px;'>", unsafe_allow_html=True)
    # 현재 오픈된 카드
    st.markdown(f"""
    <div class='card-box big-card' style='color: {cur_c}'>
        {cur_s} {cur_r}
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# 게임 메시지 출력
st.markdown(f"<h3 style='text-align:center; color:orange;'>{st.session_state.game_message}</h3>", unsafe_allow_html=True)

st.divider()

# (3) 베팅 컨트롤 영역 (스케치: 배당 박스들)
# 배당률 실시간 계산
odds_h, odds_l = calculate_odds(st.session_state.current_card[0])
potential_win_h = int(st.session_state.bet_amount * odds_h)
potential_win_l = int(st.session_state.bet_amount * odds_l)
potential_win_rb = int(st.session_state.bet_amount * 1.95)

# 2x2 그리드 버튼
b_col1, b_col2 = st.columns(2)

with b_col1:
    # Hi 버튼
    if st.button(f"Hi (▲) \nx{odds_h}\nWin: {potential_win_h:,}", use_container_width=True):
        process_bet("Hi")
        st.rerun()
    
    # Black 버튼
    if st.button(f"Black (♠♣) \nx1.95\nWin: {potential_win_rb:,}", use_container_width=True):
        process_bet("Black")
        st.rerun()

with b_col2:
    # Lo 버튼
    if st.button(f"Lo (▼) \nx{odds_l}\nWin: {potential_win_l:,}", use_container_width=True):
        process_bet("Lo")
        st.rerun()
    
    # Red 버튼
    if st.button(f"Red (♥♦) \nx1.95\nWin: {potential_win_rb:,}", use_container_width=True):
        process_bet("Red")
        st.rerun()

st.divider()

# (4) 칩 선택 및 정보 (스케치 하단)
st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
st.markdown(f"#### 현재 베팅 금액: <span style='color:gold'>{st.session_state.bet_amount:,} 원</span>", unsafe_allow_html=True)

# 칩 버튼들 (가로로 배열)
chips = [1000, 5000, 10000, 50000, 100000, 500000]
cols = st.columns(len(chips))
for i, amount in enumerate(chips):
    with cols[i]:
        if st.button(f"{amount//1000}k", key=f"chip_{amount}"):
            st.session_state.bet_amount = amount
            st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# (5) 보유 머니 (스케치 맨 아래)
st.markdown(f"""
<div style='background-color:#333; padding:15px; border-radius:10px; text-align:center; margin-top:20px;'>
    <span style='font-size:20px; color:white;'>보유 머니 (Balance)</span><br>
    <span style='font-size:32px; color:#4CAF50; font-weight:bold;'>₩ {st.session_state.balance:,}</span>
</div>
""", unsafe_allow_html=True)
