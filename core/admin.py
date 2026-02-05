from django.contrib import admin
from .models import Categoria, Elemento, Valoracion, Ranking

# Configuración visual para CATEGORÍAS
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

# Configuración visual para ELEMENTOS (Películas/Series)
@admin.register(Elemento)
class ElementoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'anio', 'categoria', 'fecha_creacion')
    list_filter = ('categoria', 'anio') # Filtros laterales
    search_fields = ('titulo',)

# Configuración visual para VALORACIONES
@admin.register(Valoracion)
class ValoracionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'elemento', 'puntuacion', 'fecha')
    list_filter = ('puntuacion', 'fecha')

# Configuración visual para RANKINGS
@admin.register(Ranking)
class RankingAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'usuario', 'fecha_creacion')