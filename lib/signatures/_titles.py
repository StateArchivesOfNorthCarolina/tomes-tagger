""" This file contains a list of personal titles and abbreviations.

The original source for the list is:
    https://mediawiki.middlebury.edu/wiki/LIS/Name_Standards
"""

# modified as needed.
_data = """
A
An
2Lt
2nd Lieutenant
Abbot
Adm
Admiral
Amb
Ambassador
Baron
Baroness
BG
Bishop
Br
Brig Gen
Brigadier General
Brnss
Brother
Capt
Captain
CDR
Cdr
Chan
Chancellor
Chaplain
Chapln
Chief Petty Officer
Cmdr
Cntss
Col
Colonel
Commander
Commissioner
Corporal
Count
Countess
Cpl
CPO
Cpt
Dean
Deputy
Director
Dr
Drs
Duke
Ens
Ensign
Estate of
Father
Fr
Frau
Friar
Gen
General
Gov
Governor
Judge
Justice
Jr
Lieutenant
Lieutenant Colonel
Lieutenant Commander
Lieutenant General
Lieutenant Governor
Lieutenant junior grade
Lord
Lt
Lt Cmdr
Lt Col
Lt Gen
Lt Gov
Lt jg
Ltc
Ltg
Madame
Mademoiselle
Maj
Major
Master
Master Sergeant
Master Sgt
MD
MIDN
Midshipman
Miss
Mlle
Mme
Monsieur
Monsignor
Mr
Mrs
Ms
Msgr
Mx
Pres
President
Princess
Prof
Professor
RAdm
Rabbi
Rear Admiral
Rep
Representative
Rev
Reverend
Reverends
Revs
Right Reverend
RtRev
S Sgt
Secretary
Sen
Senator
Senor
Senora
Senorita
Sergeant
Sgt
Sheikh
Sir
Sister
Sr
Sra
Srta
Staff Sergeant
The Hon
The Honorable
The Venerable
Trust(ees)of
VAdm
Vice Admiral
"""

# dedupe.
titles = set(t for t in _data.split())
