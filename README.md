# Presentazione "Intelligenza Artificiale" — Orientamento ITS

Deck per ragazzi delle superiori, pensato per la giornata di orientamento dell'**ITS-ICT Academy di Roma** (corso **AI & Digital Innovation Specialist**). Aggiornata a **novembre 2026**.

## Come si usa

- Apri `index.html` con un doppio click (funziona anche offline, tranne i video YouTube che richiedono internet).
- **Frecce ← →** (o click ai lati, PgAv/PgInd) per navigare · **F** fullscreen · **N** mostra/nasconde le **note del relatore** · **Home/End** inizio/fine.
- Slide 2: i riquadri dell'indice sono **cliccabili** e saltano alla sezione relativa.
- Slide 13 (Chi c'è dietro): **quiz** — mostra solo le facce, poi **click** sulla slide per rivelare nomi e aziende.
- I video partono automaticamente da 0:00 con audio e fanno loop dall’inizio (YouTube ignora `start` al loop, quindi non lo usiamo). Per tagliare la clip: `data-end` (secondi) nel `.yt` della slide.

## Struttura (23 slide)

1. Titolo · 2. Indice in 5 tappe cliccabili · 3. Cos'è l'AI: DATI → SCHEMI → PREDIZIONI con esempio reale del "prossimo token" (Roma 91%…)
4–11. **Video di frontiera nov-2026** (~15 s in loop): GPT-6.2 Astra (OpenAI), Claude Fable 5.2 (Anthropic), Veo 3.1 (Google Flow), Runway Gen-4.5, Kling 4.0, Higgsfield, ElevenLabs v4, Suno v6. *(Sora 2 e Oasis tagliati: Sora è stato dismesso nel 2026)*
12. **Chi fa cosa** — matrice piattaforme top nov-2026 (crea / costruisce)
13. **Chi c'è dietro** — quiz con click per rivelare nomi/aziende
14. **Mappa datacenter + numeri 2026**: ~12.000 nel mondo, USA 5.427 (45%), Europa 3.346, Cina ~600, Italia >100, USA ≈ 75% del compute AI di frontiera
15. Dentro un datacenter + dettaglio GPU NVIDIA, wafer, chip
16. **Filiera chip**: NVIDIA 🇺🇸 → TSMC 🇹🇼 → ASML 🇳🇱 → HBM 🇰🇷 → assemblaggio
17. **Cavi sottomarini 2026**: 607 attivi + 102 in programma; tagli Mar Rosso 2024, Baltico (10 dal 2022), Taiwan (5 nel 2024-25); Cable Hub UE da giu 2026
18. **Energia**: mappa consumi per area (USA 45% / Cina 25% / Europa 15% — IEA) + mix USA (gas >40%, rinnovabili 24%…); 485→950 TWh entro 2030; USA 4-5%→9-17% (EPRI 2026)
19. **Fragilità** con immagini: cavi, rete, alluvioni/incendi, cyber, deepfake, bias, pochi fornitori, AI Act UE
20. **Cosa puoi fare tu oggi** — piattaforme top nov-2026
21–23. Corso ITS (1800 h, gratis, EQF 5) · Iscriviti (QR, contatti, sede) · Domande?

## Cartelle

- `index.html`, `css/`, `js/` — il deck
- `assets/img/people/` — foto dei fondatori (Wikipedia)
- `assets/img/logos/` — loghi dei brand
- `assets/img/photos/` — datacenter, GPU NVIDIA, chip, cavi, rete elettrica, rischi (Wikimedia Commons)
- `assets/img/thumbs/` — miniature dei video YouTube
- `assets/data/world.js` — mappa del mondo (GeoJSON incorporato, funziona offline)
- `fetch_assets*.py` — script usati per scaricare gli asset

## Note

- I video sono embed YouTube con segmento start/end: serve connessione internet. Se offline resta la miniatura con play.
- Fonti: siti ufficiali (OpenAI, Anthropic, Google DeepMind, Runway, Kling, Higgsfield, ElevenLabs, Suno), its-ictacademy.com, report IEA "Energy and AI" / "Electricity 2026", EPRI 2026, TeleGeography 2026, Cloudscene/Statista per i datacenter, Wikipedia/Wikimedia per foto e loghi.
