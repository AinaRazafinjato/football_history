from datetime import timedelta, date
from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Sum, Count, F, Case, When, IntegerField
from django.http import JsonResponse
from .models import Match, Team, League, Season

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

def search_matches(request):
    # Get search parameters
    query = request.GET.get('q', '')
    year = request.GET.get('year', '')
    team = request.GET.get('team', '')
    league = request.GET.get('league', '')
    
    # Start with all matches
    matches = Match.objects.select_related(
        'team_home', 'team_away', 'day__league_season__league', 'day__league_season__season'
    ).all()
    
    # Apply keyword search
    if query:
        matches = matches.filter(
            Q(team_home__team_name__icontains=query) |
            Q(team_away__team_name__icontains=query) |
            Q(day__league_season__league__league_name__icontains=query)
        )
    
    # Apply year filter
    if year:
        matches = matches.filter(match_date__year=year)
    
    # Apply team filter
    if team:
        matches = matches.filter(
            Q(team_home__id=team) | Q(team_away__id=team)
        )
    
    # Apply league filter
    if league:
        matches = matches.filter(day__league_season__league__id=league)
    
    # Order results by date
    matches = matches.order_by('-match_date', 'time')
    
    # Pagination
    paginator = Paginator(matches, 20)  # 20 matches per page
    page = request.GET.get('page')
    try:
        matches_page = paginator.page(page)
    except PageNotAnInteger:
        matches_page = paginator.page(1)
    except EmptyPage:
        matches_page = paginator.page(paginator.num_pages)
    
    # Get filter options for the search form
    years = Match.objects.dates('match_date', 'year').values_list('match_date__year', flat=True).distinct().order_by('-match_date__year')
    teams = Team.objects.all().order_by('team_name')
    leagues = League.objects.all().order_by('league_name')
    
    context = {
        'page_title': 'Search Results',
        'matches': matches_page,
        'query': query,
        'selected_year': year,
        'selected_team': team,
        'selected_league': league,
        'years': years,
        'teams': teams,
        'leagues': leagues,
        'total_results': paginator.count,
    }
    
    return render(request, 'search_results.html', context)


def statistics(request):
    """
    Statistics dashboard view with interactive charts and filters
    """
    # Get filter parameters
    league_id = request.GET.get('league', '')
    season_id = request.GET.get('season', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base queryset
    matches = Match.objects.select_related(
        'team_home', 'team_away', 'day__league_season__league', 'day__league_season__season'
    ).all()
    
    # Apply filters
    if league_id:
        matches = matches.filter(day__league_season__league__id=league_id)
    if season_id:
        matches = matches.filter(day__league_season__season__id=season_id)
    if date_from:
        matches = matches.filter(match_date__gte=date_from)
    if date_to:
        matches = matches.filter(match_date__lte=date_to)
    
    # Only include matches with results
    matches = matches.filter(score_home__isnull=False, score_away__isnull=False)
    
    # Calculate team statistics
    team_stats = {}
    
    # Get all teams that played in filtered matches
    teams = set()
    for match in matches:
        teams.add(match.team_home)
        teams.add(match.team_away)
    
    for team in teams:
        # Home matches
        home_matches = matches.filter(team_home=team)
        home_goals = home_matches.aggregate(total=Sum('score_home'))['total'] or 0
        home_wins = home_matches.filter(score_home__gt=F('score_away')).count()
        home_draws = home_matches.filter(score_home=F('score_away')).count()
        home_losses = home_matches.filter(score_home__lt=F('score_away')).count()
        
        # Away matches
        away_matches = matches.filter(team_away=team)
        away_goals = away_matches.aggregate(total=Sum('score_away'))['total'] or 0
        away_wins = away_matches.filter(score_away__gt=F('score_home')).count()
        away_draws = away_matches.filter(score_away=F('score_home')).count()
        away_losses = away_matches.filter(score_away__lt=F('score_home')).count()
        
        # Combined statistics
        team_stats[team.team_name] = {
            'team': team,
            'matches_played': home_matches.count() + away_matches.count(),
            'goals_scored': home_goals + away_goals,
            'wins': home_wins + away_wins,
            'draws': home_draws + away_draws,
            'losses': home_losses + away_losses,
            'points': (home_wins + away_wins) * 3 + (home_draws + away_draws)
        }
    
    # Sort teams by points
    sorted_teams = sorted(team_stats.items(), key=lambda x: x[1]['points'], reverse=True)
    
    # League statistics
    league_stats = {}
    for match in matches:
        league_name = match.day.league_season.league.league_name
        if league_name not in league_stats:
            league_stats[league_name] = {
                'matches': 0,
                'goals': 0,
                'avg_goals_per_match': 0
            }
        league_stats[league_name]['matches'] += 1
        league_stats[league_name]['goals'] += match.score_home + match.score_away
    
    # Calculate averages
    for league_name, stats in league_stats.items():
        if stats['matches'] > 0:
            stats['avg_goals_per_match'] = round(stats['goals'] / stats['matches'], 2)
    
    # Monthly goal trends
    monthly_goals = {}
    for match in matches:
        month_key = match.match_date.strftime('%Y-%m')
        if month_key not in monthly_goals:
            monthly_goals[month_key] = 0
        monthly_goals[month_key] += match.score_home + match.score_away
    
    # Sort monthly data
    sorted_monthly = sorted(monthly_goals.items())
    
    # Get filter options
    leagues = League.objects.all().order_by('league_name')
    seasons = Season.objects.all().order_by('-start_date')
    
    context = {
        'page_title': 'Statistics Dashboard',
        'team_stats': sorted_teams,
        'league_stats': league_stats,
        'monthly_goals': sorted_monthly,
        'leagues': leagues,
        'seasons': seasons,
        'selected_league': league_id,
        'selected_season': season_id,
        'selected_date_from': date_from,
        'selected_date_to': date_to,
        'total_matches': matches.count(),
        'total_goals': matches.aggregate(total=Sum('score_home') + Sum('score_away'))['total'] or 0,
    }
    
    return render(request, 'statistics.html', context)


def statistics_api(request):
    """
    API endpoint for chart data
    """
    # Get filter parameters
    league_id = request.GET.get('league', '')
    season_id = request.GET.get('season', '')
    
    # Base queryset
    matches = Match.objects.select_related(
        'team_home', 'team_away', 'day__league_season__league', 'day__league_season__season'
    ).filter(score_home__isnull=False, score_away__isnull=False)
    
    # Apply filters
    if league_id:
        matches = matches.filter(day__league_season__league__id=league_id)
    if season_id:
        matches = matches.filter(day__league_season__season__id=season_id)
    
    # Team goals data for chart
    team_goals = {}
    teams = set()
    
    for match in matches:
        teams.add(match.team_home)
        teams.add(match.team_away)
    
    for team in teams:
        home_goals = matches.filter(team_home=team).aggregate(total=Sum('score_home'))['total'] or 0
        away_goals = matches.filter(team_away=team).aggregate(total=Sum('score_away'))['total'] or 0
        team_goals[team.team_name] = home_goals + away_goals
    
    # Sort by goals
    sorted_team_goals = sorted(team_goals.items(), key=lambda x: x[1], reverse=True)
    
    # Monthly goals for line chart
    monthly_goals = {}
    for match in matches:
        month_key = match.match_date.strftime('%Y-%m')
        if month_key not in monthly_goals:
            monthly_goals[month_key] = 0
        monthly_goals[month_key] += match.score_home + match.score_away
    
    return JsonResponse({
        'team_goals': sorted_team_goals,
        'monthly_goals': sorted(monthly_goals.items())
    })