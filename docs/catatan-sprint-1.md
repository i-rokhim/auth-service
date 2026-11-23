# Catatan Sprint 1: inti autentikasi

## Yang selesai

- T1.1 Model User didaftarkan di Django admin (#8)
- T1.2 Membuat dan mengubah user lewat shell dan admin, melihat hash di database (tanpa perubahan kode)
- T1.3 Tes model User (#9)
- T1.4 Tes `authenticate` (#10)
- T1.5 Tes validator password (#11)
- T1.6 Semua tes dijalankan, catatan ini ditulis
- Hasil akhir: 13 tes otomatis lulus, Ruff bersih, tidak ada migrasi yang tertinggal

## Yang saya pelajari

- Password tidak disimpan apa adanya, tetapi sebagai hash. Di tabel `users` kolom password berisi teks seperti `pbkdf2_sha256$1500000$<salt>$<hash>`: nama algoritma, jumlah putaran, salt acak, dan hasil hash. Password asli tidak bisa dibaca kembali, dan `check_password` hanya membandingkan hasil hash.
- Salt membuat dua user dengan password yang sama tetap punya hash berbeda. Ini terlihat dari potongan awal hash tiga user uji yang semuanya berlainan.
- `authenticate` mengembalikan `None` untuk password salah, email yang tidak terdaftar, dan akun dengan `is_active=False`. Akun nonaktif sengaja tidak boleh masuk walaupun password-nya benar.
- Tes otomatis menulis sekali apa yang tadinya saya cek dengan tangan di admin, dan bisa diulang kapan saja. Kalau suatu perubahan merusak perilaku lama, tes langsung gagal.
- Model User buatan sendiri membuat form admin bawaan tidak cocok (karena tidak punya kolom `username`), jadi form tambah dan ubah user ditulis sendiri di `admin.py`.

## Kendala dan solusinya

- Terminal baru tanpa `(.venv)`: muncul `No module named 'django'` dan `ruff` tidak dikenal. Solusinya mengaktifkan lagi virtual environment dengan `.\.venv\Scripts\Activate.ps1`.
- Posisi folder salah: `manage.py` tidak ditemukan saat terminal di folder `users`, dan jalur `backend/backend` atau `docs/docs` dicari Git. Solusinya melihat ujung prompt sebelum menjalankan perintah, lalu pindah folder dengan `cd` atau memakai jalur yang sesuai posisi.
- Berkas belum tersimpan di VS Code, misalnya `.env` yang masih 0 byte dan Ruff yang masih melihat kode lama. Solusinya menyimpan dengan Ctrl+S dan memeriksa titik bulat di tab.
- Pull request terlewat: pada T0.8 commit sudah ter-push tetapi `main` belum berubah, dan catatan T1.6 sempat ter-merge dalam bentuk kerangka kosong. Solusinya memeriksa `git log` dan halaman Pull requests setelah setiap push, lalu membuat branch baru untuk memperbaikinya.
- Isian otomatis Chrome mengisi kolom Name dan Password di formulir Add user. Solusinya memakai jendela penyamaran.

## Waktu nyata

Perkiraan kasar saya: sekitar 60 menit untuk satu sesi kerja. Waktu per tugas belum saya catat, dan akan saya catat mulai Sprint 2.

## Yang masih ingin saya pahami

- Mengapa Django membuat database sementara yang terpisah setiap kali tes dijalankan, dan bagaimana penghapusannya setelah tes selesai?
  Jawaban sementara: supaya tes tidak mengubah data asli dan selalu mulai dari kondisi bersih. Dengan SQLite, database tes dibuat di memori dan hilang sendiri saat tes selesai (tertulis `Destroying test database`). Tiap tes juga dibungkus transaksi yang dibatalkan, sehingga satu tes tidak memengaruhi tes lain.
- Bagaimana praktik terbaik membagi ukuran tugas per sprint agar beban tetap realistis?
  Jawaban sementara: pakai waktu nyata dari sprint sebelumnya sebagai dasar, buat tiap tugas cukup kecil untuk selesai dalam satu sesi dengan kriteria selesai yang jelas, dan sisakan ruang cadangan sekitar 20 sampai 30 persen.