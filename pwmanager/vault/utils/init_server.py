from .otek import RollingEncryptionKeys
from .tokens import TokenApi
import os

class InitializeServerEnvironment(object):

    def __init__(self):
        RollingEncryptionKeys.initialize()
        token = os.environ['ACCESS_TOKEN']
        TokenApi(token)
