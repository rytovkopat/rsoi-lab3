from datetime import datetime, timedelta
import requests
from flask import Flask, request, redirect, make_response, jsonify
import json

app = Flask(__name__)

#TODO: make map of URLs to servers
server_data = {
    'host': '127.0.0.1',
    'port': '9091',
    'api_key': 'EftqgfZ8YCxmUSa7tLIm9NZYW3X0hLhzktyUlwHV',
    'api_secret': 'It9aTzpJP9bzS1KLCEyPi8xBsB1WPxHpMxbArCec7tT7ifky5RodBHeiOzJ9lMEv8tkb9Fzs4Zc1zLY5Uqj43OQKVWq15QmN5dPtHxl2wEmlL0ZKPJppAElyfs6cO9Jm',
}
client_data = {
    'host': '127.0.0.1',
    'port': '9090',
}
company_data = {
	'host': '127.0.0.1',
    'port': '9092',
    'api_key': 'EftqgfZ8YCxmUSa7tLIm9NZYW3X0hLhzktyUlwHV',
    'api_secret': 'It9aTzpJP9bzS1KLCEyPi8xBsB1WPxHpMxbArCec7tT7ifky5RodBHeiOzJ9lMEv8tkb9Fzs4Zc1zLY5Uqj43OQKVWq15QmN5dPtHxl2wEmlL0ZKPJppAElyfs6cO9Jm',
}
route_data = {
	'host': '127.0.0.1',
    'port': '9093',
    'api_key': 'EftqgfZ8YCxmUSa7tLIm9NZYW3X0hLhzktyUlwHV',
    'api_secret': 'It9aTzpJP9bzS1KLCEyPi8xBsB1WPxHpMxbArCec7tT7ifky5RodBHeiOzJ9lMEv8tkb9Fzs4Zc1zLY5Uqj43OQKVWq15QmN5dPtHxl2wEmlL0ZKPJppAElyfs6cO9Jm',
}
aggregator_data = {
	'host': '127.0.0.1',
    'port': '9094',
    'api_key': 'EftqgfZ8YCxmUSa7tLIm9NZYW3X0hLhzktyUlwHV',
    'api_secret': 'It9aTzpJP9bzS1KLCEyPi8xBsB1WPxHpMxbArCec7tT7ifky5RodBHeiOzJ9lMEv8tkb9Fzs4Zc1zLY5Uqj43OQKVWq15QmN5dPtHxl2wEmlL0ZKPJppAElyfs6cO9Jm',
}
AUTHORIZE_URL = 'authorize'
ACCESS_TOKEN_URL = 'token'


def get_server_route(route, service):
    backslash = '?' not in route
    port = {
	    'client':9090,
	    'authorization':9091,
	    'company':9092,
	    'route':9093,
	    'aggregator':9094,
    }.get(service,0)
    return 'http://{0}:{1}/{2}'.format(
        server_data['host'], port, route) + ('/' if backslash else '')


def get_client_route(route):
    backslash = '?' not in route
    return 'http://{0}:{1}/{2}'.format(client_data['host'], client_data['port'], route) + ('/' if backslash else '')


def send_response(status, obj=None):
    json = jsonify({'code': status, 'response': obj})
    response = make_response(json)
    response.headers['Content-Type'] = "application/json"
    return response


query_template = '''
<html>
<head><title>LR3 Client</title><meta charset="utf-8"></head>
<body>
  <div>Access Token: {1}</div>
  <h3>Сделать запрос в API</h3>
  <div id="query-form">

  <form action="/query/" method="POST">
    <label><input type="checkbox" name= "chb1" value="contentjsonheader">Отправить заголовок с типом контента json</label><br>
    <label><input type="checkbox" name= "chb2" value="emailheader">Отправить заголовок с почтой</label><br>
    <label><input type="checkbox" name= "chb3" value="secretheader">Отправить заголовок с секретиком</label><br>
    <select name="method">
      <option value="GET">GET</option>
      <option value="POST">POST</option>
      <option value="PATCH">PATCH</option>
      <option value="DELETE">DELETE</option>
    </select>
    <select name="service">
      <option value="client">Client service</option>
      <option value="authorization">Authorization service</option>
      <option value="company">Company service</option>
      <option value="route">Route service</option>
      <option value="aggregator">Aggregation service</option>
    </select>
    <input type="text" name="query" style="width:400px" value="{2}"><br><br>
    <textarea name="body1">{3}</textarea><br><br>
    <button type="submit">Запросить данные!</button>
  </form>

  </div><pre id="query-data">{0}</pre>
</body>
</html>
'''


@app.route('/query/', methods=['GET', 'POST'])
def send_query():
    token = client_data.get('access_token')
    if not token:
        return send_response('ERROR', {'msg': 'No token'})

    if request.method == 'POST':
        query = request.form.get('query')
        method = request.form.get('method')
        body = request.form.get('body1')
        service = request.form.get('service')
        url = get_server_route(query, service)
        headers = {'Authorization': 'Bearer:{0}'.format(token)}
        need_header_json = request.form.get('chb1')
        need_header_email = request.form.get('chb2')
        need_header_secret = request.form.get('chb3')
        
        if need_header_json:
            headers['Content-Type'] = 'application/json'
			
        if need_header_email:
            headers.update({"X_EMAIL": client_data.get("email")})
			
        if need_header_secret:
            headers.update({"X_SECRET": client_data.get("client_secret")})
            
        print(headers)
        
        if not body:
            response = requests.request(method, url, headers=headers)
        else:
            data = json.dumps(body.replace(r'\n\r', '').replace(',}', '}'))
            print(data)
            
            response = requests.request(method, url, headers=headers, data=data)

        if response.status_code != 200:
            result = 'ERROR', '{} code for {}'.format(response.status_code, url)
        else:
            result = json.dumps(response.json(), indent=4, ensure_ascii=False)
        return query_template.format(result, client_data.get('access_token'), query, body or '')
    return query_template.format('', client_data.get('access_token'), '', '')


@app.route('/redirect/', methods=['GET'])
def finish_auth():
    code = request.args.get('code')
    if not code:
        return send_response('ERROR')

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': get_client_route('redirect'),
    }
    finish_url = get_server_route(ACCESS_TOKEN_URL, 'authorization')
    auth_data = (server_data['api_key'], server_data['api_secret'])

    response = requests.post(finish_url, data=data, auth=auth_data)
    
    if response.status_code == 200:
        resp_data = response.json()
       # print(resp_data.get('expires_in'))
        client_data.update({
            'access_token': resp_data.get('access_token'),
            'refresh_token': resp_data.get('refresh_token'),
            'expires_in': datetime.now() + timedelta(minutes=5),
        })

        return redirect('/query/')
    return send_response('ERROR', 'Not 200')


@app.route('/start_auth/', methods=['GET'])
def start_auth():
    start_url = get_server_route(AUTHORIZE_URL, 'authorization')
    start_params = {
        'client_id': server_data['api_key'],
        'response_type': 'code',
    }
    params = '?'
    for param, value in start_params.items():
        params += '{0}={1}&'.format(param, value)
    return redirect(start_url + params[:-1])


index_template = '''
<html>
<head><title>LR3 Client</title></head>
<body><a href="/start_auth/">Авторизоваться</a></body>
</html>
'''


@app.route('/', methods=['GET'])
def index():
    return index_template


if __name__ == '__main__':
    app.run(host=client_data['host'], port=client_data['port'])

