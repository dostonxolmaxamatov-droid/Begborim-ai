# Shirin 0.1.0 imkoniyatlari

Bu ro‘yxat Shirin’da real yozilgan imkoniyatlarni Higgsfieldning to‘liq mahsulotidan
ajratib ko‘rsatadi. Barcha modellar yoki veb-saytning barcha ichki funksiyalari
ko‘chirilgani da’vo qilinmaydi.

| Bo‘lim | Shu nashrdagi holat |
| --- | --- |
| Shirin Android APK | O‘z nomi, belgisi va `uz.shirin.ai` paketi; manba kodi berilgan. |
| Mobil/desktop studiya | Moslashuvchan ko‘rinish, modellarni qidirish va tanlash. |
| Galereya | Qurilmada rasm/video/audio saqlash, import, filtrlash, qayta foydalanish, eksport. |
| Rasm tahriri | Nisbat, aylantirish, yorqinlik, kontrast, rang; bir rangli fonni olib tashlash. |
| Video montaj | Rasmlar ketma-ketligi, zoom/pan, audio va SRT; AI jonlantirishdan alohida. |
| Video tahriri | Kesish, oddiy rang uslubi, audio va subtitr; ko‘p trekli timeline yo‘q. |
| Ovoz | Qurilma TTS, mikrofon yozuvi; Android TTS WAV eksport kodi. Til qurilmaga bog‘liq. |
| Storyboard | Kadr tavsifi, tartiblash, o‘chirish, JSON eksport va studiyaga yuborish. |
| Harakat/effekt g‘oyalari | 12 ta original prompt qo‘shimchasi. Higgsfieldning tayyor preset katalogi emas. |
| AI yordamchi | Alohida OpenAI/Ollama/n8n konfiguratsiyasi kerak; bu paketda ulanmagan. |
| Haqiqiy AI rasm/video | Quyidagi 9 endpoint/rejim uchun adapter yozilgan. Server, API kaliti va balans kerak. Jonli sinov yo‘q. |
| AI navbati | Holatni tekshirish, natijani galereyaga olish, bir so‘rov ID’sini saqlash. |

## Higgsfield API adapterlari

| Model / rejim | Asosiy parametrlar |
| --- | --- |
| Seedance 2.5 · rasm → video | Boshlang‘ich rasm, ixtiyoriy oxirgi rasm, prompt, 4–30 s, 480/720/1080p, audio. |
| Seedance 2.5 · matn → video | Prompt, 4–30 s, 6 nisbat, 480/720/1080p, audio. |
| Genjutsu · motion transfer | Reference MP4, 1–8 rasm, ixtiyoriy prompt, 480/720/1080p. |
| Soul 2 · matn → rasm | Prompt, nisbat, 720/1080p, seed va prompt yaxshilash; bitta rasm. |
| Kling 2.5 Turbo Pro · rasm → video | Reference rasm, prompt va model parametrlari. |
| Kling 2.5 Turbo Pro · matn → video | Prompt va model parametrlari. |
| Kling 2.5 Turbo Standard · rasm → video | Reference rasm, prompt va model parametrlari. |
| Hailuo 2.3 Standard · rasm → video | Reference rasm, prompt va model parametrlari. |
| Hailuo 2.3 Standard · matn → video | Prompt va model parametrlari. |

Video MP4 sifatida olinadi. Soul batch / Soul ID, MOV eksport, bir ishda bir nechta
AI natija va barcha API advanced parametrlari hozir kiritilmagan. Modelning hisobda
mavjudligi, navbati, narxi, cheklovi va natija sifati providerga bog‘liq.

## Shu nashrga kirmagan Higgsfield bo‘limlari

Cinema Studio, Ads/Marketing Studio, AI Influencer/Soul ID, Supercomputer,
3D Jutsu, Higgsfield Canvas node engine, Community/Originals/Academy,
rasmiy Plugins/MCP serveri va to‘liq Effects katalogi mavjud emas.
Higgsfieldning barcha boshqa modellari, ichki presetlari, hisob/billing tizimi,
credit mexanizmi va cheksiz generatsiya rejalari ham berilmagan.

Shirin’dagi storyboard — oddiy kadr rejalashtirgichi. Shirin’dagi effektlar —
prompt shablonlari. Ular yuqoridagi yopiq xizmatlar tayyor ko‘chirilganini bildirmaydi.

## Amaliy chegaralar

- API xizmatlari pullik; bepul/cheklovsiz real AI generatsiyasi va’da qilinmaydi.
- Bitta reference 128 MB gacha; server jami JSON so‘rovi odatda 256 MB gacha.
  Base64 hajmni oshiradi, shuning uchun bir nechta katta fayl bundan oldin limitga yetishi mumkin.
- Genjutsu reference videosi uchun provider hujjatidagi davomiylik talabi amal qiladi;
  brauzer to‘liq video kontentini oldindan tekshirmaydi.
- Natijani kutish 30 daqiqagacha; server restartidan keyin avtomatik provider recovery yo‘q.
- Android WebView formatlari, mikrofon va TTS imkoniyatlari telefon modeliga bog‘liq.
- Bulutdagi foydalanuvchi hisobi, galereya sinxroni, avtomatik yangilanish va store nashri yo‘q.
