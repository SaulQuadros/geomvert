# app_concordancia

Aplicação Streamlit para cálculo e visualização de perfis longitudinais de concordância vertical em projetos de vias, com identificação automática dos pontos notáveis (A, B, I, V).

## Como usar

1. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
2. Execute o aplicativo:
   ```
   streamlit run app_concordancia.py
   ```
3. Use o menu lateral para inserir:
   - Tipo de curva (Convexa ou Côncava)
   - Inclinações i₁ e i₂ (em % — sempre insira valores positivos)
   - Cota do PIV (I)
   - Comprimento da curva

O aplicativo exibirá o gráfico do perfil longitudinal e as principais informações calculadas.

---

**Obs:** Para dúvidas, sugestões ou melhorias, entre em contato.
