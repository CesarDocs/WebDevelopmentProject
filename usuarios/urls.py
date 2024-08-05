from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'usuarios'

urlpatterns = [
    #PARA EL USUARIO EN GENERAL
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),
    path('aviso-privacidad/', views.aviso_privacidad, name='aviso_privacidad'), 
    path('perfil/', views.perfil_view, name='perfil'),
    path('accounts/password_reset/', views.password_reset_custom, name='password_reset_custom'),

    #EMAIL
    
    #PARA EL ALUMNO
    path('home_alumno/', views.home_alumno, name='home_alumno'),
    path('alumno/calificaciones/', views.ver_calificaciones_alumno, name='ver_calificaciones_alumno'),
    
    
    #PARA EL PROFESOR
    path('home_profesor/', views.home_profesor, name='home_profesor'),
    path('profesor/modificar_calificaciones/', views.modificar_calificaciones_profesor, name='modificar_calificaciones_profesor'),

    #PARA EL ADMINISTRADOR
    path('home_admin/', views.home_admin, name='home_admin'),
    path('user_list/', views.catalogo_usuarios, name='user_list'), 
    path('modificar-usuario/<int:user_id>/', views.modificar_usuario, name='modificar_usuario'),
    path('eliminar-usuario/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('registrar/', views.registrar_usuario, name='registrar_usuario'),
    path('registro_exitoso/<str:username>/<str:password>/', views.registro_exitoso, name='registro_exitoso'),
    path('asignar_grupo_alumno/', views.asignar_grupo_alumno, name='asignar_grupo_alumno'),
    path('asignar_materia_grupo_profesor/', views.asignar_materia_grupo_profesor, name='asignar_materia_grupo_profesor'),
] 
