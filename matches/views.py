from datetime import timedelta, date
from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Match

def home(request):
    # Récupération de tous les matches triés par date croissante
    all_matches = Match.objects.all().order_by('match_date')
    
    # Calcul des semaines
    weeks_dict = {}
    for match in all_matches:
        # Trouver le lundi de la semaine du match
        week_start = match.match_date - timedelta(days=match.match_date.weekday())
        
        if week_start not in weeks_dict:
            weeks_dict[week_start] = []
        weeks_dict[week_start].append(match)
    
    # Tri des semaines par date croissante
    weeks = sorted(weeks_dict.items(), key=lambda x: x[0])

    # Pagination (1 semaine par page)
    paginator = Paginator(weeks, 1)
    
    # Trouver la semaine correspondant à aujourd'hui
    today = date.today()
    today_week_start = today - timedelta(days=today.weekday())
    page_number = 1  # Par défaut, aller à la première page

    # Chercher l'index de la semaine en cours
    for i, (week_start, _) in enumerate(weeks):
        if week_start == today_week_start:
            page_number = i + 1  # Les pages commencent à 1 dans Django
    
    # Récupérer la page demandée ou celle de la semaine actuelle
    requested_page = request.GET.get('page', page_number)
    
    try:
        page_obj = paginator.page(requested_page)
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
            'matches': sorted(matches, key=lambda m: m.match_date)
        }
    
    context = {
        'current_week': current_week,
        'page_obj': page_obj,
        'page_title': 'Matches par semaine'
    }
    
    return render(request, 'home.html', context)
