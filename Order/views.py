from ninja import NinjaAPI, Router, Form, File
from ninja.files import UploadedFile
from Order import schemas as SchemasBody
from Order.models import Orders, Pembayaran
from Pembeli.models import PembeliDB
from Penjual.models import PenjualDB, ProdukDB
from typing import List
from Pembeli.views import Upload

# Create your views here.
app = NinjaAPI()
router = Router(
    tags=['Orders']
)

@router.post('new-order/')
def newOrder(request, payload: SchemasBody.NewOrderBody = Form(...)):
    if (not PembeliDB.objects.filter(pk=payload.ID_PEMBELI).exists()):
        return app.create_response(
            request,
            {'message': f'Pembeli with id {payload.ID_PEMBELI} not found when create new order'},
            status=404
        )
    if (not PenjualDB.objects.filter(pk=payload.ID_TOKO).exists()):
        return app.create_response(
            request,
            {'message': f'Toko with id {payload.ID_TOKO} not found when create new order'},
            status=404
        )
    if (not ProdukDB.objects.filter(pk=payload.ID_BARANG).exists()):
        return app.create_response(
            request,
            {'message': f'Product with id {payload.ID_BARANG} not found when create new order'},
            status=404
        )

    try:
        pembayaranObj = Pembayaran.objects.create(
            bukti_bayar='None',
            rekening=payload.rekening,
            total_harga=float(payload.total_harga),
            biaya_pengiriman=float(payload.biaya_pengiriman),
            kode_unik=int(payload.kode_unik),
            status='M'
        )
        newOrderObj = Orders.objects.create(
            ID_PEMBAYARAN=pembayaranObj.pk,
            ID_PEMBELI=int(payload.ID_PEMBELI),
            ID_TOKO=int(payload.ID_TOKO),
            ID_BARANG=ProdukDB.objects.get(pk=int(payload.ID_BARANG)),
            catatan=payload.catatan,
            alamat_pengiriman=payload.alamat_pengiriman,
            metode_pembayaran=payload.metode_pembayaran,
            total_barang=payload.total_barang
        )
        pembayaranObj.FK_Order = newOrderObj
        pembayaranObj.save()
    except:
        return app.create_response(
            request,
            {'message': f'Error with database when create new order'},
            status=500
        )

    return {
        'message': 'success add order',
        'id_order': newOrderObj.pk,
        'data_pembayaran': {
            'bank': newOrderObj.metode_pembayaran,
            'nomor_rekening': pembayaranObj.rekening,
            'atas_nama': PenjualDB.objects.get(pk=newOrderObj.ID_TOKO).nama_toko,
            'total_pembayaran': pembayaranObj.total_harga
        }
    }

@router.post('upload-bukti/')
def uploadBuktiBayar(request, id_order: int = Form(...), file_image: UploadedFile = File(...)):
    if (not Orders.objects.filter(pk=id_order).exists()):
        return app.create_response(
            request,
            {'message': f'Order with id {id_order} not found'},
            status=404
        )
    orderObj = Orders.objects.get(pk=id_order)
    if (not Pembayaran.objects.filter(pk=orderObj.ID_PEMBAYARAN).exists()):
        return app.create_response(
            request,
            {'message': f'Pembayaran with id {orderObj.ID_PEMBAYARAN} not found'},
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
        pembayaranObj = Pembayaran.objects.get(pk=orderObj.ID_PEMBAYARAN)
        pembayaranObj.bukti_bayar = urlGambar
        pembayaranObj.status = 'T'
        pembayaranObj.save()
    except:
        return app.create_response(
            request,
            {'message': f'Error with database when upload bukti bayar'},
            status=500
        )

    return {'message': 'success upload bukti bayar'}

@router.get('order-in-process/', response=List[SchemasBody.OrderProceessResponse])
def orderProcess(request, id_pembeli: int = None, id_toko:int = None):
    if (id_toko is None):
        orderProcessObj = Orders.objects.filter(ID_PEMBELI=id_pembeli, status='Diproses')
        return orderProcessObj
    elif (id_pembeli is None):
        orderProcessObj = Orders.objects.filter(ID_TOKO=id_toko, status='Diproses')
        return orderProcessObj

@router.get('order-in-waiting/', response=List[SchemasBody.OrderProceessResponse])
def orderWaiting(request, id_pembeli: int = None, id_toko:int = None):
    if (id_toko is None):
        orderProcessObj = Orders.objects.filter(ID_PEMBELI=id_pembeli, status='Menunggu')
        return orderProcessObj
    elif (id_pembeli is None):
        orderProcessObj = Orders.objects.filter(ID_TOKO=id_toko, status='Menunggu')
        return orderProcessObj

@router.get('order-in-complete/', response=List[SchemasBody.OrderProceessResponse])
def orderComplete(request, id_pembeli: int = None, id_toko:int = None):
    if (id_toko is None):
        orderProcessObj = Orders.objects.filter(ID_PEMBELI=id_pembeli, status='Selesai')
        return orderProcessObj
    elif (id_pembeli is None):
        orderProcessObj = Orders.objects.filter(ID_TOKO=id_toko, status='Selesai')
        return orderProcessObj

@router.get('detail/{id_order}')
def getOrderDetail(request, id_order: int):
    if (not Orders.objects.filter(pk=id_order).exists()):
        return app.create_response(
            request,
            {'message': f'Order with id {id_order}'},
            status=404
        )

    orderObj = Orders.objects.get(pk=id_order)
    tokoObj = PenjualDB.objects.get(pk=orderObj.ID_TOKO)
    pembayaranObj = Pembayaran.objects.get(pk=orderObj.ID_PEMBAYARAN)
    pembeliObj = PembeliDB.objects.get(pk=orderObj.ID_PEMBELI)

    responseBody = {
        'message': f'Success get detail order for id order {id_order}',
        'Barang': {
            'nama barang': orderObj.ID_BARANG.nama_barang,
            'harga barang': orderObj.ID_BARANG.harga,
            'tanggal pesanan': orderObj.tanggal_order.date(),
            'catatan': orderObj.catatan,
            'total barang': orderObj.total_barang
        },

        'Bukti pembayaran': pembayaranObj.bukti_bayar,

        'Toko': {
            'logo toko': tokoObj.logo_toko,
            'nama toko': tokoObj.nama_toko,
            'nomor telepon toko': tokoObj.nomor_telp,
            'alamat toko': tokoObj.alamat_lengkap
        },

        'Detail pembeli': {
            'nama_penerima': pembeliObj.nama_penerima,
            'alamat': pembeliObj.alamat_lengkap,
            'nomor telepon pembeli': pembeliObj.nomor_telp
        },

        'Detail rincian': {
            'harga barang': orderObj.ID_BARANG.harga,
            'biaya pengiriman': pembayaranObj.biaya_pengiriman,
            'kode unik': pembayaranObj.kode_unik,
            'total harga': pembayaranObj.total_harga
        }
    }

    return responseBody

@router.get('order-belum-bayar/', response=List[SchemasBody.OrderBelumDibayarResponse])
def orderBelumBayar(request, id_pembeli: int = None, id_toko: int = None):
    if (id_toko is None):
        orderObj = Pembayaran.objects.filter(FK_Order__ID_PEMBELI=id_pembeli, status='M')
        return orderObj
    elif (id_pembeli is None):
        orderObj = Pembayaran.objects.filter(FK_Order__ID_TOKO=id_toko, status='M')
        return orderObj

@router.get('order-sudah-bayar/', response=List[SchemasBody.OrderBelumDibayarResponse])
def orderSudahBayar(request, id_pembeli: int = None, id_toko: int = None):
    if (id_toko is None):
        orderObj = Pembayaran.objects.filter(FK_Order__ID_PEMBELI=id_pembeli, status='T')
        return orderObj
    elif (id_pembeli is None):
        orderObj = Pembayaran.objects.filter(FK_Order__ID_TOKO=id_toko, status='T')
        return orderObj

@router.get('orders/', response=List[SchemasBody.OrderProceessResponse])
def orders(request, id_pembeli: int = None, id_toko:int = None):
    ordersObj = Orders.objects.filter(ID_PEMBELI=id_pembeli)
    return ordersObj


