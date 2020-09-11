from bottle import *
import os
import json
import datetime as dt



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
            helper =  [i['cena'], i['id_ponudnika']]
            seznam.append(helper)
    cene = []
    if seznam == []:
        return 0,0
    for i in seznam:
        cene.append(i[0])
    cena = max(cene)
    stevilo = cene.index(cena)
    zmagovalec = seznam[stevilo][1]
    return zmagovalec, cena
    

def preglej_stare():
    podatki = odpri_json('podatki/oglasi.json')
    now = dt.datetime.now().timestamp()
    seznam = []
    for i in podatki:
        if dt.datetime.strptime(i['zakljucek'], '%d.%m.%Y %H:%M').timestamp() - now < 0:
            zmagovalec, cena = najdi_zmagovalca(i["id_ponudbe"])
            podatek = {"id_ponudbe": i["id_ponudbe"], "id_zmagovalca": zmagovalec, "cena": cena}
            dodaj_in_zapisi('podatki/stari_oglasi.json', podatek)
        else:
            seznam.append(i)
    zapisi_json('podatki/oglasi.json', seznam)




@route("/static/<filename:path>")
def static(filename):
    return static_file(filename, root=static_dir)



@get('/')
def index():
    preglej_stare()
    stanje = id_uporabnik()
    return rtemplate('zacetna_stran.html', stanje = stanje)

@get('/zacetna_stran/')
def zacetna():
    preglej_stare()
    redirect('{0}'.format(ROOT))



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

@get('/prijava/')
def prijava():
    preglej_stare()
    stanje = id_uporabnik()
    return rtemplate('prijava.html', napaka = 0, stanje = stanje)

@post('/prijava/')
def prijavljanje():
    uid = request.forms.uid
    geslo = request.forms.geslo
    print(uid)
    print(geslo)
    if preveri_uporabnika(uid, geslo):
        uporabnik = pridobi_podatke(uid)
        stevilka = uporabnik['id']
        response.set_cookie("id",stevilka, path='/', secret = kodiranje)
        redirect('{0}uporabnik/{1}/'.format(ROOT, stevilka))
    else:
        return rtemplate('prijava.html', stanje = 0, napaka = 1)


def podatki(no):
    no = int(no)
    uporabniki = odpri_json('podatki/uporabniki.json')
    for uporabnik in uporabniki:
        if uporabnik['id'] == no:
            return uporabnik

@get('/uporabnik/<oznaka>/')
def uporabnik(oznaka):
    preglej_stare()
    stanje = id_uporabnik()
    podatek = podatki(oznaka)
    ime = podatek['ime']
    priimek = podatek['priimek']
    return rtemplate('uporabnik.html',stanje = stanje, ime = ime, priimek = priimek)



@get('/registracija/')
def registracija():
    preglej_stare()
    stanje = id_uporabnik()
    polja_registracija = ("ime", "priimek", "uid", "pass1", "pass2")
    podatki = {polje: "" for polje in polja_registracija} 
    napaka = 0
    return rtemplate('registracija.html', napaka = 0,stanje = stanje, **podatki)


def vstavi_novega(ime, priimek, uid, geslo):
    data = odpri_json('podatki/uporabniki.json')
    seznam = []
    for i in data:
        seznam.append(i['id'])
    try: 
        naslednja_stevilka = max(seznam) + 1
    except: naslednja_stevilka = 1

    data.append({'id':naslednja_stevilka, 'ime':ime, 'priimek': priimek, 'uid': uid, 'geslo':geslo})
    zapisi_json('podatki/uporabniki.json', data)
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
        return rtemplate('registracija.html', napaka = 1, stanje = stanje, **podatki)

    data = odpri_json('podatki/uporabniki.json')
    for i in data:
        if i['uid'] == uid:
            return rtemplate('registracija.html', napaka = 2,stanje = stanje, **podatki)


    if len(geslo1) < 6:
        return rtemplate('registracija.html', napaka =5,stanje = stanje,  **podatki)
    if geslo1 == geslo2:
        uid = vstavi_novega(ime, priimek, uid, geslo1)
        response.set_cookie("id",uid, path='/', secret = kodiranje)
        string = '{0}uporabnik/{1}/'.format(ROOT,uid)
        redirect(string)
    else:
        return rtemplate('registracija.html', stanje = stanje, napaka = 4, **podatki)

@get('/odjava/')
def odjava():
    preglej_stare()
    response.delete_cookie("id", path='/')
    redirect('{0}zacetna_stran/'.format(ROOT))



def iskanje(poizvedba, polje):
    if polje.find(poizvedba) != -1:
        return True
    return False




@get('/oglasi/')
def oglasi():
    stanje = id_uporabnik()
    preglej_stare()
    data = odpri_json('podatki/oglasi.json')
    oglasi = []
    now = dt.datetime.now()
    for i in data:
        if dt.datetime.strptime(i['zakljucek'], '%d.%m.%Y %H:%M').timestamp() - now.timestamp() < 0:
            print(dt.datetime.strptime(i['zakljucek'], '%d.%m.%Y %H:%M').timestamp() - now.timestamp())
            pass
        else:
            helper = []
            for key in i:
                helper.append(i[key])
            oglasi.append(helper)
    return rtemplate('oglasi.html', stanje = stanje, oglasi = oglasi)

@get('/oglas/<oznaka>')
def oglas(oznaka):
    stanje = id_uporabnik()
    preglej_stare()
    data = odpri_json('podatki/oglasi.json')
    for i in data:
        if int(i['id']) == int(oznaka):
            podatki = i    
    cas_do_konca = str(dt.datetime.strptime(i['zakljucek'], '%d.%m.%Y %H:%M') - dt.datetime.now())
    i = cas_do_konca.find('days')
    pretvorba = cas_do_konca[:i] + 'dni' + cas_do_konca[i+4:]
    cas_do_konca = ':'.join(str(pretvorba).split(':')[:2])

    podatk = odpri_json('podatki/stave.json')
    seznam = []
    for i in podatk:
        if int(i['id_ponudbe']) == int(oznaka):
            helper = []
            helper.append(i['id_ponudnika'])
            helper.append(i['cena'])
            seznam.append(helper)
    return rtemplate('oglas.html', stanje = stanje, konec = cas_do_konca, napaka = 0, ostali = seznam, **podatki)





@get('/uporabnik/oglasi')
def oglasi_uporabnika():
    stanje = id_uporabnik()
    preglej_stare()
    data = odpri_json('podatki/oglasi.json')
    oglasi = []
    for i in data:
        if int(i['prodajalec_id']) == stanje:
            pomozni = []
            for key in i:
                pomozni.append(i[key])
            oglasi.append(pomozni)
    return rtemplate('oglasi_uporabnik.html', oglasi = oglasi, stanje = stanje)

@post('/uporabnik/oglasi/<oznaka>')
def odstrani(oznaka):
    stanje = id_uporabnik()
    data = odpri_json('podatki/oglasi.json')
    oglasi = []
    for i in data:
        if int(i['id']) != int(oznaka):
            oglasi.append(i)
    zapisi_json('podatki/oglasi.json', oglasi)
    redirect('{0}uporabnik/oglasi'.format(ROOT))


@post('/oglas/<oznaka>')
def stavi(oznaka):
    stanje = id_uporabnik()
    data = odpri_json('podatki/oglasi.json')
    for i in data:
        if i['id'] == int(oznaka):
            podatki = i    
    cas_do_konca = str(dt.datetime.strptime(i['zakljucek'], '%d.%m.%Y %H:%M') - dt.datetime.now())
    j = cas_do_konca.find('days')
    pretvorba = cas_do_konca[:j] + 'dni' + cas_do_konca[j+4:]
    cas_do_konca = ':'.join(str(pretvorba).split(':')[:2])

    podatk = odpri_json('podatki/stave.json')
    seznam = []
    for i in podatk:
        if int(i['id_ponudbe']) == int(oznaka):
            helper = []
            helper.append(i['id_ponudnika'])
            helper.append(i['cena'])
            seznam.append(helper)
    try:
        cena = int(request.forms.cena)
    except:
        return rtemplate('oglas.html', stanje = stanje, konec = cas_do_konca, napaka = 1, ostali = seznam, **podatki)
    data = odpri_json('podatki/oglasi.json')
    for i in data:
        if int(i['id']) == int(oznaka):
            oglas = i
    if cena < i['zacetna_cena']:
        return rtemplate('oglas.html', stanje = stanje, konec = cas_do_konca, napaka = 2, ostali = seznam, **podatki)

    stava = {'id_ponudbe':oglas['id'], 'id_ponudnika': stanje, 'cena':cena}
    dodaj_in_zapisi('podatki/stave.json', stava)
    redirect('{0}oglas/{1}'.format(ROOT, oznaka))

    

@get('/uporabnik/ponudbe')
def ponudbe():
    stanje = id_uporabnik()
    podatki = odpri_json('podatki/stave.json')
    seznam = []
    for i in podatki:
        if int(i['id_ponudnika']) == int(stanje):
            helper = []
            helper.append(i['id_ponudbe'])
            helper.append(i['cena'])
            seznam.append(helper)
    return rtemplate('ponudbe.html', stanje = stanje, ponudbe = seznam)
















run(host='localhost', port=SERVER_PORT, reloader=RELOADER)