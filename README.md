# Shirin · Android 0.1.1

Shirin — Android uchun mustaqil ijod studiyasi. Paket nomi `uz.shirin.ai`.
Begborim ilovasidan alohida o‘rnatiladi. APK ichida server manzili tayyor. Shaxsiy ulanish kodi va pullik AI kaliti APK ichiga kiritilmagan.

**Bu Higgsfieldning to‘liq nusxasi emas.** Shirin interfeysi va manba kodi berilgan;
Higgsfieldning yopiq kodi, modellari va barcha sayt funksiyalari bu paketga kirmaydi.
Qaysi imkoniyat mavjudligini [FEATURES.md](FEATURES.md) ko‘rsatadi.

## Telefonga o‘rnatish

1. `Shirin-0.1.1.apk` faylini Android 8.0 yoki yangiroq telefonda och.
2. Telefon so‘rasa, faylni ochayotgan dasturga APK o‘rnatish ruxsatini ber.
3. Shirin’ni och. Rasm tahriri, galereya va storyboard uchun server kerak emas.
4. **Ulanish → Ulanish faylini ochish** orqali shaxsiy `Shirin-Ulanish.json` faylini tanla.
   Server manzili va kod avtomatik tekshiriladi; muvaffaqiyatli bo‘lsa, shu qurilmada eslab qolinadi.
5. Avvalgi Shirin 0.1.0 ni o‘chirmasdan APK ustidan yangila: paket nomi va imzo saqlangan.
6. Haqiqiy AI yaratish uchun serverga Higgsfield API kaliti va API hisobida balans kerak.

Android yangilanishi serverning 0.1.0 protokoli bilan mos. Tayyor ulanish fayli shaxsiy: uni ommaviy repozitoriyga qo‘shma.

Galereya ilova ma’lumotlarida saqlanadi. Muhim ishlarni `Yuklash` yoki Androiddagi
`Telefon galereyasiga` tugmasi orqali alohida saqla. Ilova ma’lumotlarini o‘chirish
ichki galereya va qoralamalarni ham o‘chiradi. Qurilmalararo bulut sinxronlash yo‘q.

## Haqiqiy AI’ni ulash

Ikki xil kalitning vazifasi alohida:

| Qiymat | Qayerga qo‘yiladi | Vazifasi |
| --- | --- | --- |
| `SHIRIN_TOKEN` | Server va ilovadagi “Ulanish kodi” | O‘z Shirin serveringga kirish |
| `HF_KEY` | Faqat server muhiti | Higgsfield API’ga murojaat; `KEY_ID:KEY_SECRET` shaklida |

Higgsfield API hisobida modelga ruxsat va yetarli balans bo‘lishi kerak.
Higgsfield saytidagi obuna/creditlar va API balansi alohida.
Kalitlar ushbu arxivda yo‘q; ularni chatga yoki APK kodiga yozma.

1. [Higgsfield API hisobida](https://open.higgsfield.ai/) kalit yarat.
2. Ushbu manba kodining `server/` qismini o‘z serveringda ishga tushir.
3. Server muhitida `HF_KEY` va kamida 32 belgili tasodifiy `SHIRIN_TOKEN` sozla.
4. Tashqi manzil HTTPS bo‘lsin. `PUBLIC_BASE_URL` aynan shu manzil bo‘lsin.
5. Ilovada **Ulanish → Server manzili** maydoniga shu HTTPS manzilni yoz.
6. **Ulanish kodi** maydoniga aynan `SHIRIN_TOKEN` qiymatini kirit.
7. **Saqlash va tekshirish** ni bos. Server “Ulangan”, AI “Sozlangan” bo‘lishi kerak.
8. **Yaratish** bo‘limida model va reference tanla, tavsif yoz, API xarajatiga
   rozilikni belgilab, avval qisqa video bilan sinab ko‘r.

“Sozlangan” — kalit borligini bildiradi. Hisob balansi yoki haqiqiy generatsiya
muvaffaqiyati oldindan tasdiqlanganini anglatmaydi. Bu nashrda jonli pullik AI
generatsiyasi sinovdan o‘tkazilmadi.

### Kompyuterda mahalliy ishga tushirish

Python 3.12 va FFmpeg/FFprobe kerak. Ishlash uchun Python paketlari shart emas.

```bash
cd server
python3 server.py
```

Brauzerda `http://127.0.0.1:8080` ochiladi. Faqat localhost rejimida kodsiz ishlaydi.
AI uchun `HF_KEY` muhit o‘zgaruvchisini jarayonni boshlashdan oldin sozla.
Android APK tashqi serverga xavfsiz HTTPS orqali ulanadi; kompyuterning localhost
manzili telefonda o‘sha kompyuterni anglatmaydi.

### Docker bilan server

`.env.example` faylini `.env` nomiga nusxala, namunadagi qiymatlarni almashtir.
Token yaratish uchun kompyuteringda `python3 -c 'import secrets; print(secrets.token_urlsafe(32))'`
buyrug‘idan foydalanish mumkin. `.env` ni ommaviy repozitoriyga qo‘shma.

```bash
docker build -t shirin-ai .
docker volume create shirin-data
docker run -d --name shirin --restart unless-stopped \
  -p 127.0.0.1:8080:8080 --env-file .env \
  -v shirin-data:/data shirin-ai
```

Telefon uchun server oldiga o‘z domening bilan HTTPS reverse proxy qo‘y.
`/healthz` faqat server ishga tushganini ko‘rsatadi. `/health` token bilan tekshiriladi.
Railway uchun `Dockerfile` va `railway.json` ham mavjud; `/data` doimiy diskka
biriktirilishi kerak. APK hosting yaratmaydi; ushbu nashrga tayyor Shirin serverining ochiq manzili biriktirilgan.

Server bir egali shaxsiy foydalanish uchun. Ko‘p foydalanuvchili ro‘yxatdan o‘tish,
alohida hisoblar, to‘lov sotish va foydalanuvchilarni ajratish kiritilmagan.

## Xato yuz bersa

| Xabar / holat | Nima tekshiriladi |
| --- | --- |
| “Ulanish kodi bo‘sh/noto‘g‘ri” | Ilovaga serverdagi `SHIRIN_TOKEN` qiymatini yoz; `HF_KEY` ni emas. |
| “Bu Shirin serveri emas” | Eski Begborim URL o‘rniga shu koddan ishga tushirilgan Shirin serveri kerak. |
| “Serverga ulanib bo‘lmadi” | HTTPS manzil, sertifikat, domen va server logini tekshir. |
| “Higgsfield API kaliti qabul qilinmadi” | Serverdagi ID va secret juftligini tekshir. |
| Balans / ruxsat / limit xabari | API hisobidagi aynan tanlangan modelni tekshir. |
| “Oxirgi so‘rovni tekshirish” | Shu tugmani bos; bir xil ish uchun yana pullik so‘rov yuborilmaydi. |
| Server qayta ishga tushdi / 30 daqiqa o‘tdi | API konsolida avvalgi ishni tekshir. Avtomatik yangi generatsiya yuborilmaydi. |

Server qayta ishga tushganda davom etayotgan AI ish avtomatik tiklanmaydi.
Provider kvitansiyasi `SHIRIN_MEDIA/<job-id>/hf-receipt.json` da saqlanadi.
Providerda ish davom etishi mumkin; yangi generatsiyadan oldin uning holatini tekshir.

## APK’ni qayta yig‘ish

Android SDK platform 35, Build Tools 35.0.0, JDK, `zip` va `bash` kerak.

```bash
ANDROID_SDK_ROOT=/sdk/manzili bash build.sh
```

ECJ ishlatilsa `ECJ_JAR=/ecj.jar/manzili` ni ham ber. Natija `Shirin-AI.apk`.
`development.keystore` — aynan berilgan APK imzo kaliti; uni shaxsiy nusxada saqla.
Keyingi yangilanishlar shu kalit bilan imzolanishi va `versionCode` oshirilishi kerak.
Kalit/parollar demo tarqatish uchun; do‘konga chiqarishdan oldin alohida release
imzolash tartibini tayyorla. Imzo kalitini ommaga joylashtirma.

## Tekshiruv va manbalar

[TESTING.md](TESTING.md) — bajarilgan va bajarilmagan tekshiruvlar.
Model endpointlari va parametrlar `server/hf-models.json` da, har birining rasmiy
API hujjati `source` maydonida ko‘rsatilgan.

- [API va sayt obunasining farqi](https://higgsfield.ai/creator-hub/help-center/integrations/what-is-the-higgsfield-api)
- [Autentifikatsiya](https://docs.higgsfield.ai/docs/authentication)
- [So‘rovlar va natijalar](https://docs.higgsfield.ai/docs/concepts/requests)
- [Fayl yuklash](https://docs.higgsfield.ai/docs/concepts/file-uploads)
- [Bir so‘rovni takrorlamaslik](https://docs.higgsfield.ai/docs/concepts/idempotency)

Hujjatlar 2026-10-03 kuni tekshirildi. Xizmat keyinchalik o‘zgarsa, model
konfiguratsiyasi yangilanishi mumkin.
