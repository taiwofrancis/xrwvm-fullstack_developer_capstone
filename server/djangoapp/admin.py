from django.contrib import admin
from .models import CarMake, CarModel

# Show CarModel rows inline (inside CarMake edit page)
class CarModelInline(admin.StackedInline):
    model = CarModel
    extra = 1  # how many empty CarModel forms to show by default

# How CarModel itself appears in the admin list
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'car_make', 'type', 'year')
    list_filter = ('car_make', 'type', 'year')
    search_fields = ('name', 'car_make__name')

# How CarMake appears in admin, with inline CarModels
class CarMakeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    inlines = [CarModelInline]

# Finally register both models with their admins
admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel, CarModelAdmin)
