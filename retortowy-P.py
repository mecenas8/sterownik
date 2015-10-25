#!/usr/bin/python
# -*- coding: utf-8 -*-

#==================================================================================
# Algorytm proporcjonalnej korekcji pracy (auto) w trybie retortowym-recznym
# z zalozenia nalezy dobrac tak parametry aby nie wychodzic w podtrzymanie
#
# pomysl algorytmu kol. janusz z forum http://esterownik.pl/forum
# pomysl z korekcjami kol. mark3k
#==================================================================================

# PARAMETRY
ip = '192.168.2.2'
login = 'admin'
password = 'admin'

moc_100 = 1.0/1.0
zadana_co = 65

korekcja_podawania = 1.0
korekcja_postoju =  10.0
korekcja_dmuchania = 0.5

start_podawanie = 15
start_postoj = 35
start_dmuchawa = 43

rozped_podawanie= start_podawanie
rozped_postoj   = start_postoj
rozped_dmuchawa = start_dmuchawa


# PROGRAM GLOWNY
from sterownik import *
import time

rozped = True
c = sterownik(ip,login,password)
c.getStatus()
#c.setRetRecznyDmuchawa(rozped_dmuchawa)
#c.setRetRecznyPostoj(rozped_postoj)
#c.setRetRecznyPodawanie(rozped_podawanie)
poprzednia_co = c.getTempCO()
poprzednie_dmuchanie = nowe_dmuchanie = rozped_dmuchawa
poprzednie_postoj = nowe_postoj = rozped_postoj
poprzednie_podawanie = nowe_podawanie = rozped_podawanie

if (c.version == "BRULI"):
  pod_min = 2
  pod_max = 180
else:
  pod_min = 3
  pod_max = 20

pos_min = 1
pos_max = 600
dmu_min = 25
dmu_max = 100

tryb_info = False

while (c.getStatus()):
  if (c.getTrybAuto() and c.getTypKotla() == "RETORTOWY-RECZNY"):
    tryb_info = False
    delta = int(zadana_co - c.getTempCO() +0.5)
    delta_poprzednia = int(poprzednia_co - c.getTempCO() +0.5)
    
    if (c.getTempCO() < zadana_co):
      nowe_podawanie = delta * korekcja_podawania + start_podawanie
      nowe_postoj    = delta * korekcja_postoju   + start_postoj
      nowe_dmuchanie = delta * korekcja_dmuchania + start_dmuchawa
      if (nowe_podawanie < pod_min):
        moc = nowe_postoj/nowe_podawanie
        nowe_podawanie = pod_min
        nowe_postoj = pod_min*moc
      if (nowe_podawanie > pod_max):
        moc = nowe_postoj/nowe_podawanie
        nowe_podawanie = pod_max
        nowe_postoj = pod_max*moc
      if (nowe_postoj    < pod_min): nowe_postoj = pos_min
      if (nowe_postoj    > pod_max): nowe_postoj = pos_max
      if (nowe_dmuchanie < dmu_min): nowe_dmuchanie = dmu_min
      if (nowe_dmuchanie > dmu_max): nowe_dmuchanie = dmu_max
      rozped = True
      rozped = False
      print("NOWE   Delta:"+ str(delta)+" dmuchanie:" + str(nowe_dmuchanie) + " podawanie:" + str(nowe_podawanie) + " postoj:" + str(nowe_postoj))
    #elif (delta_poprzednia >= 0 and delta <= 0 and rozped == True):
    #  nowe_dmuchanie = rozped_dmuchawa
    #  nowe_postoj = rozped_postoj
    #  nowe_podawanie =rozped_podawanie
    #  rozped = False
    #  print("ROZPED Delta:"+ str(delta)+" dmuchanie:" + str(rozped_dmuchawa) + " podawanie:" + str(rozped_podawanie) + " postoj:" + str(rozped_postoj))
    else:
      print("Delta:"+ str(delta)+" Poprzednia:" + str(delta_poprzednia))

  else:
    if (tryb_info == False):
      tryb_info = True
      print("Sterownik nie jest w trybie auto lub nie ma wlaczonego trybu RETORTOWY-RECZNY")

  nowe_dane = False
  if (nowe_dmuchanie != poprzednie_dmuchanie):
    c.setRetRecznyDmuchawa(nowe_dmuchanie)
    poprzednie_dmuchanie = nowe_dmuchanie
    nowe_dane = True

  if (nowe_postoj != poprzednie_postoj):
    c.setRetRecznyPostoj(nowe_postoj)
    poprzednie_postoj = nowe_postoj
    nowe_dane = True

  if (nowe_podawanie != poprzednie_podawanie):
    c.setRetRecznyPodawanie(nowe_podawanie)
    poprzednie_podawanie = nowe_podawanie
    nowe_dane = True

  if (nowe_dane == True):
    print("Nowa moc: " +str(int(100*moc_100*nowe_podawanie/nowe_postoj))+"%")
    nowe_dane = False
  
  poprzednia_co = c.getTempCO()
  opoznienie = int(nowe_postoj+nowe_podawanie-2)
  if (opoznienie <= 0):
    opoznienie = 1
  time.sleep(opoznienie)
