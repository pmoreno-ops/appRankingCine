import csv
import pymongo

# 1. Configuración de conexión a la BDD origen (peliculas_db)
# Asegúrate de que tu MongoDB esté corriendo en el puerto 27017
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["peliculas_db"]
collection = db["peliculas"]

# Diccionario para traducir géneros de Inglés a Español
TRADUCCION_GENEROS = {
    "Action": "Acción",
    "Adventure": "Aventura",
    "Sci-Fi": "Ciencia Ficción",
    "Crime": "Crimen",
    "Drama": "Drama",
    "Thriller": "Thriller",
    "Horror": "Terror",
    "War": "Bélica",
    "Documentary": "Documental",
    "Comedy": "Comedia",
    "Fantasy": "Fantasía",
    "Romance": "Romance",
    "Animation": "Animación",
    "Historical": "Histórica",
}

def generar_csv():
    # Definimos las columnas del CSV perfecto
    columnas = ['titulo', 'anio', 'categoria', 'descripcion', 'imagen_url', 'tipo', 'director', 'actores']

    with open('../../../peliculas.csv', 'w', newline='', encoding='utf-8') as archivo_csv:
        writer = csv.DictWriter(archivo_csv, fieldnames=columnas)
        writer.writeheader()

        # Obtenemos los documentos de Mongo
        cursor = collection.find()

        contador = 0
        for peli in cursor:
            # 1. GESTIÓN DEL GÉNERO
            # La BDD tiene un Array (ej: ["Drama", "Crime"]). Cogemos el primero.
            generos = peli.get('genre', [])
            genero_ingles = generos[0] if isinstance(generos, list) and len(generos) > 0 else "Varios"

            # Traducimos (si no encuentra traducción, deja el original)
            categoria_final = TRADUCCION_GENEROS.get(genero_ingles, genero_ingles)

            # 2. GESTIÓN DEL TIPO (P o S)
            # Como la BDD se llama 'peliculas_db', asumimos que todo es 'P' (Película).
            # Si tuvieras una forma de saber si es serie, pon aquí la lógica.
            tipo_final = 'P'

            # Preparamos la fila
            fila = {
                'titulo': peli.get('title'),
                'anio': peli.get('year'),
                'categoria': categoria_final, # Ya traducido: "Crimen"
                'descripcion': peli.get('description', 'Sin descripción'),
                # Usamos una imagen genérica si no hay URL en la BDD origen
                'imagen_url': peli.get('poster', 'https://via.placeholder.com/300x450?text=No+Poster'),
                'tipo': tipo_final
            }

            writer.writerow(fila)
            contador += 1

    print(f"¡Éxito! Se ha generado 'peliculas.csv' con {contador} registros.")

if __name__ == "__main__":
    generar_csv()