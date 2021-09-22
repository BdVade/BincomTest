from .models import Lga


def local_governments(request):
    lgas = Lga.objects.all()
    return {
        'lgas': lgas
    }
