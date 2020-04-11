import json


class RevereObjs(object):
    def __init__(self, **kwargs):
        self.params = {}

    @classmethod
    def from_json(cls, content, **kwargs):
        json_data = content.copy()
        if kwargs:
            for key, value in kwargs.items():
                json_data[key] = value

        x = cls(**json_data)
        x._json = content
        return x


class List(RevereObjs):
    def __init__(self, **kwargs):
        self.params = {
            'account': None,
            'createdBy': None,
            'group': None,
            'id': None,
            'name': None,
            'noOfSubscribers': None,
            'shortCode': None,
            'status': None,
        }

        for param_name, default_value in self.params.items():
            setattr(self, param_name, kwargs.get(param_name, default_value))

class Person(RevereObjs):
    def __init__(self, **kwargs):
        self.params = {
            'given_name' : None,
            'family_name' : None,
            'identifiers' : None,
            'party_identification' : None,
            'custom_fields' : None,
            'birthdate' : None,
            'email_addresses' : None,
            'phone_numbers' : None,
            'postal_addresses' : None,
            'profiles' : None,
            'triggers' : None,
        }

        for param_name, default_value in self.params.items():
            setattr(self, param_name, kwargs.get(param_name, default_value))