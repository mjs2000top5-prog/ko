import streamlit as st
import pandas as pd

st.set_page_config(page_title="3개년 통합고용세액공제 계산기", layout="wide")

st.title("📊 3개년 통합고용세액공제 시뮬레이터")
st.info("2026년 공제액을 계산하기 위해 2024년~2025년 데이터와 연동하여 계산합니다.")

# 1. 설정 (사이드바)
with st.sidebar:
    st.header("⚙️ 기본 설정")
    tax_type = st.radio("공제 종류", ["통합고용세액공제", "고용증대세액공제"])
    biz_type = st.selectbox("기업 유형", ["중소기업", "중견기업", "일반기업"])
    location = st.radio("사업장 소재지", ["수도권", "비수도권"])

# 2. 공제 단가 결정 함수
def get_units(tax_type, biz_type, location):
    if biz_type == "중소기업":
        y_unit = 14500000 if location == "수도권" else 15500000
        o_unit = 8500000 if location == "수도권" else 9500000
    elif biz_type == "중견기업":
        y_unit = 8000000 if location == "수도권" else 9000000
        o_unit = 4500000 if location == "수도권" else 5000000
    else: # 일반기업 (대기업 등)
        y_unit = 0; o_unit = 0 
    return y_unit, o_unit

unit_y, unit_o = get_units(tax_type, biz_type, location)

# 3. 데이터 입력 (3개년 인원)
st.subheader("👥 연도별 상시근로자 수 입력")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 2024년 (기준)")
    y24 = st.number_input("24년 청년 (명)", min_value=0.0, value=10.0, key="y24")
    o24 = st.number_input("24년 청년외 (명)", min_value=0.0, value=10.0, key="o24")

with col2:
    st.markdown("### 2025년")
    y25 = st.number_input("25년 청년 (명)", min_value=0.0, value=12.0, key="y25")
    o25 = st.number_input("25년 청년외 (명)", min_value=0.0, value=11.0, key="o25")

with col3:
    st.markdown("### 2026년")
    y26 = st.number_input("26년 청년 (명)", min_value=0.0, value=15.0, key="y26")
    o26 = st.number_input("26년 청년외 (명)", min_value=0.0, value=12.0, key="o26")

# 4. 계산 로직 (증가분 및 공제액)
# 25년 공제액 = (25년 - 24년) 증가분
inc_y25 = max(0, y25 - y24)
inc_o25 = max(0, o25 - o24)
tax25 = (inc_y25 * unit_y) + (inc_o25 * unit_o)

# 26년 공제액 = 25년 증가분의 유지(2차분) + 26년 신규 증가분(1차분)
inc_y26 = max(0, y26 - y25)
inc_o26 = max(0, o26 - o25)
tax26_new = (inc_y26 * unit_y) + (inc_o26 * unit_o)
tax26_total = tax25 + tax26_new # 25년에 늘어난 인원이 유지된다는 가정 (추징 미고려 단순계산)

# 5. 결과 시각화
st.markdown("---")
st.subheader("💰 연도별 예상 세액공제 결과")

res_col1, res_col2 = st.columns(2)
res_col1.metric("2025년 총 공제액", f"{tax25:,.0f} 원", f"신규증가 {inc_y25+inc_o25}명")
res_col2.metric("2026년 총 공제액", f"{tax26_total:,.0f} 원", f"신규증가 {inc_y26+inc_o26}명")

# 결과 테이블
df_res = pd.DataFrame({
    "구분": ["청년 인원", "청년외 인원", "전년대비 증가(청년)", "전년대비 증가(일반)", "당해 신규 공제액"],
    "2024년": [f"{y24}명", f"{o24}명", "-", "-", "-"],
    "2025년": [f"{y25}명", f"{o25}명", f"{inc_y25}명", f"{inc_o25}명", f"{tax25:,.0f}원"],
    "2026년": [f"{y26}명", f"{o26}명", f"{inc_y26}명", f"{inc_o26}명", f"{tax26_new:,.0f}원"]
})
st.table(df_res)

st.warning("⚠️ 위 계산은 '인원이 유지된다'는 가정하에 산출된 당기 공제액입니다. 인원 감소 시 발생하는 '추가납부세액(추징)'은 포함되지 않았습니다.")