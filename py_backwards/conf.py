from argparse import Namespace


class Settings:
    def __init__(self) -> None:
        self.debug = False


settings = Settings()


def init_settings(args: Namespace) -> None:
    if args.debug:
        settings.debug = True
