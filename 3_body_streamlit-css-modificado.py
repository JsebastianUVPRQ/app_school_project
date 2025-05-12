import streamlit as st
import numpy as np
import plotly.graph_objs as go

# Función que calcula derivadas para el problema de los tres cuerpos
def three_body_derivatives(state, G, m1, m2, m3):
    # Desempaquetar estado: posiciones y velocidades
    x1, y1, z1, x2, y2, z2, x3, y3, z3, vx1, vy1, vz1, vx2, vy2, vz2, vx3, vy3, vz3 = state

    # Vectores de posición
    r1 = np.array([x1, y1, z1])
    r2 = np.array([x2, y2, z2])
    r3 = np.array([x3, y3, z3])

    # Calcular distancias
    d12 = np.linalg.norm(r2 - r1)
    d13 = np.linalg.norm(r3 - r1)
    d23 = np.linalg.norm(r3 - r2)

    # Evitar división por cero
    eps = 1e-9
    d12 = max(d12, eps)
    d13 = max(d13, eps)
    d23 = max(d23, eps)

    # Aceleraciones gravitatorias
    a1 = G * m2 * (r2 - r1) / d12**3 + G * m3 * (r3 - r1) / d13**3
    a2 = G * m1 * (r1 - r2) / d12**3 + G * m3 * (r3 - r2) / d23**3
    a3 = G * m1 * (r1 - r3) / d13**3 + G * m2 * (r2 - r3) / d23**3

    # Retornar vector de derivadas: velocidades seguidas de aceleraciones
    derivatives = np.array([
        vx1, vy1, vz1,
        vx2, vy2, vz2,
        vx3, vy3, vz3,
        *a1, *a2, *a3
    ])
    return derivatives

# Integración con RK4
def rk4_step(f, state, dt, *args):
    k1 = f(state, *args)
    k2 = f(state + dt/2 * k1, *args)
    k3 = f(state + dt/2 * k2, *args)
    k4 = f(state + dt * k3, *args)
    return state + dt/6 * (k1 + 2*k2 + 2*k3 + k4)

# Simulación de trayectorias
def simulate(initial_state, steps, dt, G, m1, m2, m3):
    traj = np.zeros((steps, len(initial_state)))
    state = initial_state.copy()
    for i in range(steps):
        traj[i] = state
        state = rk4_step(three_body_derivatives, state, dt, G, m1, m2, m3)
    return traj

# --- Streamlit UI ---
st.set_page_config(layout="wide")
st.title("Problema de los Tres Cuerpos: Sensibilidad a Condiciones Iniciales")

# Panel lateral: parámetros
st.sidebar.header("Parámetros de simulación")
G = st.sidebar.number_input("Constante G", value=1.0, format="%.3f")
m1 = st.sidebar.number_input("Masa cuerpo 1", value=1.0, format="%.3f")
m2 = st.sidebar.number_input("Masa cuerpo 2", value=1.0, format="%.3f")
m3 = st.sidebar.number_input("Masa cuerpo 3", value=1.0, format="%.3f")
epsilon = st.sidebar.slider("Desfase inicial (epsilon)", 0.0, 0.1, 1e-5, 1e-6, format="%e")
steps = st.sidebar.number_input("Número de pasos", min_value=100, max_value=5000, value=2000, step=100)
dt = st.sidebar.number_input("Delta t", min_value=1e-4, max_value=0.1, value=0.01, format="%.4f")

# Definir condiciones iniciales clásicas (figura-8)
i0 = np.array([
    -0.97000436, 0.24308753, 0.0,
     0.97000436, -0.24308753, 0.0,
     0.0,       0.0,        0.0,
    0.4662036850, 0.4323657300, 0.0,
    0.4662036850, 0.4323657300, 0.0,
   -0.93240737, -0.86473146, 0.0
])

# Generar dos estados iniciales
state1 = i0.copy()
state2 = i0.copy()
state2[0] += epsilon

# Simulación con spinner
with st.spinner("Simulando trayectorias..."):
    traj1 = simulate(state1, steps, dt, G, m1, m2, m3)
    traj2 = simulate(state2, steps, dt, G, m1, m2, m3)

# Función para graficar 3D
def plot_3d(traj, title):
    x1, y1, z1 = traj[:,0], traj[:,1], traj[:,2]
    x2, y2, z2 = traj[:,3], traj[:,4], traj[:,5]
    x3, y3, z3 = traj[:,6], traj[:,7], traj[:,8]
    fig = go.Figure([
        go.Scatter3d(x=x1, y=y1, z=z1, mode='lines', name='Cuerpo 1'),
        go.Scatter3d(x=x2, y=y2, z=z2, mode='lines', name='Cuerpo 2'),
        go.Scatter3d(x=x3, y=y3, z=z3, mode='lines', name='Cuerpo 3')
    ])
    fig.update_layout(
        title=title,
        scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'),
        margin=dict(l=0, r=0, b=0, t=30),
        width=600, height=600
    )
    return fig

# Mostrar gráficos
col1, col2 = st.columns(2)
with col1:
    st.subheader("Condición inicial base")
    st.plotly_chart(plot_3d(traj1, 'Base'), use_container_width=True)
with col2:
    st.subheader("Con pequeño desfase inicial")
    st.plotly_chart(plot_3d(traj2, 'Desfase'), use_container_width=True)

st.markdown("---")
st.write(
    "Observa cómo una mínima variación en la posición inicial conduce a divergencias significativas entre las trayectorias, "
    "ilustrando el carácter caótico del sistema. Modifica epsilon y otros parámetros para explorar el efecto."
)
