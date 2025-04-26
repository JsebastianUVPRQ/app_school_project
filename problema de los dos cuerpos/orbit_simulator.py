import numpy as np
from scipy.integrate import solve_ivp # type: ignore
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tkinter as tk # Importar tkinter
from tkinter import ttk # Usar widgets temáticos más modernos
from tkinter import messagebox # Para mostrar mensajes de error/éxito

# --- 1. Motor de Física ---
def potential_gravity(r, G, m1, m2):
    # Asegurarse r no es cero
    r_safe = np.maximum(r, 1e-9) # Evitar división por cero
    # V = -G * m1 * m2 / r_safe # Potencial (no siempre necesario para la fuerza)
    dVdr = G * m1 * m2 / r_safe**2 # Derivada necesaria para la fuerza
    return None, dVdr # Devolvemos None para V ya que solo usamos dVdr aquí


def potential_harmonic(r, k):
    V = 0.5 * k * r**2
    dVdr = k * r
    return V, dVdr

def derivatives_cartesian(t, state, potential_func, potential_params, mu):
    x, y, vx, vy = state
    r = np.sqrt(x**2 + y**2)

    if r == 0: # Evitar problemas en la singularidad
        ax, ay = 0, 0
    else:
        # Llama a la función de potencial para obtener dV/dr
        # Los parámetros específicos del potencial se pasan en potential_params
        _, dVdr = potential_func(r, **potential_params)

        # Fuerza F = -dV/dr * (vector unitario r_hat)
        Fx = -dVdr * (x / r)
        Fy = -dVdr * (y / r)
        ax = Fx / mu
        ay = Fy / mu

    return [vx, vy, ax, ay]

def simulate_orbit(potential_type, potential_params_all, initial_conditions, t_span, t_eval, m1, m2):
    if m1 + m2 <= 0:
         raise ValueError("La suma de las masas debe ser positiva.")
    mu = (m1 * m2) / (m1 + m2) if (m1 + m2) > 0 else 0 # Masa reducida

    # Filtrar parámetros y seleccionar función de potencial
    params_for_potential = {}
    if potential_type == 'gravity':
        potential_func = potential_gravity
        # Asegurarse de que G, m1, m2 están en los parámetros
        if 'G' not in potential_params_all or 'm1' not in potential_params_all or 'm2' not in potential_params_all:
             raise ValueError("Parámetros G, m1, m2 requeridos para potencial gravitacional.")
        params_for_potential = {'G': potential_params_all['G'], 'm1': m1, 'm2': m2}
    elif potential_type == 'harmonic':
        potential_func = potential_harmonic
        if 'k' not in potential_params_all:
             raise ValueError("Parámetro k requerido para potencial armónico.")
        params_for_potential = {'k': potential_params_all['k']}
    else:
        raise ValueError(f"Tipo de potencial desconocido: {potential_type}")

    print(f"Simulando con mu={mu}, func={potential_func.__name__}, params={params_for_potential}")
    print(f"Condiciones iniciales: {initial_conditions}")
    print(f"Intervalo de tiempo: {t_span}, Puntos de evaluación: {len(t_eval)}")

    sol = solve_ivp(
        derivatives_cartesian,
        t_span,
        initial_conditions, # [x0, y0, vx0, vy0]
        t_eval=t_eval,
        args=(potential_func, params_for_potential, mu),
        rtol=1e-6, atol=1e-9 # Ajustar tolerancias si es necesario
    )

    if not sol.success:
        raise RuntimeError(f"La integración falló: {sol.message}")

    # Extraer resultados (posición relativa x, y)
    x_rel = sol.y[0]
    y_rel = sol.y[1]

    # Calcular posiciones individuales respecto al CM (asumiendo CM en el origen)
    if (m1 + m2) > 0:
        r1_x = (m2 / (m1 + m2)) * x_rel
        r1_y = (m2 / (m1 + m2)) * y_rel
        r2_x = (-m1 / (m1 + m2)) * x_rel
        r2_y = (-m1 / (m1 + m2)) * y_rel
    else: # Caso límite si una masa es 0 o ambas
        r1_x, r1_y, r2_x, r2_y = x_rel, y_rel, np.zeros_like(x_rel), np.zeros_like(y_rel)


    return sol.t, r1_x, r1_y, r2_x, r2_y

# --- 2. Visualización y GIF ---
def create_animation(t, r1_x, r1_y, r2_x, r2_y, filename="orbit_animation.gif", fps=30):
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    # Determinar límites adecuados para el gráfico basados en las trayectorias
    all_x = np.concatenate((r1_x, r2_x))
    all_y = np.concatenate((r1_y, r2_y))
    # Evitar error si todos los valores son cero o NaN
    if np.all(np.isnan(all_x)) or np.all(np.isnan(all_y)) or (np.max(np.abs(np.nan_to_num(all_x))) == 0 and np.max(np.abs(np.nan_to_num(all_y))) == 0):
         max_range = 1.0 # Rango por defecto si no hay movimiento
    else:
         max_range_x = np.max(np.abs(np.nan_to_num(all_x)))
         max_range_y = np.max(np.abs(np.nan_to_num(all_y)))
         max_range = max(max_range_x, max_range_y) * 1.1
         if max_range == 0: max_range = 1.0 # Evitar rango cero

    ax.set_xlim(-max_range, max_range)
    ax.set_ylim(-max_range, max_range)
    ax.grid(True)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("Simulación Orbital")

    line1, = ax.plot([], [], 'bo-', label='Masa 1', ms=8) # Cuerpo 1
    line2, = ax.plot([], [], 'ro-', label='Masa 2', ms=5) # Cuerpo 2
    trace1, = ax.plot([], [], 'b--', alpha=0.5)
    trace2, = ax.plot([], [], 'r--', alpha=0.5)
    ax.legend(loc='upper right')

    def update(frame):
        if frame < len(r1_x):
            line1.set_data([r1_x[frame]], [r1_y[frame]])
            line2.set_data([r2_x[frame]], [r2_y[frame]])
            trace1.set_data(r1_x[:frame+1], r1_y[:frame+1])
            trace2.set_data(r2_x[:frame+1], r2_y[:frame+1])
        return line1, line2, trace1, trace2

    num_frames = len(t)
    if num_frames == 0:
        print("Advertencia: No hay frames para animar.")
        plt.close(fig)
        return

    ani = animation.FuncAnimation(fig, update, frames=num_frames, blit=True, interval=max(1, 1000/fps))

    print(f"Guardando animación en {filename}...")
    try:
        ani.save(filename, writer='pillow', fps=fps)
        print("Animación guardada exitosamente.")
        messagebox.showinfo("Éxito", f"Animación guardada como:\n{filename}")
    except Exception as e:
        print(f"Error al guardar la animación: {e}")
        messagebox.showerror("Error de Guardado", f"No se pudo guardar la animación:\n{e}\nAsegúrate de tener 'Pillow' instalado.\nPuede que necesites instalar 'ffmpeg'.")

    plt.close(fig) # Cerrar la figura para liberar memoria


# --- 3. Interfaz de Usuario (Tkinter) ---
class OrbitApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Órbitas v1.0")
        self.geometry("450x450") # Tamaño inicial de la ventana

        # Frame principal para organizar widgets
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # --- Configuración del Potencial ---
        pot_frame = ttk.LabelFrame(main_frame, text="Potencial", padding="10")
        pot_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(pot_frame, text="Tipo:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.potential_type_var = tk.StringVar(value='gravity') # Valor inicial
        # Opciones de potencial (ampliar si añades más funciones)
        potential_options = ['gravity'] #, 'harmonic']
        self.potential_combo = ttk.Combobox(pot_frame, textvariable=self.potential_type_var,
                                            values=potential_options, state="readonly", width=15)
        self.potential_combo.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(pot_frame, text="G:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.g_var = tk.StringVar(value='1.0')
        self.g_entry = ttk.Entry(pot_frame, textvariable=self.g_var, width=10)
        self.g_entry.grid(row=1, column=1, sticky=tk.W)
        # Añadir aquí entradas para otros parámetros si es necesario (ej: 'k' para armónico)

        # --- Configuración de las Masas ---
        mass_frame = ttk.LabelFrame(main_frame, text="Masas", padding="10")
        mass_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(mass_frame, text="Masa 1:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.m1_var = tk.StringVar(value='1.0')
        self.m1_entry = ttk.Entry(mass_frame, textvariable=self.m1_var, width=10)
        self.m1_entry.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(mass_frame, text="Masa 2:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.m2_var = tk.StringVar(value='0.1')
        self.m2_entry = ttk.Entry(mass_frame, textvariable=self.m2_var, width=10)
        self.m2_entry.grid(row=1, column=1, sticky=tk.W)

        # --- Condiciones Iniciales (Relativas a Masa 1) ---
        ic_frame = ttk.LabelFrame(main_frame, text="Condiciones Iniciales (Relativas)", padding="10")
        ic_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(ic_frame, text="x0:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.x0_var = tk.StringVar(value='1.0')
        self.x0_entry = ttk.Entry(ic_frame, textvariable=self.x0_var, width=8)
        self.x0_entry.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(ic_frame, text="y0:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.y0_var = tk.StringVar(value='0.0')
        self.y0_entry = ttk.Entry(ic_frame, textvariable=self.y0_var, width=8)
        self.y0_entry.grid(row=0, column=3, sticky=tk.W)

        ttk.Label(ic_frame, text="vx0:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.vx0_var = tk.StringVar(value='0.0')
        self.vx0_entry = ttk.Entry(ic_frame, textvariable=self.vx0_var, width=8)
        self.vx0_entry.grid(row=1, column=1, sticky=tk.W)

        ttk.Label(ic_frame, text="vy0:").grid(row=1, column=2, sticky=tk.W, padx=5)
        # Calcular vy inicial para órbita circular como ejemplo
        vy0_circular_approx = np.sqrt(float(self.g_var.get()) * (float(self.m1_var.get()) + float(self.m2_var.get())) / float(self.x0_var.get()))
        self.vy0_var = tk.StringVar(value=f'{vy0_circular_approx:.2f}') # Valor inicial sugerido
        self.vy0_entry = ttk.Entry(ic_frame, textvariable=self.vy0_var, width=8)
        self.vy0_entry.grid(row=1, column=3, sticky=tk.W)

        # --- Configuración de Simulación ---
        sim_frame = ttk.LabelFrame(main_frame, text="Simulación", padding="10")
        sim_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(sim_frame, text="T. Máx:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.tmax_var = tk.StringVar(value='20.0')
        self.tmax_entry = ttk.Entry(sim_frame, textvariable=self.tmax_var, width=10)
        self.tmax_entry.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(sim_frame, text="Pasos:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.steps_var = tk.StringVar(value='500')
        self.steps_entry = ttk.Entry(sim_frame, textvariable=self.steps_var, width=10)
        self.steps_entry.grid(row=0, column=3, sticky=tk.W)

        ttk.Label(sim_frame, text="Nombre GIF:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.filename_var = tk.StringVar(value='orbit_simulation.gif')
        self.filename_entry = ttk.Entry(sim_frame, textvariable=self.filename_var, width=25)
        self.filename_entry.grid(row=1, column=1, columnspan=3, sticky=tk.W)


        # --- Botón de Acción ---
        self.run_button = ttk.Button(main_frame, text="Simular y Generar GIF", command=self.run_simulation)
        self.run_button.grid(row=4, column=0, columnspan=2, pady=15)

        # --- Estado (opcional) ---
        # self.status_var = tk.StringVar(value="Listo.")
        # self.status_label = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        # self.status_label.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))


    def run_simulation(self):
        try:
            # 1. Leer valores de la GUI y convertirlos
            potential_type = self.potential_type_var.get()
            potential_params_all = {
                'G': float(self.g_var.get()),
                 # 'k': float(self.k_var.get()) # Si tuvieras potencial armónico
                 # Pasar masas también por si V depende explícitamente de ellas
                 'm1': float(self.m1_var.get()),
                 'm2': float(self.m2_var.get())
            }
            m1 = float(self.m1_var.get())
            m2 = float(self.m2_var.get())
            initial_conditions = [
                float(self.x0_var.get()),
                float(self.y0_var.get()),
                float(self.vx0_var.get()),
                float(self.vy0_var.get())
            ]
            t_max = float(self.tmax_var.get())
            num_steps = int(self.steps_var.get())
            gif_filename = self.filename_var.get()

            if not gif_filename.lower().endswith(".gif"):
                gif_filename += ".gif"

            if m1 <= 0 or m2 <= 0:
                 messagebox.showerror("Error de Entrada", "Las masas deben ser positivas.")
                 return
            if t_max <= 0:
                 messagebox.showerror("Error de Entrada", "El tiempo máximo debe ser positivo.")
                 return
            if num_steps <= 1:
                 messagebox.showerror("Error de Entrada", "El número de pasos debe ser mayor que 1.")
                 return


            # 2. Preparar simulación
            t_span = [0, t_max]
            t_eval = np.linspace(t_span[0], t_span[1], num_steps)

            # Deshabilitar botón mientras se procesa
            self.run_button.config(state=tk.DISABLED, text="Procesando...")
            self.update_idletasks() # Asegurar que la GUI se actualiza

            # 3. Ejecutar simulación
            t, r1x, r1y, r2x, r2y = simulate_orbit(
                potential_type, potential_params_all, initial_conditions, t_span, t_eval, m1, m2
            )

            # 4. Crear animación y guardarla
            create_animation(t, r1x, r1y, r2x, r2y, filename=gif_filename, fps=30) # Ajustar fps si se desea

        except ValueError as e:
            messagebox.showerror("Error de Entrada", f"Valor inválido ingresado:\n{e}")
        except RuntimeError as e:
            messagebox.showerror("Error de Simulación", f"Fallo en la integración:\n{e}")
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error:\n{e}")
        finally:
            # Rehabilitar botón
             self.run_button.config(state=tk.NORMAL, text="Simular y Generar GIF")

# --- Ejecución Principal ---
if __name__ == "__main__":
    app = OrbitApp()
    app.mainloop()