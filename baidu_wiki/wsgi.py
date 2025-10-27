"""
WSGI config for baidu_wiki project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baidu_wiki.settings')

application = get_wsgi_application()