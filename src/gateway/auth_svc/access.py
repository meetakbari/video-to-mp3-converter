import os, requests

def login(request):
    auth = request.authorization
    if not auth:
        return None, ("missing credentials", 401) 

    basicAuth = (auth.username, auth.password)

    print("getting basisAuth:--->", basicAuth)

    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login",
        auth=basicAuth
    )
    print("after response printing ---------")

    if response.status_code == 200:
        return response.text, None
    else:
        print("error is auth----------")
        return None, (response.text, response.status_code)