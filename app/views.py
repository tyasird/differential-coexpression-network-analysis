from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, StreamingHttpResponse
from django.core.files.storage import FileSystemStorage
from django.core.serializers import serialize
from django.template.defaulttags import register
from django.db.models.query import QuerySet
from django.utils.safestring import mark_safe
from django.forms.models import model_to_dict
from app.models import DiffCoExpression, Network
from django.template import Library
from django.utils import safestring
from django.utils import timezone
import helpers.helper as helper
from .forms import analyzeForm
from tools.dcna_tool import DcnaTool
from tools.network_tool import NetworkTool
import pandas as pd
import uuid
import json
import math
import os
import glob

def index(request):
    status_hash = uuid.uuid4().hex[0:10]
    return render(request, 'index.html', {'status_hash': status_hash})


def about(request):
    return render(request, 'about.html')


def database(request):
    # file_list = glob.glob("uploads/output/disease_*.xlsx")
    # file_list = [f.replace('\\','/') for f in file_list]
    networks = Network.objects.all()
    for i in networks:
        print(i.diff_coexp.input_excel)
    return render(request, 'database.html', {'networks': networks} )

def status(request, status_hash):
    with open('uploads/status/' + status_hash + '.txt', 'r') as f:
        lines = f.readlines()
    return HttpResponse('\n'.join(lines))


def logdetail(detail,status_hash):
    f = open('uploads/status/'+status_hash+'.txt', "a")
    f.write("{0}\n".format(detail))
    f.close()


def analyze(request):
    input_folder = 'uploads/input/'
    output_folder = 'uploads/output/'
    error = None
    analyze_result = None

    # METHOD POST
    if request.method == 'POST':

        form = analyzeForm(request.POST, request.FILES)
        if form.is_valid():

            status_hash = request.POST['status_hash']
            with open('uploads/status/' + status_hash + '.txt', 'w') as f:
                f.write('')

            file = request.FILES['input_excel']
            if not allowed_file(file.name):
                form.add_error('input_excel', 'file ext error')
                return render(request, 'index.html', {'form': form})

            fs = FileSystemStorage(location=input_folder)
            _, ext = os.path.splitext(file.name)
            new_filename = uuid.uuid4().hex + ext
            fs.save(new_filename, file)

            try:
                dcna = DcnaTool()
                logdetail('uploading..', status_hash)
                filename, genes, values = dcna.read_input(input_folder, new_filename)
                logdetail('normalization..', status_hash)
                normalizated_data = dcna.normalization(values)
                logdetail('explode samples..', status_hash)
                healthy, disease, disease_sample, healthy_sample = dcna.explode_samples(normalizated_data,request.POST['healthy_sample'])
                logdetail('normality test..', status_hash)
                pval_healthy, pval_disease = dcna.normality_test(healthy, disease)
                logdetail('correlation..', status_hash)
                healthy_corr, disease_corr = dcna.correlation(healthy, pval_healthy, disease, pval_disease)
                logdetail('find pcritic..', status_hash)
                pcritic, pcritic_healty, pcritic_disease = dcna.find_pcritic(healthy_corr, disease_corr)
                logdetail('make binary..', status_hash)
                healthy_genes, disease_genes = dcna.make_binary(healthy_corr, disease_corr, genes)
                logdetail('filter by pcritic..', status_hash)
                filtred_healthy, filtred_disease = dcna.filter_by_pcritic(healthy_genes, disease_genes, pcritic)
                logdetail('differential coexpression analysis..', status_hash)
                diff_healthy, diff_disease = dcna.differential_co_expression(filtred_healthy, filtred_disease, pcritic,
                                                                             0.5)
                logdetail('export to excel..', status_hash)
                dcna.export_excel(filename, output_folder, diff_healthy, diff_disease)
                logdetail('export to json..', status_hash)
                diff_healthy_json, diff_disease_json = dcna.export_json(diff_healthy, diff_disease)
                logdetail('create db record..', status_hash)
                create = DiffCoExpression.objects.create(
                    cancer_id=0,
                    input_excel=new_filename,
                    healthy_sample=healthy_sample,
                    disease_sample=disease_sample,
                    disease_pcritic=pcritic_disease,
                    healthy_pcritic=pcritic_healty,
                    healthy_normality_pvalue=pval_healthy,
                    disease_normality_pvalue=pval_disease,
                    healthy_co_expression=0,
                    disease_co_expression=0,
                    healthy_diff_co_expression=diff_healthy_json,
                    disease_diff_co_expression=diff_disease_json,
                    timestamp=timezone.now()
                )

                return redirect('diffcoexp', id=create.id)

            # manually add error
            except ValueError as e:

                return render(request, 'index.html', {'error': e.args[0]})

        # form error
        else:
            return render(request, 'index.html', {'form': form})

    # METHOD GET
    else:
        return redirect('/')


def diffcoexp(request, id):
    response = get_object_or_404(DiffCoExpression, id=int(id))
    data = {}
    data['healthy_diff_co_expression_len'] = len(response.healthy_diff_co_expression['gene1'])
    data['disease_diff_co_expression_len'] = len(response.disease_diff_co_expression['gene1'])
    return render(request, 'diff_coexp_result.html', {'response': response, 'data': data})





def network(request, id, type_id):
    # 0 = disease, 1 = healthy
    prefix = type_id == 0 and 'disease_' or 'healthy_'
    output_folder = 'uploads/output/'

    diff_coexp = DiffCoExpression.objects.get(id=id)
    network = Network.objects.filter(diff_coexp_id=id, type=type_id).first()

    # no records, open cytoscape and do analysis
    if network is None:

        try:
            network_tool = NetworkTool()
            if network_tool.get_session():
                return render(request, 'diff_coexp_result.html',
                              {'error': 'Cytoscape is busy. Please try again later or Refresh the page.',
                               'response': diff_coexp})
        except Exception as e:
            return render(request, 'diff_coexp_result.html', {'error': str(e), 'response': diff_coexp})

        else:
            try:
                session = network_tool.create_session()
                read = network_tool.read_excel(output_folder + prefix + diff_coexp.input_excel)
                create_network = network_tool.create_network(read, session)
                mcode = network_tool.run_mcode()
                clusters, error = network_tool.get_clusters(mcode, 5)
                delete = network_tool.delete_session()
                create = Network.objects.create(diff_coexp_id=id, type=type_id, mcode=clusters)

                clusters_with_interactions = []
                for c in clusters:
                    interactions, opposite_interactions = find_module_interactions(
                        diff_coexp.disease_diff_co_expression, diff_coexp.healthy_diff_co_expression,
                        c['table']['gene'].values(), diff_coexp.disease_pcritic)
                    c['interactions'] = interactions
                    c['opposite_interactions'] = opposite_interactions
                    clusters_with_interactions.append(c)

                return render(request, 'network_result.html',
                              {'clusters': clusters_with_interactions, 'network': create, 'diff_coexp': diff_coexp})

            except Exception as e:

                delete = network_tool.delete_session()
                return render(request, 'diff_coexp_result.html', {
                    'response': diff_coexp,
                    'error': str(e),
                })

    # record found in db, just show it
    else:
        clusters = network.mcode
        clusters_with_interactions = []
        for c in clusters:
            interactions, opposite_interactions = find_module_interactions(diff_coexp.disease_diff_co_expression,
                                                                           diff_coexp.healthy_diff_co_expression,
                                                                           c['table']['gene'].values(),
                                                                           diff_coexp.disease_pcritic)
            c['interactions'] = interactions
            c['opposite_interactions'] = opposite_interactions
            clusters_with_interactions.append(c)

        return render(request, 'network_result.html',
                      {'clusters': clusters_with_interactions, 'network': network, 'diff_coexp': diff_coexp})


def allowed_file(filename):
    allowed_extensions = {'.csv', '.xls', '.xlsx'}
    _, ext = os.path.splitext(filename)
    return ext in allowed_extensions


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def format_pvalue(value):
    return format(float(value), "10.2E")


@register.filter
def jsonify(object):
    if isinstance(object, QuerySet):
        return mark_safe(serialize('json', object))
    return mark_safe(json.dumps(object))


jsonify.is_safe = True


@register.filter
def find_network_density(value, arg):
    return int(round(arg / ((value * (value - 1)) / 2), 2) * 100)


def find_module_interactions(data, opposite, cluster, pcritic):
    data = pd.read_json(json.dumps(data))
    opposite = pd.read_json(json.dumps(opposite))
    # verilan tablo icinde bu clustera ait genlerin birbirleriyle olan etkilesimlerini cekiyoruz.
    interactions = data.loc[((data['gene1'].isin(cluster)) & (data['gene2'].isin(cluster)))].reset_index(drop=True)
    interactions = interactions[interactions['gene1'] < interactions['gene2']]
    # buldugumuz bu etkilesimler zit tabloda var mi ona bakiyoruz. Varsa pcritic uzerinde olanlari aliyoruz.
    search_genes = opposite[opposite[['gene1', 'gene2']].isin(interactions[['gene1', 'gene2']]).all(axis=1)]
    search_genes = search_genes[search_genes['score'] > float(pcritic)]
    # once tum etkilesimleri gosteriyoruz, sonra etkilesimlerin zit tabloda arama sonuclarini
    # returns data_interactions, opposite_interactions
    return interactions[['gene1', 'gene2']].values.tolist(), search_genes[['gene1', 'gene2']].values.tolist()
