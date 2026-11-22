# Fase 3: Desain

Halaman kerja untuk Fase 3. Tujuannya satu: semua keputusan desain tertulis dan konsisten sebelum kita menulis kode di Sprint 0. Sub-tahap dikerjakan berurutan, dimulai dari 3.1.

## Progres Fase 3

- [x] 3.1 Arsitektur sistem
- [x] 3.2 Desain database (ERD)
- [x] 3.3 Desain API (endpoint, format request/response, kode error)
- [x] 3.4 Alur autentikasi (login, refresh, logout, reset password)
- [x] 3.5 Threat modeling
- [x] 3.6 Desain UI (wireframe)
- [x] 3.7 Struktur proyek dan app Django

**Gerbang:** semua dokumen desain selesai dan konsisten satu sama lain.

## 3.1 Arsitektur Sistem

Auth Service adalah satu server API Django yang berdiri sendiri. Klien mana pun, web, mobile, atau aplikasi lain, hanya berbicara dengannya lewat HTTP dan JSON, dan tidak pernah menyentuh database secara langsung.

&#91;embedded content: arsitektur sistem · 2 jenis klien, API, database, email\]

Baca dari atas: klien memanggil API lewat HTTP dan JSON, lapisan keamanan memeriksa tiap permintaan sebelum sampai ke endpoint, dan hanya API yang membaca database atau mengirim email.

### Komponen

| Komponen | Teknologi | Tugas |
| --- | --- | --- |
| Frontend contoh | HTML + JavaScript (fetch) | Menampilkan form login dan daftar, menyimpan token, mengirim token di setiap request |
| Aplikasi klien lain | Bebas | Memakai Auth Service untuk mengetahui identitas dan role pengguna |
| Auth Service API | Django + DRF | Registrasi, login, refresh token, logout, profil, ganti dan reset password |
| Lapisan keamanan | simplejwt, throttling DRF, validator password, CORS | Menerbitkan dan memeriksa token, membatasi percobaan login, membatasi domain klien |
| Database | SQLite (development), PostgreSQL di Neon (production) | Menyimpan user, refresh token yang diterbitkan, dan yang dicabut |
| Layanan email | Console backend (development), SMTP (nanti) | Mengirim tautan reset password |

### Aliran umum

1. Klien mengirim email dan password ke endpoint login.
2. API memeriksa data dan hash password di database.
3. Jika cocok, API mengembalikan access token (pendek) dan refresh token (panjang).
4. Klien mengirim access token di header Authorization pada setiap request berikutnya.
5. Ketika access token habis, klien menukar refresh token dengan access token baru.
6. Saat logout, refresh token dimasukkan ke blacklist.

### Keputusan arsitektur

- **Satu service, bukan banyak:** untuk versi 1 semua fitur berada dalam satu proyek Django. Cukup untuk belajar, dan mudah dipecah nanti.
- **Access token stateless:** API tidak mencari sesi di database pada tiap request. Hanya refresh token yang dicek ke database (untuk blacklist).
- **Aplikasi klien lain:** di versi 1 mereka memeriksa identitas dengan memanggil endpoint cek identitas (US-10), supaya kunci rahasia tetap hanya di Auth Service. Penandatanganan asimetris (RS256) dipertimbangkan saat menuju SSO.
- **Frontend dan backend terpisah:** dipisah domainnya, sehingga CORS wajib dikonfigurasi dengan daftar domain yang diizinkan.

### Pertanyaan terbuka untuk 3.1

- [x] Tempat penyimpanan token di frontend contoh: memori JavaScript, atau cookie httpOnly? (diputuskan di 3.5: refresh token di body dan disimpan frontend untuk versi 1, cookie httpOnly sebagai peningkatan di Fase 9)
- [x] Format versi API: `/api/v1/...` sejak awal? (disetujui: ya, supaya klien lama tetap berjalan saat ada perubahan besar di versi berikutnya)

## 3.2 Desain Database (ERD)

Database memakai tiga tabel: users, outstanding\_token, dan blacklisted\_token. Satu user bisa memiliki banyak refresh token, dan token yang dicabut dicatat di tabel terpisah.

&#91;embedded content: ERD · 3 tabel, 2 relasi\]

Garis menunjukkan relasi: satu user ke banyak token (1 ke N), dan satu token ke paling banyak satu catatan pencabutan (1 ke 0..1). Kolom is\_staff dan is\_superuser dibutuhkan Django admin dan tidak dipakai API.

### Keputusan desain

- **Login dengan email:** tidak ada kolom username. Email yang unik menjadi identitas login, lewat custom user model yang dibuat di Sprint 0 sebelum migrasi pertama.
- **Password:** hanya hash yang disimpan (PBKDF2 bawaan Django), dan tidak pernah muncul di respons API.
- **Kolom role:** dipilih daripada hanya is\_staff karena endpoint cek identitas (US-10) perlu mengirim role, dan peran baru lebih mudah ditambah. Nilai awal: user dan admin.
- **Token reset password tidak disimpan:** memakai pembuat token reset bawaan Django yang kedaluwarsa otomatis (US-07), sehingga tidak perlu kolom atau tabel tambahan.
- **Ditunda ke tahap berikutnya:** verifikasi email (US-11) dan log aktivitas login (US-12), jadi kolom dan tabelnya belum ada di versi 1.
- **Tabel token dari simplejwt:** penerbitan dan pencabutan token dicatat di dua tabel terpisah. Nama kolom dicek ulang di dokumentasi saat Sprint 2.

### Pertanyaan terbuka untuk 3.2

- [x] Apakah kolom is\_staff tetap dipertahankan untuk Django admin site, atau admin cukup lewat API? (disetujui: is\_staff dipertahankan hanya untuk Django admin site, role menjadi sumber kebenaran untuk API)
- [x] Tabel token simplejwt menyimpan teks token. Apakah itu aman? (diputuskan di 3.5: dicek di Sprint 2, jika teks asli maka dibersihkan berkala dan akses database dibatasi)

## 3.3 Desain API

Semua endpoint memakai awalan /api/v1/auth/ dan bertukar data dalam JSON. Tiap endpoint dikenali dari method dan URL-nya.

### Daftar endpoint (fitur Must)

| Method | URL | Tujuan |
| --- | --- | --- |
| POST | /api/v1/auth/register/ | Membuat akun baru (US-01) |
| POST | /api/v1/auth/login/ | Login dengan email dan password (US-02) |
| POST | /api/v1/auth/token/refresh/ | Menukar refresh token dengan access token baru (US-03) |
| POST | /api/v1/auth/logout/ | Logout dan mencabut refresh token (US-04) |
| GET | /api/v1/auth/profile/ | Melihat profil sendiri (US-05) |
| PATCH | /api/v1/auth/profile/ | Mengubah profil sendiri (US-05) |
| POST | /api/v1/auth/password/change/ | Ganti password saat sudah login (US-06) |
| POST | /api/v1/auth/password/reset/request/ | Meminta tautan reset lewat email, langkah 1 (US-07) |
| POST | /api/v1/auth/password/reset/confirm/ | Memasukkan password baru dengan token dari email, langkah 2 (US-07) |

### Contoh format: login (US-02)

Request:

```json
{
  "email": "rokhim@example.com",
  "password": "passwordRahasia123"
}
```

Respons sukses, kode 200:

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "rokhim@example.com",
    "name": "Imam Rokhim",
    "role": "user"
  }
}
```

Respons gagal, kode 401:

```json
{
  "detail": "No active account found with the given credentials"
}
```

### Format semua endpoint

Kolom "Login?" berarti endpoint itu wajib memakai header Authorization dengan access token.

| Endpoint | Login? | Request | Respons sukses | Respons gagal |
| --- | --- | --- | --- | --- |
| POST /register/ | Tidak | `{"email": "...", "name": "...", "password": "..."}` | `201` + `{"id": 2, "email": "...", "name": "...", "role": "user"}` | `400` + `{"email": ["user with this email already exists."]}` |
| POST /login/ | Tidak | email dan password (contoh di atas) | `200` + refresh, access, dan user (contoh di atas) | `401` pesan generik; `429` jika terlalu sering gagal |
| POST /token/refresh/ | Tidak | `{"refresh": "..."}` | `200` + `{"access": "..."}` | `401` + `{"detail": "Token is invalid or expired"}` |
| POST /logout/ | Ya | `{"refresh": "..."}` | `204`, tanpa isi respons | `401` + `{"detail": "Token is invalid or expired"}` |
| GET /profile/ | Ya | tanpa isi | `200` + `{"id": 1, "email": "...", "name": "...", "role": "user"}` | `401` + `{"detail": "Authentication credentials were not provided."}` |
| PATCH /profile/ | Ya | `{"name": "Nama Baru"}` | `200` + profil terbaru, bentuknya sama dengan GET | `400` + `{"name": ["This field may not be blank."]}` |
| POST /password/change/ | Ya | `{"old_password": "...", "new_password": "..."}` | `204`, tanpa isi respons | `400` + `{"old_password": ["Wrong password."]}` atau pesan validator di new\_password |
| POST /password/reset/request/ | Tidak | `{"email": "..."}` | `200` + `{"detail": "If the email is registered, a reset link has been sent."}`, selalu sama | `400` hanya jika email kosong atau formatnya salah |
| POST /password/reset/confirm/ | Tidak | `{"uid": "...", "token": "...", "new_password": "..."}` | `200` + `{"detail": "Password has been reset."}` | `400` + `{"detail": "Invalid or expired reset link."}` atau pesan validator di new\_password |

### Aturan umum

- **Header login:** endpoint bertanda Ya memakai header `Authorization: Bearer <access token>`.
- **Bentuk error:** error validasi (400) memakai nama field sebagai kunci, error lain memakai kunci detail.
- **Password:** tidak pernah muncul di respons, termasuk hash-nya.
- **Profil:** hanya name yang bisa diubah. Email dan role tidak bisa diubah lewat endpoint ini.
- **Reset password:** pesan selalu sama (US-07). Sebaliknya, registrasi menyebut email sudah terdaftar (US-01), sehingga selisih ini dicatat untuk 3.5.
- **Reset password butuh uid:** token reset bawaan Django dihitung dari data user, jadi tautan di email membawa uid dan token.

### Kode status dan bentuk error

| Kode | Arti | Dipakai di |
| --- | --- | --- |
| 200 | Berhasil, ada isi respons | login, refresh, profil, reset password |
| 201 | Data baru dibuat | registrasi |
| 204 | Berhasil, tanpa isi respons | logout, ganti password |
| 400 | Data tidak valid: kosong, format salah, password lemah, email sudah terdaftar | registrasi, profil, ganti dan reset password |
| 401 | Identitas tidak valid: login salah, belum login, token kedaluwarsa atau dicabut | login, refresh, logout, profil, ganti password |
| 403 | Sudah login tetapi tidak berhak (belum dipakai di fitur Must, muncul di fitur admin) | Sprint 3 ke atas |
| 429 | Terlalu banyak percobaan (US-08 untuk login, diperluas di 3.5 ke registrasi dan reset password langkah 1) | login, registrasi, reset password langkah 1 |
| 500 | Error server tak terduga, pesan tidak boleh membuka detail teknis | semua endpoint |

### Keputusan 3.3

- **Versi API:** awalan /api/v1/ dipakai sejak awal.
- **Login gagal:** kode 401 dengan pesan yang sama untuk email salah, password salah, dan akun tidak aktif, supaya penyerang tidak bisa menebak email yang terdaftar.
- **Nama field:** harus sama dengan nama kolom di ERD (misalnya name, bukan nama\_lengkap).
- **Password:** tidak pernah muncul di respons.
- **Cek identitas (US-10):** di versi 1 aplikasi klien memakai GET /api/v1/auth/profile/ dengan access token pengguna. Endpoint khusus dibuat saat US-10 dikerjakan.

### Pertanyaan terbuka untuk 3.3

- [x] PUT atau PATCH untuk mengubah profil? (disetujui: PATCH, karena hanya sebagian data yang diubah dan klien tidak perlu mengirim semua kolom)
- [x] Format respons login memuat refresh token di body. Diputuskan di 3.5: format ini dipakai untuk versi 1, dan baru berubah jika cookie httpOnly dipilih di Fase 9.
- [x] Format request, respons, dan kode error semua endpoint sudah ditulis di atas dan disetujui.

* [x] Pesan registrasi yang menyebut email sudah terdaftar memungkinkan orang menebak email yang punya akun. US-01 memintanya. Diputuskan di 3.5: dipertahankan, dengan throttling di endpoint registrasi.
* [x] Setelah ganti atau reset password, apakah semua refresh token lama user itu ikut dicabut? (diputuskan di 3.5: ya)

## 3.4 Alur Autentikasi

Empat alur berikut menunjukkan siapa berbicara dengan siapa dan apa yang dicek di database. Panah putus-putus adalah jawaban.

### Login (US-02)

&#91;embedded content: alur login\]

API tidak menyimpan access token. Yang dicatat di database hanya refresh token yang diterbitkan.

### Refresh token (US-03)

&#91;embedded content: alur refresh token\]

Access token baru dibuat tanpa menyentuh password. Satu-satunya pemeriksaan ke database adalah daftar pencabutan.

### Logout (US-04)

&#91;embedded content: alur logout\]

Access token tidak bisa dicabut karena tidak dicek ke database, jadi umurnya dibuat pendek.

### Reset password (US-07)

&#91;embedded content: alur reset password\]

Token reset tidak disimpan di database. Django menghitungnya dari data user, sehingga token otomatis tidak berlaku lagi setelah password berubah. Setelah password disimpan, semua refresh token milik user itu juga dicabut (keputusan 3.5), dan langkah yang sama berlaku untuk ganti password.

### Keputusan 3.4

- **Dua token:** access token stateless dan berumur pendek (usulan 15 menit), refresh token berumur 7 hari. Logout hanya mencabut refresh token.
- **Pemeriksaan database:** hanya refresh token yang dicek ke daftar pencabutan.
- **Pesan yang tidak membocorkan:** login gagal memakai pesan generik (US-02), dan reset password selalu merespons sama (US-07).

### Pertanyaan terbuka untuk 3.4

- [x] Refresh token dikirim di body respons (seperti contoh login) atau di cookie httpOnly? Diputuskan di 3.5: di body untuk versi 1, jadi diagram login dan refresh tetap seperti di atas.

## 3.5 Threat Modeling

Threat modeling menjawab empat hal: apa yang dilindungi, siapa penyerangnya, bagaimana caranya, dan apa penangkalnya. Yang dilindungi di proyek ini adalah akun pengguna, password, dan token. Penyerang yang dibayangkan: orang yang menebak password, mencuri token, membaca database yang bocor, atau menyalahgunakan endpoint.

### Daftar ancaman dan mitigasi

| Ancaman | Cara serangan | Mitigasi | Dikerjakan |
| --- | --- | --- | --- |
| Brute force login | Menebak password berulang kali | Throttling DRF (usulan 5 kali per menit per IP atau akun, respons 429), validator password | Sprint 4 |
| Credential stuffing | Memakai pasangan email dan password yang bocor dari situs lain | Throttling, validator menolak password umum, 2FA di tahap lanjutan | Sprint 4, Fase 9 |
| Menebak email yang terdaftar | Membandingkan pesan registrasi, login, atau reset | Login dan reset memakai pesan generik. Registrasi tetap menyebut email sudah terdaftar (US-01) dan dibatasi throttling | Sprint 2 sampai 4 |
| Access token dicuri | Disadap di jaringan atau dicuri dari browser lewat XSS | HTTPS di production, umur 15 menit, frontend contoh tidak menyisipkan input pengguna sebagai HTML | Sprint 2, Fase 7 |
| Refresh token dicuri | Dibaca dari penyimpanan frontend | Umur 7 hari, logout mencabutnya, semua token dicabut saat ganti atau reset password, risiko ditinjau lagi di Sprint 4 | Sprint 2 sampai 4 |
| Database bocor | Salinan database jatuh ke pihak lain | Password disimpan sebagai hash, token reset tidak disimpan, teks token di outstanding\_token dicek lalu dibersihkan berkala dan akses database dibatasi | Sprint 2, Fase 7 |
| Sesi lama bertahan setelah password diganti | Penyerang masih memegang refresh token lama | Semua refresh token milik user dicabut setelah ganti atau reset password | Sprint 3 |
| Tautan reset password disalahgunakan | Tautan dicuri, dipakai ulang, atau ditebak | Token berbatas waktu dan otomatis tidak berlaku setelah password berubah, respons selalu sama | Sprint 3 |
| Spam email reset | Meminta reset berulang untuk membanjiri email korban | Throttling pada endpoint reset request | Sprint 4 |
| Eskalasi hak akses | User biasa mengubah role sendiri | PATCH profil hanya menerima name, role hanya bisa diubah admin | Sprint 3 |
| Domain asing memanggil API dari browser | CORS terlalu longgar | CORS hanya untuk daftar domain yang diizinkan | Sprint 4 |
| Secret bocor | SECRET\_KEY atau kredensial database terunggah ke GitHub | .env masuk .gitignore, di production memakai environment variable | Sprint 0, Fase 7 |
| Injeksi SQL | Input berisi perintah SQL | Memakai ORM Django, tidak menulis query mentah dari input pengguna | Semua sprint |
| Detail teknis bocor lewat error | Halaman error menampilkan isi kode | DEBUG=False di production, error 500 berpesan generik | Fase 7 |

### Keputusan 3.5

- **Refresh token di versi 1:** dikirim di body respons dan disimpan frontend contoh. Risiko XSS diterima dan ditinjau lagi di Sprint 4. Cookie httpOnly menjadi peningkatan di Fase 9. Keputusan ini menggantikan usulan awal di 3.1.
- **Teks token di database:** dicek di Sprint 2. Jika yang disimpan teks asli, tabelnya dibersihkan berkala dan akses database dibatasi.
- **Pesan registrasi:** tetap menyebut email sudah terdaftar karena diminta US-01, dengan throttling di endpoint registrasi. Alternatif yang lebih aman (mengirim email ke pemilik akun) dicatat sebagai pengembangan lanjut.
- **Cabut semua refresh token setelah ganti atau reset password:** ya. Konsekuensinya, klien perlu login ulang setelah ganti password.

### Pertanyaan terbuka untuk 3.5

- [ ] Angka throttling (usulan 5 kali per menit untuk login) dan umur token (15 menit dan 7 hari) final atau masih bisa disesuaikan? (diputuskan di Sprint 4 setelah dicoba)

## 3.6 Desain UI (Wireframe)

Wireframe menunjukkan susunan tiap halaman frontend contoh, bukan tampilan visual akhir. Frontend ini hanya contoh pemakaian API, jadi dibuat sederhana: enam halaman dengan HTML dan JavaScript.

### Masuk dan daftar (US-01, US-02)

&#91;embedded content: wireframe masuk dan daftar\]

### Profil dan ganti password (US-05, US-06)

&#91;embedded content: wireframe profil dan ganti password\]

### Lupa password dan atur password baru (US-07)

&#91;embedded content: wireframe lupa password dan atur password baru\]

### Alur antar halaman

- Masuk lalu Profil, setelah login berhasil.
- Masuk dan Daftar saling terhubung lewat tautan. Daftar berhasil lalu kembali ke Masuk.
- Masuk, Lupa password, email, Atur password baru, lalu kembali ke Masuk.
- Profil, Ganti password, lalu Masuk (semua sesi berakhir). Profil, Keluar, lalu Masuk.

### Keputusan 3.6

- **Enam halaman:** masuk, daftar, profil, ganti password, lupa password, dan atur password baru. Halaman admin menunggu fitur Should (US-09).
- **Pesan error:** frontend menampilkan pesan dari API apa adanya. Pesan login gagal tidak dibuat lebih spesifik.
- **Access token kedaluwarsa:** jika request gagal dengan 401, frontend menukar refresh token satu kali lalu mengulang request. Jika penukaran gagal, user diarahkan ke Masuk.
- **Setelah ganti password:** token dihapus dan user diarahkan ke Masuk, sebagai konsekuensi keputusan di 3.5.
- **Ulangi password:** hanya dicek di frontend karena API tidak menerimanya.
- **Tampilan (CSS):** satu file frontend/css/style.css yang ditulis sendiri, sekitar satu halaman, tanpa pustaka atau framework. Wireframe di atas menjadi acuannya. Pengerjaannya dibatasi waktu (usulan 2 sampai 3 jam) dan dilakukan di akhir Sprint 2, setelah semua halaman berfungsi. Fungsi dulu, tampilan sesudahnya.

### Pertanyaan terbuka untuk 3.6

- [x] Bahasa teks antarmuka frontend contoh: Indonesia atau Inggris? (disetujui: Indonesia untuk teks antarmuka, pesan error dari API tetap berbahasa Inggris)

## 3.7 Struktur Proyek

Satu repository Git berisi backend Django dan frontend contoh, dipisah dalam dua folder. Backend dibagi menjadi dua app Django supaya tiap app punya satu tanggung jawab.

### Susunan folder

```text
auth-service/
  backend/
    manage.py
    requirements.txt
    requirements-dev.txt
    .env.example
    config/
      settings/
        base.py
        development.py
        production.py
      urls.py
      wsgi.py
    users/
      models.py
      managers.py
      serializers.py
      views.py
      urls.py
      admin.py
      tests/
    authentication/
      serializers.py
      views.py
      urls.py
      throttles.py
      tests/
  frontend/
    index.html
    register.html
    profile.html
    change-password.html
    forgot-password.html
    reset-password.html
    js/
      api.js
      auth.js
    css/
      style.css
  docs/
  .github/
    workflows/
      ci.yml
  .gitignore
  README.md
```

Skema berikut menunjukkan isi yang sama secara visual: dua bagian utama (backend dan frontend) dan beberapa file di akar repository.

&#91;embedded content: skema susunan folder\]

### Pembagian app Django

| App | Tanggung jawab | Endpoint |
| --- | --- | --- |
| config | Pengaturan proyek, pembagian settings, dan daftar URL utama | tidak ada |
| users | Model User (login dengan email), manager, profil, dan halaman admin Django | /api/v1/auth/profile/ |
| authentication | Registrasi, login, refresh token, logout, ganti dan reset password, serta pembatasan percobaan login | semua endpoint /api/v1/auth/ lainnya |

### Keputusan 3.7

- **Custom user model dibuat pertama:** model User di app users diatur lewat AUTH\_USER\_MODEL sebelum migrasi pertama dijalankan (Sprint 0).
- **Nama tabel sesuai ERD:** tabel User diberi nama users lewat db\_table. Tabel token memakai nama asli dari simplejwt, sehingga nama outstanding\_token dan blacklisted\_token di ERD adalah nama logis. Nama aslinya dicek di Sprint 2.
- **Settings dipisah tiga:** base.py untuk pengaturan bersama, development.py untuk komputer sendiri, production.py untuk Render. Secret dibaca dari file .env (development) atau environment variable (production), dan .env masuk .gitignore.
- **Dua file requirements:** requirements.txt untuk kebutuhan production, requirements-dev.txt untuk alat pengujian dan pengembangan.
- **Tes di dalam tiap app:** folder tests ada di users dan authentication, sehingga tes dekat dengan kodenya.
- **Frontend tanpa framework:** file HTML biasa dengan JavaScript. api.js menangani pemanggilan API dan penukaran refresh token, auth.js menangani penyimpanan token dan pengalihan halaman.
- **Folder docs:** berisi salinan dokumen desain 3.1 sampai 3.6 dan nanti panduan integrasi (Fase 8).

### Pertanyaan terbuka untuk 3.7

- [x] Satu repository untuk backend dan frontend, atau dua repository terpisah? (disetujui: satu repository selama belajar, karena lebih mudah dikelola)
- [x] Frontend contoh dihosting di mana saat deploy? (diputuskan: Cloudflare Pages, karena gratis, bandwidth aset statis tidak dibatasi, dan terpisah dari backend. Render Static Site dan Netlify jadi cadangan. AWS tidak dipilih karena paket gratisnya menutup akun setelah 6 bulan atau saat kredit habis. Paket gratis dicek ulang di Fase 7)

## Pemeriksaan Gerbang Fase 3

Semua dokumen desain 3.1 sampai 3.7 dibandingkan satu sama lain. Hasilnya:

### Sudah konsisten

- Nama field di API sama dengan nama kolom di ERD (email, name, role, is\_active).
- Kode status dan pesan error sama di tabel API, diagram alur, dan wireframe.
- Umur token (15 menit dan 7 hari) serta pesan generik untuk login dan reset password sama di semua bagian.
- Pemisahan backend dan frontend, serta daftar CORS, sejalan di 3.1, 3.5, dan 3.7.
- Nama file dan folder di skema 3.7 sama dengan daftar teks dan tabel app.

### Ketidaksesuaian yang sudah diperbaiki

- ERD belum memuat is\_staff dan is\_superuser padahal 3.2 memutuskan mempertahankannya. Kolom ditambahkan.
- Diagram 3.1 hanya menyebut token yang dicabut, padahal login juga mencatat token yang diterbitkan. Teks diperbaiki.
- Diagram reset password di 3.4 belum menunjukkan pencabutan semua refresh token (keputusan 3.5). Langkahnya ditambahkan.
- Tabel kode status di 3.3 menyebut 429 hanya untuk login, padahal 3.5 menambah pembatasan di registrasi dan reset password langkah 1. Tabel disesuaikan.

### Pertanyaan terbuka dari pemeriksaan

- [x] Endpoint cek identitas untuk aplikasi klien (US-10) disebut di 3.1 tetapi belum ada di daftar endpoint 3.3, karena prioritasnya Should. Diputuskan: di versi 1 aplikasi klien memakai GET /api/v1/auth/profile/ dengan access token pengguna, dan endpoint khusus dibuat saat US-10 dikerjakan.

## Kesimpulan Fase 3

Ringkasan keputusan desain yang sudah disepakati.

### 3.1 Arsitektur

- Jalur B: API Django + DRF dan frontend JavaScript yang terpisah, berkomunikasi lewat HTTP dan JSON.
- Hanya API yang menyentuh database. SQLite saat belajar, PostgreSQL di Neon saat deploy.
- Backend di Render, frontend di Cloudflare Pages.
- Email dicetak ke terminal saat development, SMTP menyusul.
- Aplikasi klien lain memeriksa identitas lewat GET /api/v1/auth/profile/ dengan access token pengguna. Endpoint khusus (US-10) menyusul.

### 3.2 Database (ERD)

- Tiga tabel: users, outstanding\_token (token yang diterbitkan), dan blacklisted\_token (token yang dicabut).
- Login dengan email dan tanpa kolom username. Hak akses lewat kolom role (user atau admin), sedangkan is\_staff dan is\_superuser hanya untuk Django admin.
- Password disimpan sebagai hash. Token reset password tidak disimpan di database.
- Ditunda: verifikasi email dan log aktivitas login.

### 3.3 Desain API

- Sembilan endpoint di bawah /api/v1/auth/: register, login, refresh, logout, profil (GET dan PATCH), ganti password, dan reset password dua langkah.
- Pesan login gagal sama untuk semua penyebab (401). Password tidak pernah muncul di respons.
- Kode status: 200, 201, 204, 400, 401, 403, 429, dan 500.

### 3.4 Alur autentikasi

- Access token berumur 15 menit dan tidak dicek ke database. Refresh token berumur 7 hari dan dicek ke daftar pencabutan.
- Logout hanya mencabut refresh token. Access token lama habis dengan sendirinya.
- Setelah ganti atau reset password, semua refresh token user dicabut sehingga klien harus login ulang.

### 3.5 Keamanan

- Empat belas ancaman dengan mitigasi dan sprint pengerjaannya.
- Refresh token di versi 1 dikirim di body respons. Cookie httpOnly menjadi peningkatan di Fase 9.
- Pesan registrasi "email sudah terdaftar" dipertahankan karena diminta US-01, dengan throttling.

### 3.6 Antarmuka

- Enam halaman dengan teks bahasa Indonesia, sedangkan pesan error dari API tetap berbahasa Inggris.
- Saat access token habis, frontend menukar refresh token satu kali lalu mengulang request. Setelah ganti password, user diarahkan ke Masuk.

### 3.7 Struktur proyek

- Satu repository dengan folder backend dan frontend.
- Tiga bagian Django: config, users, dan authentication. Settings dipisah menjadi tiga file.
- Custom user model dibuat sebelum migrasi pertama, dan tabelnya diberi nama users lewat db\_table.

### Yang masih terbuka

- **Sprint 2:** memastikan nama tabel dan kolom simplejwt serta apakah token disimpan sebagai teks asli.
- **Sprint 4:** menyesuaikan angka throttling dan umur token setelah dicoba.
- **Fase 7:** mengecek ulang paket gratis Cloudflare Pages.
- **Fase 9:** cookie httpOnly dan 2FA.

## Langkah berikutnya

Fase 3 selesai. Langkah berikutnya adalah Fase 4 Perencanaan Proyek.
