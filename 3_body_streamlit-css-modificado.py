import streamlit as st
import numpy as np
import plotly.graph_objs as go

# =============================
# LÓGICA DEL PROBLEMA DE TRES CUERPOS
# =============================
def derivadas_tres_cuerpos(estado, G, m1, m2, m3):
    """
    Calcula las derivadas (velocidades y aceleraciones) para el sistema de tres cuerpos.
    estado: vector de posiciones y velocidades
    G: constante gravitacional
    m1, m2, m3: masas de los cuerpos
    """
    x1, y1, z1, x2, y2, z2, x3, y3, z3, vx1, vy1, vz1, vx2, vy2, vz2, vx3, vy3, vz3 = estado
    r1 = np.array([x1, y1, z1])
    r2 = np.array([x2, y2, z2])
    r3 = np.array([x3, y3, z3])
    d12 = np.linalg.norm(r2 - r1)
    d13 = np.linalg.norm(r3 - r1)
    d23 = np.linalg.norm(r3 - r2)
    eps = 1e-9
    d12 = max(d12, eps)
    d13 = max(d13, eps)
    d23 = max(d23, eps)
    a1 = G * m2 * (r2 - r1) / d12**3 + G * m3 * (r3 - r1) / d13**3
    a2 = G * m1 * (r1 - r2) / d12**3 + G * m3 * (r3 - r2) / d23**3
    a3 = G * m1 * (r1 - r3) / d13**3 + G * m2 * (r2 - r3) / d23**3
    return np.array([
        vx1, vy1, vz1,
        vx2, vy2, vz2,
        vx3, vy3, vz3,
        *a1, *a2, *a3
    ])


def paso_rk4(f, estado, dt, *args):
    """
    Realiza un paso del método de Runge-Kutta 4.
    f: función de derivadas
    estado: vector de estado actual
    dt: paso de tiempo
    args: argumentos extra para f
    """
    k1 = f(estado, *args)
    k2 = f(estado + dt/2 * k1, *args)
    k3 = f(estado + dt/2 * k2, *args)
    k4 = f(estado + dt * k3, *args)
    return estado + dt/6 * (k1 + 2*k2 + 2*k3 + k4)


def simular_trayectorias(estado_inicial, pasos, dt, G, m1, m2, m3):
    """
    Simula la evolución temporal del sistema de tres cuerpos.
    estado_inicial: vector de estado inicial
    pasos: número de pasos de integración
    dt: paso de tiempo
    G, m1, m2, m3: parámetros físicos
    """
    trayectoria = np.zeros((pasos, len(estado_inicial)))
    estado = estado_inicial.copy()
    for i in range(pasos):
        trayectoria[i] = estado
        estado = paso_rk4(derivadas_tres_cuerpos, estado, dt, G, m1, m2, m3)
    return trayectoria

# =============================
# UTILIDADES DE VISUALIZACIÓN
# =============================
def graficar_3d(trayectoria, titulo):
    """
    Genera una figura 3D de las trayectorias de los tres cuerpos.
    """
    x1, y1, z1 = trayectoria[:,0], trayectoria[:,1], trayectoria[:,2]
    x2, y2, z2 = trayectoria[:,3], trayectoria[:,4], trayectoria[:,5]
    x3, y3, z3 = trayectoria[:,6], trayectoria[:,7], trayectoria[:,8]
    fig = go.Figure([
        go.Scatter3d(x=x1, y=y1, z=z1, mode='lines', name='Cuerpo 1'),
        go.Scatter3d(x=x2, y=y2, z=z2, mode='lines', name='Cuerpo 2'),
        go.Scatter3d(x=x3, y=y3, z=z3, mode='lines', name='Cuerpo 3')
    ])
    fig.update_layout(
        title=titulo,
        scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'),
        margin=dict(l=0, r=0, b=0, t=30),
        width=600, height=600
    )
    return fig

# =============================
# INTERFAZ DE USUARIO STREAMLIT
# =============================
st.set_page_config(layout="wide")
st.title("Problema de los Tres Cuerpos: Sensibilidad a Condiciones Iniciales")

# Panel lateral: parámetros
st.sidebar.header("Parámetros de simulación")
G = st.sidebar.number_input("Constante G", value=1.0, format="%.3f")
m1 = st.sidebar.number_input("Masa cuerpo 1", value=1.0, format="%.3f")
m2 = st.sidebar.number_input("Masa cuerpo 2", value=1.0, format="%.3f")
m3 = st.sidebar.number_input("Masa cuerpo 3", value=1.0, format="%.3f")
epsilon = st.sidebar.slider("Desfase inicial (epsilon)", 0.0, 0.1, 1e-5, 1e-6, format="%e")
pasos = st.sidebar.number_input("Número de pasos", min_value=100, max_value=5000, value=2000, step=100)
dt = st.sidebar.number_input("Delta t", min_value=1e-4, max_value=0.1, value=0.01, format="%.4f")

# Condiciones iniciales clásicas (figura-8)
condiciones_iniciales = np.array([
    -0.97000436, 0.24308753, 0.0,
     0.97000436, -0.24308753, 0.0,
     0.0,       0.0,        0.0,
    0.4662036850, 0.4323657300, 0.0,
    0.4662036850, 0.4323657300, 0.0,
   -0.93240737, -0.86473146, 0.0
])

# Generar dos estados iniciales
estado1 = condiciones_iniciales.copy()
estado2 = condiciones_iniciales.copy()
estado2[0] += epsilon

# Simulación con spinner
with st.spinner("Simulando trayectorias..."):
    tray1 = simular_trayectorias(estado1, pasos, dt, G, m1, m2, m3)
    tray2 = simular_trayectorias(estado2, pasos, dt, G, m1, m2, m3)

# Mostrar gráficos
col1, col2 = st.columns(2)
with col1:
    st.subheader("Condición inicial base")
    st.plotly_chart(graficar_3d(tray1, 'Base'), use_container_width=True)
with col2:
    st.subheader("Con pequeño desfase inicial")
    st.plotly_chart(graficar_3d(tray2, 'Desfase'), use_container_width=True)

st.markdown("---")
st.write(
    "Observa cómo una mínima variación en la posición inicial conduce a divergencias significativas entre las trayectorias, "
    "ilustrando el carácter caótico del sistema. Modifica epsilon y otros parámetros para explorar el efecto."
)
