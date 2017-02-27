from .otek import RollingEncryptionKeys
from .tokens import TokenApi


class InitializeServerEnvironment(object):

    def __init__(self):
        RollingEncryptionKeys.initialize()
        token = input('Please provide seedling token:\n')
        TokenApi(token)
