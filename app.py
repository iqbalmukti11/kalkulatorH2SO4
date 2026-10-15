import streamlit as st

# Konfigurasi Halaman Web
st.set_page_config(page_title="Kalkulator Leaching MHP / MHP浸出酸量计算器", page_icon="🧪", layout="wide")

st.title("🧪 Kalkulator Kebutuhan Asam Sulfat / 硫酸需求量计算器")
st.markdown("Alat bantu perhitungan neraca reagen pelindian (MHP leaching) berdasarkan suplai anoda dan kebutuhan stoikiometri nikel.\n\n"
            "基于阳极液供应和镍化学计量需求的 MHP 浸出试剂平衡计算工具。")

# --- 1. VARIABEL TETAP (KONSTANTA PROSES MHP) / 固定参数 ---
st.sidebar.header("📌 Variabel Tetap / 固定参数")
density_slurry = st.sidebar.number_input("Densitas Slurry MHP / MHP矿浆密度 (kg/m³)", value=1300.0, step=10.0)
solid_content_pct = st.sidebar.number_input("Solid Content / 固含量 (% w/w)", value=25.0, step=1.0) / 100.0
ni_in_solid_pct = st.sidebar.number_input("Kadar Nikel (Ni) / 干基镍品位 (% w/w)", value=40.0, step=1.0) / 100.0

# Debit Slurry MHP sebagai basis perhitungan
slurry_flow_rate = st.sidebar.number_input("Debit Slurry MHP / MHP矿浆流量 (m³/jam)", value=10.0, step=0.5)

# --- 2. VARIABEL BEBAS (INPUT ANODA) / 自变量（阳极液输入） ---
st.sidebar.markdown("---")
st.sidebar.header("⚙️ Variabel Bebas / 自变量 (Anode)")
anode_flow_rate = st.sidebar.number_input("Debit Anoda / 阳极液流量 (m³/jam)", min_value=0.0, value=5.0, step=0.5)
h2so4_concentration_gpl = st.sidebar.number_input("Konsentrasi H₂SO₄ Anoda / 阳极液酸浓度 (g/L)", min_value=0.0, value=150.0, step=5.0)

# Faktor Excess (Ditetapkan 110%)
excess_pct = 110.0
excess_factor = excess_pct / 100.0

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

# E. Defisit / Kekurangan Asam
kmol_h2so4_deficit = kmol_h2so4_actual_required - kmol_h2so4_anode_supplied
if kmol_h2so4_deficit < 0:
    kmol_h2so4_deficit = 0.0

mass_h2so4_deficit_kg = kmol_h2so4_deficit * MR_H2SO4 # kg/jam H2SO4 murni yang kurang

# --- 4. KESIMPULAN & TAMPILAN UTAMA / 结论与输出 ---
st.markdown("---")
st.subheader("📊 Kesimpulan Neraca & Debit / 结论与流量汇总")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="1️⃣ Debit Slurry MHP / MHP 矿浆流量", 
        value=f"{slurry_flow_rate:,.2f} m³/jam"
    )
    st.caption(f"Laju Ni / 镍质量流量: {mass_flow_ni_kg_h:,.2f} kg/h ({kmol_ni_per_hour:,.2f} kmol/h)")

with col2:
    st.metric(
        label="2️⃣ Debit Larutan Anoda / 阳极液流量", 
        value=f"{anode_flow_rate:,.2f} m³/jam"
    )
    st.caption(f"Suplai H₂SO₄ / 硫酸供应量: {kmol_h2so4_anode_supplied:,.2f} kmol/h")

with col3:
    st.metric(
        label="3️⃣ Kebutuhan H₂SO₄ Tambahan / 补充浓硫酸需求量", 
        value=f"{mass_h2so4_deficit_kg:,.2f} kg/jam"
    )
    if kmol_h2so4_deficit == 0:
        st.success("Suplai anoda sudah mencukupi excess 110%! / 阳极液酸量已满足110%过量需求！")
    else:
        st.warning(f"Kekurangan H₂SO₄ / 需额外补充硫酸: {kmol_h2so4_deficit:,.2f} kmol/h")

# Detail Perincian Mol
with st.expander("🔍 Detail Parameter Perhitungan / 详细计算参数"):
    st.write(f"- **Kmol Ni MHP / 镍物质的量:** `{kmol_ni_per_hour:,.4f} kmol/jam`")
    st.write(f"- **Kebutuhan Stoikiometri H₂SO₄ / 理论酸耗:** `{kmol_h2so4_stoich_per_hour:,.4f} kmol/jam`")
    st.write(f"- **Kebutuhan Excess 110% H₂SO₄ / 110%过量酸需求:** `{kmol_h2so4_actual_required:,.4f} kmol/jam`")
    st.write(f"- **Suplai H₂SO₄ Anoda / 阳极液供酸量:** `{kmol_h2so4_anode_supplied:,.4f} kmol/jam`")
    st.write(f"- **Defisit H₂SO₄ / 酸缺口:** `{kmol_h2so4_deficit:,.4f} kmol/jam` ({mass_h2so4_deficit_kg:,.2f} kg H₂SO₄/jam)")
