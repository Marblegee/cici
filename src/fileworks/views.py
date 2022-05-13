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
import hvac
from django.conf import settings

BASE_DIR = Path(__file__).resolve().parent.parent
VAULT_HOSTNAME = 'http://127.0.0.1'
VAULT_PORT = 8200
VAULT_TOKEN = 'root'

# instantiate hvac
vault_client = hvac.Client(
    url=f'{VAULT_HOSTNAME}:{VAULT_PORT}',
    token=VAULT_TOKEN,
)

#vault_client.secrets.transit.create_key(name='hvac-key')
# list_keys_response = vault_client.secrets.transit.read_key(name='hvac-key')


def encrypt(value, path='cici_data', name='orders'):
    try:
        response = vault_client.secrets.transit.encrypt_data(
            name=name,
            plaintext=base64.b64encode(value.encode()).decode('ascii'))
        # print('Response: {}'.format(response))
        return response['data']['ciphertext']
    except Exception as e:
        print('There was an error encrypting the data: {}'.format(e))


def decrypt(value, path='cici_data', name='orders'):
    # support unencrypted messages on first read
    if not value.startswith('vault:v'):
        return value
    else:
        try:
            response = vault_client.secrets.transit.decrypt_data(
                name=name, ciphertext=value)
            # print('Response: {}'.format(response))
            plaintext = response['data']['plaintext']
            # print('Plaintext (base64 encoded): {}'.format(plaintext))
            decoded = base64.b64decode(plaintext).decode()
            # print('Decoded: {}'.format(decoded))
            return decoded
        except Exception as e:
            print('There was an error encrypting the data: {}'.format(e))


def save_to_database(data, path='cici_data'):
    for idx, row in data.iterrows():
        #hvac_secret = {str(idx): str(row["ptss"])}
        #print(hvac_secret)
        #val = str(row["ptss"])
        #print(val)
        ptss = encrypt(str(row["ptss"]))
        time = encrypt(str(row["time"]))
        exp = encrypt(str(row["exp"]))
        t2ies = encrypt(str(row["t2ies"]))
        cset = encrypt(str(row["cset"]))
        # print(pts_response)
        db_data = DfUpload(ptss=ptss,
                           time=time,
                           exp=exp,
                           t2ies=t2ies,
                           cset=cset)
        try:
            db_data.save()
        except:
            print("Cannot save data")


# Create your views here.
# for d in data:
#     print(d, data[d])
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

    # Trauma History
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
    save_to_database(adj_data)
    #print(VAULT_CLIENT.is_authenticated())

    # print(adj_data.corr())
    mod = ols('ptss~time+exp+t2ies', data=adj_data).fit()

    mod2 = ols('ptss~time+exp+t2ies+cset', data=adj_data).fit()
    # mod = ols('y~x1+x2+x3', data=df).fit()

    # sns.lmplot(x='ptss', y='cset', data=adj_data)
    # plt.savefig('plot1.png')

    # data_upload.aov = sm.stats.anova_lm(mod, type=2)
    data_upload.mod_res = mod.summary()

    data_upload.mod2_res = mod2.summary()

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
    # sns.lmplot(x='cset', y='ptss', data=adj_data)
    sns.pairplot(adj_data,
                 x_vars=['time', 'exp', 't2ies', 'cset'],
                 y_vars='ptss',
                 height=5,
                 aspect=0.5)
    plt.savefig(BASE_DIR / 'static' / 'plot1.png')

    context = {}
    return render(request, template, context)


def result(request):
    template = "result.html"
    res = data_upload.mod_res
    res = res.as_html()

    res2 = data_upload.mod2_res
    res2 = res2.as_html()

    print(MEDIA_ROOT)

    context = {
        'result': res,
        'result2': res2,
        'BASE_DIR': BASE_DIR,
        'MEDIA_ROOT': MEDIA_ROOT
    }
    return render(request, template, context)