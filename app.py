import streamlit as st

# Konfigurasi Halaman Web
st.set_page_config(page_title="Kalkulator Leaching MHP / MHP浸出酸量计算器", page_icon="🧪", layout="wide")

st.title("🧪 Kalkulator Kebutuhan Asam Sulfat / 硫酸需求量计算器")
st.markdown("Alat bantu perhitungan neraca reagen pelindian (MHP leaching) berdasarkan suplai anoda dan kebutuhan stoikiometri nikel.\n\n"
            "基于阳极液供应和镍化学计量需求的 MHP 浸出试剂平衡计算工具。")

# --- 1. VARIABEL TETAP (KONSTANTA PROSES) / 固定参数 ---
st.sidebar.header("📌 Variabel Tetap / 固定参数")
density_slurry = st.sidebar.number_input("Densitas Slurry MHP / MHP矿浆密度 (kg/m³)", value=1300.0, step=10.0)
solid_content_pct = st.sidebar.number_input("Solid Content / 固含量 (% w/w)", value=25.0, step=1.0) / 100.0
ni_in_solid_pct = st.sidebar.number_input("Kadar Nikel (Ni) / 干基镍品位 (% w/w)", value=40.0, step=1.0) / 100.0

# Konsentrasi asam sulfat di anoda dipindah ke Variabel Tetap
h2so4_concentration_gpl = st.sidebar.number_input("Konsentrasi H₂SO₄ Anoda / 阳极液酸浓度 (g/L)", min_value=0.0, value=55.0, step=5.0)

# --- 2. VARIABEL BEBAS (INPUT OPERASIONAL) / 自变量（操作输入） ---
st.sidebar.markdown("---")
st.sidebar.header("⚙️ Variabel Bebas / 自变量 (Operation)")
slurry_flow_rate = st.sidebar.number_input("Debit Slurry MHP / MHP矿浆流量 (m³/jam)", value=10.0, step=0.5)
anode_flow_rate = st.sidebar.number_input("Debit Anoda / 阳极液流量 (m³/jam)", min_value=0.0, value=5.0, step=0.5)

# Faktor Excess (Ditetapkan 110%)
excess_pct = 110.0
excess_factor = excess_pct / 100.0

# Molaritas H2SO4 98% (18.4 kmol/m3)
MOLARITY_H2SO4_98 = 18.4 

# --- 3. PERHITUNGAN (ENGINE) / 计算逻辑 ---
AR_NI = 58.69   # Berat atom Ni (g/mol)
MR_H2SO4 = 98.08 # Berat molekul H2SO4 (g/mol)

# A. Mass Flow Slurry & Nickel
mass_flow_slurry_kg_h = slurry_flow_rate * density_slurry        # kg/jam slurry
mass_flow_solid_kg_h = mass_flow_slurry_kg_h * solid_content_pct # kg/jam padatan
mass_flow_ni_kg_h = mass_flow_solid_kg_h * ni_in_solid_pct       # kg/jam nikel murni

# Konversi kg/jam Ni ke kmol/jam Ni
kmol_ni_per_hour = mass_flow_ni_kg_h / AR_NI

# B. Kebutuhan Asam Stoikiometri (1 mol Ni : 1 mol H2SO4)
kmol_h2so4_stoich_per_hour = kmol_ni_per_hour 

# C. Kebutuhan Aktual dengan Excess 110%
kmol_h2so4_actual_required = kmol_h2so4_stoich_per_hour * excess_factor

# D. Suplai Asam dari Anoda
mass_h2so4_anode_kg_h = anode_flow_rate * h2so4_concentration_gpl # kg/jam H2SO4 dari anoda
kmol_h2so4_anode_supplied = mass_h2so4_anode_kg_h / MR_H2SO4       # kmol/jam H2SO4 dari anoda

# E. Defisit / Kekurangan Asam (dalam kmol/jam)
kmol_h2so4_deficit = kmol_h2so4_actual_required - kmol_h2so4_anode_supplied
if kmol_h2so4_deficit < 0:
    kmol_h2so4_deficit = 0.0

# Konversi defisit kmol ke Debit Volume H2SO4 98% (m3/jam)
volume_h2so4_deficit_m3_h = kmol_h2so4_deficit / MOLARITY_H2SO4_98
volume_h2so4_deficit_l_h = volume_h2so4_deficit_m3_h * 1000.0 # Konversi ke Liter/jam

# --- 4. KESIMPULAN & TAMPILAN UTAMA / 结论与输出 ---
st.markdown("---")
st.subheader("📊 Kesimpulan Neraca & Debit / 结论与流量汇总")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="1️⃣ Slurry MHP / MHP 矿浆", 
        value=f"{slurry_flow_rate:,.2f} m³/jam"
    )
    st.caption(f"Laju Ni / 镍质量流量: {mass_flow_ni_kg_h:,.2f} kg/h ({kmol_ni_per_hour:,.2f} kmol/h)")

with col2:
    st.metric(
        label="2️⃣ Larutan Anoda / 阳极液", 
        value=f"{anode_flow_rate:,.2f} m³/jam"
    )
    st.caption(f"Suplai H₂SO₄ / 硫酸供应量: {kmol_h2so4_anode_supplied:,.2f} kmol/h (Konsentrasi: {h2so4_concentration_gpl} g/L)")

with col3:
    st.metric(
        label="3️⃣ H₂SO₄ 98% Tambahan / 补充98%硫酸", 
        value=f"{volume_h2so4_deficit_m3_h:,.3f} m³/jam"
    )
    if kmol_h2so4_deficit == 0:
        st.success("Suplai anoda sudah mencukupi excess 110%! / 阳极液酸量已满足110%过量需求！")
    else:
        st.warning(f"Setara dengan: {volume_h2so4_deficit_l_h:,.2f} Liter/jam")

# Detail Perincian Mol
with st.expander("🔍 Detail Parameter Perhitungan / 详细计算参数"):
    st.write(f"- **Kmol Ni MHP / 镍物质的量:** `{kmol_ni_per_hour:,.4f} kmol/jam`")
    st.write(f"- **Kebutuhan Stoikiometri H₂SO₄ / 理论酸耗:** `{kmol_h2so4_stoich_per_hour:,.4f} kmol/jam`")
    st.write(f"- **Kebutuhan Excess 110% H₂SO₄ / 110%过量酸需求:** `{kmol_h2so4_actual_required:,.4f} kmol/jam`")
    st.write(f"- **Suplai H₂SO₄ Anoda / 阳极液供酸量:** `{kmol_h2so4_anode_supplied:,.4f} kmol/jam`")
    st.write(f"- **Defisit H₂SO₄ (Kmol) / 酸缺口 (物质的量):** `{kmol_h2so4_deficit:,.4f} kmol/jam`")
    st.write(f"- **Molaritas H₂SO₄ 98% / 98%硫酸摩尔浓度:** `{MOLARITY_H2SO4_98} kmol/m³`")
