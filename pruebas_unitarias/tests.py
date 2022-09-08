import email
import os
from ssl import _PasswordType
from urllib import response
from django import setup

os.environ.setdefault("DJANGO_SETTINGS_MODULE","gestion_proyectos_agile.settings")
setup()

# Create your tests here.
from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, User

from usuarios.models import PermisoProyecto, RolSistema
from proyectos.models import Proyecto
from usuarios.views import listar_proyectos, vista_equipo
from usuarios.models import RolProyecto, Usuario
from phonenumber_field.modelfields import PhoneNumber
from proyectos.views import cancelar_proyecto, proyectos,crear_proyecto, editar_proyecto, roles_proyecto, crear_rol_proyecto,ver_rol_proyecto
from django.forms import forms


class UsuariosTests(TestCase):
    """
    Pruebas unitarias relacionadas a la creacion de usuarios.
    """

    def test_create_user(self):
        """
        Prueba la creación de usuarios normales
        """
        User = get_user_model()
        user = User.objects.create_user(
            email='normal@user.com', password='foo')
        self.assertEqual(user.email, 'normal@user.com')
        self.assertTrue(user.is_active)

        # Verificamos que se trata de un usuario normal
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        # Verificamos que se exige correo y contraseña
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(TypeError):
            User.objects.create_user(email='')
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password="foo")

    def test_create_superuser(self):
        """
        Prueba la creación de superusuarios
        """
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            email='super@user.com', password='foo')
        self.assertEqual(admin_user.email, 'super@user.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='super@user.com', password='foo', is_superuser=False)

    def test_crear_primer_admin(self):
        """
        Prueba que el primer usuario creado se vuelve admin
        """
        Usuario = get_user_model()
        Usuario.objects.all().delete()
        self.assertEqual(Usuario.objects.all().count(), 0, "No se pudo limpiar la base de datos")
        Usuario.objects.create_user(email='normal@user.com', password='foo')
        rol_admin, _ = RolSistema.objects.get_or_create(nombre='gpa_admin')
        self.assertEqual(Usuario.objects.filter(roles_sistema__id=rol_admin.id).count(), 1)
    

class MiembrosRolesTest(TestCase):
    """
    Pruebas unitarias relacionadas al manejo de roles y miembros en proyectos
    """

    def test_listar_proyectos(self):
        request_factory = RequestFactory()
        request = request_factory.post('/usuarios/equipo/')
        request.user = AnonymousUser()
        response = listar_proyectos(request)
        self.assertEqual(response.status_code, 401,
                         'La respuesta no fue un estado HTTP 401 a un usuario no autorizado')
    
    
    def test_vizualizar_proyecto(self):
        request_factory = RequestFactory()
        request = request_factory.post('/usuarios/equipo/')
        usuarioTest = Usuario(
            username="test", email='normal@user.com', password='foo')
        master = Usuario(username="master",
                         email='master@user.com', password='foo')
        usuarioTest.save()
        master.save()

        proyectoTest = Proyecto(nombre="proyecto Test", scrumMaster=master)
        proyectoTest.save()

        scrum = RolProyecto(nombre="Scrum Master", proyecto=proyectoTest)
        rolTest = RolProyecto(nombre="rol test", proyecto=proyectoTest)
        scrum.save()
        rolTest.save()
        master.roles_proyecto.add(scrum)

        request = request_factory.post(f'/usuarios/equipo/{proyectoTest.id}')
        request.user = usuarioTest
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 403,
                         'La respuesta no fue un estado HTTP 403 a un usuario no autorizado para esta operacion')


    def test_agregar_miembro_proyecto(self):
        """
        Prueba de la vista de agregar miembro de un proyecto
        """
        request_factory = RequestFactory()
        request = request_factory.post('/usuarios/equipo/')
        usuarioTest = Usuario(
            username="test", email='normal@user.com', password='foo')
        master = Usuario(username="master",
                         email='master@user.com', password='foo')
        usuarioTest.save()
        master.save()

        proyectoTest = Proyecto(nombre="proyecto Test", scrumMaster=master)
        proyectoTest.save()

        scrum = RolProyecto(nombre="Scrum Master", proyecto=proyectoTest)
        rolTest = RolProyecto(nombre="rol test", proyecto=proyectoTest)
        scrum.save()
        rolTest.save()
        master.roles_proyecto.add(scrum)

        request = request_factory.post(f'/usuarios/equipo/{proyectoTest.id}', data={
            'usuario_a_agregar': usuarioTest.email,
            'roles_agregar': rolTest.id,
            'hidden_action': 'agregar_miembro_proyecto'
        })
        request.user = usuarioTest
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 403,
                         'La respuesta no fue un estado HTTP 403 a un usuario no autorizado para esta operacion')

        request = request_factory.post(f'/usuarios/equipo/{proyectoTest.id}', data={
            'usuario_a_agregar': '',
            'roles_agregar': rolTest.id,
            'hidden_action': 'agregar_miembro_proyecto'
        })
        request.user = master
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 422,
                         'La respuesta no fue un estado HTTP 422 ante un usuario que no existe')

        request = request_factory.post(f'/usuarios/equipo/{proyectoTest.id}', data={
            'usuario_a_agregar': usuarioTest.email,
            'roles_agregar': rolTest.id,
            'hidden_action': 'agregar_miembro_proyecto'
        })
        request.user = master
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 302,
                         'La respuesta no fue un estado HTTP 302 ante una presunta operacion exitosa')
        self.assertTrue(proyectoTest in usuarioTest.equipo.all(),
                        'El usuario no pertenece al proyecto')
        self.assertTrue(rolTest in usuarioTest.roles_proyecto.all(),
                        'El usuario no tiene el rol asignado en el proyecto')

    def test_eliminar_miembro_proyecto(self):
        """
        Prueba de la vista de eliminar miembro de un proyecto
        """
        request_factory = RequestFactory()
        request = request_factory.post('usuarios/equipo/')

        usuarioTest = Usuario(
            username="test", email='normal@user.com', password='foo')
        master = Usuario(username="master",
                         email='master@user.com', password='foo')
        usuarioTest.save()
        master.save()

        proyectoTest = Proyecto(nombre="proyecto Test", scrumMaster=master)
        proyectoTest.save()

        scrum = RolProyecto(nombre="Scrum Master", proyecto=proyectoTest)
        rolTest = RolProyecto(nombre="rol test", proyecto=proyectoTest)
        scrum.save()
        rolTest.save()
        master.roles_proyecto.add(scrum)

        master.equipo.add(proyectoTest)
        usuarioTest.equipo.add(proyectoTest)
        usuarioTest.roles_proyecto.add(rolTest)

        request = request_factory.post(f'/usuarios/equipo/{proyectoTest.id}', data={
            'usuario_a_eliminar': usuarioTest.email,
            'hidden_action': 'eliminar_miembro_proyecto'
        })
        request.user = usuarioTest
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 403,
                         'La respuesta no fue un estado HTTP 403 a un usuario no autorizado para esta operacion')

        request = request_factory.post(f'/usuarios/equipo/{proyectoTest.id}', data={
            'usuario_a_eliminar': '',
            'hidden_action': 'eliminar_miembro_proyecto'
        })
        request.user = master
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 422,
                         'La respuesta no fue un estado HTTP 422 ante un usuario que no existe')

        request = request_factory.post(f'/usuarios/equipo/{proyectoTest.id}', data={
            'usuario_a_eliminar': usuarioTest.email,
            'hidden_action': 'eliminar_miembro_proyecto'
        })
        request.user = master
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 302,
                         'La respuesta no fue un estado HTTP 302 ante una presunta operacion exitosa')
        self.assertFalse(proyectoTest in usuarioTest.equipo.all(),
                         'El usuario pertenece al proyecto')
        self.assertFalse(rolTest in usuarioTest.roles_proyecto.all(),
                         'El usuario tiene el rol asignado en el proyecto')

    def test_asignar_rol_proyecto(self):
        """
        Prueba de la vista de asignar rol de proyecto a un miembro
        """
        request_factory = RequestFactory()
        request = request_factory.post('usuarios/equipo')

        usuarioTest = Usuario(username="test", email='normal@user.com', password='foo')
        master = Usuario(username="master", email='master@user.com', password='foo')
        usuarioTest.save()
        master.save()

        proyectoTest = Proyecto(nombre="proyecto Test", scrumMaster=master)
        proyectoTest.save()

        scrum = RolProyecto(nombre="Scrum Master", proyecto=proyectoTest)
        rolTest = RolProyecto(nombre="rol test", proyecto=proyectoTest)
        scrum.save()
        rolTest.save()
        master.roles_proyecto.add(scrum)

        request = request_factory.post(f'/usuarios/equipo/{proyectoTest.id}', data={
            'usuario_a_cambiar_rol': usuarioTest.username,
            f'roles{usuarioTest.username}': rolTest.id,
            'hidden_action': 'asignar_rol_proyecto'
        })
        request.user = usuarioTest
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 403,
                         'La respuesta no fue un estado HTTP 403 a un usuario no autorizado para esta operacion')

        request = request_factory.post(f'/usuarios/equipo/{proyectoTest.id}', data={
            'usuario_a_cambiar_rol': '',
            f'roles{usuarioTest.username}': rolTest.id,
            'hidden_action': 'asignar_rol_proyecto'
        })
        request.user = master
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 422,
                         'La respuesta no fue un estado HTTP 422 ante un usuario que no existe')

        request = request_factory.post(f'/usuarios/equipo/{proyectoTest.id}', data={
            'usuario_a_cambiar_rol': usuarioTest.email,
            f'roles{usuarioTest.email}': rolTest.id,
            'hidden_action': 'asignar_rol_proyecto'
        })
        request.user = master
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 302,
                         'La respuesta no fue un estado HTTP 302 ante una presunta operacion exitosa')
        self.assertTrue(rolTest in usuarioTest.roles_proyecto.all(),
                        'El usuario tiene el rol asignado en el proyecto')

    def test_eliminar_rol_proyecto(self):
        """
        Prueba de la vista de desasignar rol de proyecto a un miembro
        """
        request_factory = RequestFactory()
        request = request_factory.post('usuarios/equipo')

        usuarioTest = Usuario(username="test", email='normal@user.com', password='foo')
        master = Usuario(username="master",
                         email='master@user.com', password='foo')
        usuarioTest.save()
        master.save()

        proyectoTest = Proyecto(nombre="proyecto Test", scrumMaster=master)
        proyectoTest.save()

        scrum = RolProyecto(nombre="Scrum Master", proyecto=proyectoTest)
        rolTest = RolProyecto(nombre="rol test", proyecto=proyectoTest)
        scrum.save()
        rolTest.save()
        master.roles_proyecto.add(scrum)
        usuarioTest.roles_proyecto.add(rolTest)

        request = request_factory.post(f'/usuarios/equipo/{proyectoTest.id}', data={
            'usuario_a_sacar_rol': usuarioTest.email,
            'rol_id': rolTest.id,
            'hidden_action': 'eliminar_rol_proyecto'
        })
        request.user = usuarioTest
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 403,
                         'La respuesta no fue un estado HTTP 403 a un usuario no autorizado para esta operacion')

        request = request_factory.post(f'/usuarios/equipo/{proyectoTest.id}', data={
            'usuario_a_cambiar_rol': '',
            'rol_id': rolTest.id,
            'hidden_action': 'eliminar_rol_proyecto'
        })
        request.user = master
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 422,
                         'La respuesta no fue un estado HTTP 422 ante un usuario que no existe')

        request = request_factory.post(f'/usuarios/equipo/{proyectoTest.id}', data={
            'usuario_a_sacar_rol': usuarioTest.email,
            'rol_id': rolTest.id,
            'hidden_action': 'eliminar_rol_proyecto'
        })
        request.user = master
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 302,
                         'La respuesta no fue un estado HTTP 302 ante una presunta operacion exitosa')
        self.assertFalse(rolTest in usuarioTest.roles_proyecto.all(),
                         'El usuario tiene el rol asignado en el proyecto')


class PerfilTests(TestCase):
    def test_login(self):
        """
        Prueba que el login funciona.
        - usuarios pueden tener campos esperados
        - login usa correo
        """
        self.user = get_user_model().objects.create_user(email='testemail@example.com', password='A123B456c.',
                                                         avatar_url='avatar@example.com', direccion='Calle 1 # 2 - 3', telefono=PhoneNumber.from_string('0983 738040'))
        login = self.client.login(email='testemail@example.com', password='')
        self.assertFalse(login, "Usuario no se puede loguear con contraseña vacia")
        login = self.client.login(email='testemail@example.com', password='A123B456c.')
        self.assertTrue(login, "Usuario se puede loguear con email y contraseña correctos")

    def test_ver_perfil(self):
        res = self.client.get('/perfil/')
        self.assertNotContains(res, '<form action="/perfil/" method="post">', 1,
                               401, "Usuario no loguedao debe iniciar sesion para ver su perfil")
        self.client.logout()

    def test_ver_perfil(self):
        self.client.login(email='testemail@example.com', password='A123B456c.')
        res = self.client.get('/perfil/')
        self.assertContains(res, '<form action="/perfil/" method="post">', 1,
                            200, "Usuario loguedao puede ver su perfil")
        self.client.logout()

    def test_logout(self):
        """
        Prueba que el logout funciona
        """
        self.user = get_user_model().objects.create_user(email='testemail@example.com', password='A123B456c.',
                                                         avatar_url='avatar@example.com', direccion='Calle 1 # 2 - 3', telefono=PhoneNumber.from_string('0983 738040'))
        self.client.login(email='testemail@example.com', password='A123B456c.')
        res = self.client.get('/perfil/')
        self.assertContains(res, '<form action="/perfil/" method="post">', 1,
                            200, "Usuario loguedao puede ver su perfil")

    def test_ver_perfil(self):
        """
        Prueba que el usuario puede ver su perfil correcto
        """
        self.user = get_user_model().objects.create_user(email='testemail@example.com', password='A123B456c.',
                                                         avatar_url='avatar@example.com', direccion='Calle 1 # 2 - 3', telefono=PhoneNumber.from_string('0983 738040'))
        self.client.login(email='testemail@example.com', password='A123B456c.')
        res = self.client.get('/perfil/')
        self.assertContains(res, 'testemail@example.com', 1, 200, "Usuario loguedao puede ver su perfil con email")
        self.assertContains(res, '0983 738040', 1, 200, "Usuario loguedao puede ver su perfil con número de telefono")
        self.assertContains(res, 'Calle 1 # 2 - 3', 1, 200, "Usuario loguedao puede ver su perfil con direccion")
        self.assertContains(res, 'avatar@example.com', None, 200, "Usuario loguedao puede ver su perfil con foto")

    def test_editar_perfil(self):
        """
        Prueba que el usuario puede editar su perfil correcto
        """
        self.user = get_user_model().objects.create_user(email='testemail@example.com', password='A123B456c.',
                                                         avatar_url='avatar@example.com', direccion='Calle 1 # 2 - 3', telefono=PhoneNumber.from_string('0983 738040'))
        self.client.login(email='testemail@example.com', password='A123B456c.')
        res = self.client.post("/perfil/", {'email': 'testemail2@example.com', 'first_name': 'TestUserFirst', 'last_name': 'TestUserLast',
                                            'avatar_url': 'avatar2@example.com', 'direccion': 'Calle 2 # 3 - 4', 'telefono': '0983 738041'}, follow=True)
        self.assertContains(res, 'testemail2@example.com', 1, 200,
                            "Usuario loguedao puede ver su perfil con email cambiado después de un post")
        self.assertContains(res, 'TestUserFirst', 3, 200,
                            "Usuario loguedao puede ver su perfil con nombre cambiado después de un post")
        self.assertContains(res, 'TestUserLast', 3, 200,
                            "Usuario loguedao puede ver su perfil con apellido cambiado después de un post")
        self.assertContains(res, '0983 738041', 1, 200,
                            "Usuario loguedao puede ver su perfil con número de telefono cambiado después de un post")
        self.assertContains(res, 'Calle 2 # 3 - 4', 1, 200,
                            "Usuario loguedao puede ver su perfil con direccion cambiado después de un post")
        self.assertContains(res, 'avatar2@example.com', 3, 200,
                            "Usuario loguedao puede ver su perfil con foto cambiado después de un post")


class ProyectoTests(TestCase):

    def test_ver_proyectos(self):
        """
        Prueba que el usuario puede ver los proyectos
        """
        request_factory = RequestFactory()
        request = request_factory.get('/proyectos/')
        request.user = AnonymousUser()
        response = proyectos(request)
        self.assertEqual(response.status_code, 401, "Usuario puede ver los proyectos pero no esta autenticado")
        
        #Creamos un usuario con roles del sistema Admin
        master = Usuario(username="master",
                         email='master@user.com', password='foo')
        master.save()
        RolSistema.objects.get(nombre="gpa_admin").usuario.add(master)
        
        #Creamos un usuario sin roles de admin
        user = Usuario(username="user",
                        email='user@user.com', password='foo')
        user.save()

        #Verificamos que el usuario sin de admin puede ver los proyectos
        request.user = user
        response = proyectos(request)
        self.assertEqual(response.status_code, 403, "Usuario puede ver los proyectos pero no tiene roles de gpa_admin")

        #Verificamos que el usuario puede ver los proyectos
        request.user = master
        response = proyectos(request)
        self.assertEqual(response.status_code, 200, "Usuario no puede ver los proyectos")
        



    def test_crear_proyecto(self):
        """
        Prueba que el usuario puede crear un proyecto
        """
        request_factory = RequestFactory()
        request = request_factory.post('/proyectos/crear/')
        request.user = AnonymousUser()
        response = crear_proyecto(request)
        self.assertEqual(response.status_code, 401, 'La respuesta no fue un estado HTTP 401 a un usuario no autorizado')
        
        #Verificar que gpa_admin puede crear proyectos
        usuarioTest = Usuario(
            username="test", email='normal@user.com', password='foo')
        master = Usuario(username="master",
                         email='master@user.com', password='foo')
        master.save()
        usuarioTest.save()

        RolSistema.objects.get(nombre="gpa_admin").usuario.add(master)
        
        request.user = usuarioTest
        response = crear_proyecto(request)
        self.assertEqual(response.status_code, 403, 'La respuesta no fue un estado HTTP 403 a un usuario sin permisos GPA_ADMIN')

        #Verfificamos la creacion de un proyecto
        request = request_factory.post('/proyectos/crear/', {'nombre': 'Proyecto de prueba', 'descripcion': 'Descripcion de prueba', 'scrum_master': master.id})
        request.user = master
        response = crear_proyecto(request)
        self.assertEqual(response.status_code, 200, 'La respuesta no fue un estado HTTP 200 de la creacion de un proyecto')

        #Verificamos que el proyecto se creo correctamente
        proyecto = Proyecto.objects.get(nombre='Proyecto de prueba')
        self.assertEqual(proyecto.nombre, 'Proyecto de prueba', 'El nombre del proyecto no es el correcto')
        self.assertEqual(proyecto.descripcion, 'Descripcion de prueba', 'La descripcion del proyecto no es la correcta')
        self.assertEqual(proyecto.scrumMaster, master, 'El scrum master del proyecto no es el correcto')
        self.assertEqual(proyecto.estado, 'Planificacion', 'El estado del proyecto no es el correcto')



    def test_editar_proyecto(self):
        """
        Prueba que el usuario puede editar un proyecto
        """
        #Iniciamos seccion con acceso de Admin
        master = Usuario(username="master",
                         email='master@user.com', password='foo')
        master.save()
        RolSistema.objects.get(nombre="gpa_admin").usuario.add(master)


        # Creamos un proyecto y lo guardamos en la base de datos 
        proyecto = Proyecto(nombre="Proyecto de prueba", descripcion="Descripcion de prueba", estado="Planificacion", scrumMaster=master)
        proyecto.save()

        # Creamos un usuario que no este logueado
        usuarioTest = Usuario(
            username="test",
            email='test@example.com',
            password='foo'
        )
        usuarioTest.save()

        #Creamos la solicitud
        request_factory = RequestFactory()
        request = request_factory.post(f'/proyectos/{proyecto.id}/editar')

        #Verficicamos un usuario no logueado
        request.user = AnonymousUser()
        response = editar_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 401, 'La respuesta no fue un estado HTTP 401 a un usuario no autenticado')
        
        #Verficicamos un usuario logueado sin permisos
        request.user = usuarioTest
        response = editar_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 403, 'La respuesta no fue un estado HTTP 403 a un usuario sin permisos')

        #Verficicamos la edicion correcta de un proyecto
        request  = request_factory.post(f'/proyectos/{proyecto.id}/editar', {'nombre': 'Proyecto de prueba 2', 'descripcion': 'Descripcion de prueba 2'})
        request.user = master
        response = editar_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 422, 'La respuesta no fue un estado HTTP 422 a una petición incorrecta')

        #Verficicamos la edicion correcta de un proyecto
        request  = request_factory.post(f'/proyectos/{proyecto.id}/editar', {'nombre': 'Proyecto de prueba 22', 'descripcion': 'Descripcion de prueba 2', 'estado': 'Planificacion', 'scrumMaster': master.id})
        request.user = master
        response = editar_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 422, 'La respuesta fue un estado HTTP 422 a una petición correcta')
        self.assertFalse(Proyecto.objects.filter(nombre="Proyecto de prueba 22").exists(), 'El proyecto no se edito correctamente')
        

    def test_cancelar_proyecto(self):
        """
        Prueba que el usuario puede cancelar un proyecto
        """
        
        #Creamos un usuario gpa_admin
        master = Usuario(username="master",
                         email='master@user.com', password='foo')
        master.save()
        RolSistema.objects.get(nombre="gpa_admin").usuario.add(master)

        #Creamos un proyecto de prueba
        proyecto = Proyecto(nombre="Proyecto de prueba", descripcion="Descripcion de prueba", estado="Planificacion", scrumMaster=master)
        proyecto.save()
        
        #Verificamos que un usuario no logueado no puede cancelar un proyecto
        request_factory = RequestFactory()
        request = request_factory.get(f'proyectos/cancelar/{proyecto.id}/')
        request.user = AnonymousUser()
        response = cancelar_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 401, 'La respuesta no fue un estado HTTP 401 a un usuario no autenticado')

        #Verificamos que un usuario sin permisos no puede cancelar un proyecto
        usuarioTest = Usuario(username="test",email='user@user.com', password='foo')
        usuarioTest.save()
        request.user = usuarioTest
        response = cancelar_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 403, 'La respuesta no fue un estado HTTP 403 a un usuario sin permisos')

        #Verificamos que un usuario con permisos puede cancelar un proyecto
        request = request_factory.post(f'proyectos/cancelar/{proyecto.id}/', {'nombre':'Proyecto de prueba'})
        request.user = master
        response = cancelar_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 200, 'La respuesta no fue un estado HTTP 200 a una petición incorrecta')
        
        #Verificamos que el proyecto se cancelo correctamente
        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEqual(proyecto.estado, 'Cancelado', 'El estado del proyecto al cancelar no es el correcto')

        #Verificamos que no se puede cancelar un proyecto cuando no tiene nombre correcto
        proyecto = Proyecto(nombre="PruebaCancelar", descripcion="Descripcion de prueba", estado="Planificacion", scrumMaster=master)
        proyecto.save()

        request = request_factory.post(f'proyectos/cancelar/{proyecto.id}/', {'nombre':'Proyecto de prueba 2'})
        request.user = master
        response = cancelar_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 422, 'La respuesta no fue un estado HTTP 422 a una petición incorrecta')
        #Verificamos que el proyecto no se cancelo
        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEqual(proyecto.estado, 'Planificacion', 'Se cancelo el proyecto por mas que introdujo un nombre incorrecto')


    def test_ver_roles_proyecto(self):
        """
        Prueba que el usuario puede ver la pantalla de los roles de un proyecto
        """
        #Creamos un usuario gpa_admin
        master = Usuario(username="master",
                         email='master@user.com', password='foo')
        master.save()
        RolSistema.objects.get(nombre="gpa_admin").usuario.add(master)

        #Verificamos que el usuario no logueado no puede ver los roles de un proyecto
        request_factory = RequestFactory()
        request = request_factory.get(f'proyectos/roles_proyecto/{master.id}/')
        request.user = AnonymousUser()
        response = roles_proyecto(request)
        self.assertEqual(response.status_code, 401, 'La respuesta no fue un estado HTTP 401 a un usuario no autenticado')

        #Verificamos que el usuario sin permisos no puede ver los roles de un proyecto
        usuarioTest = Usuario(username="test", email="test@user.com", password="foo")
        usuarioTest.save()
        request.user = usuarioTest
        response = roles_proyecto(request)
        self.assertEqual(response.status_code, 403, 'La respuesta no fue un estado HTTP 403 a un usuario sin permisos')
    
        #Verificamos que el usuario con permisos puede ver los roles de un proyecto
        request.user = master
        response = roles_proyecto(request)
        self.assertEqual(response.status_code, 200, 'La respuesta no fue un estado HTTP 200 a una petición correcta')

    def test_crear_rol_proyecto(self):
        """
        Prueba que el usuario puede crear un rol de proyecto opcion para admin
        """
        #Creamos un usuario gpa_admin
        master = Usuario(username="master",
                         email='master@user.com', password='foo')
        master.save()
        RolSistema.objects.get(nombre="gpa_admin").usuario.add(master)

        #Creamos un usuario normal
        usuarioTest = Usuario(username="test", email="test@user.com", password="foo")
        usuarioTest.save()

        #Creamos un rol de proyecto con un usuario no autenticado
        
        request_factory = RequestFactory()
        request = request_factory.post(f'proyectos/roles_proyecto/crear/', {
            'nombre':'Rol de prueba', 
            'descripcion':'Descripcion de prueba',
            'permisos': [1,2,3]
            })
        request.user = AnonymousUser()
        response = crear_rol_proyecto(request)
        self.assertEqual(response.status_code, 401, 'La respuesta no fue un estado HTTP 401 a un usuario no autenticado')
        
        #Creamos un rol de proyecto con un usuario sin permisos
        request.user = usuarioTest
        response = crear_rol_proyecto(request)
        self.assertEqual(response.status_code, 403, 'La respuesta no fue un estado HTTP 403 a un usuario sin permisos')

        #Creamos un rol de proyecto con un usuario con permisos
        request.user = master
        response = crear_rol_proyecto(request)
        self.assertEqual(response.status_code, 200, 'La respuesta no fue un estado HTTP 200 a una petición correcta')

    def test_ver_rol_de_proyecto(self):
        """
        Prueba que el usuario puede ver un rol de proyecto
        """
        #Creamos un usuario gpa_admin
        
        #Creamos un usuario gpa_admin
        master = Usuario(username="master",
                         email='master@user.com', password='foo')
        master.save()
        RolSistema.objects.get(nombre="gpa_admin").usuario.add(master)

        #Creamos un usuario normal
        usuarioTest = Usuario(username="test", email="test@user.com", password="foo")
        usuarioTest.save()
        
        #Creamos un rol de proyecto
        rol = RolProyecto(nombre="Rol de prueba", descripcion="Descripcion de prueba")
        rol.save()
        
        #Recuperamos el rol en la base de datos
        rol = RolProyecto.objects.get(nombre="Rol de prueba")

        #Verificamos que el usuario no logueado no puede ver un rol de proyecto
        request_factory = RequestFactory()
        request = request_factory.get(f'proyectos/roles_proyecto/{rol.id}/')
        request.user = AnonymousUser()
        response = ver_rol_proyecto(request, rol.id)
        self.assertEqual(response.status_code, 401, 'La respuesta no fue un estado HTTP 401 a un usuario no autenticado')

        #Verificamos que el usuario con permisos puede ver un rol de proyecto
        request.user = master
        response = ver_rol_proyecto(request, rol.id)
        self.assertEqual(response.status_code, 200, 'La respuesta no fue un estado HTTP 200 a una petición correcta')
        
        #Creamos un proyecto con el rol de proyecto
        proyecto = Proyecto(nombre="Proyecto de prueba", descripcion="Descripcion de prueba", estado="Planificacion", scrumMaster_id=usuarioTest.id)
        proyecto.save()
        
        #Obtenemos la id del proyecto
        proyecto = Proyecto.objects.get(nombre="Proyecto de prueba")

        #Creamos un usuario con rol Scrum Master
        usuarioTest = Usuario(username="test2", email="test@example.com", password="foo")
        usuarioTest.save()

        #Asignamos el rol de Scrum Master al usuario
        proyecto.scrumMaster = usuarioTest

        #Verificamos que el usuario con rol Scrum Master puede ver un rol de proyecto
        request.user = usuarioTest
        response = ver_rol_proyecto(request, rol.id)
        self.assertEqual(response.status_code, 200, 'La respuesta no fue un estado HTTP 200 a una petición correcta')
    
    def test_modificar_rol_proyecto(self):
        """
        Prueba que el usuario puede modificar un rol de proyecto
        """
        #Creamos un usuario gpa_admin
        master = Usuario(username="master", email="master@master.com", password="foo")
        master.save()
        RolSistema.objects.get(nombre="gpa_admin").usuario.add(master)

        #Creamos un usuario normal
        usuarioTest = Usuario(username="test", email="test@user.com", password="foo")
        usuarioTest.save()

        #Creamos un usuario que sera el Scrum Master del proyecto
        usuarioTest2 = Usuario(username="test2", email="test2@test.com", _Password="foo")
        usuarioTest2.save()

        #Creamos un proyecto de ejemplo
        proyecto = Proyecto(nombre="Proyecto de prueba", descripcion="Descripcion de prueba", estado="Planificacion", scrumMaster_id=usuarioTest2.id)

        #Creamos un rol de proyecto
        rol = RolProyecto(nombre="Rol de prueba", descripcion="Descripcion de prueba", proyecto=proyecto)
        rol.save()

        
