from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .forms import UserRegisterForm, UserUpdateForm
from django.shortcuts import render,redirect
from django.contrib.auth import login,authenticate
from django.contrib.auth.decorators import login_required
from movies.models import Movie , Booking
from django.utils import timezone

def home(request):
    movies = Movie.objects.all()
    return render(request,'home.html',{'movies':movies})
def register(request):
    if request.method == 'POST':
        form=UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data.get('username')
            password=form.cleaned_data.get('password1')
            user=authenticate(username=username,password=password)
            login(request,user)
            return redirect('profile')
    else:
        form=UserRegisterForm()
    return render(request,'users/register.html',{'form':form})

def login_view(request):
    if request.method == 'POST':
        form=AuthenticationForm(request,data=request.POST)
        if form.is_valid():
            user=form.get_user()
            login(request,user)
            return redirect('/')
    else:
        form=AuthenticationForm()
    return render(request,'users/login.html',{'form':form})

@login_required
def profile(request):
    # Get all bookings for the user, order by booking date descending
    all_bookings = Booking.objects.filter(user=request.user).select_related('movie', 'theater', 'seat').order_by('-booked_at')
    now = timezone.now()
    # Upcoming: theater time is in the future
    upcoming_bookings = all_bookings.filter(theater__time__gte=now)
    # Past: theater time is in the past
    past_bookings = all_bookings.filter(theater__time__lt=now)

    # Recommendation logic
    booked_movie_ids = all_bookings.values_list('movie_id', flat=True)
    booked_movies = Movie.objects.filter(id__in=booked_movie_ids)
    # Get cast keywords from user's booked movies
    cast_keywords = []
    for movie in booked_movies:
        cast_keywords.extend([c.strip() for c in movie.cast.split(',')])
    # Recommend movies with similar cast or not yet booked
    if cast_keywords:
        recommended_movies = Movie.objects.exclude(id__in=booked_movie_ids).filter(
            cast__icontains=cast_keywords[0]
        )[:4]
        # If not enough, fill with other movies not yet booked
        if recommended_movies.count() < 4:
            extra_movies = Movie.objects.exclude(id__in=booked_movie_ids).exclude(id__in=recommended_movies.values_list('id', flat=True))[:4-recommended_movies.count()]
            recommended_movies = list(recommended_movies) + list(extra_movies)
    else:
        # If no history, recommend top-rated or recent movies
        recommended_movies = Movie.objects.all().order_by('-rating')[:4]

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)

    return render(
        request,
        'users/profile.html',
        {
            'u_form': u_form,
            'bookings': all_bookings,  # for backward compatibility
            'upcoming_bookings': upcoming_bookings,
            'past_bookings': past_bookings,
            'recommended_movies': recommended_movies,
        }
    )

@login_required
def reset_password(request):
    if request.method == 'POST':
        form=PasswordChangeForm(user=request.user,data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form=PasswordChangeForm(user=request.user)
    return render(request,'users/reset_password.html',{'form':form})