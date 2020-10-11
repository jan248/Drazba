import json
import datetime as dt # uvozim knjižnico za efektivno delo s časom v pythonu
from bottle import *
import os # operacijski sistem za uporabo funkcije ROOT

kodiranje = 'skrivnost' # za uporabo piškotkov v id_uporabnika
ROOT = os.environ.get('BOTTLE_ROOT', '/')

# uporaba relativne poti
def rtemplate(*largs, **kwargs):
    """
    Izpis predloge s podajanjem spremenljivke ROOT z osnovnim URL-jem.
    """
    return template(ROOT=ROOT, *largs, **kwargs)



# funkcija za preverjanje ali je uporabnik že prijavljen in uporabo piškotkov
def id_uporabnik():
    if request.get_cookie("id", secret = kodiranje):
        piskotek = request.get_cookie("id", secret = kodiranje)
        return int(piskotek)
    else:
        return 0

# pomožne funkcije za delo z jsoni
# funkcija odpre datoteko
def odpri_json(pot):
    with open(pot, 'r') as f:
        return json.load(f)

# funkcija zapiše v datoteko
def zapisi_json(pot, podatki):
    with open(pot, 'w') as f:
        json.dump(podatki, f)

# funkcija doda podatke in jih zapiše v json
def dodaj_in_zapisi(pot, podatek):
    data = odpri_json(pot)
    data.append(podatek)
    zapisi_json(pot, data)

# funkcija poišče zmagovalca, njegovo ceno in id
def najdi_zmagovalca(id):
    data = odpri_json('podatki/stave.json') # odpre vse stave
    seznam = []
    # naredimo seznam vseh stav narejenih na določeno ponudbo
    for i in data:
        if int(i['id_ponudbe']) == int(id):
            helper =  [i['cena'], i['id_ponudnika'], i['ime']]
            seznam.append(helper)
    cene = []
    if seznam == []:
        return 0,0,'Nihče' # ni zmagovalca
    for i in seznam:
        cene.append(i[0])
    cena = max(cene)
    stevilo = cene.index(cena) # na katerem  mestu se nahaja maksimalna ponujena cena
    zmagovalec = seznam[stevilo][1]
    ime = seznam[stevilo][2]
    return zmagovalec, cena, ime
    
# strtime preformatira string v datetime objekt
# funkcija odpre vse podatke o ponudbah in pregleda njihovo veljavnost
def preglej_stare():
    podatki = odpri_json('podatki/oglasi.json')
    seznam = []
    for i in podatki:
        if dt.datetime.strptime(i['zakljucek'], '%d.%m.%Y %H:%M') < dt.datetime.now(): # pregled če je dražba že potekla
            zmagovalec, cena, ime = najdi_zmagovalca(i["id_ponudbe"])
            podatek = {"id_ponudbe": i["id_ponudbe"], "id_zmagovalca": zmagovalec, "cena": cena, "id_ponudnika":i['prodajalec_id'], 'ime_zmagovalca':ime} # slovar zaključenih ogalsov
            dodaj_in_zapisi('podatki/stari_oglasi.json', podatek)
        else:
            seznam.append(i) # seznam oglasov, ki še niso pretekli
    zapisi_json('podatki/oglasi.json', seznam)

# funkcija za preverbo uporabnika
def preveri_uporabnika(ime, geslo):
    uporabniki = odpri_json('podatki/uporabniki.json') # odpremo vse podatke o uporabnikih
    for uporabnik in uporabniki:
        if uporabnik['uid'] == ime and uporabnik['geslo'] == geslo: # preveri če se ime in geslo ujemata
            return True
    return False

# funkcija za pridobivanje podatkov uporabniškega imena
def pridobi_podatke(uid):
    uporabniki = odpri_json('podatki/uporabniki.json')
    for uporabnik in uporabniki:
        if uporabnik['uid'] == uid:
            return uporabnik

# funkcija za pridobivanje podatkov id uporabnikov
def uporabnik_podatki(no):
    no = int(no)
    uporabniki = odpri_json('podatki/uporabniki.json')
    for uporabnik in uporabniki:
        if uporabnik['id'] == no:
            return uporabnik

# funkcija za iskanje nove številke za id uporabnika 
def vstavi_novega(ime, priimek, uid, geslo):
    data = odpri_json('podatki/uporabniki.json')
    seznam = []
    for i in data:
        seznam.append(i['id'])
    try: 
        naslednja_stevilka = max(seznam) + 1
    except: naslednja_stevilka = 1 # v primeru registracije prvega uporabnika

    dodaj_in_zapisi('podatki/uporabniki.json', {'id':naslednja_stevilka, 'ime':ime, 'priimek': priimek, 'uid': uid, 'geslo':geslo})
    return naslednja_stevilka

