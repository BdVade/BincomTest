from django.shortcuts import render, redirect
from django.db.models import Sum
from django.http.response import JsonResponse
from .models import PollingUnit, AnnouncedPuResults, Lga, AnnouncedLgaResults
from django.views.decorators.csrf import csrf_exempt
import json
from .forms import ResultUploadForm
# Create your views here.


def home(request):
    polling_unit_list = PollingUnit.objects.exclude(polling_unit_name="", polling_unit_name__isnull=True)
    return render(request, 'index.html', {'polling_units': polling_unit_list})


def polling_unit(request, _id):
    try:
        polling_unit_object = PollingUnit.objects.get(uniqueid=_id)
    except PollingUnit.DoesNotExist:
        return redirect('not_found')

    polling_unit_results = AnnouncedPuResults.objects.filter(polling_unit_uniqueid=polling_unit_object.uniqueid)
    return render(request, 'pu_result.html', {'polling_unit': polling_unit_object, 'results': polling_unit_results})


def local_government(request, _id):
    polling_units_id = list(PollingUnit.objects.filter(uniqueid=_id).values_list('uniqueid', flat=True))
    print(polling_units_id)

    local_government_object = Lga.objects.get(uniqueid=_id)
    pu_results = AnnouncedPuResults.objects.filter(polling_unit_uniqueid__in=polling_units_id)
    pu_results_party_abbreviations = list(set(pu_results.values_list('party_abbreviation', flat=True)))
    # pu_results_party_abbreviations = [y for x in pu_results_party_abbreviations_pc for y in x]
    # parties = Party.objects.all().annotate(result=Sum(pu_results.filter()))
    results_list = []
    for party in pu_results_party_abbreviations:
        lga_results = AnnouncedLgaResults.objects.filter(lga_name=local_government_object.lga_name)
        if lga_results:
            lga_results = lga_results[0].party_score
        else:
            lga_results = 0
        results_list.append({'name': party, 'polling_unit_result_sum': sum(
            list(pu_results.filter(party_abbreviation=party).values_list('party_score', flat=True))),
                             'lg_result': lga_results})
    return render(request, 'local_government_result.html',
                  {'results_list': results_list, 'local_government': local_government_object})


@csrf_exempt
def result_upload(request):
    if request.method == 'POST':
        print(request.POST)
        form = ResultUploadForm(request.POST)
        try:
            if form.is_valid():
                cd = form.cleaned_data
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            AnnouncedPuResults.objects.create(**cd, user_ip_address=ip)

            return JsonResponse("Successful", safe=False)
        except Exception as e:
            print(e)
            return JsonResponse("Failed", safe=False)

    return render(request, 'result_upload.html')


def not_found(request):
    return render(request, 'not_found.html')
