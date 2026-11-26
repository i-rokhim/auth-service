# Catatan Sprint 2: API autentikasi dan halaman dasar

## Yang selesai

- T2.1 simplejwt dengan token blacklist (#14)
- T2.2 Endpoint daftar `POST /api/v1/auth/register/` (#15)
- T2.3 Endpoint masuk `POST /api/v1/auth/login/` (#16)
- T2.4 Endpoint tukar token `POST /api/v1/auth/token/refresh/` (#17)
- T2.5 Endpoint keluar `POST /api/v1/auth/logout/` (#18)
- T2.6 CORS untuk development (#19)
- T2.7 Tes API: daftar 7, masuk 6, tukar token 7, keluar 10 (#20)
- T2.8 Frontend `api.js` dan `auth.js` (#21)
- T2.9 Halaman Masuk dan Daftar (#22)
- T2.10 Halaman Profil sementara dengan tombol Keluar (#23)
- T2.11 Tampilan sederhana di `style.css` (#24)
- T2.12 Demo alur daftar, masuk, dan keluar, lalu catatan ini
- Hasil akhir: 43 tes otomatis lulus (13 dari Sprint 1 ditambah 30 baru), `ruff check` bersih, dan `makemigrations --check` menjawab `No changes detected`

## Demo

Satu kali jalan penuh di browser dengan akun baru `demo2@example.com`: Daftar, pesan hijau "Akun berhasil dibuat", Masuk, halaman Profil (Email, Role, Nama), lalu Keluar. Sesudah Keluar, `Object.keys(localStorage)` menghasilkan `[]`, dan konsol browser tidak menampilkan error. Di database, akun itu punya 1 token yang diterbitkan dan 1 token di blacklist. Akun demo lalu dihapus beserta tokennya.

## Yang saya pelajari

- Access token (15 menit) dikirim di header `Authorization: Bearer ...` dan diperiksa dari tanda tangan serta masa berlakunya. Refresh token (7 hari) hanya dipakai untuk meminta access token baru. Access token yang dipakai sebagai refresh token ditolak dengan pesan "wrong type".
- Saat Keluar, refresh token dicatat di tabel `token_blacklist_blacklistedtoken`. Sesudahnya endpoint tukar token menjawab `401 Token is blacklisted`. Access token lama tidak dicabut dan habis sendiri dalam 15 menit.
- Login yang gagal memberi pesan yang persis sama untuk password salah, email tidak terdaftar, dan akun nonaktif, supaya penyerang tidak bisa menebak email mana yang terdaftar. Keluar juga memberi satu pesan untuk token yang tidak valid, sudah dicabut, atau milik user lain.
- Serializer daftar hanya menerima `email`, `name`, dan `password`. Tes memastikan klien tidak bisa menjadikan dirinya `admin` atau `is_staff` dengan menambah field itu, dan password tidak pernah muncul di respons.
- CORS: sebelum memanggil API dari asal lain, browser mengirim permintaan `OPTIONS` (preflight). `django-cors-headers` menambahkan header izin hanya untuk asal yang terdaftar (`localhost:5173` dan `localhost:3000`). Asal asing tidak mendapat header itu, dan `CorsMiddleware` harus berada di urutan pertama. `production.py` tidak diberi daftar asal.
- `api.js` menukar refresh token satu kali saat menerima 401, mengulang permintaan satu kali, dan kalau tetap gagal menghapus sesi lalu mengalihkan ke Masuk. Log server membuktikan tiga permintaan serentak hanya memicu satu penukaran. Login dengan password salah tidak memicu penukaran. Penukaran otomatis juga terlihat nyata saat Keluar dengan access token kedaluwarsa: `logout 401`, `token/refresh 200`, lalu `logout 204`.
- Semua teks dari server ditulis ke halaman dengan `textContent`, bukan `innerHTML`, supaya nama atau email berisi tanda `<` tidak bisa menjalankan skrip.
- Tes API memakai `APITestCase`. Token kedaluwarsa bisa dibuat di tes dengan `set_exp`, dan umur token diperiksa dari selisih `exp` dan `iat`. Satu tes sengaja mencatat bahwa rotasi refresh token belum aktif, supaya gagal dan mengingatkan saya kalau rotasi dinyalakan di T4.2.
- Seluruh tes naik dari sekitar 19 detik menjadi sekitar 90 detik, karena setiap tes yang membuat user menjalankan hashing password yang sengaja lambat.

## Temuan keamanan

- Refresh token disimpan sebagai teks asli di kolom `token` tabel `token_blacklist_outstandingtoken` (awalan `eyJ`, 232 karakter). Siapa pun yang bisa membaca database bisa memakai refresh token yang belum kedaluwarsa dan belum dicabut. Ditinjau di T4.6 dan Fase 7.
- Token di frontend disimpan di `localStorage`, jadi skrip yang disisipkan (XSS) bisa membacanya. Mitigasi yang sudah ada: `textContent`. Yang menyusul di Fase 7: header CSP. Cookie `HttpOnly` lebih aman tetapi mengubah desain backend, jadi tidak dipilih sekarang.
- Rotasi refresh token belum aktif (T4.2). Refresh token lama tetap berlaku sampai 7 hari atau sampai dicabut lewat Keluar.
- Tombol Keluar selalu menghapus sesi di browser, walau permintaan ke server gagal (misalnya jaringan putus). Kalau itu terjadi, refresh token di server tetap berlaku sampai kedaluwarsa.
- Pembatasan percobaan login (respons 429) belum ada. Terjadwal di fase penguatan, Sprint 4.

## Kendala dan solusinya

- Terminal baru tanpa `(.venv)`: `pip install django-cors-headers` masuk ke Python global ("Defaulting to user installation"). Solusinya mengaktifkan virtual environment lalu memasang ulang. Sisa paket di Python global tidak memengaruhi proyek.
- Posisi folder salah: `manage.py` dijalankan dari `backend\authentication` dan jalur `config\settings` dicari dari dalam `config\settings`, sehingga muncul "can't open file" dan "path does not exist". Solusinya melihat ujung prompt sebelum menjalankan perintah. Lupa menulis `python` di depan `manage.py runserver` juga membuat PowerShell mengira itu program lain.
- Perubahan belum tersimpan atau salah salin: `requirements.txt` dan `base.py` masih berisi versi lama saat dicek, dan teks keterangan (label) sempat ikut tersalin ke `base.py` padahal itu bukan kode. Solusinya menyimpan dengan Ctrl+S dan memeriksa dengan `git diff` dan `Get-Content`.
- Akhir baris file: file di repository berakhiran CRLF. Saya sempat mengubah satu file ke LF sehingga seluruh isinya tampil berubah di `git diff`. Solusinya mengembalikannya ke CRLF dan membiarkan semua file konsisten.
- Memori habis sesaat: `ruff` menampilkan "memory allocation failed" dan tes berhenti dengan `MemoryError`, padahal `manage.py check` lolos. Setelah proses lain ditutup, semuanya lulus tanpa mengubah kode.
- `ruff format --check` tidak pernah bersih karena seluruh kode memakai kutip tunggal. Saya memakai `ruff check` sebagai gerbang dan tidak memformat ulang 15 file di tengah tugas.
- Browser mengunduh `register.html_` dan `index.html_` alih-alih menampilkannya. Penyebabnya titik di akhir alamat yang ikut tersalin dari tulisan. Solusinya mengetik alamat langsung di bilah alamat tanpa titik.
- Isian otomatis Chrome mengisi kolom Password sehingga percobaan "password salah" sempat berhasil login. Solusinya mengosongkan kolom, memeriksa jumlah titik, atau memakai jendela penyamaran.
- Pull request T2.9 ter-merge sebelum semua pemeriksaan browser selesai. Tidak dibatalkan. Pemeriksaannya dilanjutkan di `main` dan hasilnya sesuai.

## Waktu nyata

Pekerjaan Sprint 2 saya lakukan putus-sambung, jadi lama pengerjaan per tugas tidak tercatat dan saya tidak menebaknya. Yang bisa dibuktikan adalah kapan tiap tugas ter-merge (jam lokal, dari `git log`):

| Tanggal | Jam | Tugas |
|---|---|---|
| 24 Nov | 13:45 | T2.1 |
| 24 Nov | 19:11 | T2.2 |
| 24 Nov | 23:21 | T2.3 |
| 24 Nov | 23:55 | T2.4 |
| 25 Nov | 08:11 | T2.5 |
| 25 Nov | 12:30 | T2.6 |
| 25 Nov | 15:13 | T2.7 |
| 25 Nov | 16:25 | T2.8 |
| 26 Nov | 07:38 | T2.9 |
| 26 Nov | 14:39 | T2.10 |
| 26 Nov | 15:07 | T2.11 |

Sebelas tugas ter-merge dalam tiga hari kalender. Selisih jam merge tidak bisa dibaca sebagai lama pengerjaan, karena ada jeda panjang di antaranya (misalnya T2.9 ke T2.10 sekitar 7 jam). Mulai Sprint 3, saya akan menulis jam mulai dan jam selesai tiap tugas di deskripsi pull request.

## Yang masih ingin saya pahami

- Mengapa tes terasa lama, dan bagaimana mempercepatnya?
  Jawaban sementara: hashing password sengaja lambat, dan setiap tes yang membuat user ikut menanggungnya. Cara yang umum adalah memakai hasher yang cepat khusus untuk tes. Belum saya coba.
- Apakah token di `localStorage` cukup aman untuk proyek ini, atau perlu pindah ke cookie `HttpOnly`?
  Jawaban sementara: cukup untuk latihan selama tidak ada `innerHTML` dari data pengguna dan CSP dipasang. Cookie `HttpOnly` mengurangi risiko XSS tetapi menambah kebutuhan perlindungan CSRF. Diputuskan di Fase 7.
- Bagaimana kalau dua tab menukar refresh token bersamaan?
  Jawaban sementara: penggabungan penukaran di `api.js` hanya berlaku dalam satu tab. Tanpa rotasi, dua penukaran sama-sama berhasil dan tidak merugikan. Kalau rotasi diaktifkan di T4.2, hal ini perlu dipikirkan ulang.

## Keputusan yang masih terbuka

- Visibilitas repository (public atau private).
- Mengganti email commit ke alamat noreply GitHub.
- Mencocokkan model `User` dengan ERD di 3.2.
- Gaya kutipan kode dan `ruff format` (satu pull request terpisah di luar tugas sprint).