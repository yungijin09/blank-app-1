import streamlit as st
import plotly.graph_objects as go
import random
import time

# --- 앱 기본 설정 ---
st.set_page_config(layout="centered", page_title="간단 룰렛")

# --- CSS 스타일 (선택된 이름 강조 및 룰렛 시각화 조정) ---
st.markdown("""
<style>
/* Streamlit 제목 및 부제목 중앙 정렬 */
h1 {
    text-align: center;
}
h2 {
    text-align: center;
    color: #4CAF50; /* 초록색 */
}
/* Plotly 차트 컨테이너 크기 조정 (필요시) */
.stPlotlyChart {
    width: 100% !important;
    height: 500px !important; /* 룰렛 높이 조정 */
}
</style>
""", unsafe_allow_html=True)

# --- 세션 상태 초기화 ---
# 'names' 리스트가 세션 상태에 없으면 빈 리스트로 초기화합니다.
if 'names' not in st.session_state:
    st.session_state.names = []
# 'winner'가 세션 상태에 없으면 None으로 초기화합니다.
if 'winner' not in st.session_state:
    st.session_state.winner = None
# 'roulette_spun'이 세션 상태에 없으면 False로 초기화합니다.
if 'roulette_spun' not in st.session_state:
    st.session_state.roulette_spun = False

# --- 함수: 룰렛 그리기 ---
def draw_roulette(names, highlight_index=None):
    """
    주어진 이름 리스트로 룰렛 원형 차트를 그립니다.
    highlight_index가 있으면 해당 부분을 강조합니다.
    """
    if not names:
        # 이름이 없으면 빈 차트 반환
        return go.Figure()

    # 각 조각의 색상 (선택된 조각은 다른 색)
    colors = ['#FFDDC1', '#DCF8C6', '#ADD8E6', '#FFAB91', '#DCE775', '#B39DDB', '#FFCDD2', '#A1887F']
    num_names = len(names)
    pie_colors = colors * (num_names // len(colors) + 1) # 이름 개수만큼 색상 반복

    # 파이 조각의 텍스트 설정
    # labels: 각 조각에 표시될 이름
    # values: 각 조각의 크기 (모두 동일하게 1로 설정하여 균등하게 분할)
    fig = go.Figure(data=[go.Pie(
        labels=names,
        values=[1]*num_names,
        marker_colors=pie_colors[:num_names],
        hole=.3, # 룰렛 중앙에 구멍을 만듭니다.
        hoverinfo='label', # 마우스 오버 시 이름만 표시
        textinfo='label', # 차트에 직접 이름 표시
        textfont_size=16 # 텍스트 크기
    )])

    # 룰렛 레이아웃 설정
    fig.update_layout(
        showlegend=False, # 범례 숨기기
        margin=dict(t=0, b=0, l=0, r=0), # 여백 최소화
        height=500, # 차트 높이
        paper_bgcolor="rgba(0,0,0,0)", # 배경 투명
        plot_bgcolor="rgba(0,0,0,0)", # 플롯 영역 투명
        annotations=[dict(text='룰렛', x=0.5, y=0.5, font_size=20, showarrow=False, xref="paper", yref="paper")]
    )

    # 특정 조각 강조 (선택된 이름)
    if highlight_index is not None and 0 <= highlight_index < num_names:
        # 강조할 조각의 색상을 변경합니다.
        highlight_color = '#FF4B4B' # 강조 색상 (빨간색)
        fig.data[0].marker.colors[highlight_index] = highlight_color
        
        # 강조된 조각을 약간 튀어나오게 합니다 (pulled effect)
        pulled = [0] * num_names
        pulled[highlight_index] = 0.1 # 0.1만큼 바깥으로 빼냅니다.
        fig.data[0].pull = pulled

    return fig

# --- 함수: 룰렛 돌리기 ---
def spin_roulette():
    """룰렛을 돌리고 당첨자를 결정하는 함수."""
    if not st.session_state.names:
        st.warning("먼저 룰렛에 이름을 입력해주세요!")
        return

    st.session_state.roulette_spun = True # 룰렛이 돌아가는 중임을 표시
    st.session_state.winner = None # 기존 당첨자 초기화

    # 룰렛 애니메이션 효과 (반복적으로 차트 업데이트)
    # 실제로는 회전 애니메이션이 아니라, 빠르게 결과를 예측하는 것처럼 보이게 합니다.
    # 여러 번 빠르게 당첨 후보를 보여줍니다.
    num_spins = 20 # 돌리는 횟수
    for i in range(num_spins):
        temp_winner_idx = random.randrange(len(st.session_state.names))
        
        # 룰렛 그리기 (선택된 이름을 강조)
        current_fig = draw_roulette(st.session_state.names, temp_winner_idx)
        st.session_state.chart_placeholder.plotly_chart(current_fig, use_container_width=True)
        
        # 마지막으로 갈수록 속도 줄이기
        time.sleep(0.05 + (i / num_spins) * 0.2) # 점점 느려지게

    # 최종 당첨자 선택
    final_winner_idx = random.randrange(len(st.session_state.names))
    st.session_state.winner = st.session_state.names[final_winner_idx]

    # 최종 룰렛 결과 표시 (당첨자 강조)
    final_fig = draw_roulette(st.session_state.names, final_winner_idx)
    st.session_state.chart_placeholder.plotly_chart(final_fig, use_container_width=True)
    
    st.balloons() # 당첨 시 축하 풍선 효과!

# --- 메인 앱 로직 ---
def main():
    st.title("간단 룰렛 🎡")

    # --- 1. 이름 입력 ---
    st.subheader("룰렛 참가자 이름 입력")
    # 텍스트 입력창에서 쉼표로 구분된 이름을 받습니다.
    # `key`를 사용하여 Streamlit이 이 위젯을 고유하게 식별하도록 합니다.
    names_input = st.text_input(
        "이름을 쉼표(,)로 구분하여 입력하세요 (예: 김철수, 이영희, 박지민)",
        value=", ".join(st.session_state.names), # 세션 상태의 값을 기본값으로 표시
        key="names_text_input"
    )

    # 입력된 이름을 리스트로 변환 (공백 제거 및 빈 문자열 필터링)
    current_names = [name.strip() for name in names_input.split(',') if name.strip()]
    
    # 세션 상태의 이름 리스트와 현재 입력된 리스트가 다르면 업데이트
    if current_names != st.session_state.names:
        st.session_state.names = current_names
        # 이름 목록이 변경되면 당첨자 및 룰렛 상태 초기화
        st.session_state.winner = None
        st.session_state.roulette_spun = False
        st.rerun() # 이름 변경 시 UI를 다시 그립니다.

    # --- 2. 룰렛 돌리기 버튼 ---
    # 룰렛 차트를 표시할 빈 공간을 미리 만듭니다.
    # `st.empty()`를 사용하면 나중에 이 공간을 업데이트할 수 있습니다.
    st.session_state.chart_placeholder = st.empty()

    # '돌리기' 버튼
    # `on_click`을 사용하여 버튼 클릭 시 `spin_roulette` 함수를 호출합니다.
    st.button("돌리기 🚀", on_click=spin_roulette, use_container_width=True, help="룰렛을 돌려 당첨자를 뽑습니다.")
    
    # --- 3. 룰렛 초기 상태 또는 결과 표시 ---
    if not st.session_state.roulette_spun and st.session_state.names:
        # 룰렛이 아직 돌아가지 않았지만 이름이 있을 경우 초기 룰렛을 그립니다.
        initial_fig = draw_roulette(st.session_state.names)
        st.session_state.chart_placeholder.plotly_chart(initial_fig, use_container_width=True)
    elif st.session_state.roulette_spun and st.session_state.winner:
        # 룰렛이 돌아갔고 당첨자가 있을 경우 최종 결과를 표시합니다.
        final_fig = draw_roulette(st.session_state.names, st.session_state.names.index(st.session_state.winner))
        st.session_state.chart_placeholder.plotly_chart(final_fig, use_container_width=True)
        st.subheader(f"✨ 당첨자는 바로... {st.session_state.winner}님 입니다! 🎉")
    elif not st.session_state.names:
        # 이름이 없을 경우 안내 메시지 표시
        st.session_state.chart_placeholder.warning("이름을 입력하고 '돌리기' 버튼을 눌러주세요!")


if __name__ == "__main__":
    main()