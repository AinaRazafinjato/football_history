from datetime import timedelta, date
from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Match

def home_v1(request):
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
    
    return render(request, 'home_v1.html', context)

def home_v2(request):
    # Déterminer la date du jour et le début de la semaine courante (lundi)
    today = date.today()
    current_week_start = today - timedelta(days=today.weekday())
    current_week_end = current_week_start + timedelta(days=6)
    
    # 1. Récupération des matchs de la semaine actuelle
    current_week_matches = Match.objects.filter(
        match_date__gte=current_week_start,
        match_date__lte=current_week_end
    ).order_by('match_date', 'time')
    
    # 2. Récupération des matchs futurs (après la semaine courante)
    future_matches = Match.objects.filter(
        match_date__gt=current_week_end
    ).order_by('match_date', 'time')
    
    # 3. Récupération des matchs passés (avant la semaine courante)
    # Maintenant en ordre chronologique (les plus anciens d'abord)
    past_matches = Match.objects.filter(
        match_date__lt=current_week_start
    ).order_by('match_date', 'time')
    
    # Combinaison des résultats dans l'ordre chronologique: passés → semaine actuelle → futurs
    matches = list(past_matches) + list(current_week_matches) + list(future_matches)
    
    # Récupération d'une ligue (pour l'en-tête)
    league = None
    if current_week_matches.exists():
        # Privilégier un match de la semaine courante pour la ligue affichée
        league = current_week_matches.first().day.league_season.league
    elif matches:
        # Si pas de match cette semaine, prendre le premier match disponible
        league = matches[0].day.league_season.league
    
    context = {
        'page_title': 'Home_v2',
        'matches': matches,
        'league': league,
        'current_week_start': current_week_start,
        'current_week_end': current_week_end
    }
    
    return render(request, 'home_v2.html', context)