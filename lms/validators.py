from django.core.exceptions import ValidationError
import re


def youtube_validator(value):
    """Проверяет, что ссылка ведёт только на youtube.com"""
    if not value:  # если поле пустое — пропускаем
        return value

    if not isinstance(value, str):
        raise ValidationError(
            'Поле video_url должно быть строкой',
            code='invalid_type'
        )

    youtube_regex = r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$'
    if not re.match(youtube_regex, value):
        raise ValidationError(
            'Разрешены только ссылки на YouTube (youtube.com или youtu.be)',
            code='invalid_youtube_url'
        )
    return value