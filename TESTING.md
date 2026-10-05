# Shirin Android 0.1.1 tekshiruvi

- Ulanish fayli: 6 ta Node testi muvaffaqiyatli. Noto‘g‘ri JSON/kod/URL, kattalik limiti, eski sozlama bilan aralashish va muvaffaqiyatsiz kirishda saqlanmaslik tekshirildi.
- APK: package `uz.shirin.ai`, versionCode 2; 0.1.0 bilan bir xil sertifikat; v2 va v3 imzolari tasdiqlandi.
- Shaxsiy server kodi APK yoki ommaviy kodga qo‘shilmagan.
- Jonli Railway serveri: /healthz 200, kodsiz /health 401, to‘g‘ri kod bilan /health 200.
- Jonli server montaji: 2 soniya, 480×480, H.264, 24 FPS, 48 kadr. MP4 yuklab olinib FFprobe orqali tekshirildi. Bu AI jonlantirish emas.
- Server 0.1.0, Android 0.1.1: API protokoli mos.
- Higgsfield kaliti yo‘q; haqiqiy AI generatsiyasi sinovdan o‘tkazilmagan.
- Android qurilmada o‘rnatish va yangi oynaning vizual sinovi bu muhitda bajarilmagan. Mahalliy oldindan ko‘rish brauzerda ERR_BLOCKED_BY_CLIENT bilan ochilmadi.

Qayta tekshirish: `node --test verification/connection.test.cjs`.
