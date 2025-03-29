from django.contrib import admin
from .models import reg_form_us, reg_form_ch, foodpost, Review, Orders  # Import models

admin.site.register(reg_form_us)
admin.site.register(reg_form_ch)
admin.site.register(foodpost)
admin.site.register(Review)
admin.site.register(Orders)