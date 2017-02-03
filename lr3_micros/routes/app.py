from datetime import datetime
from flask import Flask, request
from flask_pymongo import PyMongo, ASCENDING, DESCENDING, ObjectId
from utils import send_error, send_response, paginate, Error, cursor_to_list
import requests
import json


app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'routes_bd'
mongo = PyMongo(app)

ROUTE_FIELDS = ['name', 'departure', 'arrival', 'locations', 'price', 'company']
COMPANY_SERVICE_URL = 'http://127.0.0.1:9092/'


@app.route('/routes/', methods=['GET'])
def routes_view():
    """
    curl -X get 'http://127.0.0.1:9093/routes/?size=2&page=1'
    """

    try:
        routes = mongo.db.route.find({}).sort('created', DESCENDING)
        result = paginate(request, data=routes)
        return send_response(request, result)

    except Error as e:
        return send_error(request, e.code)


@app.route('/my_routes/', methods=['GET'])
def my_routes_view():
    email = request.headers.environ.get('HTTP_X_EMAIL')
    print(request.headers)
    print(email)
    
    if not email:
        return send_error(request, 403)

    routes = mongo.db.route.find({'users': email})
    routes = cursor_to_list(routes)
    return send_response(request, {'status': 'OK', 'data': routes})


@app.route('/route/', methods=['POST'])
def create_route_view():
    """
    curl -X POST -H "Content-Type: application/json" 'http://127.0.0.1:9093/route/' \
    -d '{"name": "North Russia", "departure": "2015-10-10 12:00:00", "arrival": "2015-10-15 18:00:00", "price": 100, "company": "TTS"}'
    """

    #TODO: check company owner
    json_s = request.get_json(force=True)
    json_d = json.loads(json_s)
    if json_d is None:
        return send_error(request, 400)

    #route = {field: request.json.get(field) for field in ROUTE_FIELDS}
    route = {}
    for field in ROUTE_FIELDS:
        if field in json_d:
            value = json_d[field]
            if value is not None:
                route.update({field: value})
        else:
            route.update({field: None})
            
    if route['company'] is None:
        return send_error(request, 404)
    
    response = requests.get(COMPANY_SERVICE_URL + 'company/' + route['company'])
    if response.status_code == 404:
        return send_error(request, 404)

    route['created'] = datetime.now()
   # max_response = mongo.db.route.find().sort({'self_id': -1}).limit(1)
    max_response = mongo.db.route.find({}, {'self_id': 1})
    
    print({'max_response':max_response})
    if max_response.count() == 0:
        route['self_id'] = int(1)
    else:
        max_id = 1
        for r in max_response:
            if r['self_id'] > max_id:
                max_id = r['self_id']
        route['self_id'] = int(max_id) + 1
    mongo.db.route.insert(route)
    return send_response(request, {'status': 'OK', 'data': route})


@app.route('/route/<route_id>/', methods=['GET', 'PATCH', 'DELETE'])
def get_route_view(route_id):
    """
    curl -X get 'http://127.0.0.1:9093/route/586f956f050df411919ca464'
    curl -X delete 'http://127.0.0.1:9093/route/586f956f050df411919ca464'
    """
    idid = int(route_id)
    if not idid:
        return send_error(request, 404)

    if request.method == 'GET':
        route = mongo.db.route.find({'self_id': idid})
        route = cursor_to_list(route)
        print({'method': 'get', 'route': route})
        if len(route) > 0:
            return send_response(request, route[0])
        else:
            return send_error(request, 404)

    elif request.method == 'PATCH':
        #TODO: check company owner
        
        json_s = request.get_json(force=True)
        print(json_s)
        json_d = json.loads(json_s)
        print({"jayson": json_d})
        if json_d is None:
            return send_error(request, 400)
            
    #    route = {field: json_d[field] for field in ROUTE_FIELDS if json_d[field] is not None}
        route = {}
        for field in ROUTE_FIELDS:
            if field in json_d:
                value = json_d[field]
                if value is not None:
                    route.update({field: value})
        
        print({'method': 'patch', 'route': route})
        if len(route) == 0:
            return send_error(request, 400)

        route['updated'] = datetime.now()
        result = mongo.db.route.update({'self_id': idid}, {'$set': route})
        return send_response(request, {'status': 'OK', 'updated': result['nModified']})

    elif request.method == 'DELETE':
        #TODO: check company owner

        result = mongo.db.route.delete_one({'self_id': idid})
        return send_response(request, {'self_id': idid, 'deleted': result.deleted_count})


@app.route('/route/<route_id>/register/', methods=['POST'])
def register_view(route_id):
    """
    curl -X post 'http://127.0.0.1:9093/route/586f9570050df411919ca465/register/' -H 'X_EMAIL: xammi@yandex.ru' -H 'X_SECRET: ewifyw521763eyuwfgeuwYTWDYA'
    """
    idid = int(route_id)
    if not idid:
        return send_error(request, 404)

    email = request.headers.environ.get('HTTP_X_EMAIL')
    if not email:
        return send_error(request, 404)

    route = mongo.db.route.find({'self_id': idid})
    
    if route.count() == 0:
        return send_error(request, 404)

    route = cursor_to_list(route)[0]
    users_on_route = route.get('users', [])
    if email not in users_on_route:
        users_on_route.append(email)
        result = mongo.db.route.update_one({'self_id': idid}, {'$set': {'users': users_on_route}})
        return send_response(request, {'status': 'OK', 'updated': result.matched_count})
    else:
        return send_response(request, {'status': 'OK', 'updated': 0})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9093)
