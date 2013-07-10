

AUTHENTICATION_NAME_MAX_LENGTH = 128


class Authentication(object):
    
    class Meta:
        abstract = True


class IceKey(Authentication):
    name = 'icekey'

    def request_token():

        #...
        token = 'asdffdsa'

        return token

