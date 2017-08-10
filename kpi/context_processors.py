from django.conf import settings
from hub.models import SitewideMessage


def external_service_tokens(request):
    out = {}
    if settings.TRACKJS_TOKEN:
        out['trackjs_token'] = settings.TRACKJS_TOKEN
    if settings.GOOGLE_ANALYTICS_TOKEN:
        out['google_analytics_token'] = settings.GOOGLE_ANALYTICS_TOKEN
    return out

def email(request):
    out = {}
    # 'kpi_protocol' used in the activation_email.txt template
    out['kpi_protocol'] = request.META.get('wsgi.url_scheme', 'http')
    return out

def git_commit(request):
    return {
        'git_commit': settings.CACHEBUSTER_UNIQUE_STRING,
    }


def sitewide_messages(request):
    '''
    required in the context for any pages that need to display
    custom text in django templates
    '''
    if request.path_info.endswith("accounts/register/"):
        try:
            return {
                'welcome_message': SitewideMessage.objects.get(
                    slug='welcome_message').body
            }
        except SitewideMessage.DoesNotExist as e:
            return {}
    return {}


def auth_password_reset_url(request):
    return { 'auth_password_reset': settings.FORGOT_PASSWORD_URL }