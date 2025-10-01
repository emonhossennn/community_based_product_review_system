import os
import sys
from django.core.wsgi import get_wsgi_application

# Add the parent directory to sys.path so Django can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# Get the WSGI application
application = get_wsgi_application()
