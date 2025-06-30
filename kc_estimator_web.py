import streamlit as st
import pandas as pd

# 시험 항목 단가표
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
    "나무 방부제": {"base": 220000, "add": 110000},
}

# 제품별 자동 적용 항목
PRESET_PRODUCTS = {
    "치발기": ["기계적·물리적 특성(기본)", "유해원소용출시험(19종)", "총납 + 총카드뮴", "모노머", "솔벤트용출", "프탈레이트 가소제시험(7종)"],
    "전동차": ["기계적·물리적 특성(기본)", "유해원소용출시험(19종)", "총납 + 총카드뮴", "프탈레이트 가소제시험(7종)", "2차전지"],
    "고무공": ["기계적·물리적 특성(기본)", "유해원소용출시험(19종)", "총납 + 총카드뮴", "니트로사민"],
    "젤 완구": ["기계적·물리적 특성(기본)", "유해원소용출시험(19종)", "총납 + 총카드뮴", "방부제"],
    "섬유인형": ["기계적·물리적 특성(기본)", "유해원소용출시험(19종)", "총납 + 총카드뮴", "착색제", "1차방향성아민", "pH"],
    "입/코 덮는 마스크 - 플라스틱": ["모노머", "솔벤트용출"],
    "입/코 덮는 마스크 - 섬유": ["착색제", "1차방향성아민", "솔벤트용출"],
    "입/코 덮는 마스크 - 종이": ["착색제", "1차방향성아민"]
}

# 인터페이스
st.title("완구 시험수수료 셀프 계산기")
preset = st.selectbox("제품 유형 (표 9-1 기준)", ["선택 안 함"] + list(PRESET_PRODUCTS.keys()))
age = st.selectbox("제품 사용 연령", ["36개월 미만", "36~72개월", "72개월 이상"])
purpose = st.selectbox("입에 넣는 용도 여부", ["예", "아니오"])
rubber_use = st.selectbox("탄성고무 사용 여부", ["예", "아니오"])
is_wood_special = st.checkbox("3세 미만 + 나무 완구 (실내용/입작동/150g 이하)")

num_materials = st.number_input("재질 종류 수", min_value=1, step=1)
color_counts = [min(st.number_input(f"재질 {i+1} 색상 수 (최대 5)", min_value=1, max_value=10, step=1), 5) for i in range(num_materials)]

st.write("### 자동 적용 시험 항목")
selected_tests = []

if preset != "선택 안 함":
    selected_tests.extend(PRESET_PRODUCTS[preset])

# 조건 기반 자동 적용
if purpose == "예":
    selected_tests += ["모노머", "솔벤트용출", "포스페이트계가소제", "유기주석화합물"]
if rubber_use == "예":
    selected_tests.append("니트로사민")
if age == "36개월 미만":
    selected_tests.append("방부제")
if is_wood_special and age == "36개월 미만":
    selected_tests.append("나무 방부제")

selected_tests += ["착색제", "1차방향성아민", "pH"]

# 수동 항목 추가 체크
st.write("### 수동으로 추가할 시험 항목")
manual_options = [
    ("PVC 재질 포함 및 입에 넣는 용도", "포스페이트계가소제"),
    ("섬유류 완구", "착색제"),
    ("염색 섬유류 완구", "1차방향성아민"),
    ("젤/폼 형태 완구", "방부제"),
    ("염색 섬유류 완구", "pH")
]
for label, key in manual_options:
    if st.checkbox(f"{label} → {key}"):
        selected_tests.append(key)

# 계산 함수

def calculate_pricing(colors, tests):
    result = []
    total_colors = sum(colors)
    num_materials = len(colors)

    def add(key, repeat=0):
        if key not in PRICING: return
        base = PRICING[key].get("base", 0)
        add = PRICING[key].get("add", 0)
        price = base + add * (repeat - 1) if repeat > 1 else base
        result.append((key, price))

    add("유해원소용출시험(19종)", repeat=total_colors)
    add("총납 + 총카드뮴", repeat=total_colors)
    add("프탈레이트 가소제시험(7종)", repeat=num_materials)
    add("기계적·물리적 특성(기본)")
    add("인증서 발급비")

    for key in set(tests):
        if key in ["착색제", "1차방향성아민", "방부제", "pH", "나무 방부제"]:
            add(key, repeat=num_materials)
        else:
            add(key)
    return result

# 결과 출력
if st.button("견적 계산하기"):
    estimate = calculate_pricing(color_counts, selected_tests)
    df = pd.DataFrame(estimate, columns=["시험 항목", "예상 비용 (원)"])
    df["예상 비용 (원)"] = df["예상 비용 (원)"].apply(lambda x: f"{x:,.0f}원")
    st.write("### 예상 견적 결과")
    st.table(df)
    total = sum([e[1] for e in estimate])
    st.success(f"총 예상 견적: {total:,.0f}원")
