from django.urls import include, path
from listings import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('browseall/', views.browseall, name='browseall'),
    path('listrental/', views.list_rental, name='listrental'),
    path('editrental/<int:rental_id>/', views.edit_rental, name='editrental'),
    path('deleterental/<int:rental_id>/', views.delete_rental, name='deleterental'),
    path('showdetails/<int:rental_id>/', views.rental_details, name='rental_details'),
    path('profile/', views.viewprofile, name='viewprofile'),
    path('editprofile/', views.editprofile, name='editprofile'),
    path('yourrentals/', views.userrentals, name='userrentals'),
    path('search/', views.search_rentals, name='rental_search'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
