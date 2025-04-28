import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from io import BytesIO

# Configuración de la página
st.set_page_config(page_title="Problema de los Tres Cuerpos", page_icon="🌟")
st.title("Simulación del Problema de los Tres Cuerpos")
st.markdown("""
Esta aplicación muestra el comportamiento caótico en el problema de los tres cuerpos.
Cambia los parámetros iniciales y observa cómo evoluciona el sistema.
""")

# Constantes físicas
G = 6.67430e-11  # Constante gravitacional (m³ kg⁻¹ s⁻²)

# Función para resolver las ecuaciones diferenciales
def three_body_equations(t, y, masses):
    n = 3
    positions = y[:2*n].reshape((n, 2))
    derivatives = np.zeros_like(y)
    
    for i in range(n):
        derivatives[6*i:6*i+2] = positions[i, 1]  # Velocidad
        derivatives[6*i+2:6*i+4] = 0  # Aceleración (se calculará)
        
        acceleration = np.zeros(2)
        for j in range(n):
            if i != j:
                r_vec = positions[j, 0] - positions[i, 0]
                r = np.linalg.norm(r_vec)
                acceleration += G * masses[j] * r_vec / (r**3)
                
        derivatives[6*i+4:6*i+6] = acceleration
    
    return derivatives

# Método de Runge-Kutta de 4to orden
def rk4_step(func, t, y, dt, *args):
    k1 = func(t, y, *args)
    k2 = func(t + dt/2, y + dt*k1/2, *args)
    k3 = func(t + dt/2, y + dt*k2/2, *args)
    k4 = func(t + dt, y + dt*k3, *args)
    return y + dt*(k1 + 2*k2 + 2*k3 + k4)/6

# Interfaz de usuario
with st.sidebar:
    st.header("Parámetros Iniciales")
    simulation_time = st.slider("Tiempo de simulación (s)", 1e3, 1e6, 1e5)
    dt = st.slider("Paso temporal (s)", 10, 1000, 100)
    
    st.subheader("Cuerpo 1")
    m1 = st.number_input("Masa 1 (kg)", 1e20, 1e30, 1e24)
    x1, y1 = st.columns(2)
    x10 = x1.number_input("x1 (m)", -1e10, 1e10, 0.0)
    y10 = y1.number_input("y1 (m)", -1e10, 1e10, 0.0)
    vx1, vy1 = st.columns(2)
    vx10 = vx1.number_input("vx1 (m/s)", -1e4, 1e4, 0.0)
    vy10 = vy1.number_input("vy1 (m/s)", -1e4, 1e4, 0.0)
    
    st.subheader("Cuerpo 2")
    m2 = st.number_input("Masa 2 (kg)", 1e20, 1e30, 1e24)
    x2, y2 = st.columns(2)
    x20 = x2.number_input("x2 (m)", -1e10, 1e10, 1e9)
    y20 = y2.number_input("y2 (m)", -1e10, 1e10, 0.0)
    vx2, vy2 = st.columns(2)
    vx20 = vx2.number_input("vx2 (m/s)", -1e4, 1e4, 0.0)
    vy20 = vy2.number_input("vy2 (m/s)", -1e4, 1e4, 500.0)
    
    st.subheader("Cuerpo 3")
    m3 = st.number_input("Masa 3 (kg)", 1e20, 1e30, 1e24)
    x3, y3 = st.columns(2)
    x30 = x3.number_input("x3 (m)", -1e10, 1e10, -1e9)
    y30 = y3.number_input("y3 (m)", -1e10, 1e10, 0.0)
    vx3, vy3 = st.columns(2)
    vx30 = vx3.number_input("vx3 (m/s)", -1e4, 1e4, 0.0)
    vy30 = vy3.number_input("vy3 (m/s)", -1e4, 1e4, -500.0)

# Condiciones iniciales
y0 = np.array([
    x10, y10, vx10, vy10, 0, 0,
    x20, y20, vx20, vy20, 0, 0,
    x30, y30, vx30, vy30, 0, 0
])

masses = [m1, m2, m3]

# Simulación
if st.button("Iniciar Simulación"):
    progress = st.progress(0)
    status_text = st.empty()
    
    n_steps = int(simulation_time // dt)
    t = 0
    y = y0.copy()
    
    positions_history = np.zeros((n_steps, 3, 2))
    
    for i in range(n_steps):
        y = rk4_step(three_body_equations, t, y, dt, masses)
        t += dt
        
        # Almacenar posiciones
        positions_history[i, 0] = y[0:2]
        positions_history[i, 1] = y[6:8]
        positions_history[i, 2] = y[12:14]
        
        progress.progress((i + 1) / n_steps)
        status_text.text(f"Progreso: {i+1}/{n_steps} pasos")
    
    # Visualización
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_title("Trayectorias de los Tres Cuerpos")
    ax.set_xlabel("Coordenada X (m)")
    ax.set_ylabel("Coordenada Y (m)")
    ax.grid(True)
    
    # Plotear trayectorias
    colors = ['red', 'blue', 'green']
    labels = ['Cuerpo 1', 'Cuerpo 2', 'Cuerpo 3']
    
    for i in range(3):
        ax.plot(positions_history[:, i, 0], positions_history[:, i, 1],
                color=colors[i], label=labels[i], alpha=0.7, lw=1)
    
    # Mostrar posiciones finales
    for i in range(3):
        ax.scatter(positions_history[-1, i, 0], positions_history[-1, i, 1],
                   color=colors[i], s=100, edgecolor='black', zorder=10)
    
    ax.legend()
    st.pyplot(fig)
    
    # Animación
    st.subheader("Animación de la Trayectoria")
    fig_anim, ax_anim = plt.subplots(figsize=(8, 6))
    
    # Calcular límites válidos
    x_min = np.nanmin(positions_history[:, :, 0])
    x_max = np.nanmax(positions_history[:, :, 0])
    y_min = np.nanmin(positions_history[:, :, 1])
    y_max = np.nanmax(positions_history[:, :, 1])
    
    # Asegurar que los límites sean finitos
    if not np.isfinite(x_min): x_min = -10.0
    if not np.isfinite(x_max): x_max = 10.0
    if not np.isfinite(y_min): y_min = -10.0
    if not np.isfinite(y_max): y_max = 10.0
    
    # Asegurar que los límites no sean iguales
    if x_min == x_max:
        x_min -= 1.0
        x_max += 1.0
    if y_min == y_max:
        y_min -= 1.0
        y_max += 1.0
    
    ax_anim.set_xlim(x_min, x_max)
    ax_anim.set_ylim(y_min, y_max)
    ax_anim.set_title("Animación de las Trayectorias")
    ax_anim.set_xlabel("Coordenada X (m)")
    ax_anim.set_ylabel("Coordenada Y (m)")
    ax_anim.grid(True)
    
    lines = [ax_anim.plot([], [], color=colors[i], label=labels[i])[0] for i in range(3)]
    points = [ax_anim.plot([], [], 'o', color=colors[i], markersize=10)[0] for i in range(3)]
    
    def init():
        for line, point in zip(lines, points):
            line.set_data([], [])
            point.set_data([], [])
        return lines + points
    
    def animate(frame):
        for i in range(3):
            # Validar que los datos sean finitos antes de graficar
            x_data = positions_history[:frame, i, 0]
            y_data = positions_history[:frame, i, 1]
            x_data = np.nan_to_num(x_data, nan=0.0, posinf=x_max, neginf=x_min)
            y_data = np.nan_to_num(y_data, nan=0.0, posinf=y_max, neginf=y_min)
            
            lines[i].set_data(x_data, y_data)
            points[i].set_data(positions_history[frame, i, 0], positions_history[frame, i, 1])
        return lines + points
    
    # Crear la animación
    anim = FuncAnimation(
        fig_anim,
        animate,
        init_func=init,
        frames=min(n_steps, 100),  # Limitar a 100 frames para mejor rendimiento
        interval=50,
        blit=True
    )
    
    # Mostrar la animación en Streamlit
    st.pyplot(fig_anim)
    
    # Guardar la animación como GIF
    try:
        anim.save('animation.gif', writer='pillow', fps=20)
        st.image('animation.gif', caption="Animación de las trayectorias")
    except Exception as e:
        st.error(f"Error al guardar la animación: {str(e)}")

st.markdown("""
**Nota:** Esta es una simulación simplificada que:
- Ignora efectos relativistas
- Usa integración numérica aproximada
- Considera solo movimiento en 2D
""")