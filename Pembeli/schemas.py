from ninja import Schema
from datetime import datetime

class RegisterBody(Schema):
    nama: str = 'Your Name'
    email: str = 'your@email.com'
    password: str = '12345678'


class EditPembeliBody(Schema):
    id_pembeli: str
    nama: str = 'Your name'
    alamat_lengkap: str = 'Your Address'
    nama_penerima: str = 'Your Name Receiver'
    nomor_telp: str = 'Your Phone Number'
    label_alamat: str = 'Your Label Address'


class ScanHistoryResponse(Schema):
    gambar_url: str
    tanggal: datetime
    segar: bool
    level_kesegaran: int
    jenis: str


class StoresResponse(Schema):
    pk: int
    logo_toko: str
    nama_toko: str
    rekening: str
    metode_pembayaran: str
    alamat_lengkap: str
    nomor_telp: str
    jam_operasional_buka: str
    jam_operasional_tutup: str

class ProductsResponse(Schema):
    pk: int
    ID_TOKO: int
    nama_barang: str
    deskripsi: str
    gambar: str
    harga: float