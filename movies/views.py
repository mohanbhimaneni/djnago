from django.shortcuts import render, redirect ,get_object_or_404
from .models import Movie,Theater,Seat,Booking
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def movie_list(request):
    search_query = request.GET.get('search', '')
    movies = Movie.objects.all().order_by('name')
    if search_query:
        movies = movies.filter(name__icontains=search_query)
    movies_per_page = 3
    paginator = Paginator(movies, movies_per_page)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)
    context = {
        'movies': page_obj,
        'page_obj': page_obj,
        'is_paginated': True,
        'search_query': search_query,
    }
    return render(request, 'movies/movie_list.html', context)

def theater_list(request,movie_id):
    movie = get_object_or_404(Movie,id=movie_id)
    theater=Theater.objects.filter(movie=movie)
    return render(request,'movies/theater_list.html',{'movie':movie,'theaters':theater})



@login_required(login_url='/login/')
def book_seats(request,theater_id):
    theaters=get_object_or_404(Theater,id=theater_id)
    seats=Seat.objects.filter(theater=theaters)
    # Set dynamic price for each seat before rendering
    dynamic_price = theaters.get_dynamic_price()
    for seat in seats:
        seat.price = dynamic_price
    if request.method=='POST':
        selected_Seats= request.POST.getlist('seats')
        error_seats=[]
        if not selected_Seats:
            return render(request,"movies/seat_selection.html",{'theater':theaters,"seats":seats,'error':"No seat selected", 'dynamic_price': dynamic_price})
        for seat_id in selected_Seats:
            seat=get_object_or_404(Seat,id=seat_id,theater=theaters)
            if seat.is_booked:
                error_seats.append(seat.seat_number)
                continue
            try:
                Booking.objects.create(
                    user=request.user,
                    seat=seat,
                    movie=theaters.movie,
                    theater=theaters,
                    price=seat.get_price()
                )
                seat.is_booked=True
                seat.price=seat.get_price()
                seat.save()
            except IntegrityError:
                error_seats.append(seat.seat_number)
        if error_seats:
            error_message=f"The following seats are already booked:{''.join(error_seats)}"
            return render(request,'movies/seat_selection.html',{'theater':theaters,"seats":seats,'error':"No seat selected", 'dynamic_price': dynamic_price})
        return redirect('profile')
    return render(request,'movies/seat_selection.html',{'theaters':theaters,"seats":seats, 'dynamic_price': dynamic_price})




