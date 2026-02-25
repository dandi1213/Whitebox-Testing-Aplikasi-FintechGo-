import pytest
from datetime import datetime, timedelta
from app import validate_nama, validate_nominal, validate_tanggal, hitung_total
from app import app as flask_app 

# ==========================================
# 1. TEST FUNGSI validate_nama
# ==========================================
def test_nama_path1():
    assert validate_nama("")[0] == False
def test_nama_path2():
    assert validate_nama("A" * 51)[0] == False
def test_nama_path3():
    assert validate_nama("Liburan@Bali!")[0] == False
def test_nama_path4():
    assert validate_nama("Beli Mobil 2026")[0] == True

# ==========================================
# 2. TEST FUNGSI validate_nominal
# ==========================================
def test_nominal_path1():
    assert validate_nominal("seratus ribu") == (False, 'Target nominal harus berupa angka.')

def test_nominal_path2():
    assert validate_nominal(" 50000 ") == (False, 'Target nominal minimal Rp 100.000.')

def test_nominal_path3():
    assert validate_nominal("150000000 ") == (False, 'Target nominal maksimal Rp 100.000.000.')

def test_nominal_path4():
    assert validate_nominal("5000000") == (True, 5000000)

# ==========================================
# 3. TEST FUNGSI validate_tanggal
# ==========================================
def test_tanggal_path1():
    assert validate_tanggal("25-02-2026") == (False, 'Format tanggal tidak valid.')

def test_tanggal_path2():
    assert validate_tanggal("2025-01-01") == (False, 'Tanggal mulai tidak boleh kurang dari hari ini.')

def test_tanggal_path3():
    assert validate_tanggal("2028-01-01") == (False, 'Tanggal mulai tidak boleh lebih dari 1 tahun ke depan.')

def test_tanggal_path4():
    assert validate_tanggal("2026-05-01") == (True, datetime.strptime("2026-05-01", "%Y-%m-%d").date())

# ==========================================
# 4. TEST FUNGSI hitung_total
# ==========================================
def test_total_path1():
    res = hitung_total(1200000, 12, 'Reguler', True, 'Dana Darurat')
    assert res['error_asuransi'] == True

def test_total_path2():
    res = hitung_total(1200000, 6, 'Reguler', False, 'Gadget')
    assert res['diskon'] == 0
    assert res['biaya_asuransi'] == 0

def test_total_path3():
    res = hitung_total(1200000, 12, 'Premium', False, 'Liburan')
    assert res['diskon'] == 10000
    assert res['biaya_asuransi'] == 0

def test_total_path4():
    res = hitung_total(1200000, 12, 'Reguler', True, 'Gadget')
    assert res['biaya_asuransi'] == 60000
    assert res['diskon'] == 0

# ==========================================
# 5. TEST ROUTING WEB (FLASK) 
# ==========================================
@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_halaman_index(client):
    response = client.get('/')
    assert response.status_code == 200

def test_halaman_list(client):
    response = client.get('/list')
    assert response.status_code == 200

def test_proses_create_target_valid(client):
    besok = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    form_data = {
        'nama': 'Liburan ke Jepang',
        'kategori': 'Liburan',
        'nominal': '15000000',
        'jangka_waktu': '12',
        'tanggal_mulai': besok,
        'status': 'Reguler',
        'asuransi': 'on'
    }
    response = client.post('/create', data=form_data)
    assert response.status_code == 200 

def test_proses_create_target_invalid_nama(client):
    form_data = {
        'nama': '', 
        'kategori': 'Gadget',
        'nominal': '1000000',
        'jangka_waktu': '3',
        'tanggal_mulai': '2026-12-12'
    }
    response = client.post('/create', data=form_data)
    assert response.status_code == 302

def test_proses_create_target_invalid_nominal(client):
    form_data = {
        'nama': 'Beli HP', 
        'kategori': 'Gadget',
        'nominal': '50000', 
        'jangka_waktu': '3',
        'tanggal_mulai': '2026-12-12'
    }
    response = client.post('/create', data=form_data)
    assert response.status_code == 302

def test_proses_create_target_invalid_waktu(client):
    besok = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    form_data = {
        'nama': 'Beli HP', 
        'kategori': 'Gadget',
        'nominal': '1500000',
        'jangka_waktu': '99', 
        'tanggal_mulai': besok
    }
    response = client.post('/create', data=form_data)
    assert response.status_code == 302

def test_proses_create_target_invalid_tanggal(client):
    kemarin = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    form_data = {
        'nama': 'Beli HP', 
        'kategori': 'Gadget',
        'nominal': '1500000',
        'jangka_waktu': '3',
        'tanggal_mulai': kemarin 
    }
    response = client.post('/create', data=form_data)
    assert response.status_code == 302

def test_proses_create_target_error_asuransi(client):
    besok = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    form_data = {
        'nama': 'Dana Jaga Jaga', 
        'kategori': 'Dana Darurat', 
        'nominal': '5000000',
        'jangka_waktu': '12',
        'tanggal_mulai': besok,
        'asuransi': 'on'
    }
    response = client.post('/create', data=form_data)
    assert response.status_code == 302