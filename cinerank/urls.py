from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- RUTAS PRINCIPALES ---
    path('', views.home, name='home'),
    path('series/', views.lista_series, name='series'),
    path('ranking/', views.ranking_global, name='ranking_global'),
    path('categorias/', views.lista_categorias, name='lista_categorias'),

    path('ranking-gestion/', views.panel_ranking, name='panel_ranking'),
    path('ranking-gestion/cambiar/<str:item_id>/<str:accion>/', views.cambiar_ranking, name='cambiar_ranking'),

    path('mis-listas/', views.mis_rankings, name='mis_rankings'),
    path('agregar-a-ranking/<id_elemento>/', views.agregar_a_ranking, name='agregar_a_ranking'),


    # MongoDB usa IDs alfanuméricos, así que usamos 'str' en lugar de 'int'
    path('elemento/<str:elemento_id>/', views.detalle_elemento, name='detalle'),

    path('crear/', views.crear_elemento, name='crear_elemento'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),

    #Funciones de Administrador (Crear un elemento, una categoría y importar un csv.)
    path('admin-panel/crear-elemento/', views.crear_elemento, name='crear_elemento'),
    path('admin-panel/crear-categoria/', views.crear_categoria, name='crear_categoria'),
    path('admin-panel/importar-csv/', views.importar_csv, name='importar_csv'),

    path('eliminar-elemento/<str:elemento_id>/', views.eliminar_elemento, name='eliminar_elemento'),
    path('eliminar-categoria/<str:categoria_id>/', views.eliminar_categoria, name='eliminar_categoria'),
    path('editar-elemento/<str:elemento_id>/', views.editar_elemento, name='editar_elemento'),
    path('categorias/editar/<str:categoria_id>/', views.editar_categoria, name='editar_categoria'),

    path('categorias/añadir-masivo/<str:categoria_id>/', views.añadir_masivo_categoria, name='añadir_masivo_categoria'),

    #Administrador de Django (Solo para el modelo User, no para los modelos de MongoDB)
    path('admin/', admin.site.urls),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)