# Deploy Gratis

Pentru stack-ul actual, cea mai simpla varianta este `Render Free`.

Ce primesti:
- un link public de forma `https://...onrender.com`
- HTTPS automat
- deploy fara sa rulezi comenzi pe calculatorul utilizatorului
- baza de date Postgres gratuita pentru demo

Ce trebuie sa stii:
- serviciul gratuit intra in sleep dupa inactivitate
- primul load dupa sleep poate dura aproximativ un minut
- baza de date gratuita Render expira dupa 30 de zile daca ramane pe planul free

## Varianta cea mai simpla

1. Urca proiectul pe GitHub.
2. Intra in Render si alege `New +`.
3. Alege `Blueprint`.
4. Conecteaza repository-ul care contine acest proiect.
5. Render va citi automat fisierul `render.yaml`.
6. La primul deploy completezi doar cheia `AIMONEYCOACH_GROQ_API_KEY`.
7. Dupa deploy, deschizi linkul public primit de la Render.

## Ce foloseste Render din proiect

- `render.yaml` pentru serviciul web si baza de date
- `.python-version` pentru versiunea de Python
- `/health` pentru verificarea de sanatate
- `manifest.webmanifest` si `service-worker.js` pentru PWA

## Daca vrei ceva tot gratis, dar mai stabil pentru baza de date

Poti pastra web app-ul pe Render Free si poti muta baza de date pe un serviciu Postgres gratuit separat.

In acel caz:
1. creezi baza de date externa
2. copiezi connection string-ul
3. in Render setezi `AIMONEYCOACH_DATABASE_URL` cu acel URL
4. faci redeploy

Aplicatia accepta acum si connection string-uri Postgres obisnuite, nu doar URL-uri deja pregatite pentru `asyncpg`.
