#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 18:39:02 2019

@author: Adrien CANCES
"""

import math as m
import itertools as it
import operator as op
import random as rd
from get_data import get_data
from evaluate_solution import evaluate_solution, cost_solution, verify_solution
from make_solution import (Q, F, H, L_f, a,
                           march, cost_st, cost_tr, cost_ens_tr, residual, best_tournees_residuals,
                           compute_solution, print_solution)


def copy_of_solution(st_f_0, gr_C_0, tr_P_0):
    st_f = st_f_0.copy()
    gr_C = [C.copy() for C in gr_C_0]
    tr_P = [[P[0], P[1], P[2], P[3].copy(), P[4].copy()] for P in tr_P_0]
    return st_f, gr_C, tr_P

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

def remove_tr_of_groups(ids_gr_C, tr_P):
    count = 0
    for i in range(len(tr_P)):
        if tr_P[i][0] in ids_gr_C:
            tr_P[i] = []
            count += 1
    for i in range(count):
        tr_P.remove([])

def shift_indices(c, tr_P):
    for i in range(len(tr_P)):
        if tr_P[i][0] > c:
            tr_P[i][0] -= 1


def swap_two_elements(gr_C, tr_P):
    ids_gr_C_non_sing = [c for c in range(len(gr_C)) if len(gr_C[c]) > 1]
    c1 = rd.choice(ids_gr_C_non_sing)
    c2 = rd.choice([c for c in range(len(gr_C)) if c != c1])

    id1 = rd.randrange(len(gr_C[c1]))
    id2 = rd.randrange(len(gr_C[c2]))
    
    gr_C[c1][id1], gr_C[c2][id2] = gr_C[c2][id2], gr_C[c1][id1]
    
    remove_tr_of_groups([c1, c2], tr_P)
    add_tr_of_groups([c1, c2], gr_C, tr_P)
    
def unisolate_an_element(gr_C, tr_P):
    ids_gr_C_sing = [c for c in range(len(gr_C)) if len(gr_C[c]) == 1]
    
    if ids_gr_C_sing == []:
        return
    
    c1 = rd.choice(ids_gr_C_sing)
    f1 = gr_C[c1][0]
    gr_C.remove([f1])
    
    remove_tr_of_groups([c1], tr_P)
    shift_indices(c1, tr_P)
    
    ids_gr_C_pot = [c for c in range(len(gr_C)) if len(gr_C[c]) < 4]
    c2 = rd.choice(ids_gr_C_pot)
    gr_C[c2].append(f1)
        
    remove_tr_of_groups([c2], tr_P)
    
    add_tr_of_groups([c2], gr_C, tr_P)

def change_the_group_of_an_element(gr_C, tr_P):
    ids_gr_C_non_sing = [c for c in range(len(gr_C)) if len(gr_C[c]) > 1]
    c1 = rd.choice(ids_gr_C_non_sing)
    c2 = rd.choice([c for c in range(len(gr_C)) if c != c1 and len(gr_C[c]) < 4])
    
    id1 = rd.randrange(len(gr_C[c1]))
    f = gr_C[c1][id1]
    
    gr_C[c1].remove(f)
    gr_C[c2].append(f)
    
    remove_tr_of_groups([c1, c2], tr_P)

    add_tr_of_groups([c1, c2], gr_C, tr_P)

def isolate_an_element(gr_C, tr_P):
    ids_gr_C_non_sing = [c for c in range(len(gr_C)) if len(gr_C[c]) > 1]

    if ids_gr_C_non_sing == []:
        return

    c0 = rd.choice(ids_gr_C_non_sing)
    id0 = rd.randrange(len(gr_C[c0]))
    
    f = gr_C[c0][id0]
    gr_C[c0].remove(f)
    gr_C.append([f])
        
    remove_tr_of_groups([c0], tr_P)

    add_tr_of_groups([c0, len(gr_C) - 1], gr_C, tr_P)

def st_non_isolated_element(st_f, gr_C, tr_P):
    ids_gr_C_non_sing = [c for c in range(len(gr_C)) if len(gr_C[c]) > 1]
    
    if ids_gr_C_non_sing == []:
        return
    
    c0 = rd.choice(ids_gr_C_non_sing)
    id0 = rd.randrange(len(gr_C[c0]))
    f0 = gr_C[c0][id0]
    
    gr_C[c0].remove(f0)
    st_f.append(f0)
    remove_tr_of_groups([c0], tr_P)
    add_tr_of_groups([c0], gr_C, tr_P)

def unst_element(st_f, gr_C, tr_P):
    if st_f == []:
        return
    f0 = rd.choice(st_f)
    st_f.remove(f0)
    gr_C.append([f0])
    add_tr_of_groups([len(gr_C) - 1], gr_C, tr_P)



def alter_solution(st_f_0, gr_C_0, tr_P_0, countor = 0):
    st_f, gr_C, tr_P = copy_of_solution(st_f_0, gr_C_0, tr_P_0)
    
    case = rd.randint(0, 5)
    
#    if countor < 100:
#        case = rd.randint(0, 1)
#    else:
#        case = rd.randint(0, 2)
    
    # swap deux elements
    if case == 0:
        swap_two_elements(gr_C, tr_P)
    
    # fusionne un element isole et un groupe non rempli
    elif case == 1:
        unisolate_an_element(gr_C, tr_P)
    
    # change un element de groupe
    elif case == 2:
        change_the_group_of_an_element(gr_C, tr_P)
    
    # isole un element si possible
    elif case == 3:
        isolate_an_element(gr_C, tr_P)
    
    # sous-traite un element si possible
    elif case == 4:
        st_non_isolated_element(st_f, gr_C, tr_P)

    # de-sous-traite un elememt si possible
    elif case == 5:
        unst_element(st_f, gr_C, tr_P)

    return st_f, gr_C, tr_P


                




st_f_0, gr_C_0, tr_P_0 = compute_solution(0)
verify_solution(Q, F, H, L_f, a, st_f_0, gr_C_0, tr_P_0)
cost = cost_solution(Q, F, H, L_f, a, st_f_0, gr_C_0, tr_P_0)
print(cost)

st_f_1, gr_C_1, tr_P_1 = alter_solution(st_f_0, gr_C_0, tr_P_0)
verify_solution(Q, F, H, L_f, a, st_f_1, gr_C_1, tr_P_1)

nb_iter = 10000
param = 2*10**6 # 10**7
for i in range(nb_iter):
    st_f_1, gr_C_1, tr_P_1 = alter_solution(st_f_0, gr_C_0, tr_P_0, i)
    verify_solution(Q, F, H, L_f, a, st_f_1, gr_C_1, tr_P_1)
    cost_1 = cost_solution(Q, F, H, L_f, a, st_f_1, gr_C_1, tr_P_1)
#    print(m.exp(-(cost_1 - cost)/param))
#    if cost_1 < cost or rd.uniform(0,1) < m.exp(-(cost_1 - cost)/param):
    if cost_1 < cost:
        st_f_0 = st_f_1.copy()
        gr_C_0 = [C.copy() for C in gr_C_1]
        tr_P_0 = [[P[0], P[1], P[2], P[3].copy(), P[4].copy()] for P in tr_P_1]
        cost = cost_1
        print(cost)
    
    if i == 100:
        print("Limite")




#print_solution(st_f_0, gr_C_0, tr_P_0, "solution.txt")
#print(evaluate_solution(data_file_name, "solution.txt"))






# IDEES



def estimate_lower_bound():
    S = 0
    
    # aller-retours a fournisseurs uniques
    for f in range(F):
        for s in range(H):
            S += (march(f, s)//Q) * (a[F][f] + a[f][F + 1])
    print(S)
    
    # tournees pour les restes
    for s in range(H):
        f_to_visit = [f for f in range(F) if residual(f, s) != 0]
        dist_leave = a[F][0]
        dist_return_min = min([a[f][F + 1] for f in f_to_visit])
        
        nb_f = len([f for f in range(F) if residual(f, s) != 0])
        
        dist_min_between_fs = min(a[f1][f2] for f1 in f_to_visit for f2 in f_to_visit \
                                  if f1 != f2)
        
        cost = nb_f//4 * (dist_leave + 3*dist_min_between_fs + dist_return_min)
        if nb_f%4 != 0:
            cost += (dist_leave + ((nb_f%4) - 1)*dist_min_between_fs + dist_return_min)
        
#        sum_residuals = sum([residual(f, s) for f in range(f)])
        print(dist_min_between_fs)
        S += cost

    return S

#print(estimate_lower_bound())


def immediate_neighbors(dist = 0):
    return [(f1, f2) for f1 in range(F) for f2 in range(F)
            if f1 != f2 and a[f1][f2] <= dist]


def three_sets_immediate_neighbors(dist = 0):
    return [(f1, f2, f3) for f1, f2, f3 in it.combinations(range(F), 3) if
            a[f1][f2] <= dist and a[f2][f3] <= dist and a[f1][f3] <= dist]

def four_sets_immediate_neighbors(dist = 0):
    return [(f1, f2, f3, f4) for f1, f2, f3, f4 in it.combinations(range(F), 4) if
            a[f1][f2] <= dist and a[f1][f3] <= dist and a[f1][f4] <= dist and
            a[f2][f3] <= dist and a[f2][f4] <= dist and a[f3][f4] <= dist]

def three_neighbors(dist):
    return [(f1, f2, f3) for f1, f2, f3 in it.combinations(range(F), 3) if
            a[f1][f2] + a[f2][f3] <= 2*dist or
            a[f1][f3] + a[f3][f2] <= 2*dist or
            a[f2][f1] + a[f1][f3] <= 2*dist]

#for dist in [1000, 2000, 3000, 4000, 5000]:
#    print(len(three_neighbors(dist)), len(three_sets_immediate_neighbors(dist)))
