from .secrets import api_keys
from .exceptions import quotaLimit

class keys:
    def __init__(self):
        self.keys = api_keys
        self.key_num = 0

    # Get current useable key
    def active_key(self):
        return api_keys[self.key_num]

    # Next key when called
    def next_key(self):
        if self.key_num == len(self.keys)-1:
            self.key_num = 0
            raise quotaLimit
        else:
            self.key_num += 1

    # Check key_num
    def check_key(self):
        return [self.key_num, self.keys[self.key_num]]