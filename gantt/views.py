from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from django.shortcuts import render

import pandas as pd

def home(request):
    context = dict()
    if request.method == "POST":
        print(request.POST)
        if request.FILES["tasks"].name.split('.')[-1] != "csv":
            df = pd.read_excel(request.FILES.get('tasks').file, header=None)  
        else:
            df = pd.read_csv(request.FILES.get('tasks').file, header=None)
        
        n = 0
        set_prec = set('-')
        niveaux = []
        while n < df.shape[0]:
            l = list(df[df[3].apply(lambda val: set(val.replace(' ', '').split(',')).issubset(set_prec))][0])
            l = list(set(l).difference(set_prec))
            if not l:
                break
            n += len(l)
            niveaux.append(l)
            set_prec.update(l)
        print(niveaux)
        dates = {key: [0, 0] for key in df[0]}
        date_finale = 0 
        for i, niveau in enumerate(niveaux):
            for task in niveau:
                if i == 0:
                    dates[task][1] = df[df[0] == task][2].iloc[0]
                else:
                    predecesseurs = df[df[0] == task][3].iloc[0].replace(" ", "").split(',') # Liste des prédecesseurs
                    date_debut = max([dates[predecesseur][1] for predecesseur in predecesseurs]) # predecessseur, Date de fin max
                    dates[task][0] = date_debut
                        
                    dates[task][1] = dates[task][0] + df[df[0] == task][2].iloc[0]
                if dates[task][1] > date_finale:
                    date_finale = dates[task][1]
        print(dates)
        chemin_critique = []
        while date_finale > 0:
            for task in dates:
                if dates[task][1] == date_finale:
                    date_finale = dates[task][0]
                    chemin_critique.append(task)
                    break
        context['print_diagram'] = True
        d = dict()
        for i in range(df.shape[0]):
            d[df[0][i]] = df[1][i]
        context["labels"] = list(reversed([d[key] for key in dates.keys()]))
        context["intervales"] = list(reversed([v for _, v in dates.items()]))
        context["couleurs"] = list(reversed(["red" if key in chemin_critique else "blue" for key in dates.keys()]))
        
        start_date = datetime.now()
        if date := request.POST.get("date", ""):
            start_date = datetime.strptime(date, '%Y-%m-%d')
        else:
            start_date = datetime.now()
            
        project_duration = max([dates[i][1] for i in niveau[-1]])

        if u := request.POST.get("unit", ""):
            if u == "1":
                date_fin = start_date + timedelta(days=int(project_duration))
                context["message"] = f"\tLe projet commençant le {start_date.strftime('%d-%m-%Y')} devra se terminer dans maximum {project_duration} jours c'est à dire le {date_fin.strftime('%d-%m-%Y')}"
                l = []
                for i, (debut, f) in enumerate(context["intervales"]):
                    debut1 = start_date + timedelta(days=int(debut))
                    f1 = start_date + timedelta(days=int(f))
                    l.append([context["labels"][i],debut1.strftime('%d-%m-%Y'), f1.strftime('%d-%m-%Y')])
                context["intervales_date"] = l
            elif u == "2":
                date_fin = start_date + relativedelta(months=+int(project_duration))
                context["message"] = f"\tLe projet commençant le {start_date.strftime('%d-%m-%Y')} devra se terminer dans maximum {project_duration} mois c'est à dire le {date_fin.strftime('%d-%m-%Y')}"
                for i, (debut, f) in enumerate(context["intervales"]):
                    debut1 = start_date + relativedelta(months=+int(debut))
                    f1 = start_date + relativedelta(months=+int(f))
                    l.append([context["labels"][i], debut1.strftime('%d-%m-%Y'), f1.strftime('%d-%m-%Y')])
                context["intervales_date"] = l
            elif u == "3":
                date_fin = start_date + relativedelta(years=+int(project_duration))
                context["message"] = f"\tLe projet commençant le {start_date.strftime('%d-%m-%Y')} devra se terminer dans maximum {project_duration} années c'est à dire le {date_fin.strftime('%d-%m-%Y')}"
                for i, (debut, f) in enumerate(context["intervales"]):
                    debut1 = start_date + relativedelta(years=+int(debut))
                    f1 = start_date + relativedelta(years=int(f))
                    l.append([context["labels"][i], debut1.strftime('%d-%m-%Y'), f1.strftime('%d-%m-%Y')])
                context["intervales_date"] = l
        
    return render(request, 'index.html', context=context)

def draw_gantt(request):
    return render(request, 'index.html', {'image': True})
    
    