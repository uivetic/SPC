# OPSTE

rolesOpste = [
    'Delegat na GA',
    'Delegat na RM',
    'Zapisničar na Skupštini',
    'Prisustvo na Skupštini',
    'BmB',
    'Aktivacija u godišnjim timovima',
    'Radne grupe',
    'Mandati'

]
opsteDelegatNaGA = {
    'sGA':[5],
    'aGA':[5]
}
opsteDelegatNaRM = {
    'sRM' : [3],
    'aRM' : [3]
}

kvartaliSkupstina = [1,2,3,4,5]
opsteZapisnicarNaSkupstini = {
    'I Kvartalna':     [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5],
    'II Kvartalna':    [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5],
    'III Kvartalna':   [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5],
    'Izborna':         [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5],
    'Vandredna':       [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
}

opstePrisustvoNaSkupstini = {
    'I Kvartalna':      [1],
    'II Kvartalna':     [1],
    'III Kvartalna':    [1],
    'Izborna':          [1],
    'Vanredna':         [1]
}

opsteBmB = {
    'Blagajnik':        [4],
    'HR':               [4],
    'PR':               [4],
    'Sekretar':         [4],
    'FR':               [4],
    'Predsednik':       [4],
}

kvartaliGodisnji = [1,2,3,4]
opsteAktivnostUGodisnjim = {
    'PR':       [0,1,2,3,4],
    'FR':       [0,1,2,3,4],
    'HR':       [0,1,2,3,4],
    'IT':       [0,1,2,3,4],
    'GRANT':    [0,1,2,3,4],
    'KM':       [0,1,2,3,4],
    'INT':      [0,1,2,3,4],
    'PUB':      [0,1,2,3,4]
}

opsteRadneGrupe = {
    'Radne grupe':[3]
}
opsteMandati = {
    'Bord':         [24],
    'Menadžment':   [8],
    'NO':           [7] 
}

rolesOpsteDict = {
    'Delegat na GA': opsteDelegatNaGA,
    'Delegat na RM': opsteDelegatNaRM,
    'Zapisničar na Skupštini': opsteZapisnicarNaSkupstini,
    'Prisustvo na Skupštini': opstePrisustvoNaSkupstini,
    'BmB':opsteBmB,
    'Aktivacija u godišnjim timovima':opsteAktivnostUGodisnjim,
    'Radne grupe':opsteRadneGrupe,
    'Mandati':opsteMandati
}