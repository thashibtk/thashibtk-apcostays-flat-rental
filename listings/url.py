from django.urls import include, path
from listings import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('signup_success/', views.signup_success, name='signup_success'),
    path('logout/', views.logout_view, name='logout'),
    path('browseall/', views.browseall, name='browseall'),
    path('listrental/', views.list_rental, name='listrental'),
    path('rental_success/', views.rental_success, name='rental_success'),
    path('showdetails/', views.rental_details, name='showdetails'),
    path('rental/<int:rental_id>/', views.rental_details, name='rental_details'),
    path('profile/', views.viewprofile, name='viewprofile'),
    path('editprofile/', views.editprofile, name='editprofile'),
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)