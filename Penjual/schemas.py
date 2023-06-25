from ninja import Schema
from datetime import datetime

class RegisterBody(Schema):
    nama_toko: str
    nomor_telepon: str
    email: str
    password: str

class EditPenjualBody(Schema):
    id_toko: int
    alamat_lengkap: str
    jam_operasional_buka: str
    jam_operasional_tutup: str
    metode_pembayaran: str
    rekening: str

class ProductAddBody(Schema):
    id_toko: int
    nama_barang: str
    deskripsi: str
    harga: float

class ProductsResponse(Schema):
    pk: int
    ID_TOKO: int
    gambar: str
    nama_barang: str
    deskripsi: str
    harga: float

class EditProductBody(Schema):
    id_product: int
    nama_barang: str
    deskripsi: str
    harga: float


class Barang(Schema):
    nama_barang: str
    deskripsi: str
    gambar: str
    harga: float
class OrderResponse(Schema):
    pk: int
    ID_PEMBAYARAN: int
    ID_PEMBELI: int
    ID_TOKO: int
    ID_BARANG: Barang
    catatan: str
    alamat_pengiriman: str
    metode_pembayaran: str
    tanggal_order: datetime
    status: str

