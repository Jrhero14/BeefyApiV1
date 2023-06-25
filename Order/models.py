from django.db import models
from Penjual.models import ProdukDB

# Create your models here.
class Orders(models.Model):
    ID_PEMBAYARAN = models.IntegerField()
    ID_PEMBELI = models.IntegerField()
    ID_TOKO = models.IntegerField()
    ID_BARANG = models.ForeignKey(
        ProdukDB,
        on_delete=models.SET_NULL,
        null=True
    )
    total_barang = models.IntegerField(null=True)
    catatan = models.CharField(max_length=255)
    alamat_pengiriman = models.TextField()
    metode_pembayaran = models.CharField(max_length=10)
    tanggal_order = models.DateTimeField(auto_now=True)

    STATUS_ORDER_CHOICES = (
        ('Menunggu', 'Menunggu Diterima Seller'),
        ('Diproses', 'Diproses oleh kurir'),
        ('Selesai', 'Pesanan Selesai')
    )
    status = models.CharField(max_length=80, choices=STATUS_ORDER_CHOICES, default='Menunggu')

    def __str__(self):
        return f'{self.id} | {self.tanggal_order}'

class Pembayaran(models.Model):
    bukti_bayar = models.TextField()
    rekening = models.CharField(max_length=15)
    total_harga = models.FloatField()
    biaya_pengiriman = models.FloatField()
    kode_unik = models.IntegerField()
    FK_Order = models.ForeignKey(
        Orders,
        on_delete=models.SET_NULL,
        null=True
    )

    STATUS_PEMBAYARAN_CHOICES = (
        ('M', 'Menunggu'),
        ('T', 'Dibayar')
    )
    status = models.CharField(max_length=1, choices=STATUS_PEMBAYARAN_CHOICES, default='Menunggu')

    def __str__(self):
        return f'{self.id} | {self.kode_unik}'
