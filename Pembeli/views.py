from django.contrib.auth.models import User
from Pembeli import schemas as SchemasBody
from Pembeli.models import PembeliDB, ScanHistroyDB
from Order.models import Orders
from ninja import Router
from ninja import Form, NinjaAPI
from ninja import File
from ninja.files import UploadedFile
from typing import List
import requests
from datetime import datetime
import numpy as np
from Penjual.models import PenjualDB, ProdukDB

from storages.backends.gcloud import GoogleCloudStorage
storage = GoogleCloudStorage()
class Upload:
    @staticmethod
    def upload_image(file, filename):
        try:
            target_path = 'gs://beefy-bucket/' + filename
            path = storage.save(target_path, file)
            return storage.url(path)
        except Exception as e:
            print("Failed to upload!")
            return False

app = NinjaAPI()

# Create your views here.

router = Router(
    tags=['Pembeli endpoints']
)

@router.post("register-pembeli/")
def register(request, payload: SchemasBody.RegisterBody = Form(...)):
    try:
        userNew = User.objects.create_user(
            username=payload.email,
            email='account@email.com'
        )
        userNew.set_password(payload.password)
        userNew.is_staff = False
        userNew.save()
    except:
        return app.create_response(
            request,
            {'message': f'account with email {payload.email} already exists'},
            status=409
        )
    pembeliNew = PembeliDB.objects.create(
        nama=payload.nama,
        nama_penerima=payload.nama,
        alamat_lengkap='None',
        nomor_telp='None',
        label_alamat='None',
        photo_profile='None',
        ID_USER=userNew
    )
    return {
        'message': 'register success',
        'id_user': userNew.pk,
        'id_pembeli': pembeliNew.pk
    }


@router.post('edit-pembeli/')
def editPembelit(request, payload: SchemasBody.EditPembeliBody = Form(...)):
    print(payload.id_pembeli)
    pembeliObj = PembeliDB.objects.filter(pk=int(payload.id_pembeli)).exists()
    if (pembeliObj):
        pembeliObj = PembeliDB.objects.get(pk=int(payload.id_pembeli))
        pembeliObj.nama = payload.nama
        pembeliObj.alamat_lengkap = payload.alamat_lengkap
        pembeliObj.nama_penerima = payload.nama_penerima
        pembeliObj.nomor_telp = payload.nomor_telp
        pembeliObj.label_alamat = payload.label_alamat
        pembeliObj.save()
    else:
        return app.create_response(
            request,
            {'message': f'Pembeli with id {payload.id_pembeli} Not Found'},
            status=404
        )
    return {'message': f'Success edit pembeli for pembeli id {payload.id_pembeli}'}


@router.post('edit-pp-pembeli/')
def editPhotoPembeli(request, id_pembeli: int = Form(...), file_image: UploadedFile = File(...)):
    public_uri = Upload.upload_image(file_image, str(file_image.name).replace(' ', '-'))
    if (public_uri is False):
        return app.create_response(
            request,
            {'message': 'Error when upload process'},
            status=500
        )
    if (PembeliDB.objects.filter(pk=id_pembeli).exists()):
        urlGambar = str(public_uri)
        userPembeliObj = PembeliDB.objects.get(pk=id_pembeli)
        userPembeliObj.photo_profile = str(urlGambar)
        userPembeliObj.save()
    else:
        return app.create_response(
            request,
            {'message': f'Pembeli with id {id_pembeli} not found'},
            status=404
        )
    return {'message': 'Success Edit photo profile'}


@router.get('user/detail/by-id-pembeli/{id_pembeli}')
def getPembeliDetailbyIDPembeli(request, id_pembeli: int):
    userObj = PembeliDB.objects.filter(pk=id_pembeli).exists()
    if (not userObj):
        return app.create_response(
            request,
            {'message': f'Pembeli with id {id_pembeli} not found'},
            status=404
        )
    userObj = PembeliDB.objects.get(pk=id_pembeli)
    responseBody = {
        'id_pembeli': userObj.pk,
        'nama': userObj.nama,
        'alamat_lengkap': userObj.alamat_lengkap,
        'nama_penerima': userObj.nama_penerima,
        'nomor_telp': userObj.nomor_telp,
        'label_alamat': userObj.label_alamat,
        'photo_profile': userObj.photo_profile,
        'user_account': {
            'id_account': userObj.ID_USER.pk,
            'email': userObj.ID_USER.username,
        }
    }
    return responseBody


@router.get('user/detail/by-id-account/{id_account}')
def getPembeliDetailbyIDAccount(request, id_account: int):
    userObj = PembeliDB.objects.filter(ID_USER_id=id_account).exists()
    if (not userObj):
        return app.create_response(
            request,
            {'message': f'Pembeli with account id {id_account} not found'},
            status=404
        )
    userObj = PembeliDB.objects.get(ID_USER_id=id_account)
    responseBody = {
        'id_pembeli': userObj.pk,
        'nama': userObj.nama,
        'alamat_lengkap': userObj.alamat_lengkap,
        'nama_penerima': userObj.nama_penerima,
        'nomor_telp': userObj.nomor_telp,
        'label_alamat': userObj.label_alamat,
        'photo_profile': userObj.photo_profile,
        'user_account': {
            'id_account': userObj.ID_USER.pk,
            'email': userObj.ID_USER.username,
        }
    }
    return responseBody


@router.post('scan-meat/')
def scanDaging(request, id_pembeli: int = Form(...), file_image: UploadedFile = File(...)):
    try:
        public_uri = Upload.upload_image(file_image, str(file_image.name).replace(' ', '-'))
        if (public_uri is False):
            return app.create_response(
                request,
                {'message': 'Error when upload process'},
                status=500
            )
        urlGambar = str(public_uri)
        responeModelApi = requests.post('https://beefy-ml-b52v2foiya-et.a.run.app/predict/', params={
        }, files={
            'fileUpload': file_image.read()
        }).json()
    except:
        return app.create_response(
            request,
            {'message': 'Error communication with model API'},
            status=500
        )
    print(responeModelApi)
    ScanHistroyDB.objects.create(
        ID_Pembeli=id_pembeli,
        gambar_url=urlGambar,
        tanggal=datetime.now(),
        segar=True if responeModelApi['label'] == 'fresh' else False,
        level_kesegaran=int(float(str(responeModelApi['kesegaran']).replace('%', ''))) if str(responeModelApi['kesegaran']) != '-' else 0,
        jenis='sapi' if responeModelApi['type'] == 'beef' else 'pork'
    )
    return {
        'message': 'Meat Scan Success',
        'data': {
            'url_gambar': urlGambar,
            'hasil': responeModelApi['label'],
            'level_kesegaran': responeModelApi['kesegaran'],
            'jenis': 'sapi' if responeModelApi['type'] == 'beef' else 'pork'
        }
    }

@router.post('save-scan-result/')
def saveScanResult(request,
               id_pembeli: int = Form(...),
               label: str = Form(...),
               level_kesegaran: int = Form(...),
               type: str = Form(...),
               file_image: UploadedFile = File(...)):
    try:
        public_uri = Upload.upload_image(file_image, str(file_image.name).replace(' ', '-'))
        if (public_uri is False):
            return app.create_response(
                request,
                {'message': 'Error when upload process'},
                status=500
            )
        urlGambar = str(public_uri)
    except:
        return app.create_response(
            request,
            {'message': 'Error communication with model API'},
            status=500
        )
    historyObj = ScanHistroyDB.objects.create(
        ID_Pembeli=id_pembeli,
        gambar_url=urlGambar,
        tanggal=datetime.now(),
        segar=True if label == 'fresh' else False,
        level_kesegaran=int(level_kesegaran),
        jenis='sapi' if type == 'beef' else 'pork'
    )
    return {
        'message': 'Save scan meat result success',
        'data': {
            'id_history': historyObj.pk,
            'url_gambar': urlGambar,
            'hasil': label,
            'level_kesegaran': level_kesegaran,
            'jenis': 'sapi' if type == 'beef' else 'pork'
        }
    }


@router.get('scan-history/{id_pembeli}', response=List[SchemasBody.ScanHistoryResponse])
def scanHistory(request, id_pembeli: int):
    histroyObjs = ScanHistroyDB.objects.filter(ID_Pembeli=id_pembeli)
    return histroyObjs


@router.get('store/profile/{id_toko}')
def getProfileStore(request, id_toko: int):
    userObj = PenjualDB.objects.filter(pk=id_toko).exists()
    if (not userObj):
        return app.create_response(
            request,
            {'message': f'Toko penjual with id {id_toko} not found'},
            status=404
        )
    userObj = PenjualDB.objects.get(pk=id_toko)
    responseBody = {
        'logo_toko': userObj.logo_toko,
        'nama_toko': userObj.nama_toko,
        'rekening': userObj.rekening,
        'metode_pembayaran': userObj.metode_pembayaran,
        'alamat_lengkap': userObj.alamat_lengkap,
        'nomor_telp': userObj.nomor_telp,
        'jam_operasional_buka': userObj.jam_operasional_buka,
        'jam_operasional_tutup': userObj.jam_operasional_tutup,
        'user_account': {
            'email': userObj.ID_USER.username,
        }
    }
    return responseBody


@router.get('get-stores/', response=List[SchemasBody.StoresResponse])
def getStores(request):
    stores = PenjualDB.objects.all()
    return stores


@router.get('search-toko/', response=List[SchemasBody.StoresResponse])
def searcToko(request, toko_name: str):
    getStores = PenjualDB.objects.filter(nama_toko__icontains=toko_name)
    if (len(getStores) == 0):
        return app.create_response(
            request,
            {'message': f'Toko with name {toko_name} not found'},
            status=404
        )
    return getStores


@router.get('search-product/', response=List[SchemasBody.ProductsResponse])
def searchProduct(request, product_name: str):
    getProducts = ProdukDB.objects.filter(nama_barang__icontains=product_name)
    if (len(getProducts) == 0):
        return app.create_response(
            request,
            {'message': f'Product with name {product_name} not found'},
            status=404
        )
    return getProducts


@router.get('get-all-products/', response=List[SchemasBody.ProductsResponse])
def getProducts(request):
    try:
        products = ProdukDB.objects.all()
    except:
        return app.create_response(
            request,
            {'message': 'Error with database when get products'},
            status=500
        )
    return products


@router.get('get-products/{id_toko}', response=List[SchemasBody.ProductsResponse])
def get_Products(request, id_toko: int):
    try:
        products = ProdukDB.objects.filter(
            ID_TOKO=id_toko
        )
    except:
        return app.create_response(
            request,
            {'message': 'Error with database when get products'},
            status=500
        )
    return products


@router.post('accept-order-complete/')
def acceptOrderComplete(request, id_order: int = Form(...)):
    if (not Orders.objects.filter(pk=id_order).exists()):
        return app.create_response(
            request,
            {'message': f'Order with id {id_order} not found'},
            status=404
        )
    orderObj = Orders.objects.get(pk=id_order)
    if (orderObj.status == 'Menunggu'):
        return app.create_response(
            request,
            {
                'message': f'Order with id {id_order} tidak bisa terima pesanan dari pembeli karna status masih Menunggu diterima seller'},
            status=404
        )
    elif (orderObj.status == 'Selesai'):
        return app.create_response(
            request,
            {'message': f'Order with id {id_order} telah selesai diterima oleh pembeli'},
            status=404
        )
    else:
        orderObj.status = 'Selesai'
        orderObj.save()

    return {'message': f'Pesanan dengan id {id_order} telah diterima oleh pembeli'}


@router.get('get-trending-product', response=List[SchemasBody.ProductsResponse])
def getTrendingProduct(request):
    orders = Orders.objects.all()
    barangIDList = list(orders.values_list('ID_BARANG', flat=True))
    unik = list(np.unique(np.array(barangIDList)))
    terlaris = []
    for id_barang in unik:
        terlaris.append((id_barang, barangIDList.count(id_barang)))
    terlaris.sort(key=lambda x: x[1], reverse=True)
    print(terlaris)

    barang_terlaris = []
    for i in range(5):
        try:
            barang = ProdukDB.objects.get(pk=terlaris[i][0])
            barang_terlaris.append(barang)
        except:
            pass

    return barang_terlaris

@router.get('get-trending-store', response=List[SchemasBody.StoresResponse])
def getTrendingStore(request):
    orders = Orders.objects.all()
    tokoIDList = list(orders.values_list('ID_TOKO', flat=True))
    unik = list(np.unique(np.array(tokoIDList)))
    trending = []
    for id_barang in unik:
        trending.append((id_barang, tokoIDList.count(id_barang)))
    trending.sort(key=lambda x: x[1], reverse=True)
    print(trending)

    toko_terlaris = []
    for i in range(5):
        try:
            toko = PenjualDB.objects.get(pk=trending[i][0])
            toko_terlaris.append(toko)
        except:
            pass

    return toko_terlaris
