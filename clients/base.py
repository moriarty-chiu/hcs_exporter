class BaseClient(object):
    def __init__(self):
        pass

    def get_client(self):
        raise NotImplementedError('Clients must implement the get_client() method')
