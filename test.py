import string
import json 
import datetime as dt

st = 'Nekaj zanimivega'
s = 'zaj'
print(st.find(s))

podatki = [{"id":1, "ime":"Starina", "opis":"Nek dolg opis ki se bo skopiral iz interneta", "prodajalec_id":6, "zakljucek":"10.4.2021 16:30", "zacetna_cena" : 60}]

def odpri_json(pot):
    with open(pot, 'r') as f:
        return json.load(f)
print(odpri_json('podatki/uporabniki.json'))



def zapisi_json(pot, podatki):
    with open(pot, 'w') as f:
        json.dump(podatki, f)


zapisi_json('nekaj.json', podatki)