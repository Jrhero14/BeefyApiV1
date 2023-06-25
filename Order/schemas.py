from ninja import Schema
from datetime import datetime

class NewOrderBody(Schema):
    ID_PEMBELI: int
    ID_TOKO: int
    ID_BARANG: int
    rekening: str
    catatan: str
    alamat_pengiriman: str
    metode_pembayaran: str
    total_barang: int
    biaya_pengiriman: float
    total_harga: float
    kode_unik: int


class Barang(Schema):
    nama_barang: str
    deskripsi: str
    gambar: str
    harga: float
class OrderProceessResponse(Schema):
    pk: int
    ID_PEMBAYARAN: int
    ID_PEMBELI: int
    ID_TOKO: int
    ID_BARANG: Barang
    total_barang: int
    catatan: str
    alamat_pengiriman: str
    metode_pembayaran: str
    tanggal_order: datetime
    status: str

class OrderBelumDibayarResponse(Schema):
    bukti_bayar: str
    rekening: str
    total_harga: float
    biaya_pengiriman: float
    kode_unik: int
    FK_Order: OrderProceessResponse
    status: str
