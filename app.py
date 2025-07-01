import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="Concordância Vertical", layout="centered")

st.title("Perfil Longitudinal: Concordância Vertical")

# Identificação do projeto
st.sidebar.title("Identificação")
project_name = st.sidebar.text_input("Projeto", "")
user_name = st.sidebar.text_input("Nome do Usuário", "")

# Parâmetros da curva
st.sidebar.header("Parâmetros da Curva")
tipo = st.sidebar.selectbox("Tipo de curva", ["Convexa", "Côncava"])
Z_I = st.sidebar.number_input("Cota do PIV (I) [m]", value=200.00, step=0.01)
i1_valor = st.sidebar.number_input("Inclinação inicial i₁ [%]", value=2.50, step=0.01, min_value=0.0)
i2_valor = st.sidebar.number_input("Inclinação final i₂ [%]", value=1.00, step=0.01, min_value=0.0)
L = st.sidebar.number_input("Comprimento da curva L [m]", value=120.0, step=1.0, min_value=1.0)

# Ajuste de sinais
if tipo == "Convexa":
    i1 = i1_valor / 100    # positivo
    i2 = -i2_valor / 100   # negativo
else:
    i1 = -i1_valor / 100   # negativo
    i2 = i2_valor / 100    # positivo

curva_tipo = tipo
g = i1 - i2
e = (L / 8) * g

# Cotas dos pontos
Z_A = Z_I - i1 * (L/2) + e
Z_B = Z_A + ((i1 + i2)/2) * L

# Vértice da parábola
x_V = (i1 * L) / g if g != 0 else np.nan
y_V = (i1**2 * L) / (2 * g) if g != 0 else np.nan
Z_V = Z_A + y_V if g != 0 else np.nan

# Pontos notáveis
x_A, x_B, x_I = 0, L, L/2
Z_I_parab = Z_A + i1 * (L/2) - e

# Geração da parábola
x_vals = np.linspace(0, L, 200)
y_vals = i1 * x_vals - (g/(2*L)) * x_vals**2
Z_parab = Z_A + y_vals

# Tangentes
x_tanA = np.linspace(-L/3, L, 100)
Z_tanA = Z_A + i1 * x_tanA
x_tanB = np.linspace(0, L+L/3, 100)
Z_tanB = Z_B + i2 * (x_tanB - L)

# --- Plot
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(x_vals, Z_parab, 'k', lw=2, label='Parábola de Concordância')
ax.plot(x_tanA, Z_tanA, '--', color='gray', label='Tangente em A (PCV)')
ax.plot(x_tanB, Z_tanB, '--', color='orange', label='Tangente em B (PTV)')

# Pontos notáveis
ax.scatter([x_A, x_B, x_I], [Z_A, Z_B, Z_I_parab], color='red', zorder=5)
ax.scatter([x_V], [Z_V], color='blue', zorder=6, marker='*', s=180)

# Labels dos pontos A e B
y_offset = 0.4 if curva_tipo=="Convexa" else -0.4
ax.text(x_A, Z_A + y_offset, "A (PCV)", ha='center', fontsize=11, fontweight='bold')
ax.text(x_B, Z_B + y_offset, "B (PTV)", ha='center', fontsize=11, fontweight='bold')

# Posicionamento inteligente dos labels V (Vértice) e I (PIV)
dx = L * 0.03
dy = (abs(Z_V - Z_I_parab) + 0.6) * (1 if curva_tipo == "Convexa" else -1)

if abs(x_V - x_I) < 0.15 * L:
    if curva_tipo == "Convexa":
        ax.text(x_V, Z_V + abs(dy), "V (Vértice)", ha='center', fontsize=11, color='blue', fontweight='bold')
        ax.text(x_I, Z_I_parab - abs(dy), "I (PIV)", ha='center', fontsize=11, fontweight='bold')
    else:
        ax.text(x_V, Z_V - abs(dy), "V (Vértice)", ha='center', fontsize=11, color='blue', fontweight='bold')
        ax.text(x_I, Z_I_parab + abs(dy), "I (PIV)", ha='center', fontsize=11, fontweight='bold')
else:
    if curva_tipo == "Convexa":
        ax.text(x_V - dx, Z_V + 0.7, "V (Vértice)", ha='center', fontsize=11, color='blue', fontweight='bold')
        ax.text(x_I + dx, Z_I_parab + 0.7, "I (PIV)", ha='center', fontsize=11, fontweight='bold')
    else:
        ax.text(x_V - dx, Z_V - 0.7, "V (Vértice)", ha='center', fontsize=11, color='blue', fontweight='bold')
        ax.text(x_I + dx, Z_I_parab - 0.7, "I (PIV)", ha='center', fontsize=11, fontweight='bold')

# Inclinações
ax.text(x_I/2, Z_A + i1*(x_I/2) + (0.7 if curva_tipo == "Convexa" else -0.7),
        f"$i_1$ = {i1*100:+.2f}%", ha='center', fontsize=10, color='gray')
ax.text((x_I + L)/2, Z_B + i2 * (((x_I + L)/2 - L)) + (0.7 if curva_tipo == "Convexa" else -0.7),
        f"$i_2$ = {i2*100:+.2f}%", ha='center', fontsize=10, color='orange')

ax.set_xlabel('x (m)')
ax.set_ylabel('Cota Z (m)')
ax.set_title(f'Perfil Longitudinal: Concordância Vertical ({curva_tipo})')
ax.grid(True)
ax.legend()
fig.tight_layout()
st.pyplot(fig)

# Exibir resultados
st.subheader(f"Resultados ({curva_tipo})")
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"**Projeto:** {project_name}")
    st.markdown(f"**Usuário:** {user_name}")
    st.markdown(f"**Desnível (g)** = i₁ - i₂ = `{g:.5f}`")
    st.markdown(f"**Flecha vertical (e)** = `{e:.4f} m`")
    st.markdown(f"**Cota de A (PCV)** = `{Z_A:.3f} m`")
with col2:
    st.markdown(f"**Cota de B (PTV)** = `{Z_B:.3f} m`")
    st.markdown(f"**Cota do PIV na parábola** = `{Z_I_parab:.3f} m`")
    st.markdown(f"**Coordenada do vértice**: x = `{x_V:.3f} m`")
    st.markdown(f"**Cota do vértice**: Z = `{Z_V:.3f} m`")

# Função para criar PDF
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Projeto: {project_name}", ln=True)
    pdf.cell(0, 10, f"Usuário: {user_name}", ln=True)
    pdf.ln(5)
    pdf.cell(0, 8, "Parâmetros de entrada:", ln=True)
    pdf.cell(0, 8, f"Tipo de curva: {curva_tipo}", ln=True)
    pdf.cell(0, 8, f"Cota do PIV: {Z_I} m", ln=True)
    pdf.cell(0, 8, f"i1: {i1_valor:.2f}%", ln=True)
    pdf.cell(0, 8, f"i2: {i2_valor:.2f}%", ln=True)
    pdf.cell(0, 8, f"Comprimento L: {L} m", ln=True)
    pdf.ln(5)
    pdf.cell(0, 8, "Resultados:", ln=True)
    pdf.cell(0, 8, f"Desnível (g): {g:.5f}", ln=True)
    pdf.cell(0, 8, f"Flecha (e): {e:.4f} m", ln=True)
    pdf.cell(0, 8, f"Cota A (PCV): {Z_A:.3f} m", ln=True)
    pdf.cell(0, 8, f"Cota do PIV (parábola): {Z_I_parab:.3f} m", ln=True)
    pdf.cell(0, 8, f"Cota B (PTV): {Z_B:.3f} m", ln=True)
    pdf.cell(0, 8, f"Vértice: x={x_V:.3f} m, Z={Z_V:.3f} m", ln=True)
    pdf.ln(5)
    # inserir gráfico
    buf = BytesIO()
    fig.savefig(buf, format='PNG')
    buf.seek(0)
    pdf.image(buf, x=10, y=None, w=pdf.w - 20)
    pdf_out = BytesIO()
    pdf.output(pdf_out)
    pdf_out.seek(0)
    return pdf_out

# Botão de download de PDF
pdf_bytes = create_pdf()
st.sidebar.download_button("Salvar PDF", data=pdf_bytes, file_name="perfil_concordancia.pdf", mime="application/pdf")
