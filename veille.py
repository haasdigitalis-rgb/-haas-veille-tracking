import urllib.request, re, json, datetime

WEBHOOK = "https://script.google.com/macros/s/AKfycbzySZCPrkslkz90gatpKMSa9UiVtAlsWWAebaWrBOqXby4mG3bLdiUQYe-KRVJvBQQXoQ/exec"
maj = datetime.date.today().isoformat()

PAGES = [
    ("AXEO Lyon", "SAP", "Lyon", "https://www.axeo-lyon.fr/"),
    ("AXEO Lille", "SAP", "Lille", "https://www.axeo-lille.fr/"),
    ("AXEO Gennevilliers", "SAP", "Gennevilliers", "https://www.axeo-gennevilliers.fr/"),
    ("AXEO Haute-Gironde", "SAP", "Haute-Gironde", "https://www.axeomenage-haute-gironde.fr/"),
    ("AXEO Sevres", "SAP", "Sevres", "https://www.axeo-sevres.fr/"),
    ("AXEO Versailles", "SAP", "Versailles accueil", "https://www.axeoservicesversailles.fr/"),
    ("AXEO Versailles", "SAP", "Versailles seniors", "https://www.axeoservicesversailles.fr/seniors/"),
    ("AXEO Versailles", "SAP", "Versailles pro", "https://www.axeoservicesversailles.fr/services-pro/"),
    ("AXEO Toulouse", "SAP", "Toulouse accueil", "https://www.axeo-toulouse.fr/"),
    ("AXEO Toulouse", "SAP", "Toulouse livraison-repas", "https://www.axeo-toulouse.fr/livraison-repas/"),
    ("AXEO Toulouse", "SAP", "Toulouse seniors", "https://www.axeo-toulouse.fr/seniors/"),
    ("AXEO Toulouse", "SAP", "Toulouse pro", "https://www.axeo-toulouse.fr/services-pro/"),
    ("AXEO Manosque", "SAP", "Manosque", "https://www.axeo-manosque.fr/"),
    ("AXEO Hossegor", "SAP", "Hossegor", "https://www.axeo-hossegor.fr/"),
    ("AXEO Le Havre", "SAP", "Le Havre", "https://www.axeo-le-havre.fr/"),
    ("AXEO Maule", "SAP", "Maule", "https://www.axeo-maule.fr/"),
    ("AXEO Saint-Malo", "SAP", "Saint-Malo", "https://www.axeo-saintmalo.fr/"),
    ("AXEO Amboise", "SAP", "Amboise", "https://www.axeo-amboise.fr/"),
    ("AXEO Saint-Maur", "SAP", "Saint-Maur", "https://www.axeo-saintmaur.fr/"),
    ("AXEO Fontenay", "Paysagisme", "Fontenay", "https://axeo-fontenay-jardin.vercel.app/"),
    ("Quadra Terra", "Paysagisme", "Accueil reseau", "https://www.leads-quadraterra.fr/"),
    ("Quadra Terra", "Paysagisme", "Craponne hub", "https://www.leads-quadraterra.fr/craponne"),
    ("Quadra Terra", "Paysagisme", "Craponne entretien-jardin", "https://www.leads-quadraterra.fr/craponne-entretien-jardin"),
    ("Quadra Terra", "Paysagisme", "Craponne paysagiste", "https://www.leads-quadraterra.fr/craponne-paysagiste"),
    ("Quadra Terra", "Paysagisme", "Craponne amenagement", "https://www.leads-quadraterra.fr/craponne-amenagement-exterieur"),
    ("Quadra Terra", "Paysagisme", "Corcy hub", "https://www.leads-quadraterra.fr/corcy"),
    ("Quadra Terra", "Paysagisme", "Corcy entretien-jardin", "https://www.leads-quadraterra.fr/corcy-entretien-jardin"),
    ("Quadra Terra", "Paysagisme", "Corcy paysagiste", "https://www.leads-quadraterra.fr/corcy-paysagiste"),
    ("Quadra Terra", "Paysagisme", "Corcy amenagement", "https://www.leads-quadraterra.fr/corcy-amenagement-exterieur"),
    ("Quadra Terra", "Paysagisme", "Montmerle hub", "https://www.leads-quadraterra.fr/montmerle"),
    ("Quadra Terra", "Paysagisme", "Montmerle entretien-jardin", "https://www.leads-quadraterra.fr/montmerle-entretien-jardin"),
    ("Quadra Terra", "Paysagisme", "Montmerle paysagiste", "https://www.leads-quadraterra.fr/montmerle-paysagiste"),
    ("Quadra Terra", "Paysagisme", "Montmerle amenagement", "https://www.leads-quadraterra.fr/montmerle-amenagement-exterieur"),
    ("Actisud", "Anti-nuisibles", "Actisud", "https://www.actisud-anti-nuisibles.fr/"),
    ("Help Confort Evreux", "Plomberie", "Evreux", "https://helpconfort-evreux.vercel.app/"),
    ("Age d'Or Courbevoie", "Senior care", "Courbevoie", "https://agedor92.com/"),
]

# Compte Google Ads attendu par page (detection regression / contamination)
REF = {
    "axeo-saintmaur.fr": "AW-17334205833",
    "axeo-toulouse.fr": "AW-16876389962",
    "helpconfort-evreux": "AW-18053507821",
    "axeo-le-havre.fr": "AW-18122386907",
    "/craponne": "AW-16942204653",
    "/corcy": "AW-17031710957",
    "/montmerle": "AW-17931195489",
}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36"})
    try:
        r = urllib.request.urlopen(req, timeout=25)
        return r.getcode(), r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return 0, ""


def uniq(rx, s):
    return ",".join(sorted(set(re.findall(rx, s))))


rows = [["Client", "Vertical", "Page", "URL", "Domaine", "AW", "GT", "GTM", "Dexem", "URLpass", "Derniere MAJ"]]
critical = []   # font echouer le run (= email d'alerte)
warnings = []   # notes (run reste vert)

for client, vert, page, url in PAGES:
    code, html = fetch(url)
    aw = uniq(r"AW-[0-9]{8,}", html)
    gt = uniq(r"GT-[A-Z0-9]{6,}", html)
    gtm = uniq(r"GTM-[A-Z0-9]{5,}", html)
    dx = ",".join(sorted(set(re.findall(r"cdn\.dexem\.net/tags/([A-Za-z0-9-]{6,})", html))))
    up = "OUI" if "url_passthrough" in html else "NON"
    dom = re.sub(r"^https?://", "", url).split("/")[0]
    rows.append([client, vert, page, url, dom, aw, gt, gtm, dx, up, maj])

    # --- CRITIQUE : fait echouer le run ---
    if code != 200:
        critical.append(f"HTTP {code} : {client} - {page} ({url})")
    elif not (aw or gt or gtm or dx):
        critical.append(f"AUCUN tag : {client} - {page} ({url})")
    if "AW-18053507821" in aw and "saintmaur" in url:
        critical.append(f"CONTAMINATION : compte Help Confort sur Saint-Maur ({url})")
    for key, exp in REF.items():
        if key in url and aw and exp not in aw:
            critical.append(f"Regression AW : {url} -> {aw} au lieu de {exp}")
    # url_passthrough manquant sur une page taguee Google = perte de conversions (gclid non capte)
    if (aw or gt or gtm) and "url_passthrough" not in html:
        critical.append(f"url_passthrough MANQUANT (perte conversions gclid) : {client} - {page} ({url})")

    # --- AVERTISSEMENT : residu placeholder (souvent inoffensif, ex. noscript) ---
    if re.search(r"A-REMPLIR|G-XXXXXXXXXX|CONVERSION_LABEL|AW-XXXX", html):
        warnings.append(f"Placeholder residuel : {client} - {page} ({url})")

# Envoi vers le Google Sheet (webhook Apps Script). Reponse HTML ignoree (normal).
try:
    urllib.request.urlopen(
        urllib.request.Request(WEBHOOK, data=json.dumps({"rows": rows}).encode(), headers={"Content-Type": "application/json"}),
        timeout=30,
    ).read()
except Exception as e:
    print("POST webhook:", e)

print(f"Scan termine — {len(rows) - 1} pages, Google Sheet mis a jour ({maj}).")
if warnings:
    print("\n[Avertissements - non bloquants]")
    for w in warnings:
        print("  -", w)
if critical:
    print("\n*** ALERTES CRITIQUES ***")
    for a in critical:
        print("  -", a)
    raise SystemExit(1)
print("\nParc sain — aucune anomalie critique.")
