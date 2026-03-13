import logging
import time
from django.utils.timezone import now

request_logger = logging.getLogger('requests')


class RequestLogMiddleware:
    """
    - URL
    - Method (GET/POST)
    - User (logged in ya anonymous)
    - Status code
    - Response time
    - IP address
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration     = round((time.time() - start_time) * 1000, 2)
        user         = request.user.email if request.user.is_authenticated else 'anonymous'
        ip           = self.get_client_ip(request)
        status_code  = response.status_code
        method       = request.method
        path         = request.get_full_path()
        timestamp    = now().strftime('%Y-%m-%d %H:%M:%S')

        log_message = (
            f"[{timestamp}] {method} {path} | "
            f"status={status_code} | "
            f"user={user} | "
            f"ip={ip} | "
            f"duration={duration}ms"
        )

        if status_code >= 500:
            request_logger.error(log_message)
        elif status_code >= 400:
            request_logger.warning(log_message)
        else:
            request_logger.info(log_message)

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')