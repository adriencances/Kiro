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


# TEMPORAIRE
def add_tr_of_groups(ids_gr_C, gr_C, tr_P):
    for c in ids_gr_C:
        C = gr_C[c]
        for s in range(H):
            if len(C) == 1:
                f = C[0]
                nb_P_fs = int(march(f, s)/Q) + 1
                for i in range(nb_P_fs - 1):
                    tr_P.append([c, s, 1, [f], [Q]])
                if march(f, s)%Q != 0:
                    tr_P.append([c, s, 1, [f], [march(f, s)%Q]])
            elif sum([march(f, s) for f in C]) != 0:
                for f in C:
                    for i in range(march(f, s)//Q):
                        tr_P.append([c, s, 1, [f], [Q]])
                if sum([residual(f, s) for f in C]) != 0:
                    ens_tournees = best_tournees_residuals(C, s)
                    for route in ens_tournees:
                        tr_P.append([c, s, len(route), [f for f in route],
                                     [residual(f, s) for f in route]])

# TEMPORAIRE
def add_tr_of_groups_proportional(ids_gr_C, gr_C, tr_P):
    for c in ids_gr_C:
        C = gr_C[c]
        for s in range(H):
            if len(C) == 1:
                f = C[0]
                nb_P_fs = int(march(f, s)/Q) + 1
                for i in range(nb_P_fs - 1):
                    tr_P.append([c, s, 1, [f], [Q]])
                if march(f, s)%Q != 0:
                    tr_P.append([c, s, 1, [f], [march(f, s)%Q]])
            elif sum([march(f, s) for f in C]) != 0:
                for f in C:
                    for i in range(march(f, s)//Q):
                        tr_P.append([c, s, 1, [f], [Q]])
                if sum([residual(f, s) for f in C]) != 0:
                    set_of_f_lists_q_lists = best_tournees_residuals_proportional(C, s)
                    for f_list, q_list in set_of_f_lists_q_lists:
                        tr_P.append([c, s, len(f_list), f_list, q_list])
    
# TEMPORAIRE
def add_tr_of_groups_best_method(ids_gr_C, gr_C, tr_P):
    for c in ids_gr_C:
        C = gr_C[c]
        for s in range(H):
            if len(C) == 1:
                f = C[0]
                nb_P_fs = int(march(f, s)/Q) + 1
                for i in range(nb_P_fs - 1):
                    tr_P.append([c, s, 1, [f], [Q]])
                if march(f, s)%Q != 0:
                    tr_P.append([c, s, 1, [f], [march(f, s)%Q]])
            elif sum([march(f, s) for f in C]) != 0:
                for f in C:
                    for i in range(march(f, s)//Q):
                        tr_P.append([c, s, 1, [f], [Q]])
            
                # method 1
                tr_C_1 = []
                set_of_f_lists_q_lists = best_tournees_residuals_proportional(C, s)
                for f_list, q_list in set_of_f_lists_q_lists:
                    tr_C_1.append([c, s, len(f_list), f_list, q_list])
                    
                # method 2
                tr_C_2 = []
                if sum([residual(f, s) for f in C]) != 0:
                    ens_tournees = best_tournees_residuals(C, s)
                    for route in ens_tournees:
                        tr_C_2.append([c, s, len(route), [f for f in route],
                                     [residual(f, s) for f in route]])
                
                cost_1 = cost_ens_tr([P[-2] for P in tr_C_1])
                cost_2 = cost_ens_tr([P[-2] for P in tr_C_2])
                if cost_2 < cost_1:
    #                tr_P = tr_P + tr_C_2
                    for P in tr_C_2:
                        tr_P.append(P)
                else:
    #                tr_P = tr_P + tr_C_1
                    for P in tr_C_1:
                        tr_P.append(P)









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
#    appr_min_cost = sum([(a[F][f] + a[f][F + 1]) * m.ceil(march(f, s)/Q) for s in range(H)])
#    appr_min_cost = sum([(a[F][f] + a[f][F + 1]) * m.floor(march(f, s)/Q) for s in range(H)])
    appr_min_cost = sum([(a[F][f] + a[f][F + 1]) * (m.floor(march(f, s)/Q) + 0.1) for s in range(H)])
    if appr_min_cost >= cost_st(f):
        return True
    return False


def dist(f1, f2):
    coords_1 = coords(f1)
    coords_2 = coords(f2)
    return (coords_1[0] - coords_2[0])**2 + (coords_1[1] - coords_2[1])**2

def dist_sq(A, B):
    x1, y1 = A
    x2, y2 = A
    return (x1 - x2)**2 + (y1 - y2)**2

def rapport(f, s):
    return march(f, s)/Q


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


def last_residual(f, s, d_tot):
    return residual(f, s) - d_tot//Q * m.floor(residual(f, s)/d_tot*Q)


def best_tournees_residuals_proportional(C, s):
    C_eff = [f for f in C if residual(f, s) != 0]
    if C_eff == []:
        return []
    d_tot = sum([residual(f, s) for f in C_eff])
    
    set_of_f_lists_q_lists = []
    
    orders_costs = [(list(order), cost_tr(order)) for order in it.permutations(C_eff)]
    best_order = min(orders_costs, key = op.itemgetter(1))[0]
    
    for i in range(d_tot//Q):
        set_of_f_lists_q_lists.append([ best_order, 
                                       [m.floor(residual(f, s)/d_tot*Q) for f in best_order] ])
    
    last_residuals = [residual(f, s) - d_tot//Q * m.floor(residual(f, s)/d_tot*Q) for f in C_eff]
    
    C_eff_2 = [C_eff[i] for i in range(len(C_eff)) if last_residuals[i] > 0]
    
    if C_eff_2 != []:
        if sum(last_residuals) > Q:
            for i in range(len(C_eff_2)):
                set_of_f_lists_q_lists.append([ [C_eff[i]], [last_residuals[i]] ])
        else:
            orders_costs_2 = [(list(order), cost_tr(order)) for order in it.permutations(C_eff_2)]
            best_order_2 = min(orders_costs_2, key = op.itemgetter(1))[0]
            
            set_of_f_lists_q_lists.append([ best_order_2,
                                           [last_residual(f, s, d_tot) for f in best_order_2] ])

    return set_of_f_lists_q_lists


def compare_methods(gr_C):
    for s in range(H):
        for c in range(len(gr_C)):
            C = gr_C[c]
            tr_P_1 = []
            tr_P_2 = []
            ens_tournees = best_tournees_residuals(C, s)
            for route in ens_tournees:
                tr_P_1.append([c, s, len(route), [f for f in route],
                             [residual(f, s) for f in route]])
            set_of_f_lists_q_lists = best_tournees_residuals_proportional(C, s)
            for f_list, q_list in set_of_f_lists_q_lists:
                tr_P_2.append([c, s, len(f_list), f_list, q_list])
            cost_1 = cost_ens_tr([P[-2] for P in tr_P_1])
            cost_2 = cost_ens_tr([P[-2] for P in tr_P_2])
            if cost_2 < cost_1:
                print(c, s)
                print(cost_1)
                print(cost_2)
















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








# Coordonnees du fournisseur f en prenant le depot comme origine
def coords_rel(f):
    x, y = coords(f)
    x0, y0 = coords(F)
    return (x - x0, y - y0)

def angle_rel(A, B):
    x1, y1 = A
    x2, y2 = B
    scalar_product = x1*x2 + y1*y2
    norm_1 = (x1**2 + y1**2)**(0.5)
    norm_2 = (x2**2 + y2**2)**(0.5)
    if norm_1 == 0 or norm_2 == 0:
        return 0
    ratio = min(abs(scalar_product/(norm_1*norm_2)), 1)
    return m.acos(ratio)


def barycenter(C):
    x_bary = sum([coords(f)[0] for f in C])/len(C)
    y_bary = sum([coords(f)[1] for f in C])/len(C)
    coords_bary = (x_bary, y_bary)
    return coords_bary




def immediate_neighbors():
    return [(f1, f2) for f1 in range(F) for f2 in range(F)
            if f1 != f2 and a[f1][f2] == 0]



def compute_solution(s1):
    
    # Calcul des fournisseurs sous-traites
    st_f = [f for f in range(F) if should_st(f)]
    
    # Calcul des groupes selon la semaine s1
    gr_C = []
    f_traites = [False for f in range(F)]
    for f in st_f:
        f_traites[f] = True

        
    new_method = False
    new_method_tr = False
#    if new_method:
#        for f in range(F):
#            if not f_traites[f]:
#                f_traites[f] = True
#                C = [f]
#                
#                angles = [(f_v, angle_val(f, f_v)) for f_v in range(F) if not f_traites[f_v]]
#                angles = sorted(angles, key = op.itemgetter(1))
#
#                for f_v, angle in angles[:1]:
#                    if (not f_traites[f_v]):
#                        C.append(f_v)
#                        f_traites[f_v] = True
#                gr_C.append(C)
    if new_method:
        f = 0
        nb_groups = m.ceil((F - len(st_f))/4)
        gr_C = [[] for c in range(nb_groups)]
        
        nb_traites_non_st = 0
        c = 0
        for f in range(F):
            if not f_traites[f]:
                gr_C[c].append(f)
                f_traites[f] = True
                nb_traites_non_st += 1
                dist_to_f = [(f_v, a[f][f_v]) \
                                 for f_v in range(F) if not f_traites[f_v]]
                dist_to_f = sorted(dist_to_f, key = op.itemgetter(1))
                f_v, dist = dist_to_f[0]
                gr_C[c].append(f_v)
                f_traites[f_v] = True
                nb_traites_non_st += 1
                c += 1
                if c == nb_groups:
                    break
        
        print(nb_traites_non_st, nb_groups)
        
        for i in range(3):
            for c in range(nb_groups):
                C = gr_C[c]
                if len(C) == 4:
                    continue
                coords_bary = barycenter(C)
                dist_to_C = [(f_v, dist_sq(coords(f_v), coords_bary)) \
                                 for f_v in range(F) if not f_traites[f_v]]
                dist_to_C = sorted(dist_to_C, key = op.itemgetter(1))
                if dist_to_C != []:
                    f_v, dist = dist_to_C[0]
                    C.append(f_v)
                    f_traites[f_v] = True
                    nb_traites_non_st += 1
        print(nb_traites_non_st)

    else:
        for f in range(F):
            if not f_traites[f]:
                f_traites[f] = True
                C = [f]
                dist_to_f = [(f_v, a[f][f_v]) \
                             for f_v in range(F) if not f_traites[f_v]]
                dist_to_f = sorted(dist_to_f, key = op.itemgetter(1))
                for f_v, dist in dist_to_f:
                    if not f_traites[f_v]:
                        C.append(f_v)
                        f_traites[f_v] = True
                    if len(C) == 4:
                        break
                gr_C.append(C)
    
    # Calcul des tournees
    tr_P = []
    nb_P_tot = 0

#    for c in range(len(gr_C)):
#        C = gr_C[c]
#        for s in range(H):
#            set_of_f_lists_q_lists = best_tournees_residuals_proportional(C, s)
#            for f_list, q_list in set_of_f_lists_q_lists:
#                tr_P.append([c, s, len(f_list), f_list, q_list])
    
    if new_method_tr:
        add_tr_of_groups_best_method(list(range(len(gr_C))), gr_C, tr_P)
    else:
        for c in range(len(gr_C)):
            C = gr_C[c]
            for s in range(H):
                if len(C) == 1:
                    f = C[0]
                    nb_P_fs = int(march(f, s)/Q) + 1
                    for i in range(nb_P_fs - 1):
                        tr_P.append([c, s, 1, [f], [Q]])
                    if march(f, s)%Q != 0:
                        tr_P.append([c, s, 1, [f], [march(f, s)%Q]])
                        nb_P_tot += 1
                    nb_P_tot += nb_P_fs - 1
                elif sum([march(f, s) for f in C]) != 0:
                    for f in C:
                        for i in range(march(f, s)//Q):
                            tr_P.append([c, s, 1, [f], [Q]])
                        nb_P_tot += march(f, s)//Q
                    if sum([residual(f, s) for f in C]) != 0:
                        ens_tournees = best_tournees_residuals(C, s)
                        for route in ens_tournees:
                            tr_P.append([c, s, len(route), [f for f in route],
                                         [residual(f, s) for f in route]])
                            nb_P_tot += 1
    

#    print("Nb de fournisseurs sous-traites :", len(st_f))
#    print("Nb de groupes :", len(gr_C))
#    print("Nb de groupes non singletons :", len([C for C in gr_C if len(C) > 1]))
#    print("Cout des tournees pleines :", C_tournees_pleines)
    
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







