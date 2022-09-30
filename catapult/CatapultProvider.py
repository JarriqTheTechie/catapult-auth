from masonite.facades import View
from masonite.providers import Provider
from catapult import _render, _render_with_collection


class CatapultProvider(Provider):
    def __init__(self, application):
        self.application = application

    def register(self):
        View.share(_render())
        View.share(_render_with_collection())

    def boot(self):
        pass
