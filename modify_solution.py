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
from evaluate_solution import read_solution, evaluate_solution, cost_solution, verify_solution
from make_solution import (Q, F, H, L_f, a,
                           march, cost_st, cost_tr, cost_ens_tr, residual, best_tournees_residuals,
                           best_tournees_residuals_proportional,
                           compute_solution, print_solution, should_st,
                           coords_rel, angle_rel, dist_sq, barycenter)

from datetime import datetime

list_st_sure = [f for f in range(F) if should_st(f)]

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
    if ids_gr_C_non_sing == []:
        return
    c1 = rd.choice(ids_gr_C_non_sing)
    if [c for c in range(len(gr_C)) if c != c1] == []:
        return
    c2 = rd.choice([c for c in range(len(gr_C)) if c != c1])

    id1 = rd.randrange(len(gr_C[c1]))
    id2 = rd.randrange(len(gr_C[c2]))
    
    gr_C[c1][id1], gr_C[c2][id2] = gr_C[c2][id2], gr_C[c1][id1]
    
    remove_tr_of_groups([c1, c2], tr_P)
    add_tr_of_groups_best_method([c1, c2], gr_C, tr_P)
    
def unisolate_an_element(gr_C, tr_P):
    ids_gr_C_sing = [c for c in range(len(gr_C)) if len(gr_C[c]) == 1]
    if ids_gr_C_sing == []:
        return
    ids_gr_C_not_full = [c for c in range(len(gr_C)) if len(gr_C[c]) < 4]
    if len(ids_gr_C_not_full) < 2:
        return
    c1 = rd.choice(ids_gr_C_sing)
    f1 = gr_C[c1][0]
    gr_C.remove([f1])
    
    remove_tr_of_groups([c1], tr_P)
    shift_indices(c1, tr_P)
    
    ids_gr_C_not_full = [c for c in range(len(gr_C)) if len(gr_C[c]) < 4]
    c2 = rd.choice(ids_gr_C_not_full)
    gr_C[c2].append(f1)
    
    remove_tr_of_groups([c2], tr_P)
    
    add_tr_of_groups_best_method([c2], gr_C, tr_P)

def change_the_group_of_an_element(gr_C, tr_P):
    ids_gr_C_non_sing = [c for c in range(len(gr_C)) if len(gr_C[c]) > 1]
    if ids_gr_C_non_sing == []:
        return
    c1 = rd.choice(ids_gr_C_non_sing)
    if [c for c in range(len(gr_C)) if c != c1 and len(gr_C[c]) < 4] == []:
        return
    c2 = rd.choice([c for c in range(len(gr_C)) if c != c1 and len(gr_C[c]) < 4])
    
    id1 = rd.randrange(len(gr_C[c1]))
    f = gr_C[c1][id1]
    
    gr_C[c1].remove(f)
    gr_C[c2].append(f)
    
    remove_tr_of_groups([c1, c2], tr_P)

    add_tr_of_groups_best_method([c1, c2], gr_C, tr_P)

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

    add_tr_of_groups_best_method([c0, len(gr_C) - 1], gr_C, tr_P)

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
    add_tr_of_groups_best_method([c0], gr_C, tr_P)

def unst_element(st_f, gr_C, tr_P):
    might_not_st = [f for f in st_f if not f in list_st_sure]
    if might_not_st == []:
        return
    f0 = rd.choice(might_not_st)
    st_f.remove(f0)
    gr_C.append([f0])
    add_tr_of_groups_best_method([len(gr_C) - 1], gr_C, tr_P)

def unst_element_and_add_to_a_group(st_f, gr_C, tr_P):
    might_not_st = [f for f in st_f if not f in list_st_sure]
    non_max_filled_groups = [c for c in range(len(gr_C)) if len(gr_C[c]) < 4]
    if might_not_st == [] or non_max_filled_groups == []:
        return
    f0 = rd.choice(might_not_st)
    st_f.remove(f0)
    c0 = rd.choice(non_max_filled_groups)
    gr_C[c0].append(f0)
    remove_tr_of_groups([c0], tr_P)
    add_tr_of_groups_best_method([c0], gr_C, tr_P)

def three_permute(st_f, gr_C, tr_P):
    ids_gr_C_non_sing = [c for c in range(len(gr_C)) if len(gr_C[c]) > 1]
    if len(ids_gr_C_non_sing) < 3:
        return
    c1, c2, c3 = rd.sample(ids_gr_C_non_sing, 3)
    id1 = rd.randrange(len(gr_C[c1]))
    id2 = rd.randrange(len(gr_C[c2]))
    id3 = rd.randrange(len(gr_C[c3]))
    f1 = gr_C[c1][id1]
    f2 = gr_C[c2][id2]
    f3 = gr_C[c3][id3]
    
    gr_C[c1].remove(f1)
    gr_C[c2].remove(f2)
    gr_C[c3].remove(f3)
    
    gr_C[c1].append(f2)
    gr_C[c2].append(f3)
    gr_C[c3].append(f1)
    
    remove_tr_of_groups([c1, c2, c3], tr_P)
    add_tr_of_groups_best_method([c1, c2, c3], gr_C, tr_P)





    


# ATTENTION : C1 et C2 doivent tous deux etre de cardinal 4
def find_best_permut_in_groups(c1, c2, gr_C, tr_P):
    assert c1 != c2 and len(gr_C[c1]) == 4 and len(gr_C[c2]) == 4
    elts = gr_C[c1] + gr_C[c2]
    possible_C1s = list(it.combinations(elts, 4))
    list_of_new_C1_tr_P = []
    for C1 in possible_C1s:
        list_of_new_C1_tr_P.append([C1,[]])
        C2 = [f for f in elts if not f in C1]
        add_tr_of_groups_best_method([0, 1], [C1, C2], list_of_new_C1_tr_P[-1][1])
    all_costs = [(C1, cost_ens_tr([P[-2] for P in new_tr_P])) \
                 for C1, new_tr_P in list_of_new_C1_tr_P]
    C1 = list(min(all_costs, key = op.itemgetter(1))[0])
    C2 = [f for f in elts if not f in C1]
    gr_C[c1] = C1
    gr_C[c2] = C2
    remove_tr_of_groups([c1, c2], tr_P)
    add_tr_of_groups_best_method([c1, c2], gr_C, tr_P)
    print("done")



def new_group_from_st(st_f, gr_C, tr_P, use_angle):
    if len(st_f) < 4:
        return
    f1 = rd.choice(st_f)
    st_f.remove(f1)
    if use_angle:
        angles_to_f = [(f, angle_rel(coords_rel(f1), coords_rel(f))) for f in st_f]
        angles_to_f = sorted(angles_to_f, key = op.itemgetter(1))
        f2, f3, f4 = [f for f, angle in angles_to_f[:3]]
    else:
        dist_to_f = [(f, a[f1][f]) for f in st_f]
        dist_to_f = sorted(dist_to_f, key = op.itemgetter(1))
        f2, f3, f4 = [f for f, dist in dist_to_f[:3]]
    st_f.remove(f2)
    st_f.remove(f3)
    st_f.remove(f4)
    C = [f1, f2, f3, f4]
    gr_C.append(C)
    add_tr_of_groups_best_method([-1], gr_C, tr_P)



def complete_group(c, st_f, gr_C, tr_P):
#    bary = barycenter(gr_C[c])
#    dist_to_C = [(f, dist_sq(bary, coords_rel(f))) for f in st_f]
#    f = min(dist_to_C, key = op.itemgetter(1))[0]
    f = rd.choice(st_f)
    st_f.remove(f)
    gr_C[c].append(f)
    remove_tr_of_groups([c], tr_P)
    add_tr_of_groups_best_method([c], gr_C, tr_P)


def unst_element_intelligent(f, st_f_0, gr_C_0, tr_P_0):
    st_f, gr_C, tr_P = copy_of_solution(st_f_0, gr_C_0, tr_P_0)
    
    st_f.remove(f)
    dist_to_f = [(c, dist_sq(barycenter(gr_C[c]), coords_rel(f))) for c in range(len(gr_C))]
    c = min(dist_to_f, key = op.itemgetter(1))[0]
    if len(gr_C[c]) < 4:
        gr_C[c].append(f)
        remove_tr_of_groups([c], tr_P)
        add_tr_of_groups_best_method([c], gr_C, tr_P)
        return
    bary_C = barycenter(gr_C[c])
    dist_to_C = [(f, dist_sq(bary_C, coords_rel(f))) for f in st_f]
    f1, f2, f3 = [f_v for f_v, dist_v in sorted(dist_to_C, key = op.itemgetter(1))[:3]]
    gr_C.append([f, f1, f2, f3])
    add_tr_of_groups_best_method([-1], gr_C, tr_P)
    find_best_permut_in_groups(c, -1, gr_C, tr_P)

    return st_f, gr_C, tr_P




def alter_solution_new(st_f_0, gr_C_0, tr_P_0, c1, c2):
    st_f, gr_C, tr_P = copy_of_solution(st_f_0, gr_C_0, tr_P_0)
    find_best_permut_in_groups(c1, c2, gr_C, tr_P)
    return st_f, gr_C, tr_P


def alter_solution(st_f_0, gr_C_0, tr_P_0):
    st_f, gr_C, tr_P = copy_of_solution(st_f_0, gr_C_0, tr_P_0)

    case = rd.choice([0, 2, 6])
    
    
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

    # de-sous-traite un element si possible
    elif case == 5:
        unst_element(st_f, gr_C, tr_P)
    
    # de-sous-traite un element et l'ajoute a un groupe deja existant (si possible)
    elif case == 6:
        unst_element_and_add_to_a_group(st_f, gr_C, tr_P)

    # permute trois elements de trois groupes differents (si possible)
    elif case == 7:
        three_permute(st_f, gr_C, tr_P)

    # cree un nouveau groupe "intelligent" avec 4 elements sous-traites (si possible)
    elif case == 8:
        new_group_from_st(st_f, gr_C, tr_P, True)

    # ajoute un element sous-traite a un groupe non rempli au max
    elif case == 9:
        ids_gr_C_not_filled = [c for c in range(len(gr_C)) if len(gr_C[c]) < 4]
        if ids_gr_C_not_filled == []:
            return st_f, gr_C, tr_P
        c = rd.choice(ids_gr_C_not_filled)
        complete_group(c, st_f, gr_C, tr_P)

    return st_f, gr_C, tr_P


    




st_f_0, gr_C_0, tr_P_0 = read_solution("solution.txt")
#st_f_0, gr_C_0, tr_P_0 = read_solution("solution_super.txt")
#st_f_0, gr_C_0, tr_P_0 = compute_solution(0)
verify_solution(Q, F, H, L_f, a, st_f_0, gr_C_0, tr_P_0)
cost = cost_solution(Q, F, H, L_f, a, st_f_0, gr_C_0, tr_P_0)
print(cost)

st_f_1, gr_C_1, tr_P_1 = alter_solution(st_f_0, gr_C_0, tr_P_0)
verify_solution(Q, F, H, L_f, a, st_f_1, gr_C_1, tr_P_1)


#st_f_initial = st_f_0.copy()
#for f in st_f_initial:
#    st_f_1, gr_C_1, tr_P_1 = unst_element_intelligent(f, st_f_0, gr_C_0, tr_P_0)
#    verify_solution(Q, F, H, L_f, a, st_f_1, gr_C_1, tr_P_1)
#    cost_1 = cost_solution(Q, F, H, L_f, a, st_f_1, gr_C_1, tr_P_1)
#    if cost_1 < cost:
#        st_f_0 = st_f_1.copy()
#        gr_C_0 = [C.copy() for C in gr_C_1]
#        tr_P_0 = [[P[0], P[1], P[2], P[3].copy(), P[4].copy()] for P in tr_P_1]
#        cost = cost_1
#        print(cost)
    

#now = datetime.now()
#current_time = now.strftime("%H:%M:%S")
#print("Start at =", current_time)


#nb_iter = 20
#theta = 0.0025
#for i in range(nb_iter):
#    print(20 * " ", i)
#    for c1 in range(len(gr_C_1)):
#        C1 = gr_C_1[c1]
#        bary_1 = barycenter(C1)
#        for c2 in range(c1):
#            C2 = gr_C_1[c2]
#            bary_2 = barycenter(C2)
#            if len(gr_C_1[c1]) == 4 and len(gr_C_1[c2]) == 4 and abs(angle_rel(bary_1, bary_2)) < theta:
#                st_f_1, gr_C_1, tr_P_1 = alter_solution_new(st_f_0, gr_C_0, tr_P_0, c1, c2)
#                verify_solution(Q, F, H, L_f, a, st_f_1, gr_C_1, tr_P_1)
#                cost_1 = cost_solution(Q, F, H, L_f, a, st_f_1, gr_C_1, tr_P_1)
#                if cost_1 < cost:
#                    st_f_0 = st_f_1.copy()
#                    gr_C_0 = [C.copy() for C in gr_C_1]
#                    tr_P_0 = [[P[0], P[1], P[2], P[3].copy(), P[4].copy()] for P in tr_P_1]
#                    cost = cost_1
#                    print(cost)
#    if theta < 0.1:
#        theta *= 2

#now = datetime.now()
#current_time = now.strftime("%H:%M:%S")
#print("Done at =", current_time)



nb_iter = 10000
for i in range(nb_iter):
    st_f_1, gr_C_1, tr_P_1 = alter_solution(st_f_0, gr_C_0, tr_P_0)
    verify_solution(Q, F, H, L_f, a, st_f_1, gr_C_1, tr_P_1)
    cost_1 = cost_solution(Q, F, H, L_f, a, st_f_1, gr_C_1, tr_P_1)
    if cost_1 < cost:
        st_f_0 = st_f_1.copy()
        gr_C_0 = [C.copy() for C in gr_C_1]
        tr_P_0 = [[P[0], P[1], P[2], P[3].copy(), P[4].copy()] for P in tr_P_1]
        cost = cost_1
        print(cost)
#        print_solution(st_f_0, gr_C_0, tr_P_0, "solution.txt")
    if i%100 == 0:
        print(20* " ", i/nb_iter*100)
    








# RECUIT SIMULE

#alpha = 0.5
#T = 10**7

#alpha = 0.1
#T = 10**7
#
#st_f_0, gr_C_0, tr_P_0 = read_solution("solution_best.txt")
##st_f_0, gr_C_0, tr_P_0 = compute_solution(0)
#verify_solution(Q, F, H, L_f, a, st_f_0, gr_C_0, tr_P_0)
#cost_0 = cost_solution(Q, F, H, L_f, a, st_f_0, gr_C_0, tr_P_0)
#cost_1 = cost_0
#print(cost_0)
#
#st_f_1, gr_C_1, tr_P_1 = copy_of_solution(st_f_0, gr_C_0, tr_P_0)
#
#nb_iter = 1000
#for i in range(nb_iter):
#    for j in range(50):
#        if cost_1 < cost_0:
#            st_f_0, gr_C_0, tr_P_0 = copy_of_solution(st_f_1, gr_C_1, tr_P_1)
#            cost_0 = cost_1
##        print(cost_1)
#        st_f_2, gr_C_2, tr_P_2 = alter_solution(st_f_1, gr_C_1, tr_P_1)
#        cost_2 = cost_solution(Q, F, H, L_f, a, st_f_2, gr_C_2, tr_P_2)
#        if cost_2 < cost_1:
#            st_f_1, gr_C_1, tr_P_1 = copy_of_solution(st_f_2, gr_C_2, tr_P_2)
#            cost_1 = cost_2
#            print(cost_1)
#        elif rd.uniform(0,1) < m.exp(-(cost_2 - cost_1)/T):
#            st_f_1, gr_C_1, tr_P_1 = copy_of_solution(st_f_2, gr_C_2, tr_P_2)
#            cost_1 = cost_2
##            print(" " * 20, True)
#    print(" " * 20, i)
#    T = alpha * T

# x^b = sol_0
# x = sol_1
# x' = sol_2









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
