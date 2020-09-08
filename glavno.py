from bottle import *
import os
import json
import datetime



# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
ROOT = os.environ.get('BOTTLE_ROOT', '/')
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)


def rtemplate(*largs, **kwargs):
    """
    Izpis predloge s podajanjem spremenljivke ROOT z osnovnim URL-jem.
    """
    return template(ROOT=ROOT, *largs, **kwargs)



debug(True)

kodiranje = 'skrivnost'

#funkcija za piškotke
def id_uporabnik():
    if request.get_cookie("id", secret = kodiranje):
        piskotek = request.get_cookie("id", secret = kodiranje)
        return piskotek
    else:
        return 0

abs_app_dir_path = os.path.dirname(os.path.realpath(__file__))
abs_views_path = os.path.join(abs_app_dir_path, 'views')
TEMPLATE_PATH.insert(0, abs_views_path )

# Mapa za statične vire (slike, css, ...)
static_dir = "./static"





@route("/static/<filename:path>")
def static(filename):
    return static_file(filename, root=static_dir)



@get('/')
def index():
    stanje = id_uporabnik()
    return rtemplate('zacetna_stran.html', stanje = stanje)

@get('/zacetna_stran/')
def zacetna():
    redirect('{0}'.format(ROOT))



def preveri_uporabnika(ime, geslo):
    with open('podatki/uporabniki.json', 'r') as f:
        igralci = json.load(f)
        for igralec in igralci:
            if igralec['uid'] == ime and igralec['geslo'] == geslo:
                return True
        return False

def pridobi_podatke(uid):
    with open('podatki/uporabniki.json', 'r') as f:
        igralci = json.load(f)
        for igralec in igralci:
            if igralec['uid'] == uid:
                return igralec

@get('/prijava/')
def prijava():
    stanje = id_uporabnik()
    return rtemplate('prijava.html', napaka = 0, stanje = stanje)

@post('/prijava/')
def prijavljanje():
    uid = request.forms.uid
    geslo = request.forms.geslo
    if preveri_uporabnika(uid, geslo):
        igralec = pridobi_podatke(uid)
        stevilka = igralec['id']
        response.set_cookie("id",stevilka, path='/', secret = kodiranje)
        redirect('{0}uporabnik/{1}/'.format(ROOT, stevilka))
    else:
        return rtemplate('prijava.html', stanje = 0, napaka = 1)


def podatki(no):
    no = int(no)
    with open('podatki/uporabniki.json', 'r') as f:
        data = json.load(f)
    for igralec in data:
        if igralec['id'] == no:
            return igralec

@get('/uporabnik/<oznaka>/')
def uporabnik(oznaka):
    stanje = id_uporabnik()
    podatek = podatki(oznaka)
    ime = podatek['ime']
    priimek = podatek['priimek']
    return rtemplate('uporabnik.html',stanje = stanje, ime = ime, priimek = priimek)



@get('/registracija/')
def registracija():
    stanje = id_uporabnik()
    polja_registracija = ("ime", "priimek", "uid", "pass1", "pass2")
    podatki = {polje: "" for polje in polja_registracija} 
    napaka = 0
    return rtemplate('registracija.html', napaka = 0,stanje = stanje, **podatki)


def vstavi_novega(ime, priimek, uid, geslo):
    with open('podatki/uporabniki.json', 'r') as f:
        data = json.load(f)
    seznam = []
    for i in data:
        seznam.append(i['id'])
    try: 
        naslednja_stevilka = max(seznam) + 1
    except: naslednja_stevilka = 1

    data.append({'id':naslednja_stevilka, 'ime':ime, 'priimek': priimek, 'uid': uid, 'geslo':geslo})
    with open('podatki/uporabniki.json', 'w') as f:
        json.dump(data, f)
    return naslednja_stevilka


@post('/registracija/')
def registriranje():
    stanje = id_uporabnik()
    polja_registracija = ("ime", "priimek", "uid", "pass1", "pass2")
    podatki = {polje: "" for polje in polja_registracija}
    podatki = {polje: getattr(request.forms, polje) for polje in polja_registracija}

    ime = podatki.get('ime')
    priimek = podatki.get('priimek')
    uid = podatki.get('uid')
    geslo1 = podatki.get('pass1')
    geslo2 = podatki.get('pass2')

    if ime == '' or priimek == '' or uid == '' or geslo1 == '' or geslo2 == '':
        return rtemplate('registracija.html', napaka = 1, stanje = stanje **podatki)

    with open ('podatki/uporabniki.json', 'r') as f:
        data = json.load(f)
        for i in data:
            if i['uid'] == uid:
                return rtemplate('registracija.html', napaka = 2,stanje = stanje, **podatki)


    if len(geslo1) < 6:
        return rtemplate('registracija.html', napaka =5, **podatki)
    if geslo1 == geslo2:
        uid = vstavi_novega(ime, priimek, uid, geslo1)
        response.set_cookie("id",uid, path='/', secret = kodiranje)
        string = '{0}uporabnik/{1}/'.format(ROOT,uid)
        redirect(string)
    else:
        return rtemplate('registracija.html', stanje = stanje, napaka = 4, **podatki)

@get('/odjava/')
def odjava():
    response.delete_cookie("id", path='/')
    redirect('{0}zacetna_stran/'.format(ROOT))



def iskanje(poizvedba, polje):
    if polje.find(poizvedba) != -1:
        return True
    return False


run(host='localhost', port=SERVER_PORT, reloader=RELOADER)