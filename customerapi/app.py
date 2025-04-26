import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuración inicial
st.set_page_config(page_title="Calculadora de Inflación", layout="wide")

# Título
st.title("📈 Calculadora de Inflación Argentina")

# Cargar datos históricos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("inflacion.csv", parse_dates=["fecha"])
    df.set_index("fecha", inplace=True)
    return df

df = cargar_datos()

# Sidebar: Entradas del usuario
with st.sidebar:
    st.header("Parámetros de Entrada")
    monto_inicial = st.number_input("Monto inicial ($)", min_value=0.0, value=1000.0)
    fecha_inicio = st.date_input("Fecha inicial", df.index.min())
    fecha_fin = st.date_input("Fecha final", df.index.max())

# Filtrar datos por rango de fechas
try:
    datos_filtrados = df.loc[str(fecha_inicio):str(fecha_fin)]
except KeyError:
    st.error("⚠️ Error: No hay datos para el rango seleccionado.")
    st.stop()

# Calcular inflación acumulada
if datos_filtrados.empty:
    st.warning("No hay datos en el período seleccionado.")
else:
    factores = (1 + datos_filtrados["tasa_inflacion_mensual"] / 100)
    inflacion_acumulada = factores.prod() - 1
    monto_ajustado = monto_inicial * (1 + inflacion_acumulada)

    # Mostrar resultados
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Inflación acumulada", f"{inflacion_acumulada:.2%}")
    with col2:
        st.metric("Monto ajustado", f"${monto_ajustado:,.2f}")

    # Gráfico de evolución
    st.subheader("Evolución mensual de la inflación")
    fig, ax = plt.subplots()
    ax.plot(datos_filtrados.index, datos_filtrados["tasa_inflacion_mensual"], marker="o")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Inflación mensual (%)")
    st.pyplot(fig)

    # Descargar datos
    st.download_button(
        label="Descargar datos en CSV",
        data=datos_filtrados.to_csv(),
        file_name="datos_inflacion.csv",
        mime="text/csv"
    )