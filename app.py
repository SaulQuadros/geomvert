import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
import math

st.set_page_config(page_title="Concordância Vertical", layout="centered")

st.title("Perfil Longitudinal: Concordância Vertical")

# Identificação do projeto
st.sidebar.title("Identificação")
project_name = st.sidebar.text_input("Projeto", "")
user_name = st.sidebar.text_input("Nome do Usuário", "")

# Estaca do PIV para cálculo de tabela de estacas
st.sidebar.header("Estaca do PIV")
station_i = st.sidebar.number_input("Estaca inteira (número)", value=30, step=1, min_value=0)
offset_i = st.sidebar.number_input("Fração da estaca [m]", value=12.5, step=0.1, min_value=0.0)
Z_I = st.sidebar.number_input("Cota do PIV (I) [m]", value=200.00, step=0.01)

# Parâmetros da curva
st.sidebar.header("Parâmetros da Curva")
tipo = st.sidebar.selectbox("Tipo de curva", ["Convexa", "Côncava"])
i1_valor = st.sidebar.number_input("Inclinação inicial i₁ [%]", value=2.50, step=0.01, min_value=0.0)
i2_valor = st.sidebar.number_input("Inclinação final i₂ [%]", value=1.00, step=0.01, min_value=0.0)
L = st.sidebar.number_input("Comprimento da curva L [m]", value=120.0, step=1.0, min_value=1.0)

# Ajuste de sinais
if tipo == "Convexa":
    i1 = i1_valor / 100
    i2 = -i2_valor / 100
else:
    i1 = -i1_valor / 100
    i2 = i2_valor / 100

g = i1 - i2
e = (L / 8) * g

# Cotas dos pontos
Z_A = Z_I - i1 * (L/2) + e
Z_B = Z_A + ((i1 + i2)/2) * L

# Vértice da parábola
x_V = (i1 * L) / g if g != 0 else np.nan
y_V = (i1**2 * L) / (2 * g) if g != 0 else np.nan
Z_V = Z_A + y_V if g != 0 else np.nan

# PIV na parábola
Z_I_parab = Z_A + i1 * (L/2) - e

# Plot
x_vals = np.linspace(0, L, 200)
Z_parab = Z_A + (i1 * x_vals - (g/(2*L)) * x_vals**2)
x_tanA = np.linspace(-L/3, L, 100)
Z_tanA = Z_A + i1 * x_tanA
x_tanB = np.linspace(0, L+L/3, 100)
Z_tanB = Z_B + i2 * (x_tanB - L)

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(x_vals, Z_parab, 'k', lw=2, label='Parábola')
ax.plot(x_tanA, Z_tanA, '--', color='gray', label='Tangente A')
ax.plot(x_tanB, Z_tanB, '--', color='orange', label='Tangente B')
ax.scatter([0, L/2, L], [Z_A, Z_I_parab, Z_B], color='red', zorder=5)
ax.scatter([x_V], [Z_V], color='blue', marker='*', s=180, zorder=6)
ax.set_xlabel('x (m)')
ax.set_ylabel('Cota Z (m)')
ax.set_title(f'Perfil Longitudinal: Concordância Vertical ({tipo})')
ax.legend()
ax.grid(True)
st.pyplot(fig)

# Resultados
st.subheader("Resultados")
col1, col2 = st.columns(2)
with col1:
    st.write(f"**Desnível (g):** {g:.5f}")
    st.write(f"**Flecha (e):** {e:.4f} m")
    st.write(f"**Cota A (PCV):** {Z_A:.3f} m")
    st.write(f"**Cota PIV:** {Z_I_parab:.3f} m")
with col2:
    st.write(f"**Cota B (PTV):** {Z_B:.3f} m")
    st.write(f"**x Vértice:** {x_V:.3f} m")
    st.write(f"**Z Vértice:** {Z_V:.3f} m")

# Tabela de Estacas
stationI_m = station_i * 20 + offset_i
PCV_chain = stationI_m - L/2
PTV_chain = stationI_m + L/2

pcv_s = int(math.floor(PCV_chain/20))
pcv_o = PCV_chain - pcv_s*20
ptv_s = int(math.floor(PTV_chain/20))
ptv_o = PTV_chain - ptv_s*20

rows = []
# PCV
rows.append({
    "Estaca": f"{pcv_s}+{pcv_o:.2f}",
    "Posição": round(PCV_chain,3),
    "Dist. desde A (m)": 0.0,
    "Cota (m)": round(Z_A,3),
    "Tipo": "PCV"
})
# entre PCV e PIV
start_int = math.ceil(PCV_chain/20)
end_int = station_i if offset_i > 0 else station_i - 1
for s in range(start_int, end_int+1):
    ch = s*20
    dx = ch - PCV_chain
    z = Z_A + (i1*dx - (g/(2*L))*dx**2)
    rows.append({
        "Estaca": f"{s}+00",
        "Posição": ch,
        "Dist. desde A (m)": round(dx,3),
        "Cota (m)": round(z,3),
        "Tipo": ""
    })
# PIV
rows.append({
    "Estaca": f"{station_i}+{offset_i:.2f}",
    "Posição": round(stationI_m,3),
    "Dist. desde A (m)": round(L/2,3),
    "Cota (m)": round(Z_I_parab,3),
    "Tipo": "PIV"
})
# entre PIV e PTV
for s in range(station_i+1, math.floor(PTV_chain/20)+1):
    ch = s*20
    dx = ch - PCV_chain
    z = Z_A + (i1*dx - (g/(2*L))*dx**2)
    rows.append({
        "Estaca": f"{s}+00",
        "Posição": ch,
        "Dist. desde A (m)": round(dx,3),
        "Cota (m)": round(z,3),
        "Tipo": ""
    })
# PTV
rows.append({
    "Estaca": f"{ptv_s}+{ptv_o:.2f}",
    "Posição": round(PTV_chain,3),
    "Dist. desde A (m)": round(L,3),
    "Cota (m)": round(Z_B,3),
    "Tipo": "PTV"
})

df = pd.DataFrame(rows)
def style_row(r):
    if r.Tipo in ["PCV","PTV"]: return ['color:red']*len(df.columns)
    if r.Tipo=="PIV": return ['color:blue']*len(df.columns)
    return ['']*len(df.columns)
df_style = df.style.apply(style_row, axis=1)

st.subheader("Tabela de Estacas")
st.dataframe(df_style)

# PDF generation with actual table
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Identification
    pdf.cell(0, 10, f"Projeto: {project_name}", ln=True)
    pdf.cell(0, 10, f"Usuário: {user_name}", ln=True)
    pdf.ln(5)
    # Parameters
    pdf.cell(0, 8, "Parâmetros de entrada:", ln=True)
    pdf.cell(40, 8, f"Estaca do PIV: {station_i}+{offset_i:.2f}", ln=True)
    pdf.cell(0, 8, f"g = {g:.5f}, e = {e:.4f} m", ln=True)
    pdf.cell(0, 8, f"i₁ = {i1_valor:+.2f}%, i₂ = {i2_valor:+.2f}%", ln=True)
    pdf.cell(0, 8, f"L = {L} m", ln=True)
    pdf.ln(5)
    # Table header
    pdf.set_font("Arial", "B", 12)
    col_width = (pdf.w - 2*pdf.l_margin) / 4
    for header in ["Estaca", "Posição", "Dist. desde A", "Cota"]:
        pdf.cell(col_width, 10, header, border=1, align='C')
    pdf.ln()
    # Table rows
    pdf.set_font("Arial", size=12)
    for row in rows:
        pdf.cell(col_width, 8, row["Estaca"], border=1)
        pdf.cell(col_width, 8, f'{row["Posição"]}', border=1)
        pdf.cell(col_width, 8, f'{row["Dist. desde A (m)"]}', border=1)
        pdf.cell(col_width, 8, f'{row["Cota (m)"]}', border=1)
        pdf.ln()
    pdf.ln(5)
    # Graph
    buf = BytesIO()
    fig.savefig(buf, format='PNG')
    buf.seek(0)
    pdf.image(buf, x=10, w=pdf.w-20)
    output = BytesIO()
    pdf.output(output)
    output.seek(0)
    return output

pdf_bytes = create_pdf()
st.sidebar.download_button("Salvar PDF", data=pdf_bytes, file_name="perfil_concordancia.pdf", mime="application/pdf")
