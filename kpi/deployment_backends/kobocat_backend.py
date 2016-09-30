#!/usr/bin/python
# -*- coding: utf-8 -*-

import cStringIO
import logging
import re
import requests
import unicodecsv
import urlparse
import posixpath

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from pyxform.xls2json_backends import xls_to_dict
from rest_framework import exceptions, status
from rest_framework.authtoken.models import Token

from base_backend import BaseDeploymentBackend


class KobocatDeploymentException(exceptions.APIException):
    def __init__(self, *args, **kwargs):
        if 'response' in kwargs:
            self.response = kwargs.pop('response')
        return super(KobocatDeploymentException, self).__init__(
            *args, **kwargs)

    @property
    def invalid_form_id(self):
        # We recognize certain KC API responses as indications of an
        # invalid form id:
        invalid_form_id_responses = (
            'Form with this id or SMS-keyword already exists.',
            'In strict mode, the XForm ID must be a valid slug and '
                'contain no spaces.',
        )
        return self.detail in invalid_form_id_responses

class KobocatDeploymentBackend(BaseDeploymentBackend):
    '''
    Used to deploy a project into KC. Stores the project identifiers in the
    "self.asset._deployment_data" JSONField.
    '''

    @staticmethod
    def make_identifier(username, id_string):
        ''' Uses `settings.KOBOCAT_URL` to construct an identifier from a
        username and id string, without the caller having to specify a server
        or know the full format of KC identifiers '''
        # No need to use the internal URL here; it will be substituted in when
        # appropriate
        return u'{}/{}/assign/{}'.format(
            settings.KOBOCAT_URL,
            username,
            id_string
        )

    @staticmethod
    def external_to_internal_url(url):
        ''' Replace the value of `settings.KOBOCAT_URL` with that of
        `settings.KOBOCAT_INTERNAL_URL` when it appears at the beginning of
        `url` '''
        return re.sub(
            pattern=u'^{}'.format(re.escape(settings.KOBOCAT_URL)),
            repl=settings.KOBOCAT_INTERNAL_URL,
            string=url
        )

    @staticmethod
    def internal_to_external_url(url):
        ''' Replace the value of `settings.KOBOCAT_INTERNAL_URL` with that of
        `settings.KOBOCAT_URL` when it appears at the beginning of
        `url` '''
        return re.sub(
            pattern=u'^{}'.format(re.escape(settings.KOBOCAT_INTERNAL_URL)),
            repl=settings.KOBOCAT_URL,
            string=url
        )

    @property
    def backend_response(self):
        return self.asset._deployment_data['backend_response']

    def to_csv_io(self, asset_xls_io, id_string):
        ''' Convert the output of `Asset.to_xls_io()` or
        `Asset.to_versioned_xls_io()` into a CSV appropriate for KC's
        `text_xls_form` '''
        xls_dict = xls_to_dict(asset_xls_io)
        csv_io = cStringIO.StringIO()
        writer = unicodecsv.writer(
            csv_io, delimiter=',', quotechar='"',
            quoting=unicodecsv.QUOTE_MINIMAL
        )
        settings_arr = xls_dict.get('settings', [])
        if len(settings_arr) == 0:
            settings_dict = {}
        else:
            settings_dict = settings_arr[0]
        if 'form_id' in settings_dict:
            del settings_dict['form_id']
        settings_dict['id_string'] = id_string
        settings_dict['form_title'] = self.asset.name
        xls_dict['settings'] = [settings_dict]

        for sheet_name, rows in xls_dict.items():
            if re.search(r'_header$', sheet_name):
                continue

            writer.writerow([sheet_name])
            out_keys = []
            out_rows = []
            for row in rows:
                out_row = []
                for key in row.keys():
                    if key not in out_keys:
                        out_keys.append(key)
                for out_key in out_keys:
                    out_row.append(row.get(out_key, None))
                out_rows.append(out_row)
            writer.writerow([None] + out_keys)
            for out_row in out_rows:
                writer.writerow([None] + out_row)
        return csv_io

    def _kobocat_request(self, method, url, data):
        ''' Make a POST or PATCH request and return parsed JSON '''

        expected_status_codes = {
            'POST': 201,
            'PATCH': 200,
            'DELETE': 204,
        }
        try:
            expected_status_code = expected_status_codes[method]
        except KeyError:
            raise NotImplementedError(
                u'This backend does not implement the {} method'.format(method)
            )

        # Get or create the API authorization token for the asset's owner
        (token, is_new) = Token.objects.get_or_create(user=self.asset.owner)
        headers = {u'Authorization':'Token ' + token.key}

        # Make the request to KC
        try:
            response = requests.request(
                method, url, headers=headers, data=data)
        except requests.exceptions.RequestException as e:
            # Failed to access the KC API
            # TODO: clarify that the user cannot correct this
            raise KobocatDeploymentException(detail=unicode(e))

        # If it's a no-content success, return immediately
        if response.status_code == expected_status_code == 204:
            return {}

        # Parse the response
        try:
            json_response = response.json()
        except ValueError as e:
            # Unparseable KC API output
            # TODO: clarify that the user cannot correct this
            raise KobocatDeploymentException(
                detail=unicode(e), response=response)

        # Check for failure
        if response.status_code != expected_status_code or (
            'type' in json_response and json_response['type'] == 'alert-error'
        ) or 'formid' not in json_response:
            if 'text' in json_response:
                # KC API refused us for a specified reason, likely invalid
                # input Raise a 400 error that includes the reason
                e = KobocatDeploymentException(detail=json_response['text'])
                e.status_code = status.HTTP_400_BAD_REQUEST
                raise e
            else:
                # Unspecified failure; raise 500
                raise KobocatDeploymentException(
                    detail='Unexpected KoBoCAT error {}: {}'.format(
                        response.status_code, response.content),
                    response=response
                )

        return json_response


    @property
    def timestamp(self):
        try:
            return self.backend_response['date_modified']
        except KeyError:
            return None

    def connect(self, identifier=None, active=False):
        '''
        POST initial survey content to kobocat and create a new project.
        store results in self.asset._deployment_data.
        '''
        # If no identifier was provided, construct one using
        # `settings.KOBOCAT_URL` and the uid of the asset
        if not identifier:
            # Use the external URL here; the internal URL will be substituted
            # in when appropriate
            if not settings.KOBOCAT_URL or not settings.KOBOCAT_INTERNAL_URL:
                raise ImproperlyConfigured(
                    'Both KOBOCAT_URL and KOBOCAT_INTERNAL_URL must be '
                    'configured before using KobocatDeploymentBackend'
                )
            server = settings.KOBOCAT_URL
            username = self.asset.owner.username
            id_string = self.asset.uid
            identifier = '{server}/{username}/forms/{id_string}'.format(
                server=server,
                username=username,
                id_string=id_string,
            )
        else:
            # Parse the provided identifier, which is expected to follow the
            # format http://kobocat_server/username/forms/id_string
            parsed_identifier = urlparse.urlparse(identifier)
            server = u'{}://{}'.format(
                parsed_identifier.scheme, parsed_identifier.netloc)
            path_head, path_tail = posixpath.split(parsed_identifier.path)
            id_string = path_tail
            path_head, path_tail = posixpath.split(path_head)
            if path_tail != 'forms':
                raise Exception('The identifier is not properly formatted.')
            path_head, path_tail = posixpath.split(path_head)
            if path_tail != self.asset.owner.username:
                raise Exception(
                    'The username in the identifier does not match the owner '
                    'of this asset.'
                )
            if path_head != '/':
                raise Exception('The identifier is not properly formatted.')

        url = self.external_to_internal_url(u'{}/api/v1/forms'.format(server))
        csv_io = self.to_csv_io(self.asset.to_versioned_xls_io(), id_string)
        valid_xlsform_csv_repr = csv_io.getvalue()
        payload = {
            u'text_xls_form': valid_xlsform_csv_repr,
            u'downloadable': active
        }
        json_response = self._kobocat_request('POST', url, payload)
        self.store_data({
            'backend': 'kobocat',
            'identifier': self.internal_to_external_url(identifier),
            'active': json_response['downloadable'],
            'backend_response': json_response,
            'version': self.asset.version_id,
        })

    def redeploy(self, active=None):
        '''
        Replace (overwrite) the deployment, keeping the same identifier, and
        optionally changing whether the deployment is active
        '''
        if active is None:
            active = self.active
        url = self.external_to_internal_url(self.backend_response['url'])
        id_string = self.backend_response['id_string']
        csv_io = self.to_csv_io(self.asset.to_versioned_xls_io(), id_string)
        valid_xlsform_csv_repr = csv_io.getvalue()
        payload = {
            u'text_xls_form': valid_xlsform_csv_repr,
            u'downloadable': active
        }
        try:
            json_response = self._kobocat_request('PATCH', url, payload)
            self.store_data({
                'active': json_response['downloadable'],
                'backend_response': json_response,
                'version': self.asset.version_id,
            })
        except KobocatDeploymentException as e:
            if e.response.status_code == 404:
                # Whoops, the KC project we thought we were going to overwrite
                # is gone! Try a standard deployment instead
                return self.connect(self.identifier, active)
            raise

    def set_active(self, active):
        '''
        PATCH active boolean of survey.
        store results in self.asset._deployment_data
        '''
        # self.store_data is an alias for
        # self.asset._deployment_data.update(...)
        # self.asset.save()
        url = self.external_to_internal_url(
            self.backend_response['url'])
        payload = {
            u'downloadable': bool(active)
        }
        json_response = self._kobocat_request('PATCH', url, payload)
        assert(json_response['downloadable'] == bool(active))
        self.store_data({
            'active': json_response['downloadable'],
            'backend_response': json_response,
        })

    def delete(self):
        url = self.external_to_internal_url(
            self.backend_response['url'])
        self._kobocat_request('DELETE', url, None)
        self.asset._deployment_data = {}
        self.asset.save()

    def get_enketo_survey_links(self):
        data = {
            'server_url': u'{}/{}'.format(
                settings.KOBOCAT_URL.rstrip('/'),
                self.asset.owner.username
            ),
            'form_id': self.backend_response['id_string']
        }
        try:
            response = requests.post(
                u'{}/{}'.format(
                    settings.ENKETO_SERVER, settings.ENKETO_SURVEY_ENDPOINT),
                # bare tuple implies basic auth
                auth=(settings.ENKETO_API_TOKEN, ''),
                data=data
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            # Don't 500 the entire asset view if Enketo is unreachable
            logging.error(
                'Failed to retrieve links from Enketo', exc_info=True)
            return {}
        try:
            links = response.json()
        except ValueError:
            logging.error('Received invalid JSON from Enketo', exc_info=True)
            return {}
        for discard in ('enketo_id', 'code', 'preview_iframe_url'):
            try: del links[discard]
            except KeyError: pass
        return links
