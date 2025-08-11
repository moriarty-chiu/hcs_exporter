class BaseCollector(object):
    def __init__(self, client):
        self.client = client

    def collect(self):
        raise NotImplementedError('Collectors must implement the collect() method')
