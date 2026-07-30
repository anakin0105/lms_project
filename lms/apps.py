from django.apps import AppConfig


class LmsConfig(AppConfig):
    name = 'lms'

    def ready(self):
        # Импорт задач при старте приложения
        import lms.tasks  # noqa
