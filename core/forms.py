from django import forms
from .models import Elemento, Categoria

# --- FORMULARIO DE VALORACIÓN ---
class ValoracionForm(forms.Form):
    PUNTUACIONES = (
        (1, '★☆☆☆☆ (Mala)'),
        (2, '★★☆☆☆ (Regular)'),
        (3, '★★★☆☆ (Buena)'),
        (4, '★★★★☆ (Muy buena)'),
        (5, '★★★★★ (Excelente)'),
    )

    puntuacion = forms.ChoiceField(
        choices=PUNTUACIONES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Tu puntuación"
    )

    comentario = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Escribe tu opinión aquí (opcional)...'
        }),
        label="Comentario"
    )

# --- FORMULARIO DE ELEMENTO (PELÍCULA/SERIE) ---
class ElementoForm(forms.Form):
    TIPO_CHOICES = (
        ('P', 'Película'),
        ('S', 'Serie'),
    )

    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Tipo"
    )

    titulo = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Breaking Bad'}),
        label="Título"
    )

    # --- NUEVOS CAMPOS ---
    director = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Christopher Nolan'}),
        label="Director"
    )

    reparto = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Ej: Bryan Cranston, Aaron Paul...'
        }),
        label="Reparto Principal"
    )
    # ----------------------

    imagen_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://imagen.com/poster.jpg'}),
        label="URL del Póster"
    )

    descripcion = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        label="Sinopsis"
    )

    anio = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 2008'}),
        label="Año de lanzamiento"
    )

    categoria = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Categoría"
    )

    orden = forms.IntegerField(
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Posición en Ranking"
    )

    def __init__(self, *args, **kwargs):
        # Capturamos la instancia para evitar el TypeError en edición
        self.instance = kwargs.pop('instance', None)
        super(ElementoForm, self).__init__(*args, **kwargs)

        # Carga dinámica de categorías
        categorias = Categoria.objects.all()
        choices = [(str(c.id), c.nombre) for c in categorias]
        self.fields['categoria'].choices = choices

    def save(self):
        cat_id = self.cleaned_data['categoria']
        categoria_obj = Categoria.objects.get(id=cat_id)

        # Si editamos usamos la instancia, si no, creamos uno nuevo
        elemento = self.instance if self.instance else Elemento()

        elemento.tipo = self.cleaned_data['tipo']
        elemento.titulo = self.cleaned_data['titulo']
        elemento.director = self.cleaned_data['director']
        elemento.reparto = self.cleaned_data['reparto']
        elemento.imagen_url = self.cleaned_data['imagen_url']
        elemento.descripcion = self.cleaned_data['descripcion']
        elemento.anio = self.cleaned_data['anio']
        elemento.categoria = categoria_obj
        elemento.orden = self.cleaned_data['orden']

        elemento.save()
        return elemento