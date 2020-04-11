class RevereException(Exception):
    """
    A General Revere Exception.
    """

    def __init__(self, message):
        super(RevereException, self).__init__()
        self.message = message

    def __str__(self):
        return self.message

    @property
    def get_message(self):
        return self.message


class RateLimitException(Exception):
    """
    Exceeded Rate for Revere
    """
    def __init__(self, message, http_response):
        super(RateLimitException, self).__init__()
        self.message = message
        self.status = http_response.status

    @property
    def get_message(self):
        return self.message