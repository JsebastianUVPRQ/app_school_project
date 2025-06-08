import os
import shutil
import zipfile

# Estructura del proyecto
project_name = "app_school_project"
base_path = f"/mnt/data/{project_name}"
data_path = os.path.join(base_path, "data")
os.makedirs(data_path, exist_ok=True)

# Lista de archivos subidos
uploaded_files = {
    "standings.csv": "file-FegT3tvGfDX1GMnW9HF9Th",
    "team_possession_stats.csv": "file-Bm9La9g3W728knToUTZZqH",
    "team_salary.csv": "file-KvK7LBUMqKJBC3X2XhySFd",
    "team_stats.csv": "file-5JJ7shFVzspFiws3cHuPs9",
    "fixtures.csv": "file-4N5VzSsHTagpUKXcR6kUJu",
    "player_possession_stats.csv": "file-FDJXkrGKwo7rL2jzjZiL1X",
    "player_salaries.csv": "file-4DmX14Da1keZCJoFmRphwF",
    "player_stats.csv": "file-K3pQXc494NYCdZ9vrMoJHR"
}

# Copiar los archivos a la carpeta data/
for filename, file_id in uploaded_files.items():
    shutil.copy(f"/mnt/data/{file_id}", os.path.join(data_path, filename))

# Crear requirements.txt
with open(os.path.join(base_path, "requirements.txt"), "w") as f:
    f.write("streamlit==1.35.0\npandas>=2.0\nplotly>=5.19.0\n")

# Crear README.md
with open(os.path.join(base_path, "README.md"), "w") as f:
    f.write(f"""# ⚽ Football Data App

Una aplicación Streamlit modular y robusta para visualizar estadísticas de fútbol.

## 🚀 Cómo ejecutarla

1. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
