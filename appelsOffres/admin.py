from django.contrib import admin

# Register your models here.
from .models import fonction
from .models import service
from .models import Annonce
from .models import Lot
from .models import ImageScrol
from .models import categorie
from .models import Favoris
from .models import Devis
from .models import assoDevis

admin.site.register(fonction)
admin.site.register(service)
admin.site.register(Annonce)
admin.site.register(Lot)
admin.site.register(ImageScrol)
admin.site.register(categorie)
admin.site.register(Favoris)
admin.site.register(Devis)
admin.site.register(assoDevis)