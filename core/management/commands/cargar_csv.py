import csv
import os
import re # Importamos expresiones regulares para separar géneros
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Elemento, Categoria

class Command(BaseCommand):
    help = 'Carga peliculas.csv separando los géneros y creando categorías únicas'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, 'peliculas.csv')

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f' No encuentro el archivo: {file_path}'))
            return

        self.stdout.write(f" Procesando archivo: {file_path}")

        nuevos = 0
        actualizados = 0
        cats_creadas = 0

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    try:
                        titulo = row['titulo'].strip()
                        # Obtenemos la cadena completa de categorías (ej: "Thriller - Crimen")
                        raw_categorias = row['categoria'].strip()

                        # --- PASO 1: SEPARAR GÉNEROS ---
                        # Usamos regex para separar por " - ", " / ", o ","
                        # Esto convierte "Biografía - Música" en ["Biografía", "Música"]
                        lista_generos = re.split(r'\s*[\-\/]\s*|\s*,\s*', raw_categorias)

                        # Filtramos vacíos y limpiamos espacios
                        lista_generos = [g.strip() for g in lista_generos if g.strip()]

                        categoria_principal = None

                        # --- PASO 2: CREAR TODAS LAS CATEGORÍAS ENCONTRADAS ---
                        for index, nombre_cat in enumerate(lista_generos):
                            # Buscar si existe (insensible a mayúsculas/minúsculas para evitar duplicados como "Drama" y "drama")
                            # Nota: Mongo es case-sensitive por defecto, así que buscamos exacto primero.
                            cat_obj = Categoria.objects(nombre=nombre_cat).first()

                            if not cat_obj:
                                cat_obj = Categoria(
                                    nombre=nombre_cat,
                                    descripcion=f"Películas del género {nombre_cat}"
                                )
                                cat_obj.save()
                                cats_creadas += 1
                                self.stdout.write(self.style.SUCCESS(f"   Categoría creada: {nombre_cat}"))

                            # La primera categoría de la lista será la PRINCIPAL para la película
                            if index == 0:
                                categoria_principal = cat_obj

                        # --- PASO 3: GUARDAR PELÍCULA ---
                        anio = int(row['anio']) if row['anio'].isdigit() else 0

                        elemento = Elemento.objects(titulo=titulo).first()

                        if elemento:
                            elemento.anio = anio
                            elemento.categoria = categoria_principal # Asignamos la primera (ej: "Biografía")
                            elemento.descripcion = row['descripcion']
                            elemento.imagen_url = row['imagen_url']
                            elemento.tipo = row.get('tipo', 'P').strip().upper()
                            elemento.director = row.get('director', 'Desconocido')
                            elemento.actores = row.get('actores', 'Varios')
                            elemento.save()
                            actualizados += 1
                        else:
                            Elemento(
                                titulo=titulo,
                                anio=anio,
                                categoria=categoria_principal,
                                descripcion=row['descripcion'],
                                imagen_url=row['imagen_url'],
                                tipo=row.get('tipo', 'P').strip().upper(),
                                director=row.get('director', 'Desconocido'),
                                actores=row.get('actores', 'Varios')
                            ).save()
                            nuevos += 1
                            self.stdout.write(f"  [+] Película: {titulo} ({categoria_principal.nombre})")

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"️ Error fila '{row.get('titulo')}': {e}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f" Error archivo: {e}"))

        self.stdout.write(self.style.SUCCESS(f"\n FIN DEL PROCESO "))
        self.stdout.write(f" Categorías únicas aseguradas: {Categoria.objects.count()}")
        self.stdout.write(f" Categorías nuevas en esta ejecución: {cats_creadas}")
        self.stdout.write(f" Películas procesadas: {nuevos + actualizados}")