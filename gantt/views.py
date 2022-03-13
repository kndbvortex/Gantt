from turtle import left
from django.shortcuts import render
from django.conf import settings

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def home(request):
    return render(request, 'index.html')

def draw_gantt(request):
    print(request.POST)
    print(request.FILES)
    import time
    df = pd.read_excel(request.FILES.get('tasks').file, header=None)
    n = 0
    prec = ["-"]
    set_prec = set('-')
    niveaux = []
    while n < df.shape[0]:
        l = list(df[df[3].apply(lambda val: set(val.replace(' ', '').split(',')).issubset(set_prec))][0])
        l = list(set(l).difference(set_prec))
        if not l:
            print("GG")
            break
        n += len(l)
        prec = list(l)
        niveaux.append(l)
        set_prec.update(l)
    print(niveaux)
    dates = {key: [0, 0] for key in df[0]}
    tache_finale, date_finale = '', 0 
    for i, niveau in enumerate(niveaux):
        for task in niveau:
            if i == 0:
                dates[task][1] = df[df[0] == task][2].iloc[0]
            else:
                predecesseurs = df[df[0] == task][3].iloc[0].replace(" ", "").split(',') # Liste des prédecesseurs
                date_debut = max([dates[predecesseur][1] for predecesseur in predecesseurs]) # predecessseur, Date de fin max
                if task == 'E':
                    print(date_debut)
                dates[task][0] = date_debut
                    
                dates[task][1] = dates[task][0] + df[df[0] == task][2].iloc[0]
            if dates[task][1] > date_finale:
                tache_finale = task
                date_finale = dates[task][1]
    print(dates)
    chemin_critique = []
    while date_finale > 0:
        for task in dates:
            if dates[task][1] == date_finale:
                date_finale = dates[task][0]
                chemin_critique.append(task)
                break
    plt.figure(figsize=(10, 6), dpi=80)
    plt.grid()
    plt.yticks([50*(i+1) for i in range(len(dates)) ], [label for label in df[1]])
    for i,k in enumerate(dates.keys()):
        if k in chemin_critique:
            plt.hlines(y=50*(i+1), xmin=dates[k][0], xmax=dates[k][1], lw=10, color='red')
        else:
            plt.hlines(y=50*(i+1), xmin=dates[k][0], xmax=dates[k][1], lw=10)
            
    red_patch = mpatches.Patch(color='red', label='Chemin critique')
    plt.legend(handles=[red_patch], loc='lower right')
    plt.savefig(str(settings.BASE_DIR)+"/gantt/static/images/diagramme.png")
    return render(request, 'index.html', {'image': True})
    
    