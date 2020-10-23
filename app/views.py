import json

from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from app.models import DiffCoExpression, Network
from .forms import analyzeForm
from django.core.files.storage import FileSystemStorage
import uuid
import os
from tools.dcna_tool import DcnaTool
from tools.network_tool import NetworkTool
import math
from django.utils import timezone
import helpers.helper as helper
from django.template.defaulttags import register
from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.utils import safestring
from django.utils.safestring import mark_safe
from django.forms.models import model_to_dict
import pandas as pd


def index(request):
    cancer_ids = helper.cancer_ids()
    return render(request, 'index.html', {'cancer_ids': cancer_ids})


def database(request):
    return render(request, 'database.html')


def about(request):
    return render(request, 'about.html')


def diff_coexp_result(request, diff_coexp_id):
    cancer_ids = helper.cancer_ids()
    response = get_object_or_404(DiffCoExpression, id=int(diff_coexp_id))
    return render(request, 'diff_coexp_result.html', {'response': response, 'cancer_ids': cancer_ids})


def network_result(request, diff_coexp_id, type):
    cancer_ids = helper.cancer_ids()

    # 0 = disease
    # 1 = healthy
    prefix = type == 0 and 'disease_' or 'healthy_'
    output_folder = 'uploads/output/'

    diff_coexp = DiffCoExpression.objects.get(id=diff_coexp_id)
    network = Network.objects.filter(diff_coexp_id=diff_coexp_id, type=type).first()

    # no records, open cytoscape and do analysis
    if network is None:

        network_tool = NetworkTool()
        if network_tool.get_session():
            return render(request, 'diff_coexp_result.html', {'error': 'Cytoscape is busy. Please try again later or Refresh the page.', 'response': diff_coexp, 'cancer_ids': cancer_ids})
        else:
            session = network_tool.create_session()
            read = network_tool.read_excel(output_folder + prefix + diff_coexp.input_excel)
            create_network = network_tool.create_network(read, session)
            load_style = network_tool.load_style('yd.xml')
            set_style = network_tool.set_style(name=load_style)
            mcode = network_tool.run_mcode()
            clusters, error = network_tool.get_clusters(mcode, 0) # layout='hierarchical'
            if error is not None:
                delete = network_tool.delete_session()
                return render(request, 'diff_coexp_result.html', {
                    'response': diff_coexp,
                    'cancer_ids': cancer_ids,
                    'error': error,
                })

            delete = network_tool.delete_session()
            create = Network.objects.create(
                diff_coexp_id=diff_coexp_id,
                type=type,
                mcode=clusters
            )

            return render(request, 'network_result.html', {'clusters': json.loads(clusters), 'network': create, 'diff_coexp': diff_coexp, 'cancer_ids': cancer_ids})

    # record found in db, just show it
    else:
        return render(request, 'network_result.html', {'clusters': json.loads(network.mcode), 'network': network, 'diff_coexp': diff_coexp, 'cancer_ids': cancer_ids})


def do_analyze(request):
    input_folder = 'uploads/input/'
    output_folder = 'uploads/output/'
    error = None
    analyze_result = None

    # METHOD POST
    if request.method == 'POST':

        form = analyzeForm(request.POST, request.FILES)
        if form.is_valid():
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
                filename, genes, values = dcna.read_input(input_folder, new_filename)
                normalizated_data = dcna.normalization(values)
                healthy, disease, disease_sample, healthy_sample = dcna.explode_samples(normalizated_data, request.POST['healthy_sample'])
                pval_healthy, pval_disease = dcna.normality_test(healthy, disease)
                healthy_corr, disease_corr = dcna.correlation(healthy, pval_healthy, disease, pval_disease)
                pcritic, pcritic_healty, pcritic_disease = dcna.find_pcritic(healthy_corr, disease_corr)
                healthy_with_genes, disease_with_genes = dcna.make_binary(healthy_corr, disease_corr, genes)
                filtred_healthy, filtred_disease = dcna.filter_by_pcritic(healthy_with_genes, disease_with_genes, pcritic)
                diff_healthy, diff_disease = dcna.differential_co_expression(filtred_healthy, filtred_disease, pcritic, 0.5)
                dcna.export_excel(filename, output_folder, diff_healthy, diff_disease)
                healthy_json, disease_json = dcna.export_json(filtred_healthy, filtred_disease)
                diff_healthy_json, diff_disease_json = dcna.export_json(diff_healthy, diff_disease)

                create = DiffCoExpression.objects.create(
                    cancer_id=request.POST['cancer_id'],
                    input_excel=new_filename,
                    healthy_sample=healthy_sample,
                    disease_sample=disease_sample,
                    disease_pcritic=pcritic_disease,
                    healthy_pcritic=pcritic_healty,
                    healthy_normality_pvalue=pval_healthy,
                    disease_normality_pvalue=pval_disease,
                    healthy_co_expression=healthy_json,
                    disease_co_expression=disease_json,
                    healthy_diff_co_expression=diff_healthy_json,
                    disease_diff_co_expression=diff_disease_json,
                    timestamp=timezone.now()
                )

                return redirect('diff_coexp_result', diff_coexp_id=create.id)

            # manually add error
            except ValueError as e:

                return render(request, 'index.html', {'error': e.args[0]})

        # form error
        else:
            return render(request, 'index.html', {'form': form})

    # METHOD GET
    else:
        return redirect('/')


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'.csv', '.xls', '.xlsx'}
    _, ext = os.path.splitext(filename)
    return ext in ALLOWED_EXTENSIONS


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


@register.filter
def find_interactions(value, arg):
    data = pd.read_json(value)
    cluster = arg['table']['gene'].values()
    filter = data.loc[data['gene1'].isin(cluster)].reset_index(drop=True)
    return filter['gene2'].values.tolist()


@register.filter
def find_cluster_interactions(value, arg):
    data = pd.read_json(value)
    cluster = arg['table']['gene'].values()
    interactions = data.loc[(data['gene1'].isin(cluster)) & (data['gene2'].isin(cluster))].reset_index(drop=True)
    interactions = interactions[interactions['gene1'] < interactions['gene2']]
    return interactions[['gene1', 'gene2']].values.tolist()
