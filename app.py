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

# Parâmetros da curva
st.sidebar.header("Parâmetros da Curva")
tipo = st.sidebar.selectbox("Tipo de curva", ["Convexa", "Côncava"])
Z_I = st.sidebar.number_input("Cota do PIV (I) [m]", value=200.00, step=0.01)

# Estaca do PIV
st.sidebar.subheader("Estaca do PIV")
station_i = st.sidebar.number_input("Estaca inteira", value=30, step=1, min_value=0)
offset_i  = st.sidebar.number_input("Offset [m]", value=12.5, step=0.1, min_value=0.0)

i1_valor = st.sidebar.number_input("Inclinação i₁ [%]", value=2.50, step=0.01, min_value=0.0)
i2_valor = st.sidebar.number_input("Inclinação i₂ [%]", value=1.00, step=0.01, min_value=0.0)
L        = st.sidebar.number_input("Comprimento L [m]", value=120.0, step=1.0, min_value=1.0)

# Ajuste de sinais
if tipo == "Convexa":
    i1 =  i1_valor/100
    i2 = -i2_valor/100
else:
    i1 = -i1_valor/100
    i2 =  i2_valor/100

g = i1 - i2
e = (L/8)*g

# Cotas
Z_A = Z_I - i1*(L/2) + e
Z_B = Z_A + ((i1+i2)/2)*L

# Vértice
x_V = (i1*L)/g if g else np.nan
y_V = (i1**2 * L)/(2*g) if g else np.nan
Z_V = Z_A + y_V

# PIV na parábola
Z_I_parab = Z_A + i1*(L/2) - e

# Gráfico
x = np.linspace(0, L, 200)
Zp = Z_A + (i1*x - (g/(2*L))*x**2)
fig, ax = plt.subplots(figsize=(9,5))
ax.plot(x, Zp, 'k', lw=2)
ax.plot(np.linspace(-L/3, L,100), Z_A + i1*np.linspace(-L/3,L,100), '--', color='gray')
ax.plot(np.linspace(0, L+L/3,100), Z_B + i2*(np.linspace(0,L+L/3,100)-L), '--', color='orange')
ax.scatter([0,L,L/2], [Z_A,Z_B,Z_I_parab], color='red')
ax.scatter([x_V],[Z_V], color='blue', marker='*', s=180)
ax.set_xlabel('x (m)')
ax.set_ylabel('Cota Z (m)')
ax.set_title(f'Perfil Longitudinal ({tipo})')
ax.grid(True)
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
PCV_chain = stationI_m - L/2
PTV_chain = stationI_m + L/2

pcv_s = int(math.floor(PCV_chain/20)); pcv_o = PCV_chain - pcv_s*20
ptv_s = int(math.floor(PTV_chain/20)); ptv_o = PTV_chain - ptv_s*20

rows = []
# PCV
rows.append({"Estaca":f"{pcv_s}+{pcv_o:.2f}",
             "Chainage":round(PCV_chain,3),
             "Dist_A":0.0,"Cota":round(Z_A,3),"Tipo":"PCV"})
# entre PCV e PIV
start_i = math.ceil(PCV_chain/20)
end_i   = station_i if offset_i>0 else station_i-1
for s in range(start_i,end_i+1):
    ch=s*20; dx=ch-PCV_chain
    z=Z_A + (i1*dx - (g/(2*L))*dx**2)
    rows.append({"Estaca":f"{s}+00","Chainage":ch,"Dist_A":round(dx,3),
                 "Cota":round(z,3),"Tipo":""})
# PIV
rows.append({"Estaca":f"{station_i}+{offset_i:.2f}",
             "Chainage":round(stationI_m,3),
             "Dist_A":round(L/2,3),
             "Cota":round(Z_I_parab,3),"Tipo":"PIV"})
# entre PIV e PTV
for s in range(station_i+1, math.floor(PTV_chain/20)+1):
    ch=s*20; dx=ch-PCV_chain
    z=Z_A + (i1*dx - (g/(2*L))*dx**2)
    rows.append({"Estaca":f"{s}+00","Chainage":ch,"Dist_A":round(dx,3),
                 "Cota":round(z,3),"Tipo":""})
# PTV
rows.append({"Estaca":f"{ptv_s}+{ptv_o:.2f}",
             "Chainage":round(PTV_chain,3),
             "Dist_A":round(L,3),
             "Cota":round(Z_B,3),"Tipo":"PTV"})

df = pd.DataFrame(rows)
def style_row(r):
    if r.Tipo in ["PCV","PTV"]: return ['color:red']*5
    if r.Tipo=="PIV": return ['color:blue']*5
    return ['']*5
df_style = df.style.apply(style_row, axis=1)

st.subheader("Tabela de Estacas")
st.dataframe(df_style)