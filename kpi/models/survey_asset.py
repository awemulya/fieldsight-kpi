from django.db import models
from django.db import transaction
from shortuuid import ShortUUID
from jsonfield import JSONField
import reversion
import json
import copy


SURVEY_ASSET_TYPES = [
    ('text', 'text'),
    ('survey_block', 'survey_block'),
    ('choice_list', 'choice list'),
]

@reversion.register
class SurveyAsset(models.Model):
    name = models.CharField(max_length=100, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    content = JSONField(null=True)
    additional_sheets = JSONField(null=True)
    settings = JSONField(null=True)
    asset_type = models.CharField(choices=SURVEY_ASSET_TYPES, max_length=20, default='text')
    collection = models.ForeignKey('Collection', related_name='survey_assets', null=True)
    owner = models.ForeignKey('auth.User', related_name='survey_assets', null=True)
    uid = models.CharField(max_length=8, default='')

    class Meta:
        ordering = ('created',)

    def versions(self):
        return reversion.get_for_object(self)
    def versioned_data(self):
        return [v.field_dict for v in self.versions()]

    def to_ss_structure(self, content_tag='survey', strip_kuids=False):
        obj = {}
        rows = []
        for row in self.content:
            _r = copy.copy(row)
            if strip_kuids and 'kuid' in _r:
                del _r['kuid']
            rows.append(_r)
        obj[content_tag] = rows
        return obj

    def _populate_uid(self):
        if self.uid == '':
            self.uid = self._generate_uid()

    def _generate_uid(self):
        return ShortUUID().random(8)

    def save(self, *args, **kwargs):
        # populate uid field if it's empty
        self._populate_uid()
        with transaction.atomic(), reversion.create_revision():
            super(SurveyAsset, self).save(*args, **kwargs)