from django.urls import include, path
from listings import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('signup_success/', views.signup_success, name='signup_success'),
    path('logout/', views.logout_view, name='logout'),
    path('browseall/', views.browseall, name='browseall'),
    path('listrental/', views.listrental, name='listrental'),
    path('showdetails/', views.showdetails, name='showdetails'),
    path('profile/', views.viewprofile, name='profile'),
]