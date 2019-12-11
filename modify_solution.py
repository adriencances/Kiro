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
                           march, residual, best_tournees_residuals,
                           compute_solution, print_solution)

def alter_groups(gr_C_0, tr_P_0, countor = 0):
    gr_C = [C.copy() for C in gr_C_0]
    tr_P = [[P[0], P[1], P[2], P[3].copy(), P[4].copy()] for P in tr_P_0]
    if countor < 100:
        case = rd.randint(0, 1)
    else:
        case = rd.randint(0, 2)
    
    # swap deux elements
    if case == 0:
        ids_gr_C_non_sing = [c for c in range(len(gr_C)) if len(gr_C[c]) > 1]
        c1 = rd.choice(ids_gr_C_non_sing)
        c2 = rd.choice([c for c in range(len(gr_C)) if c != c1])

        id1 = rd.randrange(len(gr_C[c1]))
        id2 = rd.randrange(len(gr_C[c2]))
        
        gr_C[c1][id1], gr_C[c2][id2] = gr_C[c2][id2], gr_C[c1][id1]
    
        count = 0
        for i in range(len(tr_P)):
            if tr_P[i][0] in [c1, c2]:
                tr_P[i] = []
                count += 1
        for i in range(count):
            tr_P.remove([])
        
        for c in [c1, c2]:
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
        return gr_C, tr_P
    
    # fusionne un element isole et un groupe non rempli
    if case == 1:
        ids_gr_C_sing = [c for c in range(len(gr_C)) if len(gr_C[c]) == 1]
        
        if ids_gr_C_sing == []:
            return gr_C, tr_P
        
        c1 = rd.choice(ids_gr_C_sing)
        f1 = gr_C[c1][0]
        gr_C.remove([f1])

        count = 0
        for i in range(len(tr_P)):
            if tr_P[i][0] == c1:
                tr_P[i] = []
                count += 1
            elif tr_P[i][0] > c1:
                tr_P[i][0] -= 1
        for i in range(count):
            tr_P.remove([])
        
        ids_gr_C_pot = [c for c in range(len(gr_C)) if len(gr_C[c]) < 4]
        c2 = rd.choice(ids_gr_C_pot)
        gr_C[c2].append(f1)

        
        count = 0
        for i in range(len(tr_P)):
            if tr_P[i][0] == c2:
                tr_P[i] = []
                count += 1
        for i in range(count):
            tr_P.remove([])
        
        for c in [c2]:
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
    
        return gr_C, tr_P
    
    # isole un element si possible
    if case == 2:
        ids_gr_C_non_sing = [c for c in range(len(gr_C)) if len(gr_C[c]) > 1]

        if ids_gr_C_non_sing == []:
            return gr_C, tr_P

        c0 = rd.choice(ids_gr_C_non_sing)
        id0 = rd.randrange(len(gr_C[c0]))
        
        f = gr_C[c0][id0]
        gr_C[c0].remove(f)
        gr_C.append([f])
        
        count = 0
        for i in range(len(tr_P)):
            if tr_P[i][0] == c0:
                tr_P[i] = []
                count += 1
        for i in range(count):
            tr_P.remove([])

        for c in [c0, len(gr_C) - 1]:
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
        return gr_C, tr_P







st_f_0, gr_C_0, tr_P_0 = compute_solution(0)
verify_solution(Q, F, H, L_f, a, st_f_0, gr_C_0, tr_P_0)
cost = cost_solution(Q, F, H, L_f, a, st_f_0, gr_C_0, tr_P_0)
print(cost)
gr_C_1, tr_P_1 = alter_groups(gr_C_0, tr_P_0)
verify_solution(Q, F, H, L_f, a, st_f_0, gr_C_1, tr_P_1)

nb_iter = 1000
for i in range(nb_iter):
    gr_C_1, tr_P_1 = alter_groups(gr_C_0, tr_P_0, i)
#    verify_solution(Q, F, H, L_f, a, st_f_0, gr_C_1, tr_P_1)
    if cost_solution(Q, F, H, L_f, a, st_f_0, gr_C_1, tr_P_1) < cost:
        gr_C_0 = [C.copy() for C in gr_C_1]
        tr_P_0 = [[P[0], P[1], P[2], P[3].copy(), P[4].copy()] for P in tr_P_1]
        cost = cost_solution(Q, F, H, L_f, a, st_f_0, gr_C_0, tr_P_0)
        print(cost)
    if i == 100:
        print("Limite")

#print_solution(st_f_0, gr_C_0, tr_P_0, "solution.txt")
#print(evaluate_solution(data_file_name, "solution.txt"))
