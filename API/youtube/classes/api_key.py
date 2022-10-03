from functions.setup import *

class yt_api_key:
    def __init__(self):
        self.keys = api_key
        self.key_num = 0

    # Get current useable key
    def active_key(self):
        return api_key[self.key_num]

    # Next key when called
    def next_key(self):
        # If last key then raise exception
        if self.key_num == len(self.keys)-1:
            self.key_num = 0
            raise Exception('Quota exceeded for all APIs')
        else:
            self.key_num += 1

    # Check key_num
    def check_key(self):
        return [self.key_num, self.keys[self.key_num]]