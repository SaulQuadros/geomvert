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

# Estaca do PIV
st.sidebar.header("Estaca do PIV")
station_i = st.sidebar.number_input("Estaca inteira", value=30, step=1, min_value=0)
offset_i  = st.sidebar.number_input("Fração da estaca [m]", value=12.5, step=0.1, min_value=0.0)

# Parâmetros da curva
st.sidebar.header("Parâmetros da Curva")
tipo = st.sidebar.selectbox("Tipo de curva", ["Convexa", "Côncava"])
Z_I = st.sidebar.number_input("Cota do PIV (I) [m]", value=200.00, step=0.01)
i1_valor = st.sidebar.number_input("Inclinação inicial i1 [%]", value=2.50, step=0.01, min_value=0.0)
i2_valor = st.sidebar.number_input("Inclinação final i2 [%]", value=1.00, step=0.01, min_value=0.0)
L = st.sidebar.number_input("Comprimento L [m]", value=120.0, step=1.0, min_value=1.0)

# Cálculos
if tipo == "Convexa":
    i1 =  i1_valor/100; i2 = -i2_valor/100
else:
    i1 = -i1_valor/100; i2 =  i2_valor/100
g = i1 - i2; e = (L/8)*g
Z_A = Z_I - i1*(L/2) + e
Z_B = Z_A + ((i1+i2)/2)*L
x_V = (i1*L)/g if g else np.nan
y_V = (i1**2 * L)/(2*g) if g else np.nan
Z_V = Z_A + y_V
Z_I_parab = Z_A + i1*(L/2) - e

# Gráfico
x = np.linspace(0, L, 200)
Zp = Z_A + (i1*x - (g/(2*L))*x**2)
fig, ax = plt.subplots(figsize=(9,5))
ax.plot(x, Zp, 'k', lw=2, label='Parábola de Concordância')
ax.plot(np.linspace(-L/3, L,100), Z_A + i1*np.linspace(-L/3,L,100), '--', color='gray', label='Tangente em A (PCV)')
ax.plot(np.linspace(0, L+L/3,100), Z_B + i2*(np.linspace(0,L+L/3,100)-L), '--', color='orange', label='Tangente em B (PTV)')
ax.scatter([0,L,L/2], [Z_A,Z_B,Z_I_parab], color='red', label='Pontos A, B, I')
ax.scatter([x_V],[Z_V], color='blue', marker='*', s=180, label='Vértice V')
ax.set_xlabel('x (m)'); ax.set_ylabel('Cota Z (m)')
ax.set_title(f'Perfil Longitudinal ({tipo})'); ax.grid(True)
ax.legend()
st.pyplot(fig)

# Resultados
st.subheader("Resultados")
col1, col2 = st.columns(2)
with col1:
    st.write(f"- Desnível (g): {g:.5f}")
    st.write(f"- Flecha (e): {e:.4f} m")
    st.write(f"- Cota A: {Z_A:.3f} m")
    st.write(f"- Cota PIV: {Z_I_parab:.3f} m")
with col2:
    st.write(f"- Cota B: {Z_B:.3f} m")
    st.write(f"- Vértice x: {x_V:.3f} m")
    st.write(f"- Vértice Z: {Z_V:.3f} m")

# Tabela de Estacas
stationI_m = station_i*20 + offset_i
PCV_chain = stationI_m - L/2; PTV_chain = stationI_m + L/2
pcv_s, pcv_o = divmod(PCV_chain, 20)
ptv_s, ptv_o = divmod(PTV_chain, 20)

rows = []
rows.append({"Estaca":f"{int(pcv_s)}+{pcv_o:.2f}","Posição":round(PCV_chain,3),"Dist_A":0.0,"Cota":round(Z_A,3),"Tipo":"PCV"})
start_i = math.ceil(PCV_chain/20); end_i = station_i if offset_i>0 else station_i-1
for s in range(start_i,end_i+1):
    ch = s*20; dx = ch-PCV_chain
    z = Z_A + (i1*dx - (g/(2*L))*dx**2)
    rows.append({"Estaca":f"{s}+00","Posição":ch,"Dist_A":round(dx,3),"Cota":round(z,3),"Tipo":""})
rows.append({"Estaca":f"{station_i}+{offset_i:.2f}","Posição":round(stationI_m,3),"Dist_A":round(L/2,3),"Cota":round(Z_I_parab,3),"Tipo":"PIV"})
for s in range(station_i+1, math.floor(PTV_chain/20)+1):
    ch = s*20; dx = ch-PCV_chain
    z = Z_A + (i1*dx - (g/(2*L))*dx**2)
    rows.append({"Estaca":f"{s}+00","Posição":ch,"Dist_A":round(dx,3),"Cota":round(z,3),"Tipo":""})
rows.append({"Estaca":f"{int(ptv_s)}+{ptv_o:.2f}","Posição":round(PTV_chain,3),"Dist_A":round(L,3),"Cota":round(Z_B,3),"Tipo":"PTV"})

df = pd.DataFrame(rows)
def style_row(r):
    if r.Tipo in ["PCV","PTV"]: return ['color:red']*5
    if r.Tipo=="PIV": return ['color:blue']*5
    return ['']*5
df_style = df.style.apply(style_row, axis=1)

# PDF Generation
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Identificação e parâmetros
    pdf.cell(0, 10, f"Projeto: {project_name}", ln=True)
    pdf.cell(0, 10, f"Usuário: {user_name}", ln=True)
    pdf.ln(5)
    pdf.cell(0, 8, "Parâmetros de entrada:", ln=True)
    for line in [f"Tipo: {tipo}", f"Estaca PIV: {station_i}+{offset_i:.2f}", f"i1: {i1_valor:.2f}%", f"i2: {i2_valor:.2f}%", f"L: {L} m"]:
        pdf.cell(0, 8, line, ln=True)
    pdf.ln(5)
    # Resultados antes da tabela
    pdf.cell(0, 8, "Resultados:", ln=True)
    for line in [f"Desnível (g): {g:.5f}", f"Flecha (e): {e:.4f} m", f"Cota A: {Z_A:.3f} m", f"Cota PIV: {Z_I_parab:.3f} m", f"Cota B: {Z_B:.3f} m", f"Vértice x: {x_V:.3f} m, Z: {Z_V:.3f} m"]:
        pdf.cell(0, 8, line, ln=True)
    pdf.ln(5)
    # Gráfico
    buf = BytesIO()
    fig.savefig(buf, format='PNG'); buf.seek(0)
    pdf.image(buf, x=pdf.l_margin, w=pdf.w - 2*pdf.l_margin)
    pdf.ln(5)
    pdf.add_page()
    # Tabela com bordas após a imagem
    pdf.cell(0, 8, "Tabela de Estacas:", ln=True)
    table_w = pdf.w - 2*pdf.l_margin
    col_w = table_w / 5
    headers = ["Estaca","Posição","Dist_A","Cota","Tipo"]
    # Cabeçalho
    for h in headers:
        pdf.cell(col_w, 8, h, border=1)
    pdf.ln()
    # Linhas
    for row in rows:
        pdf.cell(col_w, 8, row["Estaca"], border=1)
        pdf.cell(col_w, 8, str(row["Posição"]), border=1)
        pdf.cell(col_w, 8, str(row["Dist_A"]), border=1)
        pdf.cell(col_w, 8, str(row["Cota"]), border=1)
        pdf.cell(col_w, 8, row["Tipo"], border=1)
        pdf.ln()
    out = BytesIO(); pdf.output(out); out.seek(0)
    return out

pdf_bytes = create_pdf()
st.sidebar.download_button("Salvar PDF", data=pdf_bytes, file_name="perfil_concordancia.pdf", mime="application/pdf")

# Display table in app
st.subheader("Tabela de Estacas")
st.dataframe(df_style)
