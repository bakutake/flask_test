import traceback
import json
import os
from flask import Flask, request, jsonify
from flask_redis import redis
from flask_api import FlaskAPI, status
from flask_api.renderers import JSONRenderer
from werkzeug.exceptions import HTTPException


app = FlaskAPI(__name__)
redis = redis.Redis('localhost', charset='utf-8', decode_responses=True)
redis.flushall()  # clear cache before start


def log_errors(func):
    '''
    decorator for showing errors in json format
    It must be between function and app.route decorator.
    '''
    def wrapper_log_errors(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            tb = traceback.format_exc()
            # add error logging here if needed
            return {'status': 'error', 'errors': tb}, \
                    status.HTTP_500_INTERNAL_SERVER_ERROR
    wrapper_log_errors.__name__ = 'wrapper_' + func.__name__
    return wrapper_log_errors


@app.route("/add_new_list/", methods=['POST'])
@log_errors
def add_new_list():
    '''
    add new item list into db (redis cache for now).
    list must be sended on 'new_item' argument
    '''
    items = request.data.get('new_item')
    if not items:
        error = {
            'code': status.HTTP_400_BAD_REQUEST,
            'description': 'no data[new_item]',
        }
        return {'status': 'error', 'error': error}, status.HTTP_400_BAD_REQUEST

    if type(items) is not list:
        error = {
            'code': status.HTTP_400_BAD_REQUEST,
            'description': 'new_item isn\'t list',
        }
        return {'status': 'error', 'error': error}, status.HTTP_400_BAD_REQUEST

    items_json = json.dumps(items)
    redis.set(len(redis.keys()), items_json)
    return {'status': 'ok'}, status.HTTP_201_CREATED


@app.route("/show_lists/", methods=['GET'])
@log_errors
def items_list():
    '''
    show a list of previously sended lists
    '''
    return {'lists': [json.loads(redis.get(key)) for key in redis.keys()]}


@app.route("/example_error/", methods=['GET'])
@log_errors
def example_error():
    5 / 0
    return {'result': 'result'}


@app.errorhandler(HTTPException)
def base_http_error_handler(e):
    '''
    base handler for all http errors
    send error data in json format
    '''
    try:
        error = {
            'code': e.code,
            'description': e.description,
        }
        return {'status': 'error', 'error': error}, e.code
    except Exception as ex:
        tb = traceback.format_exc()
        return {'status': 'error', 'errors': tb}, \
                status.HTTP_500_INTERNAL_SERVER_ERROR


if __name__ == '__main__':
    app.debug = True
    host = os.environ.get('IP', '0.0.0.0')
    port = int(os.environ.get('PORT', 8080))

    app.config['DEFAULT_RENDERERS'] = [
        'flask_api.renderers.JSONRenderer',
        # 'flask_api.renderers.BrowsableAPIRenderer',
    ]

    app.run(host=host, port=port)
