import random
import rest_framework_simplejwt.exceptions
from django.contrib.auth.models import User

from ninja import Router
from rest_framework_simplejwt.serializers import TokenVerifySerializer, TokenRefreshSerializer
from BeefyRest import schemas as SchemasBody
from django.shortcuts import render
from ninja import NinjaAPI, Form
from Penjual.models import PenjualDB, ProdukDB
from Pembeli.models import PembeliDB
from functools import wraps
from django.core.files.storage import default_storage

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.username
        token['tipe'] = 'penjual' if user.is_staff else 'pembeli'

        return token

def createDummy():
    # Dummy Account Pembeli
    User1 = User.objects.create(
        username='Jeremi@gmail.com',
        email='account@email.com',
    )
    User1.set_password('12345678')
    User1.save()

    Pembeli1 = PembeliDB.objects.create(
        nama='Jeremi Herodian',
        alamat_lengkap='Denpasar Selatan',
        nama_penerima='Jeremi',
        nomor_telp='081386049701',
        label_alamat='Rumah',
        photo_profile='https://i.ibb.co/945fj8Q/image.png',

        ID_USER=User1
    )

    User2 = User.objects.create(
        username='Udin@gmail.com',
        email='account@email.com',
        password='12345678'
    )
    User2.set_password('12345678')
    User2.save()

    Pembeli2 = PembeliDB.objects.create(
        nama='Udin Pertama',
        alamat_lengkap='Denpasar Utara',
        nama_penerima='Udin',
        nomor_telp='08123456789',
        label_alamat='Kantor',
        photo_profile='https://i.ibb.co/945fj8Q/image.png',

        ID_USER=User2
    )

    # Dummy Account Penjual
    User3 = User.objects.create(
        username='Makmur@gmail.com',
        email='account@email.com'
    )
    User3.set_password('12345678')
    User3.is_staff = True
    User3.save()

    Penjual1 = PenjualDB.objects.create(
        logo_toko='https://i.ibb.co/h9cfYrn/image.jpg',
        nama_toko='Makmur Abadi',
        rekening='354645864',
        metode_pembayaran='Mandiri',
        alamat_lengkap='Jakarta Selatan',
        nomor_telp='09123667896',
        jam_operasional_buka='07:00',
        jam_operasional_tutup='22:00',

        ID_USER=User3
    )

    User4 = User.objects.create(
        username='Sukses@gmail.com',
        email='account@email.com'
    )
    User4.set_password('12345678')
    User4.is_staff = True
    User4.save()

    Penjual2 = PenjualDB.objects.create(
        logo_toko='https://i.ibb.co/zH1Cwqb/image.png',
        nama_toko='Sukses Jaya',
        rekening='789645149',
        metode_pembayaran='BCA',
        alamat_lengkap='Surabaya',
        nomor_telp='0912345678',
        jam_operasional_buka='09:00',
        jam_operasional_tutup='23:00',

        ID_USER=User4
    )

    # Dummy Product Penjual
    produks = [
        [
            Penjual1.pk,
            'Wagyu A5',
            'Daging Wagyu A5 Adalah daging dengan tekstur marbling lemak paling banyak. Daging ini berasal dari Jepang dengan kualitas yang premium',
            'https://i.ibb.co/GR4WZG0/image.jpg',
            2500000.0
        ],
        [
            Penjual1.pk,
            'Daging Sapi Bandung',
            'Daging sapi Bandung kualitas terbaik, berasal dari ternak sapi yang berlokasi di Bandung dan memiliki sertifikasi Halal Nasional',
            'https://i.ibb.co/2hmR6Jy/image.jpg',
            500000.0
        ],
        [
            Penjual1.pk,
            'Sapi Kurban',
            'Sapi kurban untuk hari raya idul adha',
            'https://i.ibb.co/bN1vTGB/image.jpg',
            8000000.0
        ],

        [
            Penjual2.pk,
            'Daging Sapi Reguler',
            'Daging sapi biasa, cocok untuk masakan rumah dan rumah makan.',
            'https://i.ibb.co/pWjnTx8/image.jpg',
            400000.0
        ],
        [
            Penjual2.pk,
            'Daging Sapi GOLD',
            'Daging sapi dengan taburan emas asli nih boss senggol dong',
            'https://i.ibb.co/TT2wpN4/image.jpg',
            3500000.0
        ],
    ]

    for produk in produks:
        buatProduk = ProdukDB.objects.create(
            ID_TOKO=produk[0],
            nama_barang=produk[1],
            deskripsi=produk[2],
            gambar=produk[3],
            harga=produk[4]
        )
        print(f'Membuat produk {buatProduk.pk} | {buatProduk.nama_barang} Sukses')

def admin_decorator(view_function):
    @wraps(view_function)
    def wrap(request):
        # Any preprocessing conditions..etc.
        if (not User.objects.filter(username='admin').exists()):
            adminObj = User.objects.create(
                username='admin',
                email='admin@email.com'
            )
            adminObj.set_password('mimin123')
            adminObj.is_staff = True
            adminObj.is_superuser = True
            adminObj.save()
            createDummy()

        return view_function(request)
    return wrap

@admin_decorator
def index(request):
    print(default_storage.__class__)
    quotes = [
        "Beef. Yes. Roast beef. It's the Swedish term for beef that is roasted",
        "Not eating meat is a decision. Eating meat is an instinct.",
        "Live life. Eat meat.",
        "No Vegans, just eat meat",
        "Meat is my therapy.",
        "You can't buy happiness, but you can buy meat and that's basically the same thing.",
        "Heaven sends us good meat, but the Devil sends us cooks.",
        "First we eat meat, then we do everything else.",
        "Becoming a vegetarian is just a big mis-steak.",
        "You had me at meat tornado."
    ]
    contexs = {
        'quote': random.choice(quotes)
    }
    return render(request=request, template_name='index.html', context=contexs)


# Authentication Router
router = Router(
    tags=['Authentication']
)
app = NinjaAPI()


def validTokenCheck(token: str) -> bool:
    validasi = TokenVerifySerializer()
    try:
        validasi.validate({
            "token": token
        })
        return True
    except:
        return False


@router.post("/login")
def login(request, payload: SchemasBody.LoginBody = Form(...)):
    try:
        obtainObj = MyTokenObtainPairSerializer()
        token = obtainObj.validate(attrs={'username': payload.email, 'password': payload.password})
    except:
        return app.create_response(
            request,
            {'message': 'Wrong email or password'},
            status=401
        )
    userObj = User.objects.get(username=payload.email)
    additional = {
        'id_account': userObj.pk,
        'jenis_akun': 'penjual' if userObj.is_staff else 'pembeli'
    }
    if (userObj.is_staff):
        akunObj = PenjualDB.objects.get(ID_USER_id=userObj.pk)
        additional['id_toko'] = akunObj.pk
    else:
        akunObj = PembeliDB.objects.get(ID_USER_id=userObj.pk)
        additional['id_pembeli'] = akunObj.pk

    return additional | token


@router.post('/refresh-token')
def refresh_token(request, payload: SchemasBody.RefreshBody = Form(...)):
    token = TokenRefreshSerializer()
    try:
        new_token = token.validate({
            'refresh': payload.token_refresh
        })
    except rest_framework_simplejwt.exceptions.TokenError:
        return app.create_response(
            request,
            {
                'message': 'Token has wrong type or expired or invalid, please login again to get refresh and access token'},
            status=400
        )

    return {'token_access': str(new_token.get('access'))}


@router.post("/check-valid-token")
def valid(request, payload: SchemasBody.Validbody = Form(...)):
    if (validTokenCheck(token=payload.token)):
        return {'message': 'yes token is valid'}
    else:
        return app.create_response(
            request,
            {'message': 'token invalid'},
            status=401
        )


@router.post('forgot-password/')
def forgot_password(request, payload: SchemasBody.ForgotPasswordBody = Form(...)):
    if (not User.objects.filter(username=payload.email).exists()):
        return app.create_response(
            request,
            {'message': 'account not found'},
            status=404
        )
    user = User.objects.get(username=payload.email)
    user.set_password(payload.new_password)
    user.save()
    return {'message': 'change password success'}
