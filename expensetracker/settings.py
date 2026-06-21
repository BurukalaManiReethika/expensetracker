# Add at the bottom of settings.py

INSTALLED_APPS += ['django_celery_beat']

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'

# Email settings (using Gmail SMTP as example — use env vars in production!)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'       # use env variable in real project
EMAIL_HOST_PASSWORD = 'your-app-password'       # use env variable in real project
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
# expensetracker/settings.py — add at the bottom

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
