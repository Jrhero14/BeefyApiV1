from ninja import NinjaAPI
from ninja import Router
from ninja.security import HttpBearer
from BeefyRest.views import validTokenCheck
from BeefyRest.views import router as routerMain
from Pembeli.views import router as routerPembeli
from Penjual.views import router as routerPenjual
from Order.views import router as routerOrder


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        print(request.path)
        pathList = [
            '/api/pembeli/register-pembeli/',
            '/api/pembeli/edit-pembeli/',
            '/api/pembeli/edit-pp-pembeli/',
            '/api/penjual/register-penjual/',
            '/api/penjual/edit-pp-penjual/',
            '/api/penjual/edit-penjual/'
        ]
        if (validTokenCheck(token=token)):
            return token
        elif (token == 'DAFTAR'):
            if (request.path in pathList):
                return True
            else:
                pass
        else:
            pass


api = NinjaAPI(
    title='🥩 Beefy Endpoints',
    version='v1.0',
    description='### Hello fellows what do you want? Give me some meat, i will cook for you',
    default_router=Router(tags=['Hello World'])
)

api.add_router('auth/', routerMain)
api.add_router('pembeli/', routerPembeli, auth=AuthBearer())
api.add_router('penjual/', routerPenjual, auth=AuthBearer())
api.add_router('order/', routerOrder, auth=AuthBearer())


@api.get("/", auth=AuthBearer())
def hello(request):
    return {'message': "Hello I'm Beefy Backend"}
