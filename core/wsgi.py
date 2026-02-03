import os
import sys

# المسار الصحيح لمشروعك بناءً على رابط حسابك
path = '/home/evestreviews/evest_project' 
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()