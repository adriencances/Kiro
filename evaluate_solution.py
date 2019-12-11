#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 22:13:07 2019

@author: Adrien CANCES
"""

from get_data import get_data


def cost_solution(Q, F, H, L_f, a, st_f, gr_C, tr_P):
    # Renvoie le cout de sous-traitance pour le fournisseur F.
    def c_st(f):
        return L_f[f][0]
    
    # On calcule le cout de la solution.
    c_tot = 0
    for f in st_f:
        c_tot += c_st(f)
    for P in tr_P:
        nb_f = P[2]
        list_f = P[3]
        c_tot += a[F][list_f[0]]
        for i in range(nb_f - 1):
            c_tot += a[list_f[i]][list_f[i + 1]]
        c_tot += a[list_f[nb_f - 1]][F + 1]

    return c_tot


def verify_solution(Q, F, H, L_f, a, st_f, gr_C, tr_P):    
    # Renvoie la marchandise que l'on attend du fournisseur f a la semaine s.
    def march(f, s):
        return L_f[f][1][s]
    
    # Les fournisseurs sous-traites ne sont declares qu'une fois.
    assert len(st_f) == len(set(st_f))
    for f in st_f:
        assert f in range(F)
    
    # Les groupes sont de cardinal maximal 4, deux a deux disjoints,
    # et l'union des groupes contient tous les elements non sous-traites.
    if gr_C != []:
        assert max([len(C) for C in gr_C]) <=4
    elts_of_gr_C = [f for C in gr_C for f in C]
    assert sorted(elts_of_gr_C) == sorted(list(set(elts_of_gr_C)))
    for f in elts_of_gr_C:
        assert f in range(F)
    for f in range(F):
        assert f in st_f or f in elts_of_gr_C
    
    # Les tournees visitent des elements d'un meme
    # groupe, et le nb de marchandises chargees chez chaque fournisseur
    # visite est specifie. Un element est visite au plus une fois par tournee,
    # et n'est pas visite si le camion ne charge pas de marchandises chez lui.
    # La capacite des camions est bien respectee.
    for P in tr_P:
        c = P[0]
        s = P[1]
        nb_f = P[2]
        list_f = P[3]
        list_q = P[4]
        assert s in range(H)
        assert nb_f == len(list_f)
        assert nb_f == len(set(list_f))
        assert nb_f == len(list_q)
        for f in list_f:
            assert f in range(F)
            assert f in gr_C[c]
            assert march(f, s) != 0
        assert sum(list_q) <= Q


def evaluate_solution(data_file_name, sol_file_name):
    # On recupere les donnees du probleme.
    Q, F, H, L_f, a = get_data(data_file_name)
    
    # On ouvre le fichier solution pour recupere la solution.
    file = open(sol_file_name, 'r')
    lines = file.read().splitlines()
    
    x_line = lines[0].split()
    nb_st = int(x_line[1])
    st_f = [int(x_line[i]) for i in range(3, len(x_line))]
    
    y_line = lines[1].split()
    nb_P = int(y_line[1])
    
    z_line = lines[2].split()
    nb_C = int(z_line[1])
    
    gr_C = []
    info_gr_C = []
    for c in range(nb_C):
        line = lines[3 + c].split()
        info_gr_C.append([int(line[1]), int(line[3]), \
                      [int(line[i]) for i in range(5, len(line))] ])
        gr_C.append([int(line[i]) for i in range(5, len(line))])
    
    tr_P = []
    ids_P = []
    for p in range(nb_P):
        line = lines[3 + nb_C + p].split()
        tr_P.append([int(line[3]), int(line[5]), int(line[7]), \
                  [int(line[i]) for i in range(9, len(line), 3)], \
                  [int(line[i]) for i in range(10, len(line), 3)]
                   ])
        ids_P.append(int(line[1]))
    
    # Renvoie la marchandise que l'on attend du fournisseur f a la semaine s.
    def march(f, s):
        return L_f[f][1][s]
    
    
    # Les fournisseurs sous-traites ne sont declares qu'une fois.
    assert nb_st == len(st_f)
    assert nb_st == len(set(st_f))
    for f in st_f:
        assert f in range(F)
    
    # Les groupes sont de cardinal maximal 4, deux a deux disjoints,
    # et l'union des groupes contient tous les elements non sous-traites.
    assert nb_C == len(gr_C)
    if gr_C != []:
        assert max([len(C) for C in gr_C]) <=4
    elts_of_gr_C = [f for C in gr_C for f in C]
    assert sorted(elts_of_gr_C) == sorted(list(set(elts_of_gr_C)))
    for f in elts_of_gr_C:
        assert f in range(F)
    for f in range(F):
        assert f in st_f or f in elts_of_gr_C
    
    # Les tournees sont bien numerotees, visitent des elements d'un meme
    # groupe, et le nb de marchandises chargees chez chaque fournisseur
    # visite est specifie. Un element est visite au plus une fois par tournee,
    # et n'est pas visite si le camion ne charge pas de marchandises chez lui.
    # La capacite des camions est bien respectee.
    assert nb_P == len(tr_P)
    assert list(range(nb_P)) == sorted([i for i in ids_P])
    for P in tr_P:
        c = P[0]
        s = P[1]
        nb_f = P[2]
        list_f = P[3]
        list_q = P[4]
        assert s in range(H)
        assert nb_f == len(list_f)
        assert nb_f == len(set(list_f))
        assert nb_f == len(list_q)
        for f in list_f:
            assert f in range(F)
            assert f in gr_C[c]
            assert march(f, s) != 0
        assert sum(list_q) <= Q
    
    # On recupere exactement le nombre de marchandises demande chaque semaine
    # aupres de chaque fournisseur.
    for s in range(H):
        for f in range(H):
            march_tot_fs = 0
            for P in tr_P:
                s_P = P[1]
                list_f = P[3]
                list_q = P[4]
                if s_P == s and f in list_f:
                    i = list_f.index(f)
                    march_tot_fs += list_q[i]
            if f in st_f:
                assert march_tot_fs == 0
            else:
                assert march_tot_fs == march(f, s)

    return cost_solution(Q, F, H, L_f, a, st_f, gr_C, tr_P)

#print(evaluate_solution("Instance-plus-propre.csv", "sol_no_st_2.txt"))














