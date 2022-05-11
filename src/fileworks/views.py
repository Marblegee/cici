import csv, io
from multiprocessing import context
from django.contrib import messages
from django.contrib.auth.decorators import permission_required

from filetest.settings import MEDIA_ROOT
from .models import DfUpload
import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from django.shortcuts import render, HttpResponse
import seaborn as sns
from io import BytesIO
from matplotlib import pyplot as plt
import numpy as np
import uuid, base64

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Create your views here.


@permission_required('admin.can_add_log_entry')
def data_upload(request):
    template = "upload.html"

    if request.method == 'GET':
        return render(request, template)

    csv_file = request.FILES['file']

    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'This is not a CSV file')

    df_file = pd.read_csv(csv_file)
    df = pd.DataFrame(df_file)

    # Post Traumatic Stress Symptoms - t2ies
    ptss = df[df.columns[38:44]].sum(axis=1)

    # Time
    time = df[df.columns[0]]

    # Exposure
    exp = df[df.columns[10:22]].sum(axis=1)

    # Post Traumatic Stress Symptoms
    t2ies = df[df.columns[22:38]].sum(axis=1)

    # Coping Self-Efficacy
    cset = df[df.columns[1:10]].sum(axis=1)

    adj_data = pd.DataFrame({
        'ptss': ptss,
        'time': time,
        'exp': exp,
        't2ies': t2ies,
        'cset': cset
    })

    # print(adj_data.corr())
    mod = ols('ptss~time+exp+t2ies+cset', data=adj_data).fit()
    # mod = ols('y~x1+x2+x3', data=df).fit()

    # sns.lmplot(x='ptss', y='cset', data=adj_data)
    # plt.savefig('plot1.png')

    # data_upload.aov = sm.stats.anova_lm(mod, type=2)
    data_upload.mod_res = mod.summary()

    # Visualization
    #fig, ax = plt.subplots(figsize=(9, 9))
    x, y = adj_data['cset'], adj_data['ptss']
    plt.switch_backend('AGG')
    fig = plt.figure(figsize=(10, 4))

    plt.scatter(x, y, s=60, alpha=0.7, edgecolors="k")
    plt.savefig('plot1.png')

    # Correlation Plot
    corr = adj_data.corr()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    cax = ax.matshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
    fig.colorbar(cax)
    ticks = np.arange(0, len(adj_data.columns), 1)
    ax.set_xticks(ticks)
    plt.xticks(rotation=90)
    ax.set_yticks(ticks)
    ax.set_xticklabels(adj_data.columns)
    ax.set_yticklabels(adj_data.columns)
    save_to = '/Users/mac/dev3/csvwork/src/'
    plt.savefig(BASE_DIR / 'static' / 'correlation.png')

    # REGRESSION PLOT
    sns.lmplot(x='cset', y='ptss', data=adj_data)
    plt.savefig(BASE_DIR / 'static' / 'plot1.png')

    context = {}
    return render(request, template, context)


def result(request):
    template = "result.html"
    res = data_upload.mod_res
    res = res.as_html()

    print(MEDIA_ROOT)

    context = {'result': res, 'BASE_DIR': BASE_DIR, 'MEDIA_ROOT': MEDIA_ROOT}
    return render(request, template, context)