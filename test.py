import string
import json 
import datetime as dt

st = 'Nekaj zanimivega'
s = 'zaj'


podatki = [{"id":1, "ime":"Starina", "opis":"Nek dolg opis ki se bo skopiral iz interneta", "prodajalec_id":6, "zakljucek":"10.4.2021 16:30", "zacetna_cena" : 60}]

def odpri_json(pot):
    with open(pot, 'r') as f:
        return json.load(f)




def zapisi_json(pot, podatki):
    with open(pot, 'w') as f:
        json.dump(podatki, f)


def najdi_zmagovalca(id):
    data = odpri_json('podatki/stave.json')
    seznam = []
    print(data)
    for i in data:
        if int(i['id_ponudbe']) == int(id):
            helper =  [i['cena'], i['id_ponudnika']]
            seznam.append(helper)
    cene = []
    for i in seznam:
        cene.append(i[0])
    cena = max(cene)
    stevilo = cene.index(cena)
    print(stevilo)
    zmagovalec = seznam[stevilo][1]
    return print(zmagovalec, cena)

najdi_zmagovalca(1)
