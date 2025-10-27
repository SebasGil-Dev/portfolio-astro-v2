# cargar_datos_dw_fixed.py
import random
from datetime import datetime, timedelta
from faker import Faker
import mysql.connector

# ========= CONEXIÓN =========
CNF = dict(
    host="localhost",      # o 127.0.0.1
    port=3306,             # cambia si tu MySQL usa otro puerto
    user="root",           # ajusta si usas otro usuario
    password="",           # tu contraseña si tienes
    database="automatech"  # ya creada en phpMyAdmin
)

fake = Faker('es_ES')

# ========= PARÁMETROS DE TAMAÑO =========
NUM_CLIENTES   = 5_000
NUM_TIEMPOS    = 3_650   # ~10 años
NUM_PROYECTOS  = 8_000
NUM_EQUIPOS    = 1_000
NUM_PROCESOS   = 2_000
NUM_HECHOS     = 50_000  # Fact table

CHUNK_SIZE     = 1_000   # tamaño de lote seguro (ajústalo si quieres)

# ========= SQL DE CREACIÓN =========
DDL = [
    """
    CREATE TABLE IF NOT EXISTS Dim_Cliente (
        id_cliente INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(150),
        sector VARCHAR(100),
        region VARCHAR(100),
        tamano_empresa VARCHAR(50)
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS Dim_Tiempo (
        id_tiempo INT AUTO_INCREMENT PRIMARY KEY,
        fecha DATE,
        dia INT,
        mes INT,
        anio INT,
        trimestre INT,
        nombre_dia VARCHAR(20),
        INDEX (fecha)
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS Dim_Proyecto (
        id_proyecto INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(150),
        tipo VARCHAR(100),
        estado VARCHAR(50)
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS Dim_Equipo (
        id_equipo INT AUTO_INCREMENT PRIMARY KEY,
        nombre_lider VARCHAR(150),
        cantidad_integrantes INT
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS Dim_Proceso (
        id_proceso INT AUTO_INCREMENT PRIMARY KEY,
        nombre_proceso VARCHAR(100),
        tecnologia_usada VARCHAR(100)
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS Fact_Proyectos (
        id_hecho INT AUTO_INCREMENT PRIMARY KEY,
        id_cliente INT,
        id_proyecto INT,
        id_tiempo INT,
        id_equipo INT,
        id_proceso INT,
        ingresos BIGINT,
        costos BIGINT,
        margen_ganancia BIGINT,
        rentabilidad DECIMAL(6,2),
        horas_invertidas INT,
        procesos_automatizados INT,
        eficiencia_lograda DECIMAL(6,2),
        incidencias INT,
        FOREIGN KEY (id_cliente)  REFERENCES Dim_Cliente(id_cliente),
        FOREIGN KEY (id_proyecto) REFERENCES Dim_Proyecto(id_proyecto),
        FOREIGN KEY (id_tiempo)   REFERENCES Dim_Tiempo(id_tiempo),
        FOREIGN KEY (id_equipo)   REFERENCES Dim_Equipo(id_equipo),
        FOREIGN KEY (id_proceso)  REFERENCES Dim_Proceso(id_proceso)
    ) ENGINE=InnoDB;
    """
]

# ========= UTILIDAD: INSERTAR EN LOTES =========
def bulk_insert(cur, sql, data, chunk=CHUNK_SIZE):
    """Inserta data en lotes para evitar exceder max_allowed_packet."""
    if not data:
        return
    for i in range(0, len(data), chunk):
        cur.executemany(sql, data[i:i+chunk])

# ========= GENERADORES =========
sectores = ["Finanzas", "Salud", "Tecnología", "Manufactura", "Retail", "Educación", "Gobierno"]
regiones = ["Andina", "Caribe", "Pacífica", "Orinoquía", "Amazonía", "Centro"]
tamanos  = ["Micro", "Pequeña", "Mediana", "Grande"]

tipos_proyecto = ["Implementación", "Mantenimiento", "Migración", "Integración", "Desarrollo"]
estados = ["Planeado", "En progreso", "En pausa", "Completado", "Cancelado"]

tecnologias = ["Python", "Java", "C#", "Node.js", "Go", "RPA", "UiPath", "PowerAutomate", "SAP", "Salesforce"]

def generar_clientes(n):
    return [(fake.company(), random.choice(sectores), random.choice(regiones), random.choice(tamanos))
            for _ in range(n)]

def generar_tiempo(n, start_date=datetime(2015, 1, 1)):
    out = []
    for i in range(n):
        f = start_date + timedelta(days=i)
        trimestre = (f.month - 1) // 3 + 1
        # nombre del día en español manual para evitar tema locale
        dia_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][f.weekday()]
        out.append((f.date(), f.day, f.month, f.year, trimestre, dia_semana))
    return out

def generar_proyectos(n):
    return [(f"Proyecto {fake.word().capitalize()}", random.choice(tipos_proyecto), random.choice(estados))
            for _ in range(n)]

def generar_equipos(n):
    return [(fake.name(), random.randint(3, 10)) for _ in range(n)]

def generar_procesos(n):
    return [(f"Automatización {fake.word().capitalize()}", random.choice(tecnologias)) for _ in range(n)]

def generar_hechos(n, max_ids):
    """max_ids = (clientes, proyectos, tiempos, equipos, procesos)"""
    hechos = []
    for _ in range(n):
        ingresos = random.randint(5_000_000, 50_000_000)
        costos = random.randint(2_000_000, max(2_000_000, ingresos - 1_000_000))
        ganancia = ingresos - costos
        rentabilidad = round((ganancia / ingresos) * 100, 2) if ingresos else 0.0
        eficiencia = round(random.uniform(10, 70), 2)
        hechos.append((
            random.randint(1, max_ids[0]),  # id_cliente
            random.randint(1, max_ids[1]),  # id_proyecto
            random.randint(1, max_ids[2]),  # id_tiempo
            random.randint(1, max_ids[3]),  # id_equipo
            random.randint(1, max_ids[4]),  # id_proceso
            ingresos,
            costos,
            ganancia,
            rentabilidad,
            random.randint(100, 1000),      # horas_invertidas
            random.randint(1, 5),           # procesos_automatizados
            eficiencia,
            random.randint(0, 5)            # incidencias
        ))
    return hechos

# ========= MAIN =========
def main():
    conn = mysql.connector.connect(**CNF)
    conn.autocommit = False  # control manual de transacciones
    cur = conn.cursor()

    # Crear tablas
    for ddl in DDL:
        cur.execute(ddl)

    # Vaciar tablas (opcional, según necesidad)
    cur.execute("SET FOREIGN_KEY_CHECKS=0;")
    for t in ["Fact_Proyectos", "Dim_Proceso", "Dim_Equipo", "Dim_Proyecto", "Dim_Tiempo", "Dim_Cliente"]:
        cur.execute(f"TRUNCATE TABLE {t};")
    cur.execute("SET FOREIGN_KEY_CHECKS=1;")

    # Generar datos
    clientes = generar_clientes(NUM_CLIENTES)
    tiempos = generar_tiempo(NUM_TIEMPOS)
    proyectos = generar_proyectos(NUM_PROYECTOS)
    equipos = generar_equipos(NUM_EQUIPOS)
    procesos = generar_procesos(NUM_PROCESOS)

    # Insertar dimensiones en lotes
    bulk_insert(cur,
        "INSERT INTO Dim_Cliente (nombre, sector, region, tamano_empresa) VALUES (%s,%s,%s,%s)",
        clientes
    )
    bulk_insert(cur,
        "INSERT INTO Dim_Tiempo (fecha, dia, mes, anio, trimestre, nombre_dia) VALUES (%s,%s,%s,%s,%s,%s)",
        tiempos
    )
    bulk_insert(cur,
        "INSERT INTO Dim_Proyecto (nombre, tipo, estado) VALUES (%s,%s,%s)",
        proyectos
    )
    bulk_insert(cur,
        "INSERT INTO Dim_Equipo (nombre_lider, cantidad_integrantes) VALUES (%s,%s)",
        equipos
    )
    bulk_insert(cur,
        "INSERT INTO Dim_Proceso (nombre_proceso, tecnologia_usada) VALUES (%s,%s)",
        procesos
    )

    # Hechos (usa los ids máximos actuales)
    max_ids = (NUM_CLIENTES, NUM_PROYECTOS, NUM_TIEMPOS, NUM_EQUIPOS, NUM_PROCESOS)
    hechos = generar_hechos(NUM_HECHOS, max_ids)

    bulk_insert(cur, """INSERT INTO Fact_Proyectos
        (id_cliente, id_proyecto, id_tiempo, id_equipo, id_proceso,
         ingresos, costos, margen_ganancia, rentabilidad,
         horas_invertidas, procesos_automatizados, eficiencia_lograda, incidencias)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", hechos)

    conn.commit()

    # Verificación rápida
    cur.execute("SELECT COUNT(*) FROM Fact_Proyectos;")
    n = cur.fetchone()[0]
    print(f"✅ Carga finalizada. Filas en Fact_Proyectos: {n}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
