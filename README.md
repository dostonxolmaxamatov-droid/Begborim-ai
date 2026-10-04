# Shirin AI server · 0.1.0

Android Shirin 0.1.0 uchun mustaqil, bir egali server va web studiya.
Bu branch faqat Shirin serveri uchun; asosiy Begborim ilovasi boshqa branchda.

## Railway

- Source: `shirin-server-0.1.0` branch, repozitoriyning ildizi.
- Build: `Dockerfile`; Python 3.12, FFmpeg va FFprobe.
- Healthcheck: `/healthz`.
- Volume: `/data` — ishlar bazasi va yaratilgan media saqlanadi.
- `SHIRIN_TOKEN`: kamida 32 belgili tasodifiy shaxsiy ulanish kodi.
- `HF_KEY`: Higgsfield API hisobining `KEY_ID:KEY_SECRET` qiymati. Faqat serverda saqlanadi.
- `PUBLIC_BASE_URL`: serverning HTTPS manzili. Railway domeni ham avtomatik aniqlanadi.
- `SHIRIN_WORKERS=1`: ishlar navbat bilan bajariladi.

APK → Ulanish → Server manzili va `SHIRIN_TOKEN` qiymati → Saqlash va tekshirish.
`/health` va API so‘rovlari shu tokenni talab qiladi. `/healthz` maxfiy ma’lumot bermaydi.

## Imkoniyat holati

MP4 montaj FFmpeg bilan serverda bajariladi. Haqiqiy rasm jonlantirish uchun
Higgsfield API kaliti, modelga kirish va yetarli API balansi kerak. Kalit yo‘q
bo‘lsa AI so‘rovi rad etiladi; slayd-videoga avtomatik almashtirilmaydi.
API xizmati pulli bo‘lishi mumkin; ilova yuborishdan oldin rozilik so‘raydi.

Ko‘p foydalanuvchili akkauntlar va to‘lov tizimi bu serverga kirmaydi.
Server qayta ishga tushsa davom etayotgan ish INTERRUPTED holatiga o‘tadi;
qayta pulli so‘rov yuborishdan oldin providerda uning holatini tekshirish kerak.

## Tekshirish

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m unittest discover -s server -p 'test_*.py' -v
```

Sinovlar provider javoblarini taqlid qiladi; haqiqiy pulli generatsiya alohida tekshiriladi.
Kalitlar, .env, imzolash fayllari va foydalanuvchi media fayllarini GitHub‘ga yuklamang.
