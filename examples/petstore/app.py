#!/usr/bin/env python3
from foca.foca import foca
import jwt


def checkAuth(token):
    print("token: ", token)
    decodedToken = jwt.decode(token, "your-256-bit-secret", algorithms=["HS256"])
    print(decodedToken)
    user = decodedToken["name"]
    print(user)
    return { 
        'user': user,
        'status': '200'
    }


if __name__ == '__main__':
    app = foca("config.yaml")
    app.run()
