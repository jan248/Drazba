import json
import datetime as dt
from bottle import *
import os

kodiranje = 'skrivnost'
ROOT = os.environ.get('BOTTLE_ROOT', '/')


def rtemplate(*largs, **kwargs):
    """
    Izpis predloge s podajanjem spremenljivke ROOT z osnovnim URL-jem.
    """
    return template(ROOT=ROOT, *largs, **kwargs)




def id_uporabnik():
    if request.get_cookie("id", secret = kodiranje):
        piskotek = request.get_cookie("id", secret = kodiranje)
        return int(piskotek)
    else:
        return 0


def odpri_json(pot):
    with open(pot, 'r') as f:
        return json.load(f)

def zapisi_json(pot, podatki):
    with open(pot, 'w') as f:
        json.dump(podatki, f)

def dodaj_in_zapisi(pot, podatek):
    data = odpri_json(pot)
    data.append(podatek)
    zapisi_json(pot, data)


def najdi_zmagovalca(id):
    data = odpri_json('podatki/stave.json')
    seznam = []
    for i in data:
        if int(i['id_ponudbe']) == int(id):
            helper =  [i['cena'], i['id_ponudnika'], i['ime']]
            seznam.append(helper)
    cene = []
    if seznam == []:
        return 0,0,'Nihče'
    for i in seznam:
        cene.append(i[0])
    cena = max(cene)
    stevilo = cene.index(cena)
    zmagovalec = seznam[stevilo][1]
    ime = seznam[stevilo][2]
    return zmagovalec, cena, ime
    

def preglej_stare():
    podatki = odpri_json('podatki/oglasi.json')
    seznam = []
    for i in podatki:
        if dt.datetime.strptime(i['zakljucek'], '%d.%m.%Y %H:%M') < dt.datetime.now():
            zmagovalec, cena, ime = najdi_zmagovalca(i["id_ponudbe"])
            podatek = {"id_ponudbe": i["id_ponudbe"], "id_zmagovalca": zmagovalec, "cena": cena, "id_ponudnika":i['prodajalec_id'], 'ime_zmagovalca':ime}
            dodaj_in_zapisi('podatki/stari_oglasi.json', podatek)
        else:
            seznam.append(i)
    zapisi_json('podatki/oglasi.json', seznam)

def preveri_uporabnika(ime, geslo):
    uporabniki = odpri_json('podatki/uporabniki.json')
    for uporabnik in uporabniki:
        if uporabnik['uid'] == ime and uporabnik['geslo'] == geslo:
            return True
    return False

def pridobi_podatke(uid):
    uporabniki = odpri_json('podatki/uporabniki.json')
    for uporabnik in uporabniki:
        if uporabnik['uid'] == uid:
            return uporabnik

def uporabnik_podatki(no):
    no = int(no)
    uporabniki = odpri_json('podatki/uporabniki.json')
    for uporabnik in uporabniki:
        if uporabnik['id'] == no:
            return uporabnik

def vstavi_novega(ime, priimek, uid, geslo):
    data = odpri_json('podatki/uporabniki.json')
    seznam = []
    for i in data:
        seznam.append(i['id'])
    try: 
        naslednja_stevilka = max(seznam) + 1
    except: naslednja_stevilka = 1

    dodaj_in_zapisi('podatki/uporabniki.json', {'id':naslednja_stevilka, 'ime':ime, 'priimek': priimek, 'uid': uid, 'geslo':geslo})
    return naslednja_stevilka

