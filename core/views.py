from django.shortcuts import render, redirect

def home(request):
    if request.user.is_authenticated:
        return redirect('/foro/')
    return render(request, 'core/home.html')

def buscar(request):
    query = request.GET.get('q', '').strip()
    resultados_posts = []
    resultados_personajes = []
    resultados_guias = []

    if query:
        from foro.models import Post
        from personajes.models import Personaje
        from guias.models import Guia

        resultados_posts = Post.objects.filter(
            titulo__icontains=query
        ).order_by('-fecha')[:10]

        resultados_personajes = Personaje.objects.filter(
            nombre__icontains=query
        )[:10]

        resultados_guias = Guia.objects.filter(
            titulo__icontains=query
        ).order_by('-fecha')[:10]

    total = len(resultados_posts) + len(resultados_personajes) + len(resultados_guias)

    return render(request, 'core/buscar.html', {
        'query': query,
        'resultados_posts': resultados_posts,
        'resultados_personajes': resultados_personajes,
        'resultados_guias': resultados_guias,
        'total': total,
    })