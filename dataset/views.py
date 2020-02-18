import importlib
import json
import os
from shutil import rmtree, unpack_archive, get_archive_formats
from time import time

import numpy as np
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render

from settings.settings import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, TEMP_FOLDER
from ._utils import get_anndata_attrs
from .models import DataSet


def render_dataset(request):
    return render(request, "dataset/datasets.html")


def render_dataupload(request):
    return render(request, "dataset/dataupload.html",
                  {'allowed_file': ", ".join(ALLOWED_EXTENSIONS)})


def rest_datasets(request):
    if request.method == 'GET':
        limit = int(request.GET.get('limit', 0))
        offset = int(request.GET.get('offset', 0))
        result = DataSet.objects.all()[offset: limit]
        return JsonResponse(list(result.values('id',
                                               'user',
                                               'name',
                                               'description',
                                               'modified',
                                               'n_obs', 'n_vars',
                                               'attrs')), safe=False)
    if request.method == "POST":
        action = request.POST.get('action', "")
        id = request.POST.get("id", None)
        if not id:
            return HttpResponseForbidden()
        if action == "DELETE":
            result = DataSet.objects.get(id=id)
            if os.path.isfile(result.path):
                os.remove(result.path)
            if os.path.isdir(result.path):
                rmtree(result.path)
            result.delete()
            return JsonResponse({'id': id})
        elif action == "UPDATE":
            result = DataSet.objects.get(id=id)
            name = request.POST.get("name")
            if name:
                result.name = name
            description = request.POST.get("description")
            if description:
                result.description = description
            result.save()
            return JsonResponse(result.to_dict(), safe=False)


def data_upload(request):
    file = request.FILES.get('file', None)
    if not file:
        return HttpResponseBadRequest

    file_ori, ext = file.name.rsplit('.', 1)
    ext = ext.lower()
    hash_name = file_ori + "_" + hex(int(time()))[2:]
    path = os.path.join(UPLOAD_FOLDER, hash_name + "." + ext)

    with open(path, 'wb+') as f:
        for chunk in file.chunks():
            f.write(chunk)
    if ext in [x[0] for x in get_archive_formats()]:
        unpack_archive(path, os.path.join(UPLOAD_FOLDER))
        os.rename(os.path.join(UPLOAD_FOLDER, file_ori),
                  os.path.join(UPLOAD_FOLDER, hash_name))
        os.remove(path)
        path = os.path.join(UPLOAD_FOLDER, hash_name)

    package = request.POST.get("package")
    method = request.POST.get("method")

    if not method or not package:
        return HttpResponseBadRequest
    try:
        module = importlib.import_module(package)
        components = method.split(".")
        for attr in components:
            module = getattr(module, attr)
        adata = module(path)
        if os.path.isdir(path):
            rmtree(path)
        else:
            os.remove(path)
        path = os.path.join(UPLOAD_FOLDER, hash_name + ".h5ad")
        adata.write(path)
    except Exception as e:
        if path:
            if os.path.isdir(path):
                rmtree(path)
            else:
                os.remove(path)
        return JsonResponse({'status': False, 'info': 'Internal Error: ' + str(e)})

    saved_file = DataSet(
        user=request.POST.get("owner", "Upload"),
        name=request.POST.get("name", "uploaded-file"),
        path=path,
        description=request.POST.get("description", ""),
        n_obs=adata.n_obs,
        n_vars=adata.n_vars,
        attrs=json.dumps(get_anndata_attrs(adata))
    )
    saved_file.save()
    return JsonResponse({'status': True, 'info': "File successfully uploaded as " + saved_file.name + ".h5ad"})


def result_export(request):
    pid = request.POST.get("pid", None)
    if not pid:
        return HttpResponseBadRequest
    import scanpy as sc
    adata = sc.read_h5ad(os.path.join(TEMP_FOLDER, str(pid), "results.h5ad"))
    indexes = np.fromstring(request.POST.get("index"), dtype=int, sep=",")
    hextime = hex(int(time()))[2:]
    output_path = os.path.join(UPLOAD_FOLDER, f"exported_{pid}_{hextime}.h5ad")
    adata = adata[indexes, :]
    adata.write(output_path)

    saved_file = DataSet(
        source=request.POST.get("owner", f"Export from {pid}"),
        name=request.POST.get("name", f"export_{pid}"),
        path=output_path,
        description=request.POST.get("description", ""),
        n_obs=adata.n_obs,
        n_vars=adata.n_vars,
        attrs=json.dumps(get_anndata_attrs(adata))
    )
    saved_file.save()
    return JsonResponse(
        {'status': True, 'info': "File successfully exported as " + saved_file.name + ".h5ad",
         "output": str(adata[indexes, :])})
