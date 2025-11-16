import csv
import random

# ====== CONFIGURACIÓN BÁSICA ======
INPUT_FILE = "estudiantes_originales.csv"   # Tu archivo de entrada
OUTPUT_FILE = "salones_examen.csv"         # Archivo de salida
RANDOM_SEED = 42  # Para resultados reproducibles

random.seed(RANDOM_SEED)

# ====== 1. LEER CSV Y CARGAR LISTAS DE CLASES ======
with open(INPUT_FILE, newline="", encoding="utf-8-sig") as f:
    reader = csv.reader(f)
    rows = list(reader)

if not rows:
    raise ValueError("El archivo CSV está vacío.")

# Fila de encabezados: nombres de las clases
headers = rows[0]                # ["Y7 CARTER", "Y7 DUNANT", ...]
num_cols = len(headers)

# Diccionario: clase -> lista de estudiantes
class_students = {header: [] for header in headers}

# Rellenar las listas de estudiantes por clase
for row in rows[1:]:
    for col_idx, class_name in enumerate(headers):
        if col_idx < len(row):
            name = row[col_idx].strip()
            if name:  # Ignorar celdas vacías
                class_students[class_name].append(name)

# ====== 2. DEFINIR CAPACIDAD DE CADA SALÓN ======
# Usamos el número original de estudiantes como capacidad de cada salón
room_capacity = {
    class_name: len(students)
    for class_name, students in class_students.items()
}

# (Opcional) barajar el orden de los estudiantes dentro de cada clase
for students in class_students.values():
    random.shuffle(students)

# ====== 3. DISTRIBUCIÓN ROUND-ROBIN A CADA SALÓN ======
# Ahora guardamos tuplas (student, class_name) para poder ordenar luego.
rooms_raw = {room_name: [] for room_name in headers}  # salón -> lista de (estudiante, clase_original)
class_order = list(headers)  # orden de clases para agrupar

for room_name in headers:
    capacity = room_capacity[room_name]
    assigned = rooms_raw[room_name]

    while len(assigned) < capacity:
        any_left = False  # para saber si queda alguien en alguna clase

        for class_name in class_order:
            if class_students[class_name]:  # aún hay estudiantes en esta clase
                student = class_students[class_name].pop(0)
                # Guardamos como tupla para poder ordenar después
                assigned.append((student, class_name))
                any_left = True

                if len(assigned) == capacity:
                    break

        # Si ya no queda ningún estudiante en ninguna clase, salimos
        if not any_left:
            break

# ====== 4. ORDENAR DENTRO DE CADA SALÓN POR CLASE ORIGINAL ======
# Queremos algo así dentro del salón Y7 CARTER:
# primero todos (Y7 CARTER), luego (Y7 DUNANT), luego (Y7 GANDHI), etc.
rooms = {}

for room_name, assigned in rooms_raw.items():
    # Ordenamos por índice de la clase original en class_order
    assigned_sorted = sorted(
        assigned,
        key=lambda sc: class_order.index(sc[1])  # sc = (student, class_name)
    )
    # Formateamos de nuevo a string "Nombre (CLASE)"
    rooms[room_name] = [f"{student} ({class_name})" for student, class_name in assigned_sorted]

# ====== 5. GENERAR CSV DE SALONES ======
# Hallar la longitud máxima de lista (la mayor capacidad)
max_len = max(len(lst) for lst in rooms.values())

output_rows = []
# Primera fila: nombres de los salones
output_rows.append(headers)

# Filas siguientes: estudiantes distribuidos
for i in range(max_len):
    row = []
    for room_name in headers:
        if i < len(rooms[room_name]):
            row.append(rooms[room_name][i])
        else:
            row.append("")  # celda vacía si no hay más estudiantes en ese salón
    output_rows.append(row)

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(output_rows)

print(f"Archivo generado: {OUTPUT_FILE}")