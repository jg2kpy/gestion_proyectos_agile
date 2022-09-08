import email
import os
from django import setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gestion_proyectos_agile.settings")
setup()

# Create your tests here.
from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, User
from django.test.client import RequestFactory
from usuarios.views import *
from usuarios.models import PermisoProyecto, RolSistema
from proyectos.models import Proyecto
from usuarios.views import listar_proyectos, vista_equipo
from usuarios.models import RolProyecto, Usuario
from phonenumber_field.modelfields import PhoneNumber

from proyectos.views import cancelar_proyecto, crear_rol_a_proyecto, importar_rol, modificar_rol_proyecto, proyectos,crear_proyecto, editar_proyecto, roles_proyecto, crear_rol_proyecto,ver_rol_proyecto, ver_roles_asignados
from proyectos.views import eliminar_rol_proyecto as eliminar_rol_proyecto_view
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


class RolesGlobalesTests(TestCase):
    """
    Pruebas unitarias relacionadas al manejo de Roles Globales.
    """

    def test_crear_rol(self):
        """
        Prueba que se pueda crear el rol
        """
        self.user = get_user_model().objects.create_user(email='testemail@example.com', password='A123B456c.', username='test')
        self.client.login(email='testemail@example.com', password='A123B456c.')
        res = self.client.post('/rolesglobales/crear/',
                               data={'nombre': 'rol_global_test22', 'descripcion': 'Esto es un test'}, follow=True)
        self.assertContains(res, '<h5 class="rolEncontrado">rol_global_test22</h5>', 1, 200, "No recibe el nombre del rol correctamente")
        self.assertContains(res, 'Esto es un test', 1, 200, "No recibe la descripcion del rol correctamente")

    def test_visualizar_roles(self):
        """
        Prueba que visualicen correctamente los roles globales
        """
        self.user = get_user_model().objects.create_user(email='testemail@example.com', password='A123B456c.', username='test')
        self.client.login(email='testemail@example.com', password='A123B456c.', username='test')
        res = self.client.get('/rolesglobales/')
        self.assertContains(res, '<h5 class="rolEncontrado">', 1, 200, "No se carga correctamente la página")

    def test_eliminar_rol(self):
        """
        Prueba que se pueda eliminar un rol
        """
        self.user = get_user_model().objects.create_user(email='testemail@example.com', password='A123B456c.', username='test')
        self.client.login(email='testemail@example.com', password='A123B456c.', username='test')
        rolTest = RolSistema(nombre='test', descripcion='descripcion test')
        rolTest.save()
        res = self.client.post('/rolesglobales/', data={'accion': 'eliminar', 'nombre':'test'}, follow=True)
        self.assertContains(res, '<h5 class="rolEncontrado">test</h5>', 0, 200, "No se elimina el rol")

    def test_editar_rol(self):
        """
        Prueba que se pueda editar un rol
        """
        self.user = get_user_model().objects.create_user(email='testemail@example.com', password='A123B456c.', username='test')
        self.client.login(email='testemail@example.com', password='A123B456c.', username='test')
        rolTest = RolSistema(nombre='test', descripcion='descripcion test')
        rolTest.save()
        res = self.client.post(f'/rolesglobales/{rolTest.id}/editar/', data={
                            'nombre': 'rol_global_test_editado', 'descripcion': 'Esto es un test editado'}, follow=True)
        self.assertContains(res, '<h5 class="rolEncontrado">rol_global_test_editado</h5>', 1, 200, "No recibe el nombre del rol editado correctamente")
        self.assertContains(res, 'Esto es un test editado', 1, 200,
                            "No recibe la descripcion del rol editado correctamente")

    def test_vincular_rol(self):
        """
        Prueba que se pueda vincular un usuario a un rol
        """
        self.user = get_user_model().objects.create_user(email='testemail@example.com', password='A123B456c.', username='test')
        self.client.login(email='testemail@example.com', password='A123B456c.')
        rolTest = RolSistema(nombre='test', descripcion='descripcion test')
        rolTest.save()
        testuser = get_user_model().objects.create_user(email='testuser@example.com', password='A123B456c.', username='testuser')
        testuser.save()
        res = self.client.post(f'/rolesglobales/{rolTest.id}/usuarios/',
                               data={"usuarios": testuser.email, "vincular": "Vincular"}, follow=True)
        self.assertContains(res, 'Se ha vinculado el rol', 1, 200, "No se vincula correctamente el rol")

    def test_desvincular_rol(self):
        """
        Prueba que se pueda desvincular un usuario a un rol
        """
        self.user = get_user_model().objects.create_user(email='testemail@example.com', password='A123B456c.', username='test')
        self.client.login(email='testemail@example.com', password='A123B456c.')
        rolTest = RolSistema(nombre='test', descripcion='descripcion test')
        rolTest.save()
        testuser = get_user_model().objects.create_user(email='testuser@example.com', password='A123B456c.', username='testuser')
        testuser.save()
        self.client.post(f'/rolesglobales/{rolTest.id}/usuarios/',
                         data={"usuarios": testuser.email, "vincular": "Vincular"}, follow=True)
        res = self.client.post(f'/rolesglobales/{rolTest.id}/usuarios/',
                               data={"usuarios": testuser.email, "desvincular": "Desvincular"}, follow=True)
        self.assertContains(res, 'Se ha desvinculado el rol', 1, 200, "No se desvincula correctamente el rol")

class MiembrosRolesTest(TestCase):
    """
    Pruebas unitarias relacionadas al manejo de roles y miembros en proyectos
    """

    def test_listar_proyectos(self):
        """
        Prueba de la vista de listar proyectos
        """
        request_factory = RequestFactory()
        request = request_factory.get('/usuarios/equipo/')
        request.user = AnonymousUser()
        response = listar_proyectos(request)
        self.assertEqual(response.status_code, 401,
                         'La respuesta no fue un estado HTTP 401 a un usuario no autorizado')
    
    
    def test_get_visualizar_proyecto(self):
        """
        Prueba de la vista de visualizar gestion de miembros y roles de proyectos
        """
        request_factory = RequestFactory()

        usuario_no_miembro = Usuario(username="test", email='normal@user.com', password='foo')
        usuario_miembro = Usuario(username="master",email='master@user.com', password='foo')
        usuario_no_miembro.save()
        usuario_miembro.save()

        proyectoTest = Proyecto(nombre="proyecto Test", scrumMaster=usuario_miembro)
        proyectoTest.save()
        usuario_miembro.equipo.add(proyectoTest)
        
        request = request_factory.get(f'/usuarios/equipo/{proyectoTest.id}')
        request.user = AnonymousUser()
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 401,
                         'La respuesta no fue un estado HTTP 401 a un usuario no autorizado')

        request = request_factory.get(f'/usuarios/equipo/{proyectoTest.id}')
        request.user = usuario_miembro
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 200,
                         'La respuesta no fue un estado HTTP 200 a un usuario no autorizado para esta operacion')

        request = request_factory.get(f'/usuarios/equipo/{proyectoTest.id}')
        request.user = usuario_no_miembro
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 403,
                         'La respuesta no fue un estado HTTP 403 a un usuario no autorizado para esta operacion')
             
        proyectoTest.delete()
        
        request = request_factory.get(f'/usuarios/equipo/{proyectoTest.id}')
        request.user = usuario_miembro
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 404,
                         'La respuesta no fue un estado HTTP 404 ante una pagina que no existe')


    def test_agregar_miembro_proyecto(self):
        """
        Prueba de la vista de agregar miembro de un proyecto
        """
        request_factory = RequestFactory()

        usuarioTest = Usuario(username="test", email='normal@user.com', password='foo')
        master = Usuario(username="master",email='master@user.com', password='foo')
        usuarioTest.save()
        master.save()

        proyectoTest = Proyecto(nombre="proyecto Test", scrumMaster=master)
        proyectoTest.save()
        master.equipo.add(proyectoTest)

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

        usuarioTest = Usuario(username="test", email='normal@user.com', password='foo')
        master = Usuario(username="master", email='master@user.com', password='foo')
        usuarioTest.save()
        master.save()

        proyectoTest = Proyecto(nombre="proyecto Test", scrumMaster=master)
        proyectoTest.save()

        master.equipo.add(proyectoTest)
        usuarioTest.equipo.add(proyectoTest)

        scrum = RolProyecto(nombre="Scrum Master", proyecto=proyectoTest)
        rolTest = RolProyecto(nombre="rol test", proyecto=proyectoTest)
        scrum.save()
        rolTest.save()
        master.roles_proyecto.add(scrum)
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

        usuarioTest = Usuario(username="test", email='normal@user.com', password='foo')
        master = Usuario(username="master", email='master@user.com', password='foo')
        usuarioTest.save()
        master.save()

        proyectoTest = Proyecto(nombre="proyecto Test", scrumMaster=master)
        proyectoTest.save()

        usuarioTest.equipo.add(proyectoTest)
        master.equipo.add(proyectoTest)

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

        usuarioTest = Usuario(username="test", email='normal@user.com', password='foo')
        master = Usuario(username="master",email='master@user.com', password='foo')
        usuarioTest.save()
        master.save()

        proyectoTest = Proyecto(nombre="proyecto Test", scrumMaster=master)
        proyectoTest.save()

        master.equipo.add(proyectoTest)
        usuarioTest.equipo.add(proyectoTest)

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

        #Creamos un rol para el proyecto
        rolProyecto = RolProyecto(nombre="Rol de prueba en un proyecto", descripcion="Descripcion de prueba", proyecto=proyecto)
        rolProyecto.save()

        #Obtenemos rolProyecto de la base de datos
        rolProyecto = RolProyecto.objects.get(nombre="Rol de prueba en un proyecto")
        
        #Asignacion de Scrum Master al proyecto
        scrum = RolProyecto(nombre="Scrum Master", proyecto=proyecto)
        scrum.save()

        #Obtenemos la id del proyecto
        proyecto = Proyecto.objects.get(nombre="Proyecto de prueba")

        #Creamos un usuario con rol Scrum Master
        usuarioTest = Usuario(username="test2", email="test@example.com", password="foo")
        usuarioTest.save()

        #Asignamos el rol de Scrum Master al usuario
        proyecto.scrumMaster = usuarioTest
        proyecto.save()

        #Agregamos un usuarioTest al proyecto
        proyecto.usuario.add(usuarioTest)

        #Vinculamos el usuario al rol de Scrum Master
        scrum.usuario.add(usuarioTest)

        #Verificamos que el usuario con rol Scrum Master puede ver un rol de proyecto
        request.user = usuarioTest
        response = ver_rol_proyecto(request, rolProyecto.id)
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
        usuarioTest2 = Usuario(username="test2", email="test2@test.com", password="foo")
        usuarioTest2.save()

        #Creamos un proyecto de ejemplo
        proyecto = Proyecto(nombre="Proyecto de prueba", descripcion="Descripcion de prueba", estado="Planificacion", scrumMaster=usuarioTest2)
        proyecto.save()

        #Asignacion de Scrum Master al proyecto
        scrum = RolProyecto(nombre="Scrum Master", proyecto=proyecto)
        scrum.save()

        #Vinculamos el usuario al rol de Scrum Master
        scrum.usuario.add(usuarioTest2)

        #Vinculamos el usuario al proyecto
        proyecto.usuario.add(usuarioTest2)

        #Agregamos un usuarioTest al proyecto
        proyecto.usuario.add(usuarioTest)
        
        #Creamos un rol de proyecto
        rol = RolProyecto(nombre="Rol de prueba", descripcion="Descripcion de prueba", proyecto=proyecto)
        rol.save()

        #Recuperamos el rol en la base de datos
        rol = RolProyecto.objects.get(nombre="Rol de prueba")

        #Editamos el rol de proyecto con un usuario no autenticado
        request_factory = RequestFactory()
        request = request_factory.post(f'proyectos/roles_proyecto/editar/{rol.id}/', {
            'nombre':'Rol de prueba modificada', 
            'descripcion':'Descripcion de prueba modificada',
            'permisos': [1,2,3]
        })
        
        request.user = AnonymousUser()
        response = modificar_rol_proyecto(request, rol.id)
        self.assertEqual(response.status_code, 401, 'La respuesta no fue un estado HTTP 401 a un usuario no autenticado')


        #Un GPA Admin no puede modificar un rol de proyecto si este tiene usuarios asignados
        request.user = master
        response = modificar_rol_proyecto(request, rol.id)
        self.assertEqual(response.status_code, 403, 'La respuesta no fue un estado HTTP 403 a una edicion de GPA Admin a un proyecto asignado')

        #Editamos el rol de proyecto con un usuario Scrum Master
        request.user = usuarioTest2
        response = modificar_rol_proyecto(request, rol.id)
        self.assertEqual(response.status_code, 200, 'La respuesta no fue un estado HTTP 200 a una petición correcta')

        #Verificamos que el rol de proyecto fue modificado
        rol = RolProyecto.objects.get(nombre="Rol de prueba modificada")
        self.assertEqual(rol.descripcion, "Descripcion de prueba modificada", 'La descripcion del rol de proyecto no fue modificada')
        

        #Creamos un rol sin proyecto
        rol2 = RolProyecto(nombre="Rol de prueba 2", descripcion="Descripcion de prueba 2")
        rol2.save()

        #Recuperamos el rol en la base de datos
        rol2 = RolProyecto.objects.get(nombre="Rol de prueba 2")

        #Verificamos que solo el gpa_admin puede editar un rol de proyecto sin proyecto
        request.user = usuarioTest
        response = modificar_rol_proyecto(request, rol2.id)
        self.assertEqual(response.status_code, 403, 'La respuesta no fue un estado HTTP 403 a una petición de un usuario sin permisos')

        #Verificamos que el gpa_admin puede editar un rol de proyecto sin proyecto
        request.user = master
        response = modificar_rol_proyecto(request, rol2.id)
        self.assertEqual(response.status_code, 200, 'La respuesta no fue un estado HTTP 200 a una petición correcta')

        #Verificamos que el rol de proyecto fue modificado
        rol2 = RolProyecto.objects.get(nombre="Rol de prueba 2")
        self.assertEqual(rol2.descripcion, "Descripcion de prueba 2", 'La descripcion del rol de proyecto no fue modificada')

    def test_eliminar_rol_proyecto(self):
        """
        Prueba que el usuario puede eliminar un rol de proyecto
        """
        
        #Creamos un usuario gpa_admin
        master = Usuario(username="master", email="master@master.com", password="foo")
        master.save()
        RolSistema.objects.get(nombre="gpa_admin").usuario.add(master)

        #Creamos un usuario normal
        usuarioTest = Usuario(username="test", email="test@user.com", password="foo")
        usuarioTest.save()

        #Creamos un usuario que sera el Scrum Master del proyecto
        usuarioTest2 = Usuario(username="test2", email="test2@test.com", password="foo")
        usuarioTest2.save()

        #Creamos un proyecto de ejemplo
        proyecto = Proyecto(nombre="Proyecto de prueba", descripcion="Descripcion de prueba", estado="Planificacion", scrumMaster=usuarioTest2)
        proyecto.save()

        #Asignacion de Scrum Master al proyecto
        scrum = RolProyecto(nombre="Scrum Master", proyecto=proyecto)
        scrum.save()

        #Vinculamos el usuario al rol de Scrum Master
        scrum.usuario.add(usuarioTest2)

        #Vinculamos el usuario al proyecto
        proyecto.usuario.add(usuarioTest2)

        #Agregamos un usuarioTest al proyecto
        proyecto.usuario.add(usuarioTest)
        
        #Creamos un rol de proyecto
        rol = RolProyecto(nombre="Rol de prueba", descripcion="Descripcion de prueba", proyecto=proyecto)
        rol.save()

        #Recuperamos el rol en la base de datos
        rol = RolProyecto.objects.get(nombre="Rol de prueba")

        #Creamos el query para eliminar el rol de proyecto
        request_factory = RequestFactory()
        request = request_factory.post(f'proyectos/roles_proyecto/eliminar/{rol.id}/')
        request.user = AnonymousUser()
        response=eliminar_rol_proyecto_view(request, rol.id)
        self.assertEqual(response.status_code, 401, 'La respuesta no fue un estado HTTP 401 a un usuario no autenticado')

        #Un GPA Admin no puede eliminar un rol de proyecto si este tiene un proyecto_id asignados
        request.user = master
        response = eliminar_rol_proyecto_view(request, rol.id)
        self.assertEqual(response.status_code, 403, 'La respuesta no fue un estado HTTP 403 a una edicion de GPA Admin a un rol de proyecto asignado no global')

        #Eliminamos el rol de proyecto con un usuario Scrum Master
        request.user = usuarioTest2
        response = eliminar_rol_proyecto_view(request, rol.id)
        self.assertEqual(response.status_code, 200, 'La respuesta no fue un estado HTTP 200 a una petición correcta')

        #Verificamos que el rol de proyecto fue eliminado
        self.assertRaises(RolProyecto.DoesNotExist, RolProyecto.objects.get, nombre="Rol de prueba")

        #Creamos un rol de proyecto sin proyecto
        rol2 = RolProyecto(nombre="Rol de prueba 2", descripcion="Descripcion de prueba 2")
        rol2.save()

        #Recuperamos el rol en la base de datos
        rol2 = RolProyecto.objects.get(nombre="Rol de prueba 2")

        #Un usuario sin permisos no puede eliminar un rol de proyecto sin proyecto
        request.user = usuarioTest
        response = eliminar_rol_proyecto_view(request, rol2.id)
        self.assertEqual(response.status_code, 403, 'La respuesta no fue un estado HTTP 403 a una petición de un usuario sin permisos')

        #el scrum master no puede eliminar un rol de proyecto sin proyecto
        request.user = usuarioTest
        response = eliminar_rol_proyecto_view(request, rol2.id)
        self.assertEqual(response.status_code, 403, 'La respuesta no fue un estado HTTP 403 a una petición de un usuario sin permisos')

        
        #El gpa_admin puede eliminar un rol de proyecto sin proyecto
        request.user = master
        response = eliminar_rol_proyecto_view(request, rol2.id)
        self.assertEqual(response.status_code, 200, 'La respuesta no fue un estado HTTP 200 a una petición correcta')

        #Verificamos que el rol de proyecto fue eliminado
        self.assertRaises(RolProyecto.DoesNotExist, RolProyecto.objects.get, nombre="Rol de prueba 2")

    
    def test_ver_roles_asignados_a_un_proyecto(self):
        """
        Prueba que solamente usuario Scrum Master puede ver los roles de un proyecto
        """
        
        #Creamos un usuario gpa_admin
        master = Usuario(username="master", email="master@master.com", password="foo")
        master.save()
        RolSistema.objects.get(nombre="gpa_admin").usuario.add(master)

        #Creamos un usuario normal
        usuarioTest = Usuario(username="test", email="test@user.com", password="foo")
        usuarioTest.save()

        #Creamos un usuario que sera el Scrum Master del proyecto
        usuarioTest2 = Usuario(username="test2", email="test2@test.com", password="foo")
        usuarioTest2.save()

        #Creamos un proyecto de ejemplo
        proyecto = Proyecto(nombre="Proyecto de prueba", descripcion="Descripcion de prueba", estado="Planificacion", scrumMaster=usuarioTest2)
        proyecto.save()

        #Asignacion de Scrum Master al proyecto
        scrum = RolProyecto(nombre="Scrum Master", proyecto=proyecto)
        scrum.save()

        #Vinculamos el usuario al rol de Scrum Master
        scrum.usuario.add(usuarioTest2)

        #Vinculamos el usuario al proyecto
        proyecto.usuario.add(usuarioTest2)

        #Agregamos un usuarioTest al proyecto
        proyecto.usuario.add(usuarioTest)
        
        #Creamos un rol de proyecto
        rol = RolProyecto(nombre="Rol de prueba", descripcion="Descripcion de prueba", proyecto=proyecto)
        rol.save()

        #Verificamos que solo el Scrum Master puede ver los roles de un proyecto
        request_factory = RequestFactory()
        request = request_factory.get(f'proyectos/{proyecto.id}/roles/')
        request.user = AnonymousUser()
        response=ver_roles_asignados(request, proyecto.id)
        self.assertEqual(response.status_code, 401, 'La respuesta no fue un estado HTTP 401 a un usuario no autenticado')

        #Un usuario normal no puede ver los roles de un proyecto
        request.user = usuarioTest
        response = ver_roles_asignados(request, proyecto.id)
        self.assertEqual(response.status_code, 403, 'La respuesta no fue un estado HTTP 403 a un usuario normal')

        #Un usuario Scrum Master puede ver los roles de un proyecto
        request.user = usuarioTest2
        response = ver_roles_asignados(request, proyecto.id)
        self.assertEqual(response.status_code, 200, 'La respuesta no fue un estado HTTP 200 a un usuario Scrum Master')


    def test_crear_rol_a_proyecto(self):
        """
            Prueba que el usuario puede crear un rol de proyecto opcion para admin
        """
        #Creamos un usuario gpa_admin
        master = Usuario(username="master", email="master@master.com", password="foo")
        master.save()
        RolSistema.objects.get(nombre="gpa_admin").usuario.add(master)

        #Creamos un usuario normal
        usuarioTest = Usuario(username="test", email="test@user.com", password="foo")
        usuarioTest.save()

        #Creamos un usuario que sera el Scrum Master del proyecto
        usuarioTest2 = Usuario(username="test2", email="test2@test.com", password="foo")
        usuarioTest2.save()

        #Creamos un proyecto de ejemplo
        proyecto = Proyecto(nombre="Proyecto de prueba", descripcion="Descripcion de prueba", estado="Planificacion", scrumMaster=usuarioTest2)
        proyecto.save()

        #Obtenemos el proyecto de la base de datos
        proyecto = Proyecto.objects.get(nombre="Proyecto de prueba")

        #Asignacion de Scrum Master al proyecto
        scrum = RolProyecto(nombre="Scrum Master", proyecto=proyecto)
        scrum.save()

        #Vinculamos el usuario al rol de Scrum Master
        scrum.usuario.add(usuarioTest2)

        #Vinculamos el usuario al proyecto
        proyecto.usuario.add(usuarioTest2)

        #Agregamos un usuarioTest al proyecto
        proyecto.usuario.add(usuarioTest)

        #Probamos que solamente el ScrumMaster puede crear un rol de proyecto
        request_factory = RequestFactory()
        request = request_factory.post(f'proyectos/{proyecto.id}/roles/crear/', {
            'nombre':'Rol de prueba', 
            'descripcion':'Descripcion de prueba',
            'permisos': [1,2,3]
            }
        )

        request.user = AnonymousUser()
        response = crear_rol_a_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 401, 'La respuesta no fue un estado HTTP 401 a un usuario no autenticado')

        request.user = usuarioTest
        response = crear_rol_a_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 403, 'La respuesta no fue un estado HTTP 403 a un usuario normal')

        request.user = usuarioTest2
        response = crear_rol_a_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 200, 'La respuesta no fue un estado HTTP 200 a un usuario Scrum Master')

        #Probamos que el rol se creo correctamente
        rol = RolProyecto.objects.get(nombre="Rol de prueba")
        self.assertEqual(rol.nombre, "Rol de prueba", 'El rol no se creo correctamente')
        self.assertEqual(rol.descripcion, "Descripcion de prueba", 'El rol no se creo correctamente')
        self.assertEqual(rol.proyecto, proyecto, 'El rol no se creo correctamente')


    def test_importar_rol(self):
        """
            Prueba que el usuario puede importar un rol de proyecto
        """
        #Creamos un usuario gpa_admin
        master = Usuario(username="master", email="master@master.com", password="foo")
        master.save()
        RolSistema.objects.get(nombre="gpa_admin").usuario.add(master)

        #Creamos un usuario normal
        usuarioTest = Usuario(username="test", email="test@user.com", password="foo")
        usuarioTest.save()

        #Creamos un usuario que sera el Scrum Master del proyecto
        usuarioTest2 = Usuario(username="test2", email="test2@test.com", password="foo")
        usuarioTest2.save()

        #Creamos un proyecto de ejemplo
        proyecto = Proyecto(nombre="Proyecto de prueba", descripcion="Descripcion de prueba", estado="Planificacion", scrumMaster=usuarioTest2)
        proyecto.save()

        #Obtenemos el proyecto de la base de datos
        proyecto = Proyecto.objects.get(nombre="Proyecto de prueba")

        #Asignacion de Scrum Master al proyecto
        scrum = RolProyecto(nombre="Scrum Master", proyecto=proyecto)
        scrum.save()

        #Vinculamos el usuario al rol de Scrum Master
        scrum.usuario.add(usuarioTest2)

        #Vinculamos el usuario al proyecto
        proyecto.usuario.add(usuarioTest2)

        #Agregamos un usuarioTest al proyecto
        proyecto.usuario.add(usuarioTest)

        #Creamos un rol de proyecto
        rol = RolProyecto(nombre="Rol de prueba", proyecto=proyecto)
        rol.save()

        #Probamos que solamente el ScrumMaster puede importar un rol de proyecto
        request_factory = RequestFactory()
        request = request_factory.get(f'proyectos/{proyecto.id}/roles/import/')
        request.user = AnonymousUser()
        response = importar_rol(request, proyecto.id)
        self.assertEqual(response.status_code, 401, 'La respuesta no fue un estado HTTP 401 a un usuario no autenticado')

        request.user = usuarioTest
        response = importar_rol(request, proyecto.id)
        self.assertEqual(response.status_code, 403, 'La respuesta no fue un estado HTTP 403 a un usuario normal')

        request.user = usuarioTest2
        response = importar_rol(request, proyecto.id)
        self.assertEqual(response.status_code, 200, 'La respuesta no fue un estado HTTP 200 a un usuario Scrum Master')




