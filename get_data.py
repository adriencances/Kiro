#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 14:29:50 2019

@author: Adrien CANCES
"""


def get_data(file_name):
    file = open(file_name, 'r')
    lines = file.read().splitlines()
    
    first_line_data = lines[0].split()
    Q, F, H = int(first_line_data[1]), int(first_line_data[3]), int(first_line_data[5])
    
    L_f = [[] for i in range(F + 2)]
    
    depot_line = lines[1].split()
    d = int(depot_line[1])
    L_f[d] = [0, [], [float(depot_line[3]), float(depot_line[4])]]
    
    usine_line = lines[2].split()
    u = int(usine_line[1])
    L_f[u] = [0, [], [float(usine_line[3]), float(usine_line[4])]]
    
    for f in range(F):
        fournisseur_line = lines[3 + f].split()
        L_f[f] = [int(fournisseur_line[3]),
            [int(fournisseur_line[5 + s]) for s in range(H)],
            [float(fournisseur_line[5 + H + 1]), float(fournisseur_line[5 + H + 2])]]

    a = [[0 for j in range(F + 2)] for i in range(F + 2)]

    for k in range((F + 2) * (F + 2)):
        d_line = lines[3 + F + k].split()
        a[int(d_line[1])][int(d_line[2])] = int(d_line[4])
    
    file.close()
    
    return Q, F, H, L_f, a


    
