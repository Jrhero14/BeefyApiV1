from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class PenjualDB(models.Model):
    logo_toko = models.TextField()
    nama_toko = models.CharField(max_length=50, unique=True)
    rekening = models.CharField(max_length=12)
    metode_pembayaran = models.CharField(max_length=20)
    alamat_lengkap = models.TextField()
    nomor_telp = models.CharField(max_length=15)
    jam_operasional_buka = models.CharField(max_length=6)
    jam_operasional_tutup = models.CharField(max_length=6)
    ID_USER = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.pk} | {self.nama_toko}'

class ProdukDB(models.Model):
    ID_TOKO = models.IntegerField()
    nama_barang = models.CharField(max_length=255)
    deskripsi = models.TextField()
    gambar = models.TextField()
    harga = models.FloatField()

    def __str__(self):
        return f'{self.pk} | {self.nama_barang}'

