import geoip2.database
import geoip2.webservice
from geoip2.errors import AddressNotFoundError


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
        def get_config(key):
            return app.config.get('GEOIP2_%s' % key)

        db_path = db_path or get_config('DB_PATH')
        ws_user_id = ws_user_id or get_config('WS_USER_ID')
        ws_license_key = ws_license_key or get_config('WS_LICENSE_KEY')
        assert (db_path or (ws_user_id and ws_license_key)), 'Please specify geoip2 settings'

        if db_path:
            instance = geoip2.database.Reader(db_path)
        else:
            instance = geoip2.webservice.Client(ws_user_id, ws_license_key)
        instance.AddressNotFoundError = AddressNotFoundError

        app.extensions['geoip2'] = instance
        return instance
