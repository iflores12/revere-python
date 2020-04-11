import json
import sys

import requests

from errors import RateLimitException, RevereException
from models import List


class API(object):
    """Revere API. Providing a python interface to Revere tools

    Arguments:
        object {[type]} -- [description]
    """

    def __init__(self,
                 mobile_url='https://mobile.reverehq.com',
                 call_url='https://calling.reverehq.com',
                 sync_url='https://sync.revmsg.net',
                 api_key=None,
                 sync_key=None,
                 bearer_token=None,
                 api_version='v1',
                 retry_count=0,
                 retry_delay=3,
                 timeout=60,
                 wait_on_rate_limit=True,
                ):

        self.mobile_url = mobile_url
        self.call_url = call_url
        self.sync_url = sync_url
        self.api_key = api_key
        self.sync_key = sync_key
        self.bearer_token = bearer_token
        self.api_version = api_version
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.wait_on_rate_limit = wait_on_rate_limit

        if api_key is None and sync_key is None:
            raise RevereException("You have not supplied an API key. Must have one to make calls against the Revere API")

        if sync_key:
            self.bearer_token = self._sync_authenticate(sync_key)


    def get_list(self, list_id=None):
        """
        Return all lists if you don't pass in a list_id, by page, available to the given group. Otherwise you
        can search for a specific list by passing in a list_id.
        """

        url= f'{self.mobile_url}/api/{self.api_version}/list/'
        if list_id:
            response = self._request(url, 'GET', self.api_key, list_id)
        else:
            response = self._request(url, 'GET', self.api_key)

        content = self._parse(response.content.decode('utf-8'))

        return [List.from_json(l) for l in content]


    def list_people(self, page_num=None):
        """Returns a list of people in Revere"""
        url = "https://sync.revmsg.net/v2/api/people"
        if page_num:
            response = self._request(url, 'GET', self.bearer_token, page_num)
        else:
            response = self._request(url, 'GET', self.bearer_token)

        content = self._parse(response.content.decode('utf-8'))
        print(content)


    def get_person(self, revere_id):
        """Using a revere id we can return back a specific person"""
        url = "https://sync.revmsg.net/v2/api/people/{revere_id}"

        response = self._request(url, 'GET', self.bearer_token, revere_id)
        content = self._parse(response.content.decode('utf-8'))

        print(content)


    def create_person(self, given_name, family_name, email_addresses, phone_numbers, postal_addresses):
        url = "https://sync.revmsg.net/v2/api/people/post"

        person_payload = {
            'given_name': given_name,
            'family_name':family_name,
            'email_addresses': email_addresses,
            'phone_numbers': phone_numbers,
            'postal_addresses': postal_addresses,
        }

        response = self._request(url, 'POST', self.bearer_token, data=person_payload)
        print(response.url)
        content = self._parse(response.content.decode('utf-8'))

        print(content)


    def _build_url(self, url, params=None):
        """Building out the url paramaters so that we can more specifically query end points.
           Many endpoints if you leave out the paramater will return everything back, but if
           you specify a paramater after the object you're trying to fetch will result in a
           specific record of an object.

        Arguments:
            url {string} -- the base url that one builds upon

        Keyword Arguments:
            params {string} -- The data that we're searching for (default: {None})

        Returns:
            [string] -- results in a string with paramaters added
        """
        if params:
            return f"{url}/{params}/"
        else:
            return url


    def _request(self, url, verb, auth, data=None):
        """Here is a generic request function that determines what to do with a request
           depending on what type of request it is.

        Arguments:
            url {string} -- API URL path
            verb {string} -- GET or POST
            auth {string} -- authentication key for requests

        Keyword Arguments:
            data {[type]} -- [description] (default: {None})

        Returns:
            [json dict] -- returns back a request response.
        """
        if verb == 'GET':
            url = self._build_url(url, params=data)
            response = requests.get(url, headers={'Authorization': auth,
                                                  'Accept': 'application/json',
                                                  'Content-Type': 'application/json'})
        if verb == 'POST':
            response = requests.post(url, params=data, headers={'Authorization': auth,
                                                                'Accept': 'application/vnd.sync.v2+hal+json',
                                                                'Content-Type': 'application/json'})

        return response


    def _parse(self, data):
        """Intermediary function that parses a response. At the moment
           it's mostly checking if there's an error in the response.

        Arguments:
            data {json} -- request response data

        Returns:
            json -- request response data
        """
        self._error_check(data)
        return json.loads(data)


    @staticmethod
    def _error_check(response):
        """Checks a response for an error.

        Arguments:
            response {json} -- Request response data

        Raises:
            RevereException: a generic exception
        """
        if 'errorMsg' in response:
            error = json.loads(response)
            raise RevereException(error['errorMsg'])
        if 'error' in response:
            error = json.loads(response)
            print(error)
            raise RevereException(error['error'])


    @staticmethod
    def _sync_authenticate(sync_key):
        """Revere Sync uses a different authentication than the other API endpoings.
           The first thing that you need to do is post your osdi-api-token and you'll
           get back a bearer token that is good for 24 hours. You'll use the bearer token
           when you call anything in the sync api
        """
        url = "https://sync.revmsg.net/api/authenticate"
        response = requests.post(url, headers={'osdi-api-token': sync_key,
                                              'cache-control': 'no-cache',
                                              'accept': 'application/vnd.sync.v2+json'})

        token = response.json()['token']
        return token
