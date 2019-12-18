#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 16:05:50 2019

@author: Adrien CANCES
"""

import math as m
import itertools as it
import operator as op
import random as rd
from get_data import get_data
from evaluate_solution import evaluate_solution, cost_solution, verify_solution

#data_file_name = "Instance-plus-propre.csv"
data_file_name = "usine.csv"


Q, F, H, L_f, a = get_data(data_file_name)


def partitions(collection):
    if len(collection) == 1:
        yield [ collection ]
        return
    first = collection[0]
    for smaller in partitions(collection[1:]):
        # insert `first` in each of the subpartition's subsets
        for n, subset in enumerate(smaller):
            for i in range(len(subset) + 1):
                yield smaller[:n] + [subset[:i] + [ first ] + subset[i:]]  + smaller[n+1:]
        # put `first` in its own subset 
        yield [ [ first ] ] + smaller


def random_permutation(n):
    perm = []
    while len(perm) != n:
        i = rd.randint(0, n - 1)
        if not i in perm:
            perm.append(i)
    return perm


def coords(f):
    return L_f[f][2][0],L_f[f][2][1]


def march(f, s):
    return L_f[f][1][s]


def cost_st(f):
    return L_f[f][0]


def cost_st_gr(C):
    if C == []:
        return 0
    return sum([L_f[f][0] for f in C])


def generate_sets(C):
    return list(it.permutations(C))


def should_st(f):
    appr_min_cost = sum([(a[F][f] + a[f][F + 1]) * m.ceil(march(f, s)/Q) for s in range(H)])
#    appr_min_cost = sum([(a[F][f] + a[f][F + 1]) * m.floor(march(f, s)/Q) for s in range(H)])
#    if app_min_cost + 5000 >= cost_st(f):
    if appr_min_cost >= cost_st(f):
        return True
    return False


def dist(f1, f2):
    coords_1 = coords(f1)
    coords_2 = coords(f2)
    return (coords_1[0] - coords_2[0])**2 + (coords_1[1] - coords_2[1])**2


def rapport(f, s):
    return march(f, s)/Q


def optimal_route_bis(C):
    possible_routes = [
            (sum([a[perm_C[i]][perm_C[i + 1]] for i in range(len(C) - 1)]) + a[perm_C[-1]][F + 1],
             perm_C)
            for perm_C in it.permutations(C)]
    best_perm_C = min(possible_routes, key=op.itemgetter(0))[1]
    return best_perm_C


def optimal_route(C, s):
    f_visit = [f for f in C if march(f, s)%Q != 0]
    possible_routes = \
    [(sum([ a[perm[i]][perm[i + 1]] for i in range(len(perm) - 1) ]) + a[perm[-1]][F + 1],
      perm)
    for perm in it.permutations(f_visit)
    ]
    best_perm = min(possible_routes, key=op.itemgetter(0))[1]
    return best_perm


def residual(f, s):
    return march(f, s)%Q


def cost_tr(P):
    rt = [F] + list(P) + [F + 1]
    cost = sum([a[rt[i]][rt[i + 1]] for i in range(len(rt) - 1)])
    return cost


def cost_ens_tr(tr_P):
    return sum([cost_tr(P) for P in tr_P])


def tr_P_admissible(tr_P, s):
    admissible = True
    for route in tr_P:
        admissible = admissible and sum([residual(f, s) for f in route]) <= Q
    return admissible


def best_tournees_residuals(C, s):
    C_eff = [f for f in C if residual(f, s) != 0]
    if C_eff == []:
        return []
    costs = [(tr_P, cost_ens_tr(tr_P)) for tr_P in partitions(C_eff) if
             tr_P_admissible(tr_P, s)]
    best_tr_P = min(costs, key = op.itemgetter(1))[0]
    return best_tr_P


def get_interesting_triplets():
    return [((i, j, k), (a[i][j] + a[j][k])/a[i][k]) for i in range(F+1) for j in range(F+1) \
            for k in range(F+1)
            if a[i][j] + a[j][k] < a[i][k]]


def close_neighbors(dist):
    L = []
    for i in range(326):
        for j in range(326):
            if i != j and a[i][j] < dist :
                L.append((i,j))
    return L








    










def immediate_neighbors():
    return [(f1, f2) for f1 in range(F) for f2 in range(F)
            if f1 != f2 and a[f1][f2] == 0]



def compute_solution(s1, threshold = -1):
    if threshold == -1:
        dist_max = max([a[i][j] for i in range(F+1) for j in range(F+1)])
        threshold = dist_max + 1
    
    C_tournees_pleines = 0    
    
    # Calcul des fournisseurs sous-traites
    st_f = [f for f in range(F) if should_st(f)]
    
    # Calcul des groupes selon la semaine s1
    gr_C = []
    f_traites = [False for f in range(F)]
    for f in st_f:
        f_traites[f] = True
    
#    for f in random_permutation(F):
    for f in range(F):
        if not f_traites[f]:
            f_traites[f] = True
            if residual(f, s1) == 0:
                gr_C.append([f])
            else:
                C = [f]
                residual_sum = residual(f, s1)
                dist_to_f = [(f_v, a[f][f_v]) \
                             for f_v in range(F) if not f_traites[f_v]]
                dist_to_f = sorted(dist_to_f, key = op.itemgetter(1))
                for f_v, dist in dist_to_f:
                    if (not f_traites[f_v] and 0 <= dist < threshold
                        and residual(f_v, s1) > 0
                        and residual_sum + residual(f_v, s1) <= Q):
                        C.append(f_v)
                        f_traites[f_v] = True
                        residual_sum += residual(f_v, s1)
                    if len(C) == 4:
                        break
                gr_C.append(C)
    
    # Calcul des tournees
    tr_P = []
    nb_P_tot = 0
    for c in range(len(gr_C)):
        C = gr_C[c]
        for s in range(H):
            if len(C) == 1:
                f = C[0]
                nb_P_fs = int(march(f, s)/Q) + 1
                for i in range(nb_P_fs - 1):
                    C_tournees_pleines += cost_tr([f])
                    tr_P.append([c, s, 1, [f], [Q]])
                if march(f, s)%Q != 0:
                    tr_P.append([c, s, 1, [f], [march(f, s)%Q]])
                    nb_P_tot += 1
                nb_P_tot += nb_P_fs - 1
            elif sum([march(f, s) for f in C]) != 0:
                for f in C:
                    for i in range(march(f, s)//Q):
                        C_tournees_pleines += cost_tr([f])
                        tr_P.append([c, s, 1, [f], [Q]])
                    nb_P_tot += march(f, s)//Q
                if sum([residual(f, s) for f in C]) != 0:
                    ens_tournees = best_tournees_residuals(C, s)
                    for route in ens_tournees:
                        tr_P.append([c, s, len(route), [f for f in route],
                                     [residual(f, s) for f in route]])
                        nb_P_tot += 1
                        if sum([residual(f, s) for f in route]) == Q:
                            C_tournees_pleines += cost_tr(route)
    

#    print("Nb de fournisseurs sous-traites :", len(st_f))
#    print("Nb de groupes :", len(gr_C))
#    print("Nb de groupes non singletons :", len([C for C in gr_C if len(C) > 1]))
#    print("Cout des tournees pleines :", C_tournees_pleines)

    gr_C_non_sing = []
    for C in gr_C:
        if len(C) > 1:
            gr_C_non_sing.append(C)
#    print("Cardinal moyen des groupes non singleton:",
#          sum([len(C) for C in gr_C_non_sing]) / len(gr_C_non_sing))
    
    return st_f, gr_C, tr_P
    

def print_solution(st_f, gr_C, tr_P, sol_file_name):
    file = open(sol_file_name, "w")
    
    nb_P_tot = len(tr_P)

    # Ecriture des trois premieres lignes
    file.write("x " + str(len(st_f)) + " f " + " ".join([str(f) for f in st_f]) + "\n")
    file.write("y " + str(nb_P_tot) + "\n")
    file.write("z " + str(len(gr_C)) + "\n")

    # Ecriture des groupes
    for c in range(len(gr_C)):
        C = gr_C[c]
        file.write("C " + str(c) + " n " + str(len(C)) + " f " + " ".join([str(f) for f in C]) + "\n")

    # Ecriture des tournees
    for id_P, P in enumerate(tr_P):
        c = P[0]
        s = P[1]
        nb_f = P[2]
        list_f = P[3]
        list_q = P[4]
        file.write("P " + str(id_P)
                        + " g " + str(c) + " s " + str(s)
                        + " n " + str(nb_f) + " "
                        + " ".join(["f " + str(list_f[i]) + " "
                        + str(list_q[i]) for i in range(nb_f)]) + "\n")

    file.close()







