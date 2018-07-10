from functools import partial

import geoip2.database
import geoip2.webservice
from geoip2.errors import AddressNotFoundError


from flask import request, _request_ctx_stack


def get_remote_addr(num_proxies=1):
    # access_route is based on X-Forwarded-For and fallback to remote_addr
    if len(request.access_route) >= num_proxies:
        return request.access_route[-num_proxies]
    return request.remote_addr


def _lookup_remote_addr(method, num_proxies=1, raise_on_not_found=True, **kwargs):
    ctx = _request_ctx_stack.top
    if ctx is not None:
        if not hasattr(ctx, '_geoip2'):
            addr = get_remote_addr(num_proxies)
            try:
                ctx._geoip2 = method(addr, **kwargs)
            except AddressNotFoundError:
                ctx._geoip2 = None
                if raise_on_not_found:
                    raise
        if raise_on_not_found and not ctx._geoip2:
            raise AddressNotFoundError('The address {} is not in the database.'.format(addr))
        return ctx._geoip2


class GeoIP2(object):
    def __init__(self, app=None, **kwargs):
        self.app = app

        if app is not None:
            self.instance = self.init_app(app, **kwargs)

    def __getattr__(self, name):
        if hasattr(self, 'instance'):
            return getattr(self.instance, name)
        raise AttributeError()

    def init_app(self, app, db_path=None, ws_user_id=None,
                 ws_license_key=None):
        """Provide db_path for database reader
        or ws_user_id and ws_license_key for webservice.
        """
        def get_config(key, default=None):
            return app.config.get('GEOIP2_%s' % key, default)

        db_path = db_path or get_config('DB_PATH')
        ws_user_id = ws_user_id or get_config('WS_USER_ID')
        ws_license_key = ws_license_key or get_config('WS_LICENSE_KEY')
        assert (db_path or (ws_user_id and ws_license_key)), 'Please specify geoip2 settings'

        # Custom setting to proper determine remote addr based on X-Forwarded-For
        num_proxies = app.config.get('FLASK_ACCESS_ROUTE_NUM_PROXIES', 1)

        if db_path:
            instance = geoip2.database.Reader(db_path, locales=get_config('DB_LOCALES'),
                                              mode=get_config('DB_MODE', geoip2.database.MODE_AUTO))
        else:
            instance = geoip2.webservice.Client(ws_user_id, ws_license_key)

        instance.AddressNotFoundError = AddressNotFoundError
        instance.get_remote_addr = partial(get_remote_addr, num_proxies)

        # setting wrappers for request remote addr
        for method_name in ('country', 'city', 'anonymous_ip', 'connection_type', 'domain',
                            'enterprise', 'isp'):
            setattr(instance, '{}_remote_addr'.format(method_name),
                    partial(_lookup_remote_addr, getattr(instance, method_name), num_proxies))

        app.extensions['geoip2'] = instance
        return instance
