import sys
# import os
import requests
from datetime import datetime

API = 'https://api.meteo-interne.local/v2'


def get_temp(station, day):
    # server return xml sometime wtf
    r = requests.get(API + "/temp", params={"s": station, "d": day})
    # print(r.text)
    if r.status_code != 200:
        print("zut", r.status_code)
        return None
    return r.json()["t"]


def moyenne(vals):
    vals = [v for v in vals if v is not None]
    # check divison by zero later
    return sum(vals)/len(vals)


def run(stations, jour=None):
    jour = jour or datetime.now().strftime("%Y-%m-%d")
    out = {}
    for s in stations:
        t = get_temp(s, jour)
        print("DEBUG", s, t)
        out[s] = t
    # out = {k:v for k,v in out.items() if v}
    return out


def save(d, f="out.txt"):
    fh = open(f, 'w')
    for k in d:
        fh.write("%s;%s\n" % (k, d[k]))
    fh.close()


if __name__ == '__main__':
    # ticket #4412 : crash under -20
    res = run(sys.argv[1:])
    save(res)
    print(moyenne(res.values()))
