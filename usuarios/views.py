from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .decorators import user_is
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from .forms import PerfilForm, UserForm, CustomLoginForm, RegistroPerfilForm, ContactoForm, CambioContrasenaForm, RecuperacionContrasenaForm, CalificacionForm
from django.contrib.auth.models import User
from .models import Perfil, Calificacion, Alumno, Maestro
from django.contrib.auth import authenticate, login as auth_login
import random, string
from django import forms


####
          ##HOME##
####

def home(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            perfil_usuario = Perfil.objects.get(user=user)
            if perfil_usuario.tipo_usuario == 'estudiante':
                return redirect('usuarios:home_alumno')
            elif perfil_usuario.tipo_usuario == 'profesor':
                return redirect('usuarios:home_profesor')
            elif perfil_usuario.tipo_usuario == 'administrador':
                return redirect('usuarios:home_admin')
            else:
                return redirect('usuarios:login')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = CustomLoginForm()

    return render(request, 'registration/login.html', {'form': form})

def acceso_denegado(request):
    return render(request, 'error.html')

@login_required
@user_is('estudiante')
def home_alumno(request):
    return render(request, 'alumnos/home_alumnos.html')

@login_required
@user_is('profesor')
def home_profesor(request):
    return render(request, 'profesores/home_profesores.html')

@login_required
@user_is('administrador')
def home_admin(request):
    return render(request, 'administradores/home_admin.html')


####
          ##LOGOUT##
####

def logout_view(request):
    logout(request)
    return redirect('usuarios:login')


####
          ##HCATALOGO DE USUARIOS##
####
@login_required
@user_is('administrador')
def catalogo_usuarios(request):
    perfiles = Perfil.objects.all() 
    context = {
        'perfiles': perfiles
    }
    return render(request, 'administradores/catalogo_users.html', context)


####
          ##CONFIRMAR ELIMINACIÓN##
####
@login_required
@user_is('administrador')
def eliminar_usuario(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('usuarios:user_list')
    return render(request, 'administradores/confirmar_eliminacion.html', {'user': user})


####
          ##MODIFICAR USUARIO##
####
@login_required
@user_is('administrador')
def modificar_usuario(request, user_id):
    user = get_object_or_404(User, id=user_id)
    perfil = get_object_or_404(Perfil, user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        perfil_form = PerfilForm(request.POST, instance=perfil)
        if user_form.is_valid() and perfil_form.is_valid():
            user_form.save()
            perfil_form.save()
            return redirect('usuarios:user_list')
    else:
        user_form = UserForm(instance=user)
        perfil_form = PerfilForm(instance=perfil)

    context = {
        'user_form': user_form,
        'perfil_form': perfil_form
    }
    return render(request, 'administradores/modificar_usuario.html', context)


####
          ##AVISO DE PRIVACIDAD##
####
def aviso_privacidad(request):
    return render(request, "registration/Aviso_privacidad.html")



####
          ##pARA EL REGISTRO DE USUARIO##
####
def generar_nombre_usuario(primer_nombre, primer_apellido, segundo_apellido, fecha_nacimiento):
    return (primer_nombre[:2] + primer_apellido[:2] + segundo_apellido[:2] + fecha_nacimiento.strftime('%d%m%Y')).lower()

def generar_contraseña():
    caracteres = string.ascii_letters + string.digits + string.punctuation
    while True:
        contraseña = ''.join(random.choice(caracteres) for _ in range(8))
        if (any(c.islower() for c in contraseña) and
            any(c.isupper() for c in contraseña) and
            any(c.isdigit() for c in contraseña) and
            any(c in string.punctuation for c in contraseña)):
            break
    return contraseña

@login_required
@user_is('administrador')
def registrar_usuario(request):
    if request.method == 'POST':
        form = RegistroPerfilForm(request.POST)
        if form.is_valid():
            perfil_data = form.cleaned_data
            nombre_usuario = generar_nombre_usuario(
                perfil_data['primer_nombre'], perfil_data['primer_apellido'], 
                perfil_data['segundo_apellido'], perfil_data['fecha_nacimiento']
            )
            contraseña = generar_contraseña()

            user = User(username=nombre_usuario)
            user.set_password(contraseña)
            user.save()

            perfil = Perfil.objects.create(
                user=user,
                primer_nombre=perfil_data['primer_nombre'],
                segundo_nombre=perfil_data.get('segundo_nombre', ''),
                primer_apellido=perfil_data['primer_apellido'],
                segundo_apellido=perfil_data.get('segundo_apellido', ''),
                email=perfil_data['email'],
                telefono=perfil_data['telefono'],
                tipo_usuario=perfil_data['tipo_usuario'],
                fecha_nacimiento=perfil_data['fecha_nacimiento']
            )

            perfil.save()

            # Redirigir a la página de éxito con el nombre de usuario y la contraseña
            return redirect('usuarios:registro_exitoso', username=nombre_usuario, password=contraseña)
    else:
        form = RegistroPerfilForm()

    return render(request, 'registration/registro.html', {'form': form})

@login_required
@user_is('administrador')
def registro_exitoso(request, username, password):
    return render(request, 'registration/registro_exitoso.html', {'username': username, 'password': password})


@login_required
def perfil_view(request):
    user = request.user
    perfil = user.perfil

    if request.method == 'POST':
        if 'modificar_contacto' in request.POST:
            contacto_form = ContactoForm(request.POST, instance=user)
            if contacto_form.is_valid():
                contacto_form.save()
                messages.success(request, 'Información de contacto actualizada exitosamente.')
                return redirect('usuarios:perfil')
        elif 'cambiar_contrasena' in request.POST:
            contrasena_form = CambioContrasenaForm(request.POST)
            if contrasena_form.is_valid():
                password_actual = contrasena_form.cleaned_data['password_actual']
                nueva_password = contrasena_form.cleaned_data['nueva_password']
                
                if not user.check_password(password_actual):
                    contrasena_form.add_error('password_actual', 'La contraseña actual es incorrecta.')
                else:
                    user.set_password(nueva_password)
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, 'Contraseña cambiada exitosamente.')
                    return redirect('usuarios:perfil')
    else:
        contacto_form = ContactoForm(instance=user, initial={
            'telefono': perfil.telefono,
            'email': user.email,
        })
        contrasena_form = CambioContrasenaForm()

    return render(request, 'registration/perfil.html', {
        'contacto_form': contacto_form,
        'contrasena_form': contrasena_form,
    })


def password_reset_custom(request):
    if request.method == 'POST':
        form = RecuperacionContrasenaForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            nueva_password = form.cleaned_data.get('nueva_password')
            try:
                user = User.objects.get(username=username)
                user.set_password(nueva_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Contraseña cambiada exitosamente.')
                return redirect('usuarios:login')
            except User.DoesNotExist:
                form.add_error('username', 'El usuario no existe.')
    else:
        form = RecuperacionContrasenaForm()

    return render(request, 'registration/password_reset_custom.html', {'form': form})


@login_required
@user_is('estudiante')
def ver_calificaciones_alumno(request):
    calificaciones = Calificacion.objects.filter(alumno__perfil=request.user.perfil)
    return render(request, 'alumnos/ver_calificaciones.html', {'calificaciones': calificaciones})


@login_required
@user_is('profesor')
def modificar_calificaciones_profesor(request):
    if request.method == 'POST':
        form = CalificacionForm(request.POST)
        if form.is_valid():
            calificacion_id = form.cleaned_data.get('id')
            calificacion = get_object_or_404(Calificacion, id=calificacion_id)
            if calificacion.can_modify(request.user):
                calificacion.calificacion1 = form.cleaned_data['calificacion1']
                calificacion.calificacion2 = form.cleaned_data['calificacion2']
                calificacion.calificacion3 = form.cleaned_data['calificacion3']
                calificacion.save()
                return redirect('profesor:modificar_calificaciones_profesor')
            else:
                raise PermissionDenied("No tienes permiso para modificar esta calificación.")
    else:
        # En caso de GET, simplemente mostramos la tabla
        calificaciones = Calificacion.objects.filter(materia__perfil=request.user.perfil)
        form = CalificacionForm()
    
    return render(request, 'profesores/modificar_calificaciones.html', {'calificaciones': calificaciones, 'form': form})

@login_required
@user_is('administrador')
def asignar_grupo_alumno(request):
    alumnos = Alumno.objects.all()

    if request.method == 'POST':
        for alumno_id in request.POST.getlist('alumno_id'):
            alumno = get_object_or_404(Alumno, id=alumno_id)
            grupo = request.POST.get(f'grupo_{alumno_id}')
            if grupo:
                alumno.grupo = grupo
                alumno.save()
        return redirect('usuarios:asignar_grupo_alumno')

    return render(request, 'administradores/asignar_grupo_alumno.html', {'alumnos': alumnos})


@login_required
@user_is('administrador')
def asignar_materia_grupo_profesor(request):
    maestros = Maestro.objects.all()

    if request.method == 'POST':
        for maestro_id in request.POST.getlist('maestro_id'):
            maestro = get_object_or_404(Maestro, id=maestro_id)
            materia = request.POST.get(f'materia_{maestro_id}')
            grupo = request.POST.get(f'grupo_{maestro_id}')
            if materia:
                maestro.materia = materia
            if grupo:
                maestro.grupo = grupo
            maestro.save()
        return redirect('usuarios:asignar_materia_grupo_profesor')

    return render(request, 'administradores/asignar_materia_grupo_profesor.html', {'maestros': maestros})

