"""
Defines api.route decorator for all API routes.
"""
from functools import wraps

from flask import jsonify, make_response, request, Response

from util.exceptions import HTTPException, ServerException, UserException
from util.middleware import MIDDLEWARE


class API(object):
    def __init__(self, bp, namespace=''):
        self.bp = bp
        self.namespace = '/{}/'.format(namespace.strip('/')) if namespace else ''

    def route(self, api_routes, version=1, json_validator=None, args_validator=None, *args, **kwargs):
        # Hack to enable multiple routes to same endpoint
        if not isinstance(api_routes, list):
            api_routes = [api_routes]

        assert all(r.startswith('/') for r in api_routes), 'API routes {} must start with /'.format(api_routes)
        assert isinstance(version, int) and version >= 1, 'API version {} must be an int >= 1'.format(version)

        def decorator(f):
            @wraps(f)
            def h(*args, **kwargs):
                data, error = None, None
                try:
                    [m.pre() for m in MIDDLEWARE]
                    if args_validator:
                        request.validated_args = _validate(args_validator, request.args)
                    if json_validator:
                        request.validated_json = _validate(json_validator, request.get_json(force=True))
                    data = f(*args, **kwargs)
                except HTTPException as e:
                    error = e
                except Exception as e:
                    raise
                    error = ServerException(str(e))

                [m.post(data, error) for m in MIDDLEWARE]
                if error:
                    return _make_response(error={'error_message': error.message}, status_code=error.status_code)

                return _make_response(data=data)

            for route in api_routes:
                url_path = self.namespace + 'v{}{}'.format(version, route)
                self.bp.route(url_path, *args, **kwargs)(h)

            return h
        return decorator


def _validate(Validator, body):
    try:
        v = Validator(body)
        v.validate()
    except Exception as e:
        raise UserException('Invalid request: {}'.format(e))

    return v


def _make_response(data=None, error=None, status_code=200):
    assert status_code / 100 == 2 or error, 'Non-2XX status code {} requires an error.'.format(status_code)
    if isinstance(data, Response):
        return data

    response = make_response(
        jsonify({'data': data, 'error': error}),
        status_code,
        {'Content-Type': 'application/json'}
    )
    return response
