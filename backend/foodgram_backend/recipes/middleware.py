import logging
from logging.handlers import RotatingFileHandler

from foodgram_backend.settings import (LOGS_BACKUP_COUNT, LOGS_MAX_BYTES,
                                       LOGS_ROOT)

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

handler = RotatingFileHandler(f"{LOGS_ROOT}{__name__}.log",
                              maxBytes=LOGS_MAX_BYTES,
                              backupCount=LOGS_BACKUP_COUNT)
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(f'Request method: {request.method}, path: {request.path}')
        response = self.get_response(request)
        return response
