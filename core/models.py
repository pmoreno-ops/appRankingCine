from mongoengine import Document, StringField, IntField, URLField, DateTimeField, ReferenceField, ListField, CASCADE
import datetime

# 1. Modelo de CATEGORÍAS
class Categoria(Document):
    # En Mongo, CharField y TextField son lo mismo: StringField
    nombre = StringField(max_length=100, unique=True, required=True)
    descripcion = StringField()

    def __str__(self):
        return self.nombre

# 2. Modelo de ELEMENTOS (Películas/Series)
class Elemento(Document):
    # ReferenceField es el equivalente a ForeignKey
    # reverse_delete_rule=CASCADE borra la peli si borras la categoría
    categoria = ReferenceField(Categoria, reverse_delete_rule=CASCADE)

    titulo = StringField(max_length=200, required=True)
    anio = IntField(verbose_name="Año de lanzamiento")
    descripcion = StringField(verbose_name="Sinopsis")
    imagen_url = URLField(verbose_name="URL del Póster")

    # auto_now_add se hace con default=datetime.datetime.now
    fecha_creacion = DateTimeField(default=datetime.datetime.now)

    director = StringField(default="Desconocido")
    actores = StringField(default="Varios")

    orden = IntField(default=0)  # Nuevo campo para el ranking

    # Las choices funcionan igual
    TIPO_CHOICES = (
        ('P', 'Película'),
        ('S', 'Serie'),
    )
    tipo = StringField(choices=TIPO_CHOICES, default='P')

    def __str__(self):
        return f"{self.titulo} ({self.anio})"

# 3. Modelo de VALORACIONES (Fusionado y mejorado)
class Valoracion(Document):
    # IMPORTANTE: No podemos enlazar directamente con User (SQLite).
    # Guardamos el ID del usuario como entero.
    usuario_id = IntField(required=True)

    elemento = ReferenceField(Elemento, reverse_delete_rule=CASCADE)

    PUNTUACIONES = (
        (1, '★☆☆☆☆ (Mala)'),
        (2, '★★☆☆☆ (Regular)'),
        (3, '★★★☆☆ (Buena)'),
        (4, '★★★★☆ (Muy buena)'),
        (5, '★★★★★ (Excelente)'),
    )
    puntuacion = IntField(choices=PUNTUACIONES, required=True)
    comentario = StringField()
    fecha = DateTimeField(default=datetime.datetime.now)

    # Meta para evitar duplicados (unique_together en MongoEngine)
    meta = {
        'indexes': [
            {'fields': ['usuario_id', 'elemento'], 'unique': True}
        ]
    }

    def __str__(self):
        return f"Usuario {self.usuario_id} - Puntuación: {self.puntuacion}"

# 4. Modelo de RANKINGS
class Ranking(Document):
    usuario_id = IntField(required=True)
    nombre = StringField(max_length=100, default="Mis Favoritos")

    # ManyToMany en Mongo se hace con una lista de referencias
    elementos = ListField(ReferenceField(Elemento))

    fecha_creacion = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return f"{self.nombre} (Usuario ID: {self.usuario_id})"