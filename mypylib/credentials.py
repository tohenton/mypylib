class Credentials(object):
    def __init__(self, path=None):
        if not path:
            import os
            path = os.path.join(os.environ["HOME"], ".credentials")

        with open(path, "r") as f:
            self.username, self.password = f.read().strip().split(":")
