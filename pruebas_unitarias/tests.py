from django.test import TestCase


# Create your tests here.
import os
from django import setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gestion_proyectos_agile.settings")
setup()


import json
from django.contrib.auth.models import AnonymousUser, User
from django.test.client import RequestFactory
from usuarios.views import eliminar_miembro_proyecto, agregar_miembro_proyecto, eliminar_rol_proyecto, asignar_rol_proyecto
from usuarios.models import RolProyecto, Usuario
from proyectos.models import Proyecto
from django.contrib.auth import get_user_model



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
        self.assertEqual(Usuario.objects.filter(groups__name='gpa_admin').count(), 1)

    def test_agregar_miembro_proyecto(self):
        """
        Prueba de la vista de agregar miembro de un proyecto
        """
        request_factory = RequestFactory()
        request = request_factory.post('usuarios/agregar_usuario_proyecto')
        request.user = AnonymousUser()
        response = agregar_miembro_proyecto(request)
        self.assertEqual(response.status_code, 401,
                         'La respuesta no fue un estado HTTP 401 a un usuario no autorizado')

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

        request = request_factory.post('/usuarios/agregar_miembro_proyecto/', data={
            'usuario_a_agregar': usuarioTest.username,
            'proyecto': proyectoTest.id,
            'roles_agregar': rolTest.id
        })
        request.user = usuarioTest
        response = agregar_miembro_proyecto(request)
        self.assertEqual(response.status_code, 403,
                         'La respuesta no fue un estado HTTP 401 a un usuario no autorizado para esta operacion')

        request = request_factory.post('/usuarios/agregar_miembro_proyecto/', data={
            'usuario_a_agregar': '',
            'proyecto': proyectoTest.id,
            'roles_agregar': rolTest.id
        })
        request.user = master
        response = agregar_miembro_proyecto(request)
        self.assertEqual(response.status_code, 422,
                         'La respuesta no fue un estado HTTP 404 ante un usuario que no existe')

        request = request_factory.post('/usuarios/agregar_miembro_proyecto/', data={
            'usuario_a_agregar': usuarioTest.username,
            'proyecto': proyectoTest.id,
            'roles_agregar': rolTest.id
        })
        request.user = master
        response = agregar_miembro_proyecto(request)
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
        request = request_factory.post('usuarios/eliminar_miembro_proyecto')
        request.user = AnonymousUser()
        response = eliminar_miembro_proyecto(request)
        self.assertEqual(response.status_code, 401,
                         'La respuesta no fue un estado HTTP 401 a un usuario no autorizado')

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

        master.equipo.add(proyectoTest)
        usuarioTest.equipo.add(proyectoTest)
        usuarioTest.roles_proyecto.add(rolTest)

        request = request_factory.post('/usuarios/eliminar_miembro_proyecto/', data={
            'usuario_a_eliminar': usuarioTest.username,
            'proyecto': proyectoTest.id,
        })
        request.user = usuarioTest
        response = eliminar_miembro_proyecto(request)
        self.assertEqual(response.status_code, 403,
                         'La respuesta no fue un estado HTTP 401 a un usuario no autorizado para esta operacion')

        request = request_factory.post('/usuarios/eliminar_miembro_proyecto/', data={
            'usuario_a_eliminar': '',
            'proyecto': proyectoTest.id,
        })
        request.user = master
        response = eliminar_miembro_proyecto(request)
        self.assertEqual(response.status_code, 422,
                         'La respuesta no fue un estado HTTP 404 ante un usuario que no existe')

        request = request_factory.post('/usuarios/eliminar_miembro_proyecto/', data={
            'usuario_a_eliminar': usuarioTest.username,
            'proyecto': proyectoTest.id,
        })
        request.user = master
        response = eliminar_miembro_proyecto(request)
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
        request = request_factory.post('usuarios/asignar_rol_proyecto')
        request.user = AnonymousUser()
        response = asignar_rol_proyecto(request)
        self.assertEqual(response.status_code, 401,
                         'La respuesta no fue un estado HTTP 401 a un usuario no autorizado')

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

        request = request_factory.post('/usuarios/asignar_rol_proyecto/', data={
            'usuario_a_cambiar_rol': usuarioTest.username,
            'proyecto': proyectoTest.id,
            f'roles{usuarioTest.username}': rolTest.id
        })
        request.user = usuarioTest
        response = asignar_rol_proyecto(request)
        self.assertEqual(response.status_code, 403,
                         'La respuesta no fue un estado HTTP 401 a un usuario no autorizado para esta operacion')

        request = request_factory.post('/usuarios/asignar_rol_proyecto/', data={
            'usuario_a_cambiar_rol': '',
            'proyecto': proyectoTest.id,
            f'roles{usuarioTest.username}': rolTest.id
        })
        request.user = master
        response = asignar_rol_proyecto(request)
        self.assertEqual(response.status_code, 422,
                         'La respuesta no fue un estado HTTP 404 ante un usuario que no existe')

        request = request_factory.post('/usuarios/asignar_rol_proyecto/', data={
            'usuario_a_cambiar_rol': usuarioTest.username,
            'proyecto': proyectoTest.id,
            f'roles{usuarioTest.username}': rolTest.id
        })
        request.user = master
        response = asignar_rol_proyecto(request)
        self.assertEqual(response.status_code, 302,
                         'La respuesta no fue un estado HTTP 302 ante una presunta operacion exitosa')
        self.assertTrue(rolTest in usuarioTest.roles_proyecto.all(), 
                        'El usuario tiene el rol asignado en el proyecto')


    def test_eliminar_rol_proyecto(self):
        """
        Prueba de la vista de desasignar rol de proyecto a un miembro
        """
        request_factory = RequestFactory()
        request = request_factory.post('usuarios/eliminar_rol_proyecto')
        request.user = AnonymousUser()
        response = eliminar_rol_proyecto(request)
        self.assertEqual(response.status_code, 401,
                         'La respuesta no fue un estado HTTP 401 a un usuario no autorizado')

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
        usuarioTest.roles_proyecto.add(rolTest)

        request = request_factory.post('/usuarios/eliminar_rol_proyecto/', data={
            'usuario_a_sacar_rol': usuarioTest.username,
            'proyecto': proyectoTest.id,
            'rol_id': rolTest.id
        })
        request.user = usuarioTest
        response = eliminar_rol_proyecto(request)
        self.assertEqual(response.status_code, 403,
                         'La respuesta no fue un estado HTTP 401 a un usuario no autorizado para esta operacion')

        request = request_factory.post('/usuarios/eliminar_rol_proyecto/', data={
            'usuario_a_cambiar_rol': '',
            'proyecto': proyectoTest.id,
            'rol_id': rolTest.id
        })
        request.user = master
        response = eliminar_rol_proyecto(request)
        self.assertEqual(response.status_code, 422,
                         'La respuesta no fue un estado HTTP 404 ante un usuario que no existe')

        request = request_factory.post('/usuarios/eliminar_rol_proyecto/', data={
            'usuario_a_sacar_rol': usuarioTest.username,
            'proyecto': proyectoTest.id,
            'rol_id': rolTest.id
        })
        request.user = master
        response = eliminar_rol_proyecto(request)
        self.assertEqual(response.status_code, 302,
                         'La respuesta no fue un estado HTTP 302 ante una presunta operacion exitosa')
        self.assertFalse(rolTest in usuarioTest.roles_proyecto.all(), 
                        'El usuario tiene el rol asignado en el proyecto')
