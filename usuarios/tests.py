import os
from django import setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gestion_proyectos_agile.settings")
setup()

from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test.client import RequestFactory

from usuarios.views import *
from usuarios.models import RolSistema
from proyectos.models import Proyecto
from usuarios.views import vista_equipo
from usuarios.models import RolProyecto, Usuario
from phonenumber_field.modelfields import PhoneNumber

# Create your tests here.


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

    fixtures = [
       "databasedump.json",
    ]

    def test_crear_rol(self):
        """
        Prueba que se pueda crear el rol
        """
        self.user = get_user_model().objects.create_user(email='testemail@example.com', password='A123B456c.', username='test')
        self.client.login(email='testemail@example.com', password='A123B456c.')
        permisos = PermisoSistema.objects.all()
        res = self.client.post('/rolesglobales/crear/',
                               data={'nombre': 'rol_global_test22', 'descripcion': 'Esto es un test', 'permisos': [permisos[0].id, permisos[1].id]}, follow=True)
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
        permisos = PermisoSistema.objects.all()
        res = self.client.post(f'/rolesglobales/{rolTest.id}/editar/', data={
                            'nombre': 'rol_global_test_editado', 'descripcion': 'Esto es un test editado', 'permisos': [permisos[0].id, permisos[1].id]}, follow=True)
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

    fixtures = [
       "databasedump.json",
    ]

    def setUp(self):
        """
        Crea un usuario para realizar las pruebas y un proyecto.
        """
        self.user = get_user_model().objects.create_user(email='testemail@example.com', password='A123B456c.',
                                                         avatar_url='avatar@example.com', direccion='Calle 1 # 2 - 3', telefono=PhoneNumber.from_string('0983 738040'))
                                                         
        self.client.login(email='testemail@example.com', password='A123B456c.')
        res = self.client.post("/proyecto/crear/", {"nombre": "PROYECTO_STANDARD", "descripcion": "Existe en todas las pruebas", "scrum_master": self.user.id})
        self.assertEqual(res.status_code, 200)
        self.proyecto = Proyecto.objects.get(nombre="PROYECTO_STANDARD")
        self.assertTrue(self.proyecto.roles.filter(usuario=self.user, nombre="Scrum Master").exists())
    
    def test_get_visualizar_proyecto(self):
        """
        Prueba de la vista de visualizar gestion de miembros y roles de proyectos
        """
        request_factory = RequestFactory()

        usuario_no_miembro = Usuario(username="test", email='normal@user.com', password='foo')
        usuario_miembro = Usuario(username="master",email='master@user.com', password='foo')
        usuario_no_miembro.save()
        usuario_miembro.save()

        proyectoTest = self.proyecto
        usuario_miembro.equipo.add(proyectoTest)
        
        request = request_factory.get(f'/proyecto/{proyectoTest.id}/usuarios/')
        request.user = AnonymousUser()
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 401,
                         'La respuesta no fue un estado HTTP 401 a un usuario no autorizado')

        request = request_factory.get(f'/proyecto/{proyectoTest.id}/usuarios/')
        request.user = usuario_miembro
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 200,
                         'La respuesta no fue un estado HTTP 200 a un usuario no autorizado para esta operacion')

        request = request_factory.get(f'/proyecto/{proyectoTest.id}/usuarios/')
        request.user = usuario_no_miembro
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 403,
                         'La respuesta no fue un estado HTTP 403 a un usuario no autorizado para esta operacion')
             
        proyectoTest.delete()
        
        request = request_factory.get(f'/proyecto/{proyectoTest.id}/usuarios/')
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
        master = self.user
        usuarioTest.save()

        proyectoTest = self.proyecto

        rolTest = RolProyecto(nombre="rol test", proyecto=proyectoTest)
        rolTest.save()
        
        request = request_factory.post(f'/proyecto/{proyectoTest.id}/usuarios/', data={
            'usuario_a_agregar': usuarioTest.email,
            'roles_agregar': rolTest.id,
            'hidden_action': 'agregar_miembro_proyecto'
        })
        request.user = usuarioTest
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 403,
                         'La respuesta no fue un estado HTTP 403 a un usuario no autorizado para esta operacion')

        request = request_factory.post(f'/proyecto/{proyectoTest.id}/usuarios/', data={
            'usuario_a_agregar': '',
            'roles_agregar': rolTest.id,
            'hidden_action': 'agregar_miembro_proyecto'
        })
        request.user = master
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 422,
                         'La respuesta no fue un estado HTTP 422 ante un usuario que no existe')

        request = request_factory.post(f'/proyecto/{proyectoTest.id}/usuarios/', data={
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
        master = self.user
        usuarioTest.save()

        proyectoTest = self.proyecto

        usuarioTest.equipo.add(proyectoTest)

        rolTest = RolProyecto(nombre="rol test", proyecto=proyectoTest)
        rolTest.save()
        usuarioTest.roles_proyecto.add(rolTest)

        request = request_factory.post(f'/proyecto/{proyectoTest.id}/usuarios/', data={
            'usuario_a_eliminar': usuarioTest.email,
            'hidden_action': 'eliminar_miembro_proyecto'
        })
        request.user = usuarioTest
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 403,
                         'La respuesta no fue un estado HTTP 403 a un usuario no autorizado para esta operacion')

        request = request_factory.post(f'/proyecto/{proyectoTest.id}/usuarios/', data={
            'usuario_a_eliminar': '',
            'hidden_action': 'eliminar_miembro_proyecto'
        })
        request.user = master
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 422,
                         'La respuesta no fue un estado HTTP 422 ante un usuario que no existe')

        request = request_factory.post(f'/proyecto/{proyectoTest.id}/usuarios/', data={
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
        master = self.user
        usuarioTest.save()

        proyectoTest = self.proyecto

        rolTest = RolProyecto(nombre="rol test", proyecto=proyectoTest)
        rolTest.save()
        
        request = request_factory.post(f'/proyecto/{proyectoTest.id}/usuarios/', data={
            'usuario_a_cambiar_rol': usuarioTest.username,
            f'roles{usuarioTest.username}': rolTest.id,
            'hidden_action': 'asignar_rol_proyecto'
        })
        request.user = usuarioTest
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 403,
                         'La respuesta no fue un estado HTTP 403 a un usuario no autorizado para esta operacion')

        request = request_factory.post(f'/proyecto/{proyectoTest.id}/usuarios/', data={
            'usuario_a_cambiar_rol': '',
            f'roles{usuarioTest.username}': rolTest.id,
            'hidden_action': 'asignar_rol_proyecto'
        })
        request.user = master
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 422,
                         'La respuesta no fue un estado HTTP 422 ante un usuario que no existe')

        request = request_factory.post(f'/proyecto/{proyectoTest.id}/usuarios/', data={
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
        master = self.user
        usuarioTest.save()

        proyectoTest = self.proyecto
        proyectoTest.save()

        usuarioTest.equipo.add(proyectoTest)

        rolTest = RolProyecto(nombre="rol test", proyecto=proyectoTest)
        rolTest.save()

        usuarioTest.roles_proyecto.add(rolTest)
        
        request = request_factory.post(f'/proyecto/{proyectoTest.id}/usuarios/', data={
            'usuario_a_sacar_rol': usuarioTest.email,
            'rol_id': rolTest.id,
            'hidden_action': 'eliminar_rol_proyecto'
        })
        request.user = usuarioTest
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 403,
                         'La respuesta no fue un estado HTTP 403 a un usuario no autorizado para esta operacion')

        request = request_factory.post(f'/proyecto/{proyectoTest.id}/usuarios/', data={
            'usuario_a_cambiar_rol': '',
            'rol_id': rolTest.id,
            'hidden_action': 'eliminar_rol_proyecto'
        })
        request.user = master
        response = vista_equipo(request, proyectoTest.id)
        self.assertEqual(response.status_code, 422,
                         'La respuesta no fue un estado HTTP 422 ante un usuario que no existe')

        request = request_factory.post(f'/proyecto/{proyectoTest.id}/usuarios/', data={
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