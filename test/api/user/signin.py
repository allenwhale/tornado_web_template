data = [
    {
        "name": "test_signin",
        "url": "/api/users/signin/",
        "method": "post",
        "payload": {
            "account": "admin",
            "password": "admin",
        },
        "response_status": 200,
        "response_data": {
            "msg": {"email": "admin", "account": "admin", "token": "TOKEN@21232f297a@6244de18fb52aa3e0f95265d35380181", "id": 1}
        }
    },
    {
        "name": "test_signin_token",
        "url": "/api/users/signin/",
        "method": "post",
        "payload": {
            "token": "TOKEN@21232f297a@6244de18fb52aa3e0f95265d35380181",
        },
        "response_status": 401,
        "response_data": {
            "msg": "You have already signined."
        }
    },
]
