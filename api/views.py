from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from .forms import PostForm, RegisterForm, UserProfileForm
from .models import Post, UserProfile


def posts(request):
    response = {}
    posts = Post.objects.filter().order_by('-datetime')
    n = 1
    for post in posts:
        response[str(n)] = {
            'datetime': post.datetime,
            'title': post.title,
            'content': post.content,
            'author': f"{post.user.first_name} {post.user.last_name}",
            'hash': post.hash,
            'txId': post.txId
        }
        n += 1
    return JsonResponse(response)


# La seguente funzione permette sia di scrivere un post tramite un form specifico, pubblicarlo sul blog e certificare
# la sua esistenza caricandolo sulla blockchain di Ropsten (ottenendo l'hash e l'ID della transazione), sia di vedere
# tutti i post degli utenti in ordine cronologico
CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


@csrf_exempt
@cache_page(CACHE_TTL)
@login_required()
def post_list(request):
    posts = Post.objects.filter().order_by('-datetime')
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.datetime = datetime.now()
            post.writeOnChain()
            post.save()
            cache.clear()
            form = PostForm()
        return redirect('/posts/list', {'posts': posts, 'form': form})
    else:
        form = PostForm()
        return render(request, 'api/post_list.html', {'posts': posts, 'form': form})


# La seguente funzione permette di determinare l'IP degli utenti che accedono alla piattaforma
def getIp(request):
    try:
        x_forward = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forward:
            ip = x_forward.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
    except:
        ip = ""
    return ip


# La seguente funzione permette la gestione del form utilizzato per la registrazione
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        profileForm = UserProfileForm(request.POST)
        if form.is_valid() and profileForm.is_valid():
            user = form.save()
            profile = profileForm.save(commit=False)
            profile.user = user
            profile.save()
            return redirect("home")
    else:
        form = RegisterForm()
        profileForm = UserProfileForm(initial={'ipAddress': getIp(request)})
    return render(request, "registration/register.html", {"form": form, "profileForm": profileForm})


# La seguente funzione gestisce il login nella piattaforma
def handle_login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            # Aggiorna IP
            try:
                ip = UserProfile.objects.get(user=user)
                ip.value = getIp(request)
                ip.save()
            except:
                print("Superuser")
            if user is not None:
                login(request, user)
                messages.success(request, "Accesso effettuato correttamente")
                return redirect('/')
            else:
                return render(request, "registration/login.html", {"form": form})
        else:
            return render(request, "registration/login.html", {"form": form})
    form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})


# La seguente funzione gestisce il logout dalla piattaforma
def handle_logout(request):
    logout(request)
    messages.info(request, "Logout effettuato correttamente")
    return redirect("/")


# La seguente funziona aiuta a gestire l'home page del sito. Compara gli Ip di un utente che accede alla piattaforma
# mostrando un avvertimento quando questo è diverso dal precedente
def home(request):
    if request.user.is_authenticated:
        if not request.user.is_superuser:
            lastIp = request.user.userprofile.ipAddress
        else:
            lastIp = ""
        currentIp = getIp(request)
        if currentIp == lastIp:
            ipStat = "Account sicuro!"
        else:
            ipStat = "Attenzione! IP diverso dal solito!"
    else:
        ipStat = getIp(request)
    return render(request, "api/home.html", {"ipStat": ipStat})


# La seguente funzione permette agli amministratori di vedere il numero dei posts pubblicati da ciascun utente
def statistics(response):
    userPosts = User.objects.annotate(total_posts=Count('post'))
    return render(response, 'api/statistics.html', {'userPosts': userPosts})


# La seguente funzione permette la visione della pagina /utente/ID/ dove ID è un numero intero positivo (1, 2, 3, ecc..)
# che rappresenta l'ID di ciascun utente. La pagina mostra info sull'utente in questione e i suoi posts
def user_page(request, pk):
    user = get_object_or_404(User, pk=pk)
    user_posts = Post.objects.filter(user=user)
    user_posts_number = Post.objects.filter(user=user).count()
    return render(request, 'api/user_page.html', {'user': user, "user_posts": user_posts,
                                                  "user_posts_number": user_posts_number})


# La seguente funzione restituisce una risposta in JSON contenente le informazioni su tutti i posts pubblicati
# nell'ultima ora
def last_hour_posts(request):
    response = {}
    this_hour = datetime.now()
    one_hour_before = this_hour - timedelta(hours=1)
    posts = Post.objects.filter(datetime__range=(one_hour_before, this_hour))
    n = 1
    for post in posts:
        response[str(n)] = {
            'datetime': post.datetime,
            'title': post.title,
            'content': post.content,
            'author': f"{post.user.first_name} {post.user.last_name}",
            'hash': post.hash,
            'txId': post.txId
        }
        n += 1
    return JsonResponse(response)


# La seguente funziona stabilisce l'endpoint /stringCount?string=<GET> che ritorna il numero di volte in cui la stringa
# "<GET>" è apparsa nei post pubblicati, controllando sia nei titoli che nei contenuti di tutti i posts
def stringCount(request):
    r = request.GET.get('string')
    posts = Post.objects.filter().order_by('-datetime')
    totalOccurence = 0
    for post in posts:
        cont = post.content
        tit = post.title
        occurence = cont.count(r) + tit.count(r)
        totalOccurence += occurence
    if totalOccurence == 1:
        return HttpResponse(f'La stringa "{r}" è apparsa {totalOccurence} volta nei post pubblicati.')
    else:
        return HttpResponse(f'La stringa "{r}" è apparsa {totalOccurence} volte nei post pubblicati.')
