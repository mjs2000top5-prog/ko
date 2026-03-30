import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="통합고용세액공제 계산기", layout="wide")

st.title("💰 통합고용세액공제 통합 계산기")
st.info("일반기업(대기업) 청년 공제 단가를 400만원으로 수정 반영하였습니다.")

# 2. 사이드바: 조건 설정
with st.sidebar:
    st.header("⚙️ 시뮬레이션 조건")
    
    # 기준연도
    base_year = st.number_input("1차 세액공제 기준연도", min_value=2022, max_value=2030, value=2025)
    
    st.divider()
    
    # 공제 종류
    tax_type = st.radio("세액공제 종류", ["통합고용세액공제", "고용증대세액공제(기존)"])
    
    # 기업 유형
    biz_type = st.selectbox("기업 유형", ["중소기업", "중견기업", "일반기업(대기업)"])
    
    # 소재지
    location = st.radio("사업장 소재지", ["수도권", "비수도권"])

# 3. [단가 수정] 기업유형별 공제 단가 로직
def get_unit_prices(tax_type, biz_type, location):
    y_unit, o_unit = 0, 0
    
    if tax_type == "통합고용세액공제":
        if biz_type == "중소기업":
            y_unit = 14500000 if location == "수도권" else 15500000
            o_unit = 8500000 if location == "수도권" else 9500000
        elif biz_type == "중견기업":
            y_unit = 8000000 if location == "수도권" else 9000000
            o_unit = 4500000 if location == "수도권" else 5000000
        elif biz_type == "일반기업(대기업)":
            # [수정 반영] 일반기업 청년 등 공제 단가: 400만원
            y_unit = 4000000 
            o_unit = 0
    else:
        # 고용증대세액공제(기존) 기준
        if biz_type == "중소기업":
            y_unit = 11000000 if location == "수도권" else 12000000
            o_unit = 7000000 if location == "수도권" else 7700000
        elif biz_type == "중견기업":
            y_unit = 7000000 if location == "수도권" else 8000000
            o_unit = 4500000 if location == "수도권" else 4500000
        elif biz_type == "일반기업(대기업)":
            # 기존 고용증대에서도 일반기업은 통상 400만원(또는 제도에 따라 상이)이나 요청하신대로 400만원으로 통일
            y_unit = 4000000
            o_unit = 0
            
    return y_unit, o_unit

unit_y, unit_o = get_unit_prices(tax_type, biz_type, location)

# 공제 유지 기간 설정 (중소/중견 3년, 일반 2년)
maint_years = 2 if "일반" in biz_type else 3

# 4. 인원 입력 구간
prev_year = base_year - 1
year_1 = base_year
year_2 = base_year + 1
year_3 = base_year + 2

st.subheader(f"👥 연도별 상시근로자 수 입력 (유지기간: {maint_years}년)")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"**{prev_year}년 (직전)**")
    y_p = st.number_input(f"{prev_year} 청년", min_value=0.0, value=10.0, key="yp")
    o_p = st.number_input(f"{prev_year} 일반", min_value=0.0, value=10.0, key="op")

with col2:
    st.markdown(f"**{year_1}년 (1차)**")
    y_1 = st.number_input(f"{year_1} 청년", min_value=0.0, value=12.0, key="y1")
    o_1 = st.number_input(f"{year_1} 일반", min_value=0.0, value=11.0, key="o1")

with col3:
    st.markdown(f"**{year_2}년 (2차)**")
    y_2 = st.number_input(f"{year_2} 청년", min_value=0.0, value=12.0, key="y2")
    o_2 = st.number_input(f"{year_2} 일반", min_value=0.0, value=11.0, key="o2")

with col4:
    st.markdown(f"**{year_3}년 (3차)**")
    # 일반기업은 3차년도 공제가 없으므로 입력 비활성화
    disabled = True if maint_years < 3 else False
    y_3 = st.number_input(f"{year_3} 청년", min_value=0.0, value=12.0, key="y3", disabled=disabled)
    o_3 = st.number_input(f"{year_3} 일반", min_value=0.0, value=11.0, key="o3", disabled=disabled)

# 5. 계산 로직
# 1차년도 공제액
inc_y_1 = max(0, y_1 - y_p)
inc_o_1 = max(0, o_1 - o_p)
credit_1 = (inc_y_1 * unit_y) + (inc_o_1 * unit_o)

# 2차년도 공제액 (1차 유지분 + 2차 신규증가분)
inc_y_2 = max(0, y_2 - y_1)
inc_o_2 = max(0, o_2 - o_1)
credit_2 = credit_1 + (inc_y_2 * unit_y) + (inc_o_2 * unit_o)

# 3차년도 공제액 (일반기업은 0, 중소/중견은 누적)
if maint_years >= 3:
    inc_y_3 = max(0, y_3 - y_2)
    inc_o_3 = max(0, o_3 - o_2)
    credit_3 = credit_2 + (inc_y_3 * unit_y) + (inc_o_3 * unit_o)
else:
    credit_3 = 0

# 6. 결과 출력
st.divider()
st.subheader(f"📊 {biz_type} 세액공제 결과 분석")

m1, m2, m3 = st.columns(3)
m1.metric(f"{year_1}년 공제액", f"{credit_1:,.0f} 원")
m2.metric(f"{year_2}년 공제액", f"{credit_2:,.0f} 원")

if maint_years >= 3:
    m3.metric(f"{year_3}년 공제액", f"{credit_3:,.0f} 원")
else:
    m3.metric(f"{year_3}년 공제액", "공제 종료", help="일반기업(대기업)은 고용증가 인원에 대해 2년간만 공제됩니다.")

# 상세 데이터 테이블
results_data = {
    "연도": [f"{year_1}년", f"{year_2}년", f"{year_3}년"],
    "신규증가(청년)": [inc_y_1, inc_y_2, inc_y_3 if maint_years >= 3 else 0],
    "신규증가(일반)": [inc_o_1, inc_o_2, inc_o_3 if maint_years >= 3 else 0],
    "총 공제액 합계": [f"{credit_1:,.0f}원", f"{credit_2:,.0f}원", f"{credit_3:,.0f}원" if maint_years >= 3 else "-"]
}
st.table(pd.DataFrame(results_data))

# 하단 안내 문구
st.info(f"💡 **현재 적용 단가:** {biz_type} / {location} 기준 1인당 [청년 등: {unit_y/10000:,.0f}만원], [기타: {unit_o/10000:,.0f}만원]")
if biz_type == "일반기업(대기업)":
    st.warning("⚠️ **참고:** 일반기업은 '청년, 장애인, 60세 이상' 등의 증가에 대해서만 400만원 공제가 적용되며, 일반 근로자 증가분 및 3년차 공제는 적용되지 않습니다.")