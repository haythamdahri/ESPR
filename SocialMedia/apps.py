from django.apps import AppConfig


class SocialMediaConfig(AppConfig):
    name = 'SocialMedia'

    def ready(self):
        import SocialMedia.signals
