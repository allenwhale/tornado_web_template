import requests
import config

data = {
    "account": "admin",
    "password": "admin",
}

r = requests.post('%s/api/users/signin/'%(config.base_url), data=data)

print(r.text)
print(r.cookies)
r = requests.post('%s/api/users/signin/'%(config.base_url), cookies=r.cookies)
print(r.text)
print(r.cookies)
r = requests.post('%s/api/users/signout/'%(config.base_url), cookies=r.cookies)
print(r.text)
print(r.cookies)



