from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# 1. Modelo de CATEGORÍAS
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Categorías"

# 2. Modelo de ELEMENTOS (Películas/Series)
class Elemento(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='elementos')
    titulo = models.CharField(max_length=200)
    anio = models.IntegerField(verbose_name="Año de lanzamiento")
    descripcion = models.TextField(verbose_name="Sinopsis")
    imagen_url = models.URLField(blank=True, null=True, verbose_name="URL del Póster")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} ({self.anio})"

# 3. Modelo de VALORACIONES
class Valoracion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    elemento = models.ForeignKey(Elemento, on_delete=models.CASCADE, related_name='valoraciones')
    puntuacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Puntuación del 1 al 5"
    )
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('usuario', 'elemento')

    def __str__(self):
        return f"{self.usuario.username} - {self.elemento.titulo}: {self.puntuacion}"

# 4. Modelo de RANKINGS
class Ranking(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100, default="Mis Favoritos")
    elementos = models.ManyToManyField(Elemento, related_name='rankings')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} de {self.usuario.username}"