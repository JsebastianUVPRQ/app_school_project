import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from scipy.integrate import odeint

# =============================================
# Clase para simular órbitas
# =============================================
class OrbitalSimulator:
    def __init__(self):
        self.G = 1.0  # Constante gravitacional [unidades adimensionales]
        
    def equations_of_motion(self, state, t, potential_choice, params):
        x, y, vx, vy = state
        r = np.sqrt(x**2 + y**2)
        
        # Selección de potencial
        if potential_choice == "Newtoniano":
            F_r = -self.G * params['M'] * params['m'] / r**2
        elif potential_choice == "Armónico":
            F_r = -params['k'] * r
        elif potential_choice == "Personalizado":
            F_r = -params['a']/r**2 + params['b']/r**3  # Ejemplo personalizado
            
        # Componentes de la aceleración
        ax = (F_r * x) / (params['m'] * r)
        ay = (F_r * y) / (params['m'] * r)
        
        return [vx, vy, ax, ay]

    def compute_orbit(self, initial_conditions, t, potential, params):
        solution = odeint(self.eqns_wrapper, initial_conditions, t, args=(potential, params))
        return solution[:,0], solution[:,1]

    def eqns_wrapper(self, state, t, potential, params):
        return self.equations_of_motion(state, t, potential, params)

# =============================================
# Interfaz gráfica
# =============================================
class OrbitalApp:
    def __init__(self, master):
        self.master = master
        self.simulator = OrbitalSimulator()
        self.setup_gui()
        
    def setup_gui(self):
        # Configuración de la ventana
        self.master.title("Simulador de Órbitas")
        self.master.geometry("1000x800")
        
        # Marco de controles
        control_frame = tk.Frame(self.master)
        control_frame.pack(side=tk.LEFT, padx=10, pady=10)

        # Selección de potencial
        self.potential_var = tk.StringVar(value="Newtoniano")
        potentials = ["Newtoniano", "Armónico", "Personalizado"]
        tk.Label(control_frame, text="Tipo de potencial:").pack()
        tk.OptionMenu(control_frame, self.potential_var, *potentials).pack()

        # Parámetros iniciales
        self.params = {
            'M': tk.DoubleVar(value=100.0),
            'm': tk.DoubleVar(value=1.0),
            'k': tk.DoubleVar(value=0.5),
            'a': tk.DoubleVar(value=1.0),
            'b': tk.DoubleVar(value=0.1)
        }
        
        # Campos de entrada
        tk.Label(control_frame, text="\nParámetros:").pack()
        for param, var in self.params.items():
            tk.Entry(control_frame, textvariable=var).pack()
            tk.Label(control_frame, text=param).pack()

        # Botón de simulación
        tk.Button(control_frame, text="Simular", command=self.run_simulation).pack(pady=20)
        
        # Gráfico
        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def run_simulation(self):
        # Condiciones iniciales
        initial_conditions = [2.0, 0.0, 0.0, 1.5]  # x, y, vx, vy
        
        # Tiempo de simulación
        t = np.linspace(0, 20, 500)
        
        # Parámetros del potencial
        params = {k: v.get() for k, v in self.params.items()}
        
        # Calcular órbita
        x, y = self.simulator.compute_orbit(
            initial_conditions,
            t,
            self.potential_var.get(),
            params
        )
        
        # Animación
        self.ax.clear()
        self.ax.set_xlim(-5, 5)
        self.ax.set_ylim(-5, 5)
        
        line, = self.ax.plot([], [], 'b-')
        point, = self.ax.plot([], [], 'ro')
        
        def animate(i):
            line.set_data(x[:i], y[:i])
            point.set_data(x[i], y[i])
            return line, point
        
        self.ani = FuncAnimation(
            self.fig, animate, frames=len(t),
            interval=20, blit=True
        )
        
        self.canvas.draw()

# =============================================
# Ejecutar aplicación
# =============================================
if __name__ == "__main__":
    root = tk.Tk()
    app = OrbitalApp(root)
    root.mainloop()