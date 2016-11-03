from django.utils.translation import ugettext_lazy as _
USERNAME_REGEX = r'^[a-z][a-z0-9_]+$'
USERNAME_MAX_LENGTH = 30
USERNAME_INVALID_MESSAGE = _(
    'A username may only contain lowercase letters, numbers, and '
    'underscores (_).'
)
