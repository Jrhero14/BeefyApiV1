from ninja import NinjaAPI, Router
from Penjual import schemas as SchemasBody
from Penjual.models import PenjualDB, ProdukDB
from django.contrib.auth.models import User
from ninja import Form, File
from Order.models import Orders
from ninja.files import UploadedFile
from Pembeli.views import Upload
from typing import List

app = NinjaAPI()

router = Router(
    tags=['Penjual Endpoints']
)


@router.post('register-penjual/')
def registerPenjual(request, payload: SchemasBody.RegisterBody = Form(...)):
    usetGet = User.objects.filter(username=payload.email).exists()
    if (usetGet):
        return app.create_response(
            request,
            {'message': f'account penjual with email {payload.email} already exists'},
            status=409
        )
    penjualGet = PenjualDB.objects.filter(nama_toko=payload.nama_toko).exists()
    if (penjualGet):
        return app.create_response(
            request,
            {'message': f'Store penjual with nama Toko {payload.nama_toko} already exists'},
            status=409
        )

    try:
        userNew = User.objects.create_user(
            username=payload.email,
            email='account@email.com'
        )
        userNew.set_password(payload.password)
        userNew.is_staff = True
        userNew.save()
    except:
        return app.create_response(
            request,
            {'message': f'Problem with database when create user penjual'},
            status=500
        )

    penjualNew = PenjualDB.objects.create(
        logo_toko='None',
        nama_toko=payload.nama_toko,
        rekening='None',
        metode_pembayaran='None',
        alamat_lengkap='None',
        nomor_telp=payload.nomor_telepon,
        jam_operasional_buka='None',
        jam_operasional_tutup='None',
        ID_USER=userNew
    )

    return {
        'message': 'success create account penjual',
        'id_user': userNew.pk,
        'id_toko': penjualNew.pk,
        'nama_toko': penjualNew.nama_toko
    }

@router.post('edit-penjual/')
def editPenjual(request, payload: SchemasBody.EditPenjualBody = Form(...)):
    penjualGet = PenjualDB.objects.filter(pk=payload.id_toko)
    if (not penjualGet):
        return app.create_response(
            request,
            {'message': f'Penjual with id {payload.id_toko} not found'},
            status=404
        )

    try:
        penjualObj = PenjualDB.objects.get(pk=payload.id_toko)
        penjualObj.rekening = payload.rekening
        penjualObj.metode_pembayaran = payload.metode_pembayaran
        penjualObj.alamat_lengkap = payload.alamat_lengkap
        penjualObj.jam_operasional_buka = payload.jam_operasional_buka
        penjualObj.jam_operasional_tutup = payload.jam_operasional_tutup
        penjualObj.save()
    except:
        return app.create_response(
            request,
            {'message': 'Error with database when edit data penjual'},
            status=500
        )
    return {'message': f'success edit data toko for toko id {payload.id_toko}'}

@router.post('edit-pp-penjual/')
def editPhotoProfile(request, id_toko: int = Form(...), file_image: UploadedFile = File(...)):
    if (not PenjualDB.objects.filter(pk=id_toko).exists()):
        return app.create_response(
            request,
            {'message': f'Penjual with toko id {id_toko} not found'},
            status=404
        )
    public_uri = Upload.upload_image(file_image, str(file_image.name).replace(' ', '-'))
    if (public_uri is False):
        return app.create_response(
            request,
            {'message': 'Error when upload process'},
            status=500
        )
    urlGambar = str(public_uri)
    try:
        penjualObj = PenjualDB.objects.get(pk=id_toko)
        penjualObj.logo_toko = urlGambar
        penjualObj.save()
    except:
        return app.create_response(
            request,
            {'message': 'Error with database when update photo profile'},
            status=500
        )
    return {
        'message': f'Success upload image for toko {penjualObj.nama_toko}',
        'url_gambar': urlGambar
    }

@router.get('user/detail/by-id-toko/{id_toko}')
def getUserPenjualbyIdToko(request, id_toko: int):
    userObj = PenjualDB.objects.filter(pk=id_toko).exists()
    if (not userObj):
        return app.create_response(
            request,
            {'message': f'Toko penjual with toko id {id_toko} not found'},
            status=404
        )
    userObj = PenjualDB.objects.get(pk=id_toko)
    responseBody = {
        'id_toko': userObj.pk,
        'logo_toko':  userObj.logo_toko,
        'nama_toko': userObj.nama_toko,
        'rekening': userObj.rekening,
        'metode_pembayaran': userObj.metode_pembayaran,
        'alamat_lengkap': userObj.alamat_lengkap,
        'nomor_telp': userObj.nomor_telp,
        'jam_operasional_buka': userObj.jam_operasional_buka,
        'jam_operasional_tutup': userObj.jam_operasional_tutup,
        'user_account': {
            'id_account': userObj.ID_USER.pk,
            'email': userObj.ID_USER.username,
        }
    }
    return responseBody

@router.get('user/detail/by-id-account/{id_account}')
def getUserPenjualbyIdAccount(request, id_account: int):
    userObj = PenjualDB.objects.filter(ID_USER_id=id_account).exists()
    if (not userObj):
        return app.create_response(
            request,
            {'message': f'Toko penjual with account id {id_account} not found'},
            status=404
        )
    userObj = PenjualDB.objects.get(ID_USER_id=id_account)
    responseBody = {
        'id_toko': userObj.pk,
        'logo_toko':  userObj.logo_toko,
        'nama_toko': userObj.nama_toko,
        'rekening': userObj.rekening,
        'metode_pembayaran': userObj.metode_pembayaran,
        'alamat_lengkap': userObj.alamat_lengkap,
        'nomor_telp': userObj.nomor_telp,
        'jam_operasional_buka': userObj.jam_operasional_buka,
        'jam_operasional_tutup': userObj.jam_operasional_tutup,
        'user_account': {
            'id_account': userObj.ID_USER.pk,
            'email': userObj.ID_USER.username,
        }
    }
    return responseBody

@router.post('add-product/')
def addProduct(request, payload: SchemasBody.ProductAddBody = Form(...), file_image: UploadedFile = File(...)):
    if (not ProdukDB.objects.filter(pk=payload.id_toko).exists()):
        return app.create_response(
            request,
            {'message': f'Toko with id {payload.id_toko} not found'},
            status=404
        )
    public_uri = Upload.upload_image(file_image, str(file_image.name).replace(' ', '-'))
    if (public_uri is False):
        return app.create_response(
            request,
            {'message': 'Error when upload process'},
            status=500
        )
    urlGambar = str(public_uri)
    try:
        productBaru = ProdukDB.objects.create(
            ID_TOKO=PenjualDB.objects.get(pk=payload.id_toko).pk,
            nama_barang=payload.nama_barang,
            deskripsi=payload.deskripsi,
            gambar=urlGambar,
            harga=float(payload.harga)
        )
    except:
        return app.create_response(
            request,
            {'message': 'Error with database when add product'},
            status=500
        )

    return {'message': 'Success add new product'}

@router.get('get-products/{id_toko}', response=List[SchemasBody.ProductsResponse])
def getProducts(request, id_toko: int):
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

@router.post('edit-product/')
def editProduct(request, payload: SchemasBody.EditProductBody = Form(...), file_image: UploadedFile = File(...)):
    if (not ProdukDB.objects.filter(pk=payload.id_product).exists()):
        return app.create_response(
            request,
            {'message': f'product with id {payload.id_product} not found'},
            status=404
        )
    public_uri = Upload.upload_image(file_image, str(file_image.name).replace(' ', '-'))
    if (public_uri is False):
        return app.create_response(
            request,
            {'message': 'Error when upload process'},
            status=500
        )
    urlGambar = str(public_uri)
    try:
        getProduct = ProdukDB.objects.get(pk=payload.id_product)
        getProduct.gambar = urlGambar
        getProduct.nama_barang = payload.nama_barang
        getProduct.harga = float(payload.harga)
        getProduct.deskripsi = payload.deskripsi
        getProduct.save()
    except:
        return app.create_response(
            request,
            {'message': 'Error with database when edit product'},
            status=500
        )
    return {'message': 'edit product success'}

@router.delete('delete-product/{id_product}')
def deleteProduct(request, id_product: int):
    getProduct = ProdukDB.objects.filter(pk=id_product).exists()
    if (not getProduct):
        return app.create_response(
            request,
            {'message': f'product with id {id_product} not found'},
            status=404
        )
    try:
        getProduct = ProdukDB.objects.get(pk=id_product)
        getProduct.delete()
    except:
        return app.create_response(
            request,
            {'message': f'Error with database when delete product with id {id_product}'},
            status=500
        )
    return {'message': 'success delete product'}

@router.get('get-orders/', response=List[SchemasBody.OrderResponse])
def ordersList(request, id_toko: int):
    ordersObj = Orders.objects.filter(ID_TOKO=id_toko)
    return ordersObj

@router.post('accept-order/')
def acceptOrder(request, id_order: int = Form(...)):
    if (not Orders.objects.filter(pk=id_order).exists()):
        return app.create_response(
            request,
            {'message': f'Order with id {id_order} not found'},
            status=404
        )
    orderObj = Orders.objects.get(pk=id_order)
    orderObj.status = 'Diproses'
    orderObj.save()
    return {'message': f'Success Accept order with id {id_order}'}

