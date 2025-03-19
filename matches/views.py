from datetime import timedelta
from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Match

def home(request):
    # Récupération de tous les matches triés par date décroissante
    all_matches = Match.objects.all().order_by('-match_date')
    
    # Calcul des semaines
    weeks_dict = {}
    for match in all_matches:
        # Trouver le lundi de la semaine du match
        week_start = match.match_date - timedelta(days=match.match_date.weekday())
        
        if week_start not in weeks_dict:
            weeks_dict[week_start] = []
        weeks_dict[week_start].append(match)
    
    # Tri des semaines par date décroissante
    weeks = sorted(weeks_dict.items(), key=lambda x: x[0], reverse=True)
    
    # Pagination (1 semaine par page)
    paginator = Paginator(weeks, 1)
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)
    
    # Formatage des données pour le template
    current_week = None
    if page_obj.object_list:
        week_start, matches = page_obj.object_list[0]
        week_end = week_start + timedelta(days=6)
        current_week = {
            'start': week_start,
            'end': week_end,
            'matches': sorted(matches, key=lambda m: m.match_date, reverse=True)
        }
    
    context = {
        'current_week': current_week,
        'page_obj': page_obj,
        'page_title': 'Matches par semaine'
    }
    
    return render(request, 'home.html', context)