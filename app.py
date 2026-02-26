import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd

# 컴파일된 바이너리 임포트
try:
    import core_engine
except ImportError:
    st.error("보안 모듈(core_engine.so)을 찾을 수 없거나 아키텍처가 일치하지 않습니다.")
    st.stop()

# [WEB UI] Page Configuration
st.set_page_config(page_title="Battery Design Simulator", layout="wide")

# [CSS] 정교한 스타일 설정: 헤더는 숨기되 사이드바 토글 버튼은 유지
st.markdown(
    """
    <style>
    /* 1. 메인 컨테이너 여백 조정 */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    
    /* 2. 사이드바 내부 여백 조정 */
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0rem !important;
    }
    [data-testid="stSidebarUserContent"] {
        padding-top: 0rem !important;
        margin-top: -2rem !important;
    }

    /* 3. 헤더 전체를 숨기지 않고 내부 요소만 선택적으로 숨김 */
    /* 헤더 영역의 배경을 투명하게 하고 높이를 조절 */
    header[data-testid="stHeader"] {
        background-color: rgba(0,0,0,0);
        color: rgba(0,0,0,0);
    }
    
    /* 메뉴 버튼과 배포 버튼만 숨김 */
    header[data-testid="stHeader"] [data-testid="stToolbar"],
    header[data-testid="stHeader"] #MainMenu {
        visibility: hidden;
    }

    /* 사이드바가 닫혔을 때 나타나는 열기 버튼(화살표)은 다시 보이게 설정 */
    header[data-testid="stHeader"] button {
        visibility: visible !important;
        color: gray !important; /* 버튼 색상 지정 */
    }

    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# [WEB UI] Main Title
st.title("🔋 Battery Cell Design Engine")
st.markdown("Simulation of required nominal voltage vs. specific capacity.")
st.divider()

# [WEB UI] Sidebar Inputs
with st.sidebar:
    st.header("⚙️ Design Parameters")
    with st.form("input_form"):
        st.subheader("1. Cell Specifications")
        target_ed = st.number_input("Target Energy Density (Wh/kg)", value=120.0, step=10.0)
        cell_cap = st.number_input("Target Cell Capacity (Ah)", value=5.0, step=0.5)
        stacks = st.number_input("Number of Stacks", value=3, step=1)
        
        st.subheader("2. Electrode Design")
        np_ratio = st.number_input("N/P Ratio", value=1.5, step=0.1)
        cat_am_ratio = st.number_input("Cathode Active Ratio", value=0.8, step=0.05)
        # 2D Phosphorus 기반 고용량 음극 고려 가능
        ano_cap = st.number_input("Anode Capacity (mAh/g)", value=1166.0, step=50.0)
        
        st.subheader("3. Inactive Components")
        inactive_mass = st.number_input("Base Inactive Mass (g)", value=6.0, step=1.0)
        submitted = st.form_submit_button("Run Simulation 🚀")

if submitted:
    st.session_state.inputs = {
        "target_ed": target_ed,
        "cell_cap": cell_cap,
        "stacks": stacks,
        "np_ratio": np_ratio,
        "cat_am_ratio": cat_am_ratio,
        "ano_cap": ano_cap,
        "inactive_mass": inactive_mass,
        "areas": [(60, 5), (90, 5), (120, 5), (140, 5), (160, 5)],
    }
    st.session_state.sim_run = True

if st.session_state.get("sim_run"):
    inputs = st.session_state.inputs
    x_min, x_max = 100, 550
    cat_capacities = np.linspace(x_min, x_max, 200)
    data_dict = {"Cathode_Capacity_mAh_g": cat_capacities}
    
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#2ca02c", "#d62728", "#1f77b4", "#7f7f7f", "#ff7f0e"]
    all_voltages = []
    
    for i, (w, h) in enumerate(inputs["areas"]):
        area_cm2 = w * h
        voltages = [
            core_engine.calculate_required_voltage(c, area_cm2, inputs) for c in cat_capacities
        ]
        all_voltages.extend(voltages)
        data_dict[f"{int(w)}x{int(h)}_cm2"] = voltages
        ax.plot(
            cat_capacities,
            voltages,
            label=f"{int(w)} x {int(h)} cm$^2$",
            color=colors[i % len(colors)],
            linewidth=2,
        )

    col_title, col_download = st.columns([4, 1])
    with col_title:
        st.subheader("Simulation Results")
    with col_download:
        df = pd.DataFrame(data_dict)
        st.download_button(
            "Download CSV ⬇️",
            df.to_csv(index=False).encode("utf-8"),
            f'battery_sim_{int(inputs["target_ed"])}Whkg.csv',
            "text/csv",
        )

    ax.set_title(
        f"Target: {int(inputs['target_ed'])} Wh/kg | {inputs['cell_cap']}Ah - N/P: {inputs['np_ratio']}",
        loc="left",
        fontweight="bold",
        pad=20,
        fontsize=14,
    )
    ax.set_xlabel("Cathode Capacity (mAh/g)", fontsize=12)
    ax.set_ylabel("Required Nominal Voltage (V)", fontsize=12)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(0.5, max(all_voltages) * 1.1)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(frameon=False, loc="upper right", fontsize=10)
    st.pyplot(fig)

st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray; font-size: 13px;'>Developed by <a href='https://scholar.google.com/citations?user=McI_PLgAAAAJ&hl=en&oi=ao' style='color: gray; text-decoration: underline;'>Sangha Baek</a> / Original concept by <a href='https://scholar.google.com/citations?user=jKkQQBoAAAAJ&hl=en&oi=ao' style='color: gray; text-decoration: underline;'>Dr. Gun Jang</a></p>",
    unsafe_allow_html=True,
)
