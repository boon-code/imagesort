

class UserAborted(Exception):
    pass


class UnsupportedImageFormat(Exception):

    def __init__(self, path):
        self.path = path
        Exception.__init__(self, f"File {path} has an unsupported image format")