from typing import Any, Callable, Protocol
import requests

DataType = dict[str, Any] | list[Any] | None

class ApiException(Exception):
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status_code = status_code
    

class ApiFunction(Protocol):
    def __call__(self, url: str, data: dict[str, Any] | None = None) -> DataType:
        ...



BASE_URL = 'https://postup.lalabuff.ml/api/beta/'
SCOPE = '*'

with open('.token', 'r') as f:
    CLIENT_ID = f.readline().strip()
    CLIENT_SECRET = f.readline().strip()
    token = f.readline().strip()
    refresh_token = f.readline().strip()


def update():
    with open('.token', 'w') as f:
        f.write(CLIENT_ID + '\n')
        f.write(CLIENT_SECRET + '\n')
        f.write(token + '\n')
        f.write(refresh_token + '\n')


def refresh():
    global token, refresh_token
    
    response = requests.post('https://oauth.lalabuff.ml/token',
        data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'scope': SCOPE
        }
    )
    
    if response.ok:
        json = response.json()
        token = json['access_token']
        refresh_token = json['refresh_token']
        update()
    else:
        raise Exception(f'Failed to refresh token: {response} {response.text}')


def make_api_call(func: Callable[..., requests.Response], url: str, data: dict[str, Any] | None = None) -> requests.Response:
    return func(BASE_URL + url,
        json={
            'data': data
        } if data else None,
        headers={
            'authorization': f'Bearer {token}, Client {CLIENT_ID}, Secret {CLIENT_SECRET}'
        }
    )


def retry_api_call(func: Callable[..., requests.Response], url: str, data: dict[str, Any] | None = None) -> requests.Response:
    response = make_api_call(func, url, data)
    
    if response.status_code in (401, 403):
        refresh()
        response = make_api_call(func, url, data)
    
    if not response.ok:
        raise ApiException(f'Failed to make api call to "{url}": {response.text}', response.status_code)
    
    return response


def get_data(response: requests.Response) -> DataType:
    json = response.json()
    if json.get('ok'):
        return json.get('data')
    else:
        raise Exception(f'Failed to fetch data: [{json.get("status")}] {json.get("message")}')




def build_api_function(func: Callable[..., requests.Response]) -> ApiFunction:
    def api_function(url: str, data: dict[str, Any] | None = None) -> DataType:
        return get_data(retry_api_call(func, url, data))
    return api_function


get = build_api_function(requests.get)
post = build_api_function(requests.post)
patch = build_api_function(requests.patch)
delete = build_api_function(requests.delete)
put = build_api_function(requests.put)
