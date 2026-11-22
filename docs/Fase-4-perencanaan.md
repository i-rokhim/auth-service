# Fase 4: Perencanaan Proyek

Halaman kerja untuk Fase 4. Tujuannya mengubah desain Fase 3 menjadi rencana kerja yang bisa langsung dikerjakan. Kapasitas kerja: 10 jam per minggu (dipakai di 4.2). Sub-tahap dikerjakan berurutan, dimulai dari 4.1.

## Progres Fase 4

- [x] 4.1 Memecah backlog menjadi tugas kecil per user story
- [x] 4.2 Estimasi dan jadwal sprint
- [x] 4.3 Registrasi risiko dan mitigasinya
- [x] 4.4 Menyiapkan alat kerja: GitHub, papan tugas, editor, Python
- [x] 4.5 Menetapkan aturan kerja: konvensi branch, commit, dan code style

**Gerbang:** papan tugas terisi dan siap dikerjakan. Terpenuhi: 45 kartu tugas ada di GitHub Projects “Auth Service”.

## 4.1 Memecah Backlog Menjadi Tugas Kecil

Setiap tugas dirancang selesai dalam satu sesi belajar, sekitar 1 sampai 3 jam. Kode tugas (misalnya T2.3) menunjukkan sprint dan urutannya, dan di tugas yang berkaitan dengan user story tertera kodenya. Hanya fitur Must (US-01 sampai US-08) yang masuk sprint versi 1.

### Sprint 0: Setup

- [x] T0.1 Buat repository GitHub, clone ke komputer, tambahkan .gitignore (Python dan .env) dan README awal
- [x] T0.2 Buat folder backend, frontend, dan docs sesuai skema 3.7
- [x] T0.3 Buat virtual environment di backend dan requirements.txt awal (Django dan DRF)
- [x] T0.4 Buat proyek Django bernama config dengan settings terpisah: base, development, production
- [x] T0.5 Siapkan .env dan .env.example untuk SECRET\_KEY dan DEBUG, pastikan .env tidak ikut di-commit
- [x] T0.6 Buat app users dengan custom user model (email sebagai login, kolom sesuai ERD, db\_table users, manager) dan atur AUTH\_USER\_MODEL sebelum migrasi pertama
- [x] T0.7 Jalankan migrasi pertama, buat superuser, dan buka Django admin
- [ ] T0.8 Salin dokumen desain ke folder docs dan buat commit pertama yang bersih

### Sprint 1: Inti autentikasi (pemanasan)

- [ ] T1.1 Daftarkan model User di Django admin (email, name, role, is\_active)
- [ ] T1.2 Buat dan ubah user lewat Django shell dan admin, lalu lihat hash password di database
- [ ] T1.3 Tes model User: dibuat dengan email, password tersimpan sebagai hash, email unik, role default user (US-01)
- [ ] T1.4 Tes authenticate: email dan password benar diterima, password salah dan akun nonaktif ditolak (US-02)
- [ ] T1.5 Tes validator password: password lemah ditolak (US-01)
- [ ] T1.6 Jalankan semua tes, commit, dan tulis catatan belajar singkat

### Sprint 2: API dan JWT

- [ ] T2.1 Pasang DRF dan simplejwt dengan fitur blacklist, atur umur token 15 menit dan 7 hari, jalankan migrasi tabel token, lalu periksa nama tabel dan kolom serta apakah token disimpan sebagai teks asli (US-03)
- [ ] T2.2 Buat endpoint register dengan serializer: respons 201 tanpa password, error 400 per field (US-01)
- [ ] T2.3 Buat endpoint login: mengembalikan access, refresh, dan data user, dengan 401 pesan generik (US-02)
- [ ] T2.4 Buat endpoint refresh token (US-03)
- [ ] T2.5 Buat endpoint logout yang memasukkan refresh token ke blacklist, respons 204 (US-04)
- [ ] T2.6 Konfigurasi CORS dasar untuk development (alamat frontend lokal)
- [ ] T2.7 Tes API register, login, refresh, dan logout, masing-masing kasus sukses dan gagal sesuai tabel 3.3 (US-01 sampai US-04)
- [ ] T2.8 Frontend: tulis api.js (fetch, header Authorization, tukar refresh token satu kali saat 401) dan auth.js (simpan token, pengalihan halaman) (US-03)
- [ ] T2.9 Frontend: halaman Masuk dan Daftar sesuai wireframe 3.6 (US-01, US-02)
- [ ] T2.10 Frontend: halaman Profil sementara yang menampilkan data user dari respons login, dengan tombol Keluar (US-04)
- [ ] T2.11 Styling frontend: satu file style.css sederhana, dibatasi 2 sampai 3 jam
- [ ] T2.12 Demo alur daftar, masuk, dan keluar, lalu catatan belajar singkat

### Sprint 3: Fitur akun

- [ ] T3.1 Buat endpoint GET dan PATCH profile (PATCH hanya menerima name) (US-05)
- [ ] T3.2 Buat endpoint ganti password: wajib password lama, lolos validator, respons 204 (US-06)
- [ ] T3.3 Cabut semua refresh token user setelah ganti password, sesuai keputusan 3.5 (US-06)
- [ ] T3.4 Konfigurasi email development: console backend, email dicetak ke terminal (US-07)
- [ ] T3.5 Buat endpoint reset password langkah 1: respons selalu sama, email berisi uid dan token (US-07)
- [ ] T3.6 Buat endpoint reset password langkah 2: periksa uid dan token, validator password, cabut semua refresh token (US-07)
- [ ] T3.7 Role dan hak akses: permission class untuk admin, dan pastikan PATCH profil tidak bisa mengubah role
- [ ] T3.8 Tes profil, ganti password, dan reset password, termasuk email tidak terdaftar, token kedaluwarsa, dan token dipakai ulang (US-05 sampai US-07)
- [ ] T3.9 Frontend: hubungkan Profil ke GET dan PATCH, buat halaman Ganti password, Lupa password, dan Atur password baru (US-05 sampai US-07)
- [ ] T3.10 Frontend: arahkan ke Masuk setelah ganti password berhasil (US-06)
- [ ] T3.11 Demo semua fitur akun, lalu catatan belajar singkat

### Sprint 4: Penguatan

- [ ] T4.1 Throttling DRF: login (usulan 5 kali per menit), registrasi, dan reset password langkah 1, respons 429 (US-08)
- [ ] T4.2 Sesuaikan angka throttling dan umur token setelah dicoba (pertanyaan terbuka 3.5) (US-08)
- [ ] T4.3 Validasi input: format email, panjang name, dan pesan error yang konsisten
- [ ] T4.4 CORS production: daftar domain yang diizinkan lewat environment variable, termasuk alamat Cloudflare Pages
- [ ] T4.5 Dokumentasi Swagger dengan drf-spectacular, semua endpoint tampil dengan contoh
- [ ] T4.6 Tinjau risiko XSS di frontend dan keputusan refresh token di body respons (3.5)
- [ ] T4.7 Tes throttling, CORS, dan cakupan kode di atas 80% (US-08)
- [ ] T4.8 Demo penguatan, lalu catatan belajar singkat

### Peta user story ke tugas

| User story | Tugas |
| --- | --- |
| US-01 Registrasi | T0.6, T1.3, T1.5, T2.2, T2.7, T2.9 |
| US-02 Login | T1.4, T2.3, T2.7, T2.9 |
| US-03 Refresh token | T2.1, T2.4, T2.7, T2.8 |
| US-04 Logout | T2.5, T2.7, T2.10 |
| US-05 Profil | T3.1, T3.8, T3.9 |
| US-06 Ganti password | T3.2, T3.3, T3.8, T3.9, T3.10 |
| US-07 Reset password | T3.4, T3.5, T3.6, T3.8, T3.9 |
| US-08 Pembatasan percobaan login | T4.1, T4.2, T4.7 |

### Perubahan dari rencana awal

- **Sprint 1:** tidak lagi memakai halaman HTML bawaan Django, karena backend hanya menjawab JSON (Jalur B). Pemanasannya memakai admin, shell, dan tes.
- **CORS:** versi dasar dimajukan ke Sprint 2, karena frontend dan backend berbeda alamat sejak halaman pertama. Sprint 4 mengatur daftar domain production.
- **Profil di Sprint 2:** halaman Profil sementara memakai data dari respons login, lalu terhubung ke GET dan PATCH di Sprint 3.
- **Pertanyaan terbuka dari Fase 3:** menjadi tugas, yaitu T2.1 (isi tabel token simplejwt) dan T4.2 (angka throttling dan umur token).
- **Fitur Should dan Could** (US-09 sampai US-14) tidak masuk sprint versi 1 dan dikerjakan di Fase 9. Kebutuhan US-10 sementara dipenuhi GET profile.

### Pertanyaan terbuka untuk 4.1

- [x] Apakah ukuran tugas sekitar 1 sampai 3 jam cocok untukmu? Jika terlalu besar atau kecil, tugasnya kita pecah atau gabung. (usulan: pakai ukuran ini dulu, dan sesuaikan setelah Sprint 0)

## 4.2 Estimasi dan Jadwal Sprint

Sprint 0 sampai 4 butuh sekitar 93 jam kerja. Dengan kapasitas 10 jam per minggu itu 11 minggu, sudah termasuk cadangan sekitar 15%, dan seluruh proyek sampai dokumentasi sekitar 17 minggu.

**Dasar estimasi:** tugas rutin (commit, demo, konfigurasi kecil) 1 jam, tugas biasa 2 jam, dan tugas yang memperkenalkan konsep baru 3 jam, misalnya T0.6 custom user model, T2.1 simplejwt, serta T3.5 dan T3.6 reset password. Angka ini kasar dan dikoreksi setelah Sprint 0.

| Sprint | Fokus | Tugas | Estimasi (jam) | Minggu | Kapasitas (jam) | Cadangan (jam) | Usulan tanggal |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | Setup | 8 | 16 | 2 | 20 | 4 | 30 Nov – 13 Des 2026 |
| 1 | Inti autentikasi (pemanasan) | 6 | 10 | 1 | 10 | 0 | 14 – 20 Des 2026 |
| 2 | API dan JWT | 12 | 27 | 3 | 30 | 3 | 21 Des 2026 – 10 Jan 2027 |
| 3 | Fitur akun | 11 | 23 | 3 | 30 | 7 | 11 – 31 Jan 2027 |
| 4 | Penguatan | 8 | 17 | 2 | 20 | 3 | 1 – 14 Feb 2027 |
| Fase 6 (kasar) | Pengujian menyeluruh | belum dipecah | sekitar 14 | 2 | 20 | sekitar 6 | 15 – 28 Feb 2027 |
| Sprint 5 / Fase 7 (kasar) | Deployment | belum dipecah | sekitar 16 | 2 | 20 | sekitar 4 | 1 – 14 Mar 2027 |
| Fase 8 (kasar) | Dokumentasi dan serah terima | belum dipecah | sekitar 14 | 2 | 20 | sekitar 6 | 15 – 28 Mar 2027 |

- Sprint 1 pas 10 jam tanpa cadangan. Jika meleset, selisihnya mengurangi cadangan Sprint 2.
- Sprint 2 paling berat (12 tugas, 27 jam) dan jatuh di sekitar Natal dan Tahun Baru.
- Baris Fase 6, Sprint 5, dan Fase 8 masih kasar. Kita pecah menjadi tugas setelah Sprint 4 selesai.

### Perubahan dari rencana awal

- **Bagian 10:** "Sprint 0 sampai 4: 1-2 minggu per sprint" menjadi 1 sampai 3 minggu per sprint (Sprint 1 satu minggu, Sprint 2 dan 3 masing-masing tiga minggu).
- **Bagian 10:** "Fase 6 sampai 8: sekitar 2 minggu" menjadi sekitar 6 minggu, karena ketiganya diperkirakan sekitar 44 jam.

### Pertanyaan terbuka untuk 4.2

- [x] Apakah Sprint 0 mulai Senin, 30 November 2026? (usulan: ya, dengan 4.3 sampai 4.5 selesai sebelum itu. Jika Anda tahu kapasitas turun di sekitar Natal dan Tahun Baru, kita tambah minggu di Sprint 2.)

## 4.3 Registrasi Risiko dan Mitigasinya

Ada sembilan risiko. R1 paling mungkin terjadi, sedangkan R3, R4, dan R5 paling besar dampaknya. Mitigasinya sudah masuk ke tugas yang ada (misalnya T0.5, T0.6, dan T4.6), jadi tidak ada tugas baru dan jadwal 4.2 tidak berubah.

| Kode | Risiko | Kemungkinan | Dampak | Mitigasi | Tanda awal |
| --- | --- | --- | --- | --- | --- |
| R1 | Kurva belajar Django dan DRF lebih berat dari perkiraan | Tinggi | Sedang | Sprint 1 sebagai pemanasan, estimasi dikoreksi setelah Sprint 0, tugas yang macet lebih dari 1 jam dibawa ke Claude | Sprint 0 memakan lebih dari 20 jam |
| R2 | Kapasitas 10 jam per minggu tidak tercapai, terutama di sekitar Natal dan Tahun Baru | Sedang | Sedang | Cadangan 17 jam, tanggal yang bergeser (bukan kualitas yang dikurangi), tambah minggu di Sprint 2 | Realisasi di bawah 8 jam dua minggu berturut-turut |
| R3 | User model diubah setelah migrasi pertama | Rendah | Tinggi | T0.6 selesai dan AUTH\_USER\_MODEL diatur sebelum migrasi pertama di T0.7 | Migrasi dijalankan sebelum T0.6 selesai |
| R4 | Secret (SECRET\_KEY, kredensial database) ikut ter-commit ke GitHub | Sedang | Tinggi | .env masuk .gitignore sebelum commit pertama (T0.1, T0.5), di production pakai environment variable, jika bocor secret langsung diganti | File .env muncul di git status |
| R5 | Token dicuri lewat XSS karena disimpan di browser | Sedang | Tinggi | Tinjauan khusus di T4.6, hindari innerHTML untuk data pengguna, access token hanya 15 menit, refresh token bisa dicabut | Frontend menampilkan data pengguna tanpa dibersihkan |
| R6 | Paket gratis Render atau Neon berubah sebelum deploy | Sedang | Sedang | Cek halaman pricing resmi di awal Sprint 5 (1 Maret 2027) dan siapkan alternatif | Syarat paket gratis berubah |
| R7 | Cakupan proyek melebar | Sedang | Sedang | Hanya fitur Must di versi 1, ide baru masuk daftar Fase 9 | Ada tugas di sprint yang tidak berasal dari US-01 sampai US-08 |
| R8 | Tes tertunda sehingga gerbang Fase 6 (cakupan di atas 80%) tidak tercapai | Sedang | Sedang | Tes ditulis di sprint yang sama dengan fiturnya, T4.7 mengukur cakupan | Cakupan di bawah 70% di akhir Sprint 3 |
| R9 | Server gratis tertidur sehingga request pertama lambat | Tinggi | Rendah | Diterima sebagai batasan paket gratis dan dicatat di dokumentasi | Request pertama setelah lama diam terasa lambat |

Daftar ini ditinjau di akhir tiap sprint, saat retrospective.

### Perubahan dari rencana awal

- **Bagian 11:** tabel enam risiko diganti dengan registrasi ini setelah disetujui. Kolom kemungkinan, dampak, dan tanda awal ditambahkan, dan risiko baru R2, R5, dan R8.

### Pertanyaan terbuka untuk 4.3

- [x] Adakah hambatan pribadi yang perlu masuk daftar, misalnya perangkat, koneksi internet, atau jam kerja? (usulan: tidak ada dulu, kita tambah saat muncul)

## 4.4 Menyiapkan Alat Kerja

Lima alat disiapkan sebelum Sprint 0 mulai pada 30 November 2026, dengan perkiraan sekitar 4 jam: Git dan GitHub 1 jam, Python dan editor 1 jam, papan tugas 2 jam. Repository proyek belum dibuat di sini, karena itu tugas T0.1.

| Alat | Dipakai untuk | Usulan | Cara memeriksa |
| --- | --- | --- | --- |
| Git | Kontrol versi | Pasang Git dari situs resmi, lalu atur user.name dan user.email | Perintah git --version berjalan |
| Akun GitHub | Repository, papan tugas, dan CI | Akun gratis dengan 2FA aktif, masuk lewat SSH key atau token HTTPS | Bisa clone dan push ke repository percobaan |
| Python | Menjalankan Django | Versi stabil terbaru yang didukung Django, dicek di dokumentasi resmi Django saat memasang | Perintah python --version dan pip berjalan, virtual environment bisa dibuat |
| Editor | Menulis kode | Visual Studio Code dengan ekstensi Python | Bisa membuka folder dan menjalankan terminal di dalamnya |
| Papan tugas | Melacak tugas | GitHub Projects dengan kolom Backlog, Sprint ini, Dikerjakan, dan Selesai | Ada 45 kartu dari 4.1 dengan kolom Sprint (custom field), dan T0.1 sampai T0.8 ada di Sprint ini |

- Tiap kartu papan memakai kode dan judul tugas dari 4.1 (misalnya T2.3), dan kolom Sprint mengikuti jadwal di 4.2.
- Papan boleh dibuat tanpa repository, lalu dihubungkan ke repository saat T0.1.

### Pertanyaan terbuka untuk 4.4

- [x] Sistem operasi apa yang kamu pakai: Windows, macOS, atau Linux? Ini menentukan langkah pemasangan Python dan cara mengaktifkan virtual environment. (usulan: pakai Visual Studio Code sebagai editor, kecuali kamu sudah punya editor favorit)

## 4.5 Aturan Kerja

Tiga aturan ringan menjaga riwayat Git tetap rapi dan kode seragam: branch per tugas, format commit yang tetap, dan satu alat untuk gaya kode Python. Perkiraan waktunya sekitar 1 jam, dan aturannya disalin ke folder docs bersama dokumen desain di T0.8.

| Aturan | Usulan | Contoh |
| --- | --- | --- |
| Branch | main selalu bisa dijalankan dan lulus tes. Satu branch per tugas, bernama jenis/kode-tugas-ringkas, digabung lewat pull request (squash), lalu dihapus | feat/t2-3-login-endpoint |
| Commit | Format Conventional Commits, bahasa Inggris, satu perubahan logis per commit, kode tugas di akhir. Jenis: feat, fix, test, docs, chore, refactor | feat: add login endpoint (T2.3) |
| Gaya kode Python | PEP 8 dengan Ruff sebagai linter dan formatter (panjang baris 88), nama fungsi snake\_case dan nama class PascalCase | Jalankan ruff check dan ruff format sebelum commit |
| Gaya kode JavaScript | const dan let (tanpa var), nama camelCase, titik koma, format otomatis saat simpan di VS Code | apiFetch, authToken |

- Ruff dipasang di T0.3 sebagai paket pengembangan, tambahan sekitar 15 menit yang masuk cadangan Sprint 0.
- Tambahkan .venv dan db.sqlite3 ke .gitignore di T0.1, bersama .env.
- Commit minimal sekali per tugas selesai, dan push minimal sekali per sesi belajar sebagai cadangan.

### Pertanyaan terbuka untuk 4.5

- [x] Apakah penggabungan lewat pull request dengan squash cocok, atau lebih nyaman merge langsung ke main? (usulan: pull request dengan squash, supaya terbiasa dengan alur kerja tim)

## Langkah berikutnya

Bagian 4.1 sudah disetujui, dengan ukuran tugas 1 sampai 3 jam. Bagian 4.2 sudah disetujui, dengan Sprint 0 mulai Senin, 30 November 2026. Bagian 4.3 sudah disetujui, tanpa hambatan pribadi tambahan untuk sementara. Bagian 4.4 sudah disetujui, dengan Windows sebagai sistem operasi dan Visual Studio Code sebagai editor. Bagian 4.5 sudah disetujui, dengan pull request dan squash. Semua sub-tahap Fase 4 sudah disetujui. Gerbang Fase 4 terpenuhi: alat sudah terpasang dan papan tugas berisi 45 kartu sesuai 4.4. Fase 4 selesai. Berikutnya Fase 5, dengan Sprint 0 mulai Senin, 30 November 2026.
