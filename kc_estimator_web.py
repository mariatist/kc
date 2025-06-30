import streamlit as st
import pandas as pd

# 시험 항목 단가표 전체 반영
PRICING = {
    "인증서 발급비": {"base": 50000},
    "기계적·물리적 특성(기본)": {"base": 100000},
    "유해원소용출시험(19종)": {"base": 220000, "add": 30000},
    "총납 + 총카드뮴": {"base": 35000, "add": 10600},
    "프탈레이트 가소제시험(7종)": {"base": 125000, "add": 37500},
    "모노머": {"base": 170000},
    "솔벤트용출": {"base": 280000},
    "포스페이트계가소제": {"base": 140000},
    "착색제": {"base": 80000, "add": 40000},
    "1차방향성아민": {"base": 50000, "add": 25000},
    "방부제": {"base": 220000, "add": 110000},
    "pH": {"base": 5000, "add": 1500},
    "유기주석화합물": {"base": 200000},
    "니트로사민": {"base": 220000},
    "2차전지": {"base": 1400000},
}

st.title("KC인증 셀프 견적 계산기 (전체 항목 포함)")

# 사용자 입력
age = st.selectbox("제품 사용 연령", ["36개월 미만", "36~72개월", "72개월 이상"])
purpose = st.selectbox("입에 넣는 용도 여부", ["예", "아니오"])
num_materials = st.number_input("재질 종류 수 (예: 플라스틱, 섬유 등)", min_value=1, step=1)
color_counts = []
st.write("### 재질별 색상 수 입력")
for i in range(num_materials):
    count = st.number_input(f"재질 {i+1}번 색상 수 (최대 5색까지 적용)", min_value=1, max_value=10, step=1)
    color_counts.append(min(count, 5))

# 시험 항목 수량 계산
def calculate_pricing(color_counts):
    results = []
    total_colors = sum(color_counts)
    num_reagents = num_materials

    def apply_tiered_pricing(key, base_unit=1, repeat_unit=0):
        pricing = PRICING.get(key)
        if not pricing: return
        base = pricing.get("base", 0)
        add = pricing.get("add", 0)
        if repeat_unit > 0:
            total = base + add * (repeat_unit - 1)
        else:
            total = base * base_unit
        results.append((key, total))

    # 반복 및 고정 항목 적용
    apply_tiered_pricing("유해원소용출시험(19종)", repeat_unit=total_colors)
    apply_tiered_pricing("총납 + 총카드뮴", repeat_unit=total_colors)
    apply_tiered_pricing("프탈레이트 가소제시험(7종)", repeat_unit=num_materials)
    apply_tiered_pricing("기계적·물리적 특성(기본)")
    apply_tiered_pricing("인증서 발급비")

    # 단순 고정 항목들 추가
    for key in [
        "모노머", "솔벤트용출", "포스페이트계가소제", 
        "유기주석화합물", "니트로사민", "2차전지"]:
        if key in PRICING:
            results.append((key, PRICING[key]["base"]))

    # 추가가 존재하는 기타 항목들
    apply_tiered_pricing("착색제", repeat_unit=num_materials)
    apply_tiered_pricing("1차방향성아민", repeat_unit=num_materials)
    apply_tiered_pricing("방부제", repeat_unit=num_materials)
    apply_tiered_pricing("pH", repeat_unit=num_materials)

    return results

if st.button("견적 계산하기"):
    estimate = calculate_pricing(color_counts)
    df = pd.DataFrame(estimate, columns=["시험 항목", "예상 비용 (원)"])
    df["예상 비용 (원)"] = df["예상 비용 (원)"].apply(lambda x: f"{x:,.0f}원")
    st.write("### 예상 견적 결과")
    st.table(df)
    total_cost = sum([e[1] for e in estimate])
    st.success(f"총 예상 견적: {total_cos_cost:,.0f}원")
