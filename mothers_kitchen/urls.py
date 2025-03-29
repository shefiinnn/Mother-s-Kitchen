
from django.contrib import admin
from django.urls import path
from mothers_kitchen import settings
import app1.views
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/',app1.views.Login,name='login'),
    path('',app1.views.home,name='home'),
    path('reg_form_user/',app1.views.reg_form_user,name='reg_form_user'),
    path('reg_form_chef/',app1.views.reg_form_chef,name='reg_form_chef'),
    path('chefhm/',app1.views.chefhm,name="chefhm"),
    path('postfood/',app1.views.postfood,name="postfood"),
    path('chef-profile/',app1.views.chef_profile, name='chef_profile'),
    path('edit-chef-profile/', app1.views.edit_chef_profile, name='edit_chef_profile'),
    path('change_password',app1.views.change_password,name="change_password"),
    path('change_user_password',app1.views.change_user_password,name="change_user_password"),
    path('edit_food/<int:food_id>/',app1.views.edit_food, name='edit_food'),
    path('delete-food/<int:food_id>/',app1.views.delete_food, name="delete_food"),
    path('userhm/',app1.views.userhm,name="userhm"),
    path('user_profile',app1.views.user_profile,name="user_profile"),
    path('edit_user_profile',app1.views.edit_user_profile,name="edit_user_profile"),
    path('search-suggestions', app1.views.search_suggestions, name='search_suggestions'),
    path('food_details/<int:food_id>/', app1.views.food_details, name='food_details'),
    path('place_order/<int:food_id>/', app1.views.place_order, name='place_order'),
    path('order_page/', app1.views.order_page, name='order_page'),
    path('cancel_order/<int:order_id>/', app1.views.cancel_order, name='cancel_order'),
    path('chef_orders/',app1.views.chef_orders, name='chef_orders'),
    path("update_order_status/<int:order_id>/", app1.views.update_order_status, name="update_order_status"),
    path('initiate_payment/<int:food_id>/', app1.views.initiate_payment, name='initiate_payment'),
    path('payment/callback/', app1.views.payment_callback, name='payment_callback'),
    path("chef/reviews/", app1.views.chef_reviews, name="chef_reviews"),
    path("admin_home/", app1.views.admin_home, name="admin_home"),
    path("delete_user/<int:user_id>/", app1.views.delete_user, name="delete_user"),
    path("delete_chef/<int:chef_id>/", app1.views.delete_chef, name="delete_chef"),
    path("delete_food/<int:food_id>/", app1.views.delete_food, name="delete_food"),
    path("delete_category/<str:category>/", app1.views.delete_category, name="delete_category"),
    path("report_to_admin/",app1.views.report_to_admin, name="report_to_admin"),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
