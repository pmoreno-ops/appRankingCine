from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# ---------------------------------------------------------------
# IMPORTANTE:
# El Admin de Django NO soporta modelos de MongoEngine (NoSQL).
# Si intentas registrar Categoria, Elemento, etc. aquí, el servidor EXPLOTARÁ.
# ---------------------------------------------------------------

# Solo puedes personalizar el Admin para el modelo USER (que está en SQLite)
# Por ejemplo, si quisieras cambiar cómo se ven los usuarios:

# Des-registramos el User original para poner uno personalizado (Opcional)
# admin.site.unregister(User)
# @admin.register(User)
# class CustomUserAdmin(UserAdmin):
#     list_display = ('username', 'email', 'is_staff', 'date_joined')

# DEJA EL RESTO DEL ARCHIVO VACÍO DE MODELOS MONGO

# Configuración visual para CATEGORÍAS
#@admin.register(Categoria)
#class CategoriaAdmin(admin.ModelAdmin):
#list_display = ('nombre', 'descripcion')
#search_fields = ('nombre',)

# Configuración visual para ELEMENTOS (Películas/Series)
#@admin.register(Elemento)
#class ElementoAdmin(admin.ModelAdmin):
#list_display = ('titulo', 'anio', 'categoria', 'fecha_creacion')
#list_filter = ('categoria', 'anio') # Filtros laterales
#search_fields = ('titulo',)

# Configuración visual para VALORACIONES
#@admin.register(Valoracion)
#class ValoracionAdmin(admin.ModelAdmin):
#list_display = ('usuario', 'elemento', 'puntuacion', 'fecha')
#list_filter = ('puntuacion', 'fecha')

# Configuración visual para RANKINGS
#@admin.register(Ranking)
#class RankingAdmin(admin.ModelAdmin):
# list_display = ('nombre', 'usuario', 'fecha_creacion')