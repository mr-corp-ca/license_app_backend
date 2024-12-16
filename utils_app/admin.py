from django.contrib import admin

from utils_app.models import Province, City, Location, Radius

# Register your models here.

@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']
    search_fields = ('name', )
    ordering = ('-created_at',)

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['id', 'province', 'name', 'created_at']
    search_fields = ('name', 'province__name')
    ordering = ('-created_at',)


admin.site.register(Radius)

admin.site.register(Location)