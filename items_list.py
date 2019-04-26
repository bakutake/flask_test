import traceback
import json
import os
from flask import Flask, request, jsonify
from flask_redis import redis
from flask_api import FlaskAPI, status
from flask_api.renderers import JSONRenderer


app = FlaskAPI(__name__)
redis = redis.Redis('localhost', charset='utf-8', decode_responses=True)
redis.flushall()  # clear before start


@app.route("/add_new_list/", methods=['POST'])
def add_new_list():
    try:
        items = request.data.get('new_item')
        if not items:
            return {'status': 'error', 'errors': 'no data[new_item]'}, \
                    status.HTTP_400_BAD_REQUEST

        if type(items) is not list:
            return {'status': 'error', 'errors': 'new_item isn\'t list'}, \
                    status.HTTP_400_BAD_REQUEST

        items_json = json.dumps(items)
        redis.set(len(redis.keys()), items_json)
        return {'status': 'ok'}, status.HTTP_200_OK
    except Exception as ex:
        tb = traceback.format_exc()
        return {'status': 'error', 'errors': tb}, status.HTTP_400_BAD_REQUEST


@app.route("/show_lists/", methods=['GET'])
def items_list():
    try:
        list(map(print, [redis.get(key) for key in redis.keys()]))
        return {'lists': [json.loads(redis.get(key)) for key in redis.keys()]}
    except Exception as ex:
        tb = traceback.format_exc()
        return {'status': 'error', 'errors': tb}, status.HTTP_400_BAD_REQUEST


@app.errorhandler(404)
def page_not_found(e):
    return {'status': 'error', 'errors': 'not found'}, \
            status.HTTP_404_NOT_FOUND


if __name__ == '__main__':
    app.debug = True
    host = os.environ.get('IP', '0.0.0.0')
    port = int(os.environ.get('PORT', 8080))

    app.config['DEFAULT_RENDERERS'] = [
        'flask_api.renderers.JSONRenderer',
        # 'flask_api.renderers.BrowsableAPIRenderer',
    ]

    app.run(host=host, port=port)
