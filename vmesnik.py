from bottle import *
import os
import json
import datetime as dt
from model import *




kodiranje = 'skrivnost'



# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
ROOT = os.environ.get('BOTTLE_ROOT', '/')


debug(True)

kodiranje = 'skrivnost'



abs_app_dir_path = os.path.dirname(os.path.realpath(__file__))
abs_views_path = os.path.join(abs_app_dir_path, 'views')
TEMPLATE_PATH.insert(0, abs_views_path )

# Mapa za statične vire (slike, css, ...)
static_dir = "./static"


# pot za statične vire, torej slike in css
@route("/static/<filename:path>")
def static(filename):
    return static_file(filename, root=static_dir)


# naredimo začetno stran
@get('/')
def index():
    preglej_stare()
    stanje = id_uporabnik()
    return rtemplate('zacetna_stran.html', stanje = stanje)

@get('/zacetna_stran/')
def zacetna():
    preglej_stare()
    redirect('{0}'.format(ROOT))

# funkcija za prijavo uporabnika
@get('/prijava/')
def prijava():
    preglej_stare() # pregled vseh obstoječih uporabnikov
    stanje = id_uporabnik() # stanje nastavi na id uporabnika
    return rtemplate('prijava.html', napaka = 0, stanje = stanje)

# funkcija, ki preusmeri na uporabnika če je ta veljaven in vrne napako če ni
@post('/prijava/')
def prijavljanje():
    uid = request.forms.uid
    geslo = request.forms.geslo

    if preveri_uporabnika(uid, geslo): # preverimo če je uporabnik veljaven
        uporabnik = pridobi_podatke(uid)
        stevilka = uporabnik['id']
        response.set_cookie("id",stevilka, path='/', secret = kodiranje)
        redirect('{0}uporabnik/'.format(ROOT))
    else:
        return rtemplate('prijava.html', stanje = 0, napaka = 1)


# pridobimo podatke o uporabniku in nas pelje na stran uporabnika
@get('/uporabnik/')
def uporabnik():
    preglej_stare()
    stanje = id_uporabnik()
    podatek = uporabnik_podatki(stanje)
    ime = podatek['ime']
    priimek = podatek['priimek']
    return rtemplate('uporabnik.html',stanje = stanje, ime = ime, priimek = priimek)


# funkcija za pridobitev podatkov za registracijo
@get('/registracija/')
def registracija():
    preglej_stare()
    stanje = id_uporabnik()
    polja_registracija = ("ime", "priimek", "uid", "pass1", "pass2") # ta slovar uporabimo za registracijo in nam v primeru napačne registracije ni potrebno pisati še vse ostalo razen obeh gesel
    podatki = {polje: "" for polje in polja_registracija} 
    return rtemplate('registracija.html', napaka = 0,stanje = stanje, **podatki)



# funkcija za izpolnitev registracije
@post('/registracija/')
def registriranje():
    stanje = id_uporabnik()
    polja_registracija = ("ime", "priimek", "uid", "pass1", "pass2")
    podatki = {polje: "" for polje in polja_registracija}
    podatki = {polje: getattr(request.forms, polje) for polje in polja_registracija} # na podatkih zapolni slovar z atributi

    ime = podatki.get('ime')
    priimek = podatki.get('priimek')
    uid = podatki.get('uid')
    geslo1 = podatki.get('pass1')
    geslo2 = podatki.get('pass2')

    if ime == '' or priimek == '' or uid == '' or geslo1 == '' or geslo2 == '': # vrne napako če je kakšno polje prazno
        return rtemplate('registracija.html', napaka = 1, stanje = stanje, **podatki)

    data = odpri_json('podatki/uporabniki.json')
    for i in data:
        if i['uid'] == uid:
            return rtemplate('registracija.html', napaka = 2,stanje = stanje, **podatki) # vrne napako če je uporabniško ime že zasedeno


    if len(geslo1) < 6: # vrne napako če je geslo prekratko
        return rtemplate('registracija.html', napaka =5,stanje = stanje,  **podatki)
    if geslo1 == geslo2: # če se gesli ujemata in je ostalo veljavno preusmeri na stran uporabnika
        uid = vstavi_novega(ime, priimek, uid, geslo1)
        response.set_cookie("id",uid, path='/', secret = kodiranje)
        string = '{0}uporabnik/'.format(ROOT)
        redirect(string)
    else:
        return rtemplate('registracija.html', stanje = stanje, napaka = 4, **podatki)

# ob odjavi uporabnika se zbrišejo piškotki in vrnitev na začetno stran
@get('/odjava/')
def odjava():
    preglej_stare()

    response.delete_cookie("id", path='/')
    
    redirect('{0}zacetna_stran/'.format(ROOT))



# odpremo podatke o oglasih in iz seznama oglasov dobimo seznam seznamov oglasov
@get('/oglasi/')
def oglasi():
    stanje = id_uporabnik()
    preglej_stare()
    data = odpri_json('podatki/oglasi.json')
    oglasi = []
    for i in data:
        helper = []
        for key in i:
            helper.append(i[key])
        oglasi.append(helper)
    return rtemplate('oglasi.html', stanje = stanje, oglasi = oglasi)

# funkcija za pregled oglasov in izračun časa 
@get('/oglas/<oznaka>')
def oglas(oznaka):
    stanje = id_uporabnik()
    preglej_stare()
    data = odpri_json('podatki/oglasi.json')
    for i in data:
        if int(i['id']) == int(oznaka):
            podatki = i    

    cas_do_konca = str(dt.datetime.strptime(podatki['zakljucek'], '%d.%m.%Y %H:%M') - dt.datetime.now()) # izračun časa do konca veljavnosti dražbe oglasa
    i = cas_do_konca.find('days')
    pretvorba = cas_do_konca[:i] + 'dni' + cas_do_konca[i+4:] # pretvorba v lepši način izpisa časa do konca veljavnosti dražbe
    cas_do_konca = ':'.join(str(pretvorba).split(':')[:2])

    podatk = odpri_json('podatki/stave.json')
    seznam = []
    for i in podatk:
        if int(i['id_ponudbe']) == int(oznaka):
            helper = []
            helper.append(i['ime'])
            helper.append(i['cena'])
            seznam.append(helper)
    return rtemplate('oglas.html', stanje = stanje, konec = cas_do_konca, napaka = 0, ostali = seznam, **podatki)




# funkcija vrne oglase uporabnika
@get('/uporabnik/oglasi')
def oglasi_uporabnika():
    stanje = id_uporabnik()
    preglej_stare()
    data = odpri_json('podatki/oglasi.json')
    oglasi = []
    for i in data:
        if i["prodajalec_id"] == stanje: # če se prodajalec ujema s stanjem zapišemo vse njegove oglase
            pomozni = []
            pomozni.append(i['id'])
            pomozni.append(i['ime'])
            pomozni.append(i['opis'])
            pomozni.append(i['zakljucek'])
            pomozni.append(i['zacetna_cena'])
            oglasi.append(pomozni)
    return rtemplate('oglasi_uporabnik.html', oglasi = oglasi, stanje = stanje)

# funkcija za odstranitev oglasa določenega uporabnika
@post('/uporabnik/oglasi/<oznaka>')
def odstrani(oznaka):
    data = odpri_json('podatki/oglasi.json')
    oglasi = []
    for i in data:
        if int(i['id']) != int(oznaka):
            oglasi.append(i)
    zapisi_json('podatki/oglasi.json', oglasi)
    redirect('{0}uporabnik/oglasi'.format(ROOT)) # preusmeritev na oglase uporabnika


# najprej pridobimo podatke o oglasu in dodajanje ponudb na oglas
@post('/oglas/<oznaka>')
def stavi(oznaka):
    stanje = id_uporabnik()
    uporabnik = uporabnik_podatki(stanje)
    data = odpri_json('podatki/oglasi.json')
    for i in data:
        if i['id'] == int(oznaka):
            podatki = i    

    cas_do_konca = str(dt.datetime.strptime(podatki['zakljucek'], '%d.%m.%Y %H:%M') - dt.datetime.now())
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
    if int(stanje) == int(podatki['prodajalec_id']):
        return rtemplate('oglas.html', stanje = stanje, konec = cas_do_konca, napaka = 3, ostali = seznam, **podatki)

    try:
        cena = int(request.forms.cena)
    except:
        return rtemplate('oglas.html', stanje = stanje, konec = cas_do_konca, napaka = 1, ostali = seznam, **podatki) # vrne napako če cena ni številka

    if cena < int(podatki['zacetna_cena']):
        return rtemplate('oglas.html', stanje = stanje, konec = cas_do_konca, napaka = 2, ostali = seznam, **podatki) # vrne napako ker je cena prenizka

    stava = {'id_ponudbe':podatki['id'], 'id_ponudnika': stanje, 'cena':cena, "ime": uporabnik['ime'] + ' ' + uporabnik["priimek"]}
    dodaj_in_zapisi('podatki/stave.json', stava)
    redirect('{0}oglas/{1}'.format(ROOT, oznaka))

    
# funkcija za pregled ponudb uporabnika
@get('/uporabnik/ponudbe')
def ponudbe():
    stanje = id_uporabnik()
    preglej_stare()
    podatki = odpri_json('podatki/stave.json')
    seznam = []
    for i in podatki:
        if int(i['id_ponudnika']) == int(stanje): # doda ponudbe uporabnika če se stanje in id uporabnika ujemata
            helper = []
            helper.append(i['id_ponudbe'])
            helper.append(i['cena'])
            seznam.append(helper)
    return rtemplate('ponudbe.html', stanje = stanje, ponudbe = seznam)


# funkcija za pregled končanih dražb
@get('/uporabnik/koncane')
def koncane():
    preglej_stare()
    stanje = id_uporabnik()
    podatki = odpri_json('podatki/stari_oglasi.json')
    seznam_tvojih = []
    seznam_zmag = []
    for i in podatki:
        if int(i['id_ponudnika']) == int(stanje): # dražba na kateri je uporabnik dal neko ponudbo se je zaključila
            helper = []
            for key in i:
                helper.append(i[key])
            seznam_tvojih.append(helper)
        elif int(i['id_zmagovalca']) == int(stanje): # vrne zmago na dražbi
            helper = []
            for key in i:
                helper.append(i[key])
            seznam_zmag.append(helper)
    return rtemplate('koncane.html', moje = seznam_tvojih, stanje = stanje, zmage = seznam_zmag) # naredi seznam zmag uporabnika in seznam njegovih zaključenih dražb



# funkcija za pridobitev podatkov o dodajanju oglasa
@get('/uporabnik/dodaj')
def dodaj_oglas():
    stanje = id_uporabnik()
    preglej_stare()
    return rtemplate('dodaj_oglas.html', stanje = stanje, napaka = 0)



# funkcija, ki zapiše nov oglas uporabnika
@post('/uporabnik/dodaj')
def dodaj():
    stanje = id_uporabnik()
    ime = request.forms.ime
    opis = request.forms.opis
    cena = request.forms.cena 
    zakljucek = request.forms.zakljucek
    if ime == '' or opis == '' or cena == '' or zakljucek == '': # v primeru, da je kakšno polje prazno vrne napako
        return rtemplate('dodaj_oglas.html', stanje = stanje, napaka = 3)

    if not cena.isdigit(): # isdigit pove ali se lahko string spremeni v neko številko
        return rtemplate('dodaj_oglas.html', stanje = stanje, napaka = 1) # vrne napako če se nemore pretvorit cena v številko
    cena = int(cena)

    try: # če lahko pretvorimo čas ok drugače pa napaka neveljavnega datuma
        end = dt.datetime.strptime(zakljucek, '%d.%m.%Y %H:%M')
    except:
        return rtemplate('dodaj_oglas.html', stanje = stanje, napaka = 2)

    if end < datetime.now(): # veljavnost časa je potekla zato vrne napako
        return rtemplate('dodaj_oglas.html', stanje = stanje, napaka = 2)

    data = odpri_json('podatki/oglasi.json')
    seznam = []
    for i in data:
        seznam.append(i['id'])
    try: 
        naslednja_stevilka = max(seznam) + 1 # najdemo naslednjo številko
    except: naslednja_stevilka = 1

    nov_oglas = {"id":naslednja_stevilka, "ime":ime, "opis":opis, "prodajalec_id":stanje, "zakljucek":zakljucek, "zacetna_cena":cena}

    dodaj_in_zapisi('podatki/oglasi.json', nov_oglas) # zapišemo nov oglas

    redirect('{0}uporabnik/'.format(ROOT)) # vrne na stran uporabnika


run(host='localhost', port=SERVER_PORT, reloader=RELOADER)