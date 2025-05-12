import streamlit as st
import numpy as np
import plotly.graph_objs as go

# Three-body problem simulation using RK4 integration
def three_body(state, t=0, G=1.0, m1=1.0, m2=1.0, m3=1.0):
    x1, y1, z1, x2, y2, z2, x3, y3, z3, vx1, vy1, vz1, vx2, vy2, vz2, vx3, vy3, vz3 = state
    # Positions
    r1 = np.array([x1, y1, z1])
    r2 = np.array([x2, y2, z2])
    r3 = np.array([x3, y3, z3])
    # Distances
    d12 = np.linalg.norm(r2 - r1)
    d13 = np.linalg.norm(r3 - r1)
    d23 = np.linalg.norm(r3 - r2)
    # Accelerations
    a1 = G * m2 * (r2 - r1) / d12**3 + G * m3 * (r3 - r1) / d13**3
    a2 = G * m1 * (r1 - r2) / d12**3 + G * m3 * (r3 - r2) / d23**3
    a3 = G * m1 * (r1 - r3) / d13**3 + G * m2 * (r2 - r3) / d23**3
    return np.concatenate((
        [*r1, *r2, *r3, *[vx1, vy1, vz1], *[vx2, vy2, vz2], *[vx3, vy3, vz3]]
    )) if False else np.concatenate((
        [*vx1_to_list(vx1, vy1, vz1), *vx1_to_list(vx2, vy2, vz2), *vx1_to_list(vx3, vy3, vz3), *a1, *a2, *a3]
    ))

def rk4_step(f, y, dt):
    k1 = f(y)
    k2 = f(y + dt/2 * k1)
    k3 = f(y + dt/2 * k2)
    k4 = f(y + dt * k3)
    return y + dt/6 * (k1 + 2*k2 + 2*k3 + k4)

def simulate(initial_state, steps=1000, dt=0.01):
    traj = np.zeros((steps, len(initial_state)))
    state = initial_state.copy()
    for i in range(steps):
        traj[i] = state
        state = rk4_step(three_body, state, dt)
    return traj

# Streamlit UI
st.title("Problema de los Tres Cuerpos: Sensibilidad a Condiciones Iniciales")

offset = st.slider("Desfase inicial (epsilon)", min_value=0.0, max_value=0.1, value=1e-5, step=1e-6, format="%e")

# Condiciones iniciales base
i0 = np.array([
    -0.97000436, 0.24308753, 0.0,
     0.97000436, -0.24308753, 0.0,
     0.0,       0.0,        0.0,
     0.4662036850, 0.4323657300, 0.0,
     0.4662036850, 0.4323657300, 0.0,
    -0.93240737, -0.86473146, 0.0
])
# Two initial states
i1 = i0.copy()
i2 = i0.copy()
i2[0] += offset  # small change in x1

# Simulation parameters
steps = st.number_input("Número de pasos", min_value=100, max_value=5000, value=2000, step=100)
dt = st.number_input("Delta t", min_value=1e-4, max_value=0.1, value=0.01, format="%.4f")

with st.spinner("Simulando trayectorias..."):
    traj1 = simulate(i1, steps=steps, dt=dt)
    traj2 = simulate(i2, steps=steps, dt=dt)

# Plotting
def plot_3d(traj, name):
    x1, y1, z1 = traj[:,0], traj[:,1], traj[:,2]
    x2, y2, z2 = traj[:,3], traj[:,4], traj[:,5]
    x3, y3, z3 = traj[:,6], traj[:,7], traj[:,8]
    trace1 = go.Scatter3d(x=x1, y=y1, z=z1, mode='lines', name=f'{name} - Cuerpo 1')
    trace2 = go.Scatter3d(x=x2, y=y2, z=z2, mode='lines', name=f'{name} - Cuerpo 2')
    trace3 = go.Scatter3d(x=x3, y=y3, z=z3, mode='lines', name=f'{name} - Cuerpo 3')
    fig = go.Figure(data=[trace1, trace2, trace3])
    fig.update_layout(scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'), width=600, height=600)
    return fig

st.subheader("Trayectoria para condición inicial base")
st.plotly_chart(plot_3d(traj1, 'Base'))

st.subheader("Trayectoria con pequeño desfase inicial")
st.plotly_chart(plot_3d(traj2, 'Desfase'))

st.markdown("---")
st.write("Se observa cómo una pequeña variación en la condición inicial (epsilon) genera divergencias significativas entre las trayectorias, ilustrando el comportamiento caótico del sistema.")

# Funciones auxiliares
def vx1_to_list(vx, vy, vz):
    return [vx, vy, vz]
