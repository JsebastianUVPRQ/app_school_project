# orbital_simulation.py
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time  # Necesario para la animación paso a paso si no usamos frames de Plotly directamente

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Simulador de Órbitas 3D",
    page_icon="🪐",
    layout="wide"
)

# --- Título y Descripción ---
st.title("🪐 Simulador de Órbitas Planetarias 3D")
st.markdown("""
Esta aplicación visualiza diferentes tipos de órbitas keplerianas en 3D.
Selecciona un tipo de órbita para ver la animación de un planeta alrededor de una estrella central.
La estrella se sitúa en uno de los focos de la cónica.
""")

# --- Parámetros y Selección de Órbita ---
st.sidebar.header("Configuración de la Órbita")
orbit_type = st.sidebar.selectbox(
    "Selecciona el tipo de órbita:",
    ["Elíptica", "Circular", "Parabólica", "Hiperbólica"]
)

# Definimos parámetros base para cada órbita (puedes hacerlos interactivos con sliders si quieres)
# 'p' es el semi-latus rectum: p = a(1-e^2) para elipse, p = a(e^2-1) para hipérbola
# 'e' es la excentricidad
params = {
    "Elíptica": {"e": 0.6, "p": 5.0},
    "Circular": {"e": 0.0, "p": 7.0},  # p = radio para círculo
    "Parabólica": {"e": 1.0, "p": 5.0}, # p = 2 * distancia perihelio
    "Hiperbólica": {"e": 1.5, "p": 5.0}
}

e = params[orbit_type]["e"]
p = params[orbit_type]["p"]

st.sidebar.write(f"**Parámetros:**")
st.sidebar.write(f"Excentricidad (e): `{e}`")
st.sidebar.write(f"Semi-latus rectum (p): `{p}`")

# Número de puntos para la trayectoria completa y para la animación
n_points_trajectory = 500
n_points_animation = 150 # Menos puntos para que la animación no sea eterna

# --- Cálculo de la Trayectoria ---

def calcular_coordenadas(e, p, n_points):
    """Calcula las coordenadas (x, y, z=0) de la órbita."""
    if e < 1: # Elipse y Círculo
        theta = np.linspace(0, 2 * np.pi, n_points)
    elif e == 1: # Parábola
        # Evitar theta = pi donde r tiende a infinito
        max_angle = np.pi - 0.1 # Límite angular para evitar el infinito
        theta = np.linspace(-max_angle, max_angle, n_points)
    else: # Hipérbola
        # El ángulo está limitado por las asíntotas: cos(theta) > -1/e
        max_angle = np.arccos(-1 / e) - 0.05 # Un poco menos que la asíntota
        theta = np.linspace(-max_angle, max_angle, n_points)

    # Fórmula polar de las cónicas (foco en el origen)
    r = p / (1 + e * np.cos(theta))

    # Convertir a coordenadas cartesianas (en el plano z=0)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    z = np.zeros_like(x) # Mantenemos la órbita en el plano XY

    # Filtrar puntos infinitos o muy lejanos (importante para parábola/hipérbola)
    mask = np.isfinite(x) & np.isfinite(y) & (np.abs(r) < 50) # Limitar distancia visual
    return x[mask], y[mask], z[mask], theta[mask]

# Calcula las coordenadas para la trayectoria completa y la animación
x_traj, y_traj, z_traj, theta_traj = calcular_coordenadas(e, p, n_points_trajectory)
x_anim, y_anim, z_anim, theta_anim = calcular_coordenadas(e, p, n_points_animation)

# --- Creación de la Figura 3D con Plotly ---

fig = go.Figure()

# 1. Estrella Central (en el foco, origen)
fig.add_trace(go.Scatter3d(
    x=[0], y=[0], z=[0],
    mode='markers',
    marker=dict(
        size=10,
        color='yellow',
        symbol='circle'
    ),
    name='Estrella'
))

# 2. Trayectoria Completa (línea gris)
fig.add_trace(go.Scatter3d(
    x=x_traj, y=y_traj, z=z_traj,
    mode='lines',
    line=dict(
        color='grey',
        width=2
    ),
    name='Trayectoria'
))

# 3. Planeta (punto inicial para la animación)
fig.add_trace(go.Scatter3d(
    x=[x_anim[0]], y=[y_anim[0]], z=[z_anim[0]], # Posición inicial
    mode='markers',
    marker=dict(
        size=6,
        color='blue',
        symbol='circle'
    ),
    name='Planeta'
))

# --- Configuración de la Animación ---
frames = [go.Frame(data=[go.Scatter3d(x=[x_anim[k+1]], y=[y_anim[k+1]], z=[z_anim[k+1]])], # Solo actualiza la posición del planeta
                   traces=[2], # El índice de la traza del planeta (0: estrella, 1: trayectoria, 2: planeta)
                   name=f'frame{k}')
          for k in range(n_points_animation)]

fig.frames = frames

# Botones de Play/Pause
updatemenus = [
    dict(
        type='buttons',
        showactive=False,
        buttons=[
            dict(label='Play ▶',
                 method='animate',
                 args=[None, dict(frame=dict(duration=50, redraw=True), # Duración por frame (ms)
                                  fromcurrent=True,
                                  transition=dict(duration=0)) # Sin transición suave
                       ]
                 ),
            dict(label='Pause ⏸',
                 method='animate',
                 args=[[None], dict(frame=dict(duration=0, redraw=False),
                                    mode='immediate',
                                    transition=dict(duration=0))
                       ]
                 )
        ],
        direction="left",
        pad={"r": 10, "t": 70}, # Ajusta el padding si es necesario
        x=0.1,
        xanchor="right",
        y=0,
        yanchor="top"
    )
]


# --- Configuración del Layout del Gráfico 3D ---
# Determinar límites adecuados para los ejes
max_range = max(np.max(np.abs(x_traj)), np.max(np.abs(y_traj)), p) * 1.2
min_range = -max_range

# Manejo especial si la órbita es muy grande o infinita (parábola/hipérbola)
if not np.isfinite(max_range):
    max_range = 20 # Un valor por defecto razonable
    min_range = -max_range

fig.update_layout(
    scene=dict(
        xaxis=dict(range=[min_range, max_range], autorange=False, title='X (UA)', backgroundcolor="rgb(200, 200, 230)"),
        yaxis=dict(range=[min_range, max_range], autorange=False, title='Y (UA)', backgroundcolor="rgb(230, 200, 230)"),
        zaxis=dict(range=[min_range/2, max_range/2], autorange=False, title='Z (UA)', backgroundcolor="rgb(230, 230, 200)"), # Z más pequeño
        aspectmode='cube' # Mantiene la proporción cúbica, 'data' ajusta a los datos
    ),
    title=f"Animación de Órbita {orbit_type}",
    updatemenus=updatemenus, # Añadir botones de animación
    margin=dict(l=0, r=0, b=0, t=40), # Ajustar márgenes
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    )
)

# --- Mostrar el Gráfico en Streamlit ---
st.plotly_chart(fig, use_container_width=True)

# --- Notas Adicionales ---
st.markdown("---")
st.markdown("""
**Notas:**
* La animación utiliza un número fijo de puntos (`n_points_animation`). La velocidad del planeta no es constante (sigue la segunda ley de Kepler cualitativamente, más rápido cerca de la estrella).
* La órbita se mantiene en el plano Z=0 para simplificar.
* Los parámetros `e` (excentricidad) y `p` (semi-latus rectum) definen la forma y tamaño de la órbita.
* Para órbitas parabólicas e hiperbólicas, la trayectoria se extiende al infinito. La visualización está limitada a un rango razonable.
""")

# Para ejecutar esta aplicación:
# 1. Guarda el código como un archivo Python (ej. `orbital_simulation.py`).
# 2. Asegúrate de tener las librerías instaladas: pip install streamlit numpy plotly
# 3. Abre tu terminal y ejecuta: streamlit run orbital_simulation.py