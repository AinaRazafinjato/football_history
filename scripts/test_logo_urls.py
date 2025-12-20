import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','football_history.settings')
import django
django.setup()
from matches.serializers import _build_file_url
print('logos/leagues/Premier League.png ->', _build_file_url('logos/leagues/Premier League.png'))
print('leagues/Premier League.png ->', _build_file_url('leagues/Premier League.png'))
