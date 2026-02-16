import csv
import io

from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

# Importaciones de MongoEngine
from mongoengine import DoesNotExist
from .models import Elemento, Valoracion, Categoria, Ranking
from .forms import ValoracionForm, ElementoForm

# --- AUXILIAR PARA GÉNEROS ---
def obtener_categorias_limpias(elementos_queryset):
    """Extrae IDs únicos de categorías para evitar errores de validación"""
    ids_categorias = elementos_queryset.distinct('categoria')
    ids_limpios = [c.id if hasattr(c, 'id') else c for c in ids_categorias if c]
    return Categoria.objects(id__in=ids_limpios).order_by('nombre')


# --- VISTA 1: HOME (PELÍCULAS) ---
def home(request):
    elementos_base = Elemento.objects(tipo='P')
    elementos = elementos_base

    query = request.GET.get('q')
    if query:
        elementos = elementos.filter(titulo__icontains=query)

    categoria_id = request.GET.get('categoria')
    categoria_activa = None
    if categoria_id:
        try:
            elementos = elementos.filter(categoria=categoria_id)
            categoria_activa = Categoria.objects.get(id=categoria_id)
        except:
            pass

    return render(request, 'home.html', {
        'elementos': elementos,
        'categorias': obtener_categorias_limpias(elementos_base),
        'categoria_activa': categoria_activa,
        'titulo_pagina': 'Películas'
    })


# --- VISTA 2: LISTA DE SERIES ---
def lista_series(request):
    elementos_base = Elemento.objects(tipo='S')
    elementos = elementos_base

    query = request.GET.get('q')
    if query:
        elementos = elementos.filter(titulo__icontains=query)

    categoria_id = request.GET.get('categoria')
    categoria_activa = None
    if categoria_id:
        try:
            elementos = elementos.filter(categoria=categoria_id)
            categoria_activa = Categoria.objects.get(id=categoria_id)
        except:
            pass

    return render(request, 'home.html', {
        'elementos': elementos,
        'categorias': obtener_categorias_limpias(elementos_base),
        'categoria_activa': categoria_activa,
        'titulo_pagina': 'Series'
    })


# --- VISTA 3: DETALLE (CORREGIDA) ---
def detalle_elemento(request, elemento_id):
    try:
        elemento = Elemento.objects.get(id=elemento_id)
    except DoesNotExist:
        raise Http404("El elemento no existe")

    valoraciones = Valoracion.objects(elemento=elemento).order_by('-fecha')
    promedio = valoraciones.average('puntuacion')
    promedio = round(promedio, 1) if promedio else 0

    form = ValoracionForm()
    valoracion_existente = None
    user_rankings = []

    if request.user.is_authenticated:
        # CORRECCIÓN: Usar usuario_id=request.user.id para coincidir con el modelo
        user_rankings = Ranking.objects(usuario_id=request.user.id)
        valoracion_existente = Valoracion.objects(usuario_id=request.user.id, elemento=elemento).first()

        if request.method == 'POST':
            form = ValoracionForm(request.POST)
            if form.is_valid():
                puntuacion = int(form.cleaned_data['puntuacion'])
                comentario = form.cleaned_data['comentario']

                if valoracion_existente:
                    valoracion_existente.update(set__puntuacion=puntuacion, set__comentario=comentario)
                    messages.success(request, "¡Tu valoración ha sido actualizada!")
                else:
                    # CORRECCIÓN: Crear usando usuario_id
                    nueva_v = Valoracion(usuario_id=request.user.id, elemento=elemento,
                                         puntuacion=puntuacion, comentario=comentario)
                    nueva_v.save()
                    messages.success(request, "¡Valoración guardada!")
                return redirect('detalle', elemento_id=elemento.id)

        elif valoracion_existente:
            form = ValoracionForm(initial={'puntuacion': valoracion_existente.puntuacion,
                                           'comentario': valoracion_existente.comentario})

    return render(request, 'detalle.html', {
        'elemento': elemento,
        'valoraciones': valoraciones,
        'form': form,
        'promedio': promedio,
        'mi_valoracion': valoracion_existente,
        'user_rankings': user_rankings
    })


# --- VISTA 4: RANKING GLOBAL ---
def ranking_global(request):
    tipo_seleccionado = request.GET.get('tipo', 'P')
    elementos = Elemento.objects(tipo=tipo_seleccionado)

    lista_ranking = []
    for item in elementos:
        vals = Valoracion.objects(elemento=item)
        promedio = vals.average('puntuacion')
        if promedio:
            lista_ranking.append({
                'elemento': item,
                'promedio': round(promedio, 1),
                'total_votos': vals.count()
            })

    ranking_ordenado = sorted(lista_ranking, key=lambda x: (x['promedio'], x['total_votos']), reverse=True)

    return render(request, 'ranking_global.html', {
        'ranking': ranking_ordenado[:50],
        'tipo_actual': tipo_seleccionado
    })

#--- VISTA 5: LISTA DE CATEGORÍAS ---
def lista_categorias(request):
    todas_las_categorias = Categoria.objects.all()
    categorias_validas = []

    for cat in todas_las_categorias:
        # Buscamos elementos de esta categoría
        elementos = Elemento.objects(categoria=cat)

        # SI TIENE ELEMENTOS, la preparamos para el HTML
        if elementos.count() > 0:
            cat.elementos_lista = elementos
            categorias_validas.append(cat)

    return render(request, 'categorias.html', {'categorias': categorias_validas})

# --- VISTAS DE RANKINGS PERSONALES ---
@login_required
def mis_rankings(request):
    rankings = Ranking.objects(usuario_id=request.user.id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre_ranking')
        if nombre:
            Ranking(
                nombre=nombre,
                usuario_id=request.user.id,
                elementos=[]
            ).save()
            messages.success(request, f"Lista '{nombre}' creada.")
        return redirect('mis_rankings')

    return render(request, 'mis_rankings.html', {'rankings': rankings})

@login_required
def agregar_a_ranking(request, id_elemento):
    if request.method == 'POST':
        try:
            elemento = Elemento.objects.get(id=id_elemento)
            ranking_id = request.POST.get('ranking_id')
            ranking = Ranking.objects.get(id=ranking_id, usuario_id=request.user.id)

            if elemento not in ranking.elementos:
                ranking.elementos.append(elemento)
                ranking.save()
                messages.success(request, f"Añadido a {ranking.nombre}")
            else:
                messages.info(request, "Ya está en tu lista.")
        except Exception as e:
            messages.error(request, "No se pudo añadir a la lista.")
    return redirect('detalle', elemento_id=id_elemento)


# --- VISTAS ADMIN ---
@user_passes_test(lambda u: u.is_superuser)
def panel_estadisticas(request):
    datos_categorias = []
    categorias = Categoria.objects.all()

    for cat in categorias:
        elementos = Elemento.objects(categoria=cat)
        cantidad = elementos.count()

        # --- CÁLCULO DEL PROMEDIO (Nuevo requisito RF9) ---
        total_puntos = 0
        total_votos = 0

        # Recorremos los elementos de esta categoría para sumar sus valoraciones
        for el in elementos:
            # Obtenemos valoraciones de este elemento
            vals = Valoracion.objects(elemento=el)
            if vals:
                # Sumamos puntos y cantidad de votos
                total_puntos += vals.sum('puntuacion')
                total_votos += vals.count()

        # Evitamos división por cero
        promedio_cat = round(total_puntos / total_votos, 1) if total_votos > 0 else 0.0

        datos_categorias.append({
            'nombre': cat.nombre,
            'cantidad': cantidad,
            'promedio': promedio_cat  # Enviamos el dato al template
        })

    return render(request, 'estadisticas.html', {
        'total_elementos': Elemento.objects.count(),
        'datos_categorias': datos_categorias
    })

# Crear Elemento (Película o Serie)
@user_passes_test(lambda u: u.is_superuser)
def crear_elemento(request):
    categoria_id = request.GET.get('categoria_id')

    if request.method == 'POST':
        form = ElementoForm(request.POST)
        if form.is_valid():
            nuevo = form.save()
            # Redirigimos a categorías para ver el cambio
            return redirect('lista_categorias')
    else:
        # Preseleccionamos la categoría si viene de la URL
        initial_data = {}
        if categoria_id:
            initial_data['categoria'] = categoria_id

        form = ElementoForm(initial=initial_data)

    # CAMBIO AQUÍ: Quitamos 'admin/' de la ruta del template
    return render(request, 'crear_elemento.html', {
        'form': form,
        'categoria_id': categoria_id
    })

# Crear Categoría
@user_passes_test(lambda u: u.is_superuser)
def crear_categoria(request):
    # Traemos todos los elementos para mostrarlos en el formulario
    todos_los_elementos = Elemento.objects.all().order_by('titulo')

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        elementos_ids = request.POST.getlist('elementos_seleccionados') # IDs marcados

        if nombre:
            # 1. Crear y guardar la categoría primero
            nueva_cat = Categoria(nombre=nombre, descripcion=descripcion)
            nueva_cat.save()

            # 2. Asignar masivamente los elementos seleccionados a esta nueva categoría
            if elementos_ids:
                Elemento.objects(id__in=elementos_ids).update(set__categoria=nueva_cat)

            messages.success(request, f"Categoría '{nombre}' creada y elementos asignados.")

        return redirect('lista_categorias')

    return render(request, 'admin/crear_categoria.html', {
        'elementos_disponibles': todos_los_elementos
    })


@user_passes_test(lambda u: u.is_superuser)
def editar_categoria(request, categoria_id):
    categoria = Categoria.objects(id=categoria_id).first()
    if not categoria:
        messages.error(request, "La categoría no existe.")
        return redirect('lista_categorias')

    # Traemos todos los elementos
    todos_los_elementos = Elemento.objects.all().order_by('titulo')

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        elementos_ids = request.POST.getlist('elementos_seleccionados')

        if nombre:
            # 1. Actualizar datos básicos
            categoria.nombre = nombre
            categoria.descripcion = descripcion
            categoria.save()

            # 2. LOGICA DE ACTUALIZACIÓN DE ELEMENTOS
            # A) Primero: Los elementos que YA estaban en esta categoría pero NO se marcaron ahora,
            # se quedan sin categoría (o podrías no hacer nada, depende de tu lógica).
            # Aquí optamos por limpiar los desmarcados para que la lista sea fiel a lo que ves.
            # Buscamos elementos que son de esta cat pero su ID no está en la lista enviada.
            if elementos_ids:
                Elemento.objects(categoria=categoria, id__nin=elementos_ids).update(unset__categoria=1)
            else:
                # Si no se marcó ninguno, vaciamos la categoría
                Elemento.objects(categoria=categoria).update(unset__categoria=1)

            # B) Segundo: Asignar los marcados a esta categoría
            if elementos_ids:
                Elemento.objects(id__in=elementos_ids).update(set__categoria=categoria)

            messages.success(request, f"Categoría '{nombre}' actualizada correctamente.")
            return redirect('lista_categorias')

    return render(request, 'admin/crear_categoria.html', {
        'categoria': categoria,
        'editando': True,
        'elementos_disponibles': todos_los_elementos
    })

# Importar CSV
@user_passes_test(lambda u: u.is_superuser)
def importar_csv(request):
    if request.method == 'POST' and request.FILES.get('archivo_csv'):
        archivo = request.FILES['archivo_csv']
        data_set = archivo.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        next(io_string) # Saltar cabecera

        count = 0
        for row in csv.reader(io_string, delimiter=',', quotechar='"'):
            # NUEVO ORDEN SOLICITADO:
            # 0:titulo, 1:anio, 2:descripcion, 3:categoria, 4:imagen_url, 5:tipo(P/S), 6:director, 7:actores
            try:
                # Buscar o crear categoría
                cat_obj, _ = Categoria.objects.get_or_create(
                    nombre=row[3].strip(),
                    defaults={'descripcion': 'Categoría creada automáticamente'}
                )

                Elemento(
                    titulo=row[0].strip(),
                    anio=int(row[1]),
                    descripcion=row[2].strip(),
                    categoria=cat_obj,
                    imagen_url=row[4].strip(),
                    tipo=row[5].strip().upper(), # Tipo movido después de imagen_url
                    director=row[6].strip() if len(row) > 6 else "",
                    actores=row[7].strip() if len(row) > 7 else ""
                ).save()
                count += 1
            except Exception as e:
                print(f"Error en fila {row[0] if row else 'desconocida'}: {e}")
                continue

        messages.success(request, f"¡Éxito! Se han importado {count} elementos.")
        return redirect('home')

    return render(request, 'admin/importar_csv.html')


#Eliminar elemento (película o serie)
@user_passes_test(lambda u: u.is_superuser)
def eliminar_elemento(request, elemento_id):
    elemento = Elemento.objects(id=elemento_id).first()
    if elemento:
        elemento.delete()
        messages.success(request, "Elemento eliminado correctamente.")
    return redirect('lista_categorias')

#Eliminar categoría (y sus elementos por CASCADE)
@user_passes_test(lambda u: u.is_superuser)
def eliminar_categoria(request, categoria_id):
    cat = Categoria.objects(id=categoria_id).first()
    if cat:
        # El CASCADE del modelo se encarga de los elementos
        cat.delete()
        messages.success(request, f"Categoría {cat.nombre} y sus elementos eliminados.")
    return redirect('lista_categorias')


#Editar elemento (ej: cambiar categoría, título, etc.)
@user_passes_test(lambda u: u.is_superuser)
def editar_elemento(request, elemento_id):
    # Buscamos el elemento en MongoDB
    elemento = Elemento.objects(id=elemento_id).first()
    if not elemento:
        messages.error(request, "El elemento no existe.")
        return redirect('lista_categorias')

    if request.method == 'POST':
        # Al guardar, pasamos los datos del POST
        form = ElementoForm(request.POST)
        if form.is_valid():
            # Actualizamos los campos manualmente
            elemento.tipo = form.cleaned_data['tipo']
            elemento.titulo = form.cleaned_data['titulo']
            elemento.imagen_url = form.cleaned_data['imagen_url']
            elemento.descripcion = form.cleaned_data['descripcion']
            elemento.anio = form.cleaned_data['anio']
            elemento.categoria = form.cleaned_data['categoria']
            elemento.save()

            messages.success(request, f"'{elemento.titulo}' actualizado correctamente.")
            return redirect('lista_categorias')
    else:
        # AQUÍ ESTÁ EL CAMBIO: Pasamos los datos actuales al formulario
        initial_data = {
            'tipo': elemento.tipo,
            'titulo': elemento.titulo,
            'imagen_url': elemento.imagen_url,
            'descripcion': elemento.descripcion,
            'anio': elemento.anio,
            'categoria': str(elemento.categoria.id) if elemento.categoria else None,
        }
        form = ElementoForm(initial=initial_data)

    return render(request, 'crear_elemento.html', {
        'form': form,
        'editando': True,
        'elemento': elemento
    })

@user_passes_test(lambda u: u.is_superuser)
def añadir_masivo_categoria(request, categoria_id):
    # Nota: Si usas MongoEngine, usa .objects(id=...).first()
    # Si usas Django ORM estándar, usa get_object_or_404
    categoria_destino = Categoria.objects(id=categoria_id).first()

    if not categoria_destino:
        messages.error(request, "La categoría no existe.")
        return redirect('lista_categorias')

    if request.method == 'POST':
        elementos_ids = request.POST.getlist('elementos_seleccionados')
        if elementos_ids:
            # Actualización para MongoEngine
            Elemento.objects(id__in=elementos_ids).update(set__categoria=categoria_destino)
            messages.success(request, f"Se han movido {len(elementos_ids)} elementos a {categoria_destino.nombre}")
        return redirect('lista_categorias')

    # Elementos que NO están en esta categoría
    elementos_disponibles = Elemento.objects(categoria__ne=categoria_destino).order_by('titulo')

    return render(request, 'admin/añadir_masivo.html', {
        'categoria': categoria_destino,
        'elementos': elementos_disponibles
    })


@user_passes_test(lambda u: u.is_superuser)
def panel_ranking(request):
    # 1. Traemos todo de la base de datos
    categorias = list(Categoria.objects.all())
    todos_los_elementos = list(Elemento.objects.all())

    for cat in categorias:
        elementos_encontrados = []
        # Obtenemos el ID real de la categoría (como un objeto ObjectId)
        id_categoria_objetivo = cat.id

        for el in todos_los_elementos:
            # 2. Extraemos el ID de la categoría del elemento de la forma más cruda posible
            # Accedemos al diccionario interno de MongoEngine (_data)
            val_cat = el._data.get('categoria')

            # Si es un objeto de referencia, sacamos su ID. Si ya es un ID, lo usamos.
            id_del_elemento = getattr(val_cat, 'id', val_cat)

            # 3. Comparación Directa
            if id_del_elemento == id_categoria_objetivo:
                elementos_encontrados.append(el)

        # 4. Ordenamos (mayor orden primero)
        elementos_encontrados.sort(key=lambda x: getattr(x, 'orden', 0) or 0, reverse=True)

        # Guardamos la lista en la categoría
        cat.elementos_ranking = elementos_encontrados

    return render(request, 'admin/panel_ranking.html', {'categorias': categorias})

@user_passes_test(lambda u: u.is_superuser)
def cambiar_ranking(request, item_id, accion):
    elemento = Elemento.objects(id=item_id).first()
    if elemento:
        if accion == 'subir':
            elemento.orden = (elemento.orden or 0) + 1
        elif accion == 'bajar':
            elemento.orden = max(0, (elemento.orden or 0) - 1)
        elemento.save()

    # Esto te devuelve al panel y refresca la lista con el nuevo orden
    return redirect('panel_ranking')


# --- AUTENTICACIÓN ---
def registro(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('home')
    return render(request, 'registro.html', {'form': form})

def login_usuario(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenido de nuevo, {user.username}")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

def logout_usuario(request):
    logout(request)
    return redirect('home')