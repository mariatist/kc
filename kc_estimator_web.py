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
rubber_use = st.selectbox("탄성고무 사용 여부", ["예", "아니오"])
battery_use = st.selectbox("2차전지 포함 여부", ["예", "아니오"])
material_input = st.text_input("재질 입력 (쉼표로 구분, 예: PVC, 섬유, 젤)")
material_types = [m.strip() for m in material_input.split(",") if m.strip()]

num_materials = st.number_input("재질 종류 수 (예: 플라스틱, 섬유 등)", min_value=1, step=1)
color_counts = []
st.write("### 재질별 색상 수 입력")
for i in range(num_materials):
    count = st.number_input(f"재질 {i+1}번 색상 수 (최대 5색까지 적용)", min_value=1, max_value=10, step=1)
    color_counts.append(min(count, 5))

# 제품 특성 체크박스 (고시 기준 반영)
st.write("### 제품 특성 체크 (표 9-1 기준)")
product_features = {
    "입에 넣을 수 있는 제품": ["모노머", "솔벤트용출"],
    "PVC 재질 포함 및 입에 넣는 용도": ["포스페이트계가소제", "유기주석화합물"] if "PVC" in material_types and purpose == "예" else [],
    "탄성고무 포함": ["니트로사민"] if rubber_use == "예" else [],
    "2차전지 포함": ["2차전지"] if battery_use == "예" else [],
    "섬유류 또는 염색부직포": ["착색제", "1차방향성아민", "pH"] if any(x in material_types for x in ["섬유", "부직포"]) else [],
    "젤 또는 폼 재질": ["방부제"] if any(x in material_types for x in ["젤", "폼"]) else [],
}
selected_tests = []

for label, tests in product_features.items():
    if tests:
        st.markdown(f"- **{label}**: {', '.join(tests)}")
        selected_tests.extend(tests)

# 선택적 항목 체크
st.write("### 추가로 시험 포함을 원하는 항목 수동 체크")
optional_keys = [
    "포스페이트계가소제", "유기주석화합물", "2차전지",
    "착색제", "1차방향성아민", "방부제", "pH"
]
for key in optional_keys:
    if st.checkbox(f"{key} 시험 포함"):
        selected_tests.append(key)

# 시험 항목 수량 계산
def calculate_pricing(color_counts, selected_tests):
    results = []
    total_colors = sum(color_counts)
    num_reagents = len(color_counts)

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
    apply_tiered_pricing("프탈레이트 가소제시험(7종)", repeat_unit=num_reagents)
    apply_tiered_pricing("기계적·물리적 특성(기본)")
    apply_tiered_pricing("인증서 발급비")

    # 선택 및 조건 포함 항목 적용
    for key in set(selected_tests):
        if key in ["착색제", "1차방향성아민", "방부제", "pH"]:
            apply_tiered_pricing(key, repeat_unit=num_reagents)
        elif key in PRICING:
            results.append((key, PRICING[key]["base"]))

    return results

if st.button("견적 계산하기"):
    estimate = calculate_pricing(color_counts, selected_tests)
    df = pd.DataFrame(estimate, columns=["시험 항목", "예상 비용 (원)"])
    df["예상 비용 (원)"] = df["예상 비용 (원)"].apply(lambda x: f"{x:,.0f}원")
    st.write("### 예상 견적 결과")
    st.table(df)
    total_cost = sum([int(e[1].replace("원", "").replace(",", "")) for e in df.values])
    st.success(f"총 예상 견적: {total_cost:,.0f}원")
