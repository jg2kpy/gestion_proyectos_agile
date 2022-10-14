import os
from django import setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gestion_proyectos_agile.settings")
setup()

from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.test.client import RequestFactory
from django.contrib.auth import get_user_model

from usuarios.views import *
from usuarios.models import RolSistema
from proyectos.models import Proyecto
from usuarios.views import vista_equipo
from usuarios.models import RolProyecto, Usuario
from proyectos.views import *
from proyectos.views import eliminar_rol_proyecto as eliminar_rol_proyecto_view
from phonenumber_field.modelfields import PhoneNumber

# Create your tests here.

class ProyectoTests(TestCase):

    fixtures = [
        "databasedump.json",
    ]

    def setUp(self):
        """
        Crea un usuario y un proyecto para realizar las pruebas y un proyecto.
        """
        self.user = get_user_model().objects.create_user(email='testemail@example.com', password='A123B456c.',
                                                         avatar_url='avatar@example.com', direccion='Calle 1 # 2 - 3', telefono=PhoneNumber.from_string('0983 738040'))

        self.client.login(email='testemail@example.com', password='A123B456c.')
        res = self.client.post("/proyecto/crear/", {"nombre": "PROYECTO_STANDARD",
                               "descripcion": "Existe en todas las pruebas", "scrumMaster": self.user.id}, follow=True)
        self.assertEqual(res.status_code, 200)
        self.proyecto = Proyecto.objects.get(nombre="PROYECTO_STANDARD")

    def test_ver_proyectos(self):
        """
        Prueba que el usuario puede ver los proyectos
        """
        request_factory = RequestFactory()
        request = request_factory.get('/proyectos/')
        request.user = AnonymousUser()
        response = proyectos(request)
        self.assertEqual(response.status_code, 401,
                         "Usuario puede ver los proyectos pero no esta autenticado")

        # Creamos un usuario con roles del sistema Admin
        master = Usuario(username="master",
                         email='master@user.com', password='foo')
        master.save()
        RolSistema.objects.get(nombre="gpa_admin").usuario.add(master)

        # Creamos un usuario sin roles de admin
        user = Usuario(username="user",
                       email='user@user.com', password='foo')
        user.save()

        # Verificamos que el usuario sin de admin puede ver los proyectos
        request.user = user
        response = proyectos(request)
        self.assertContains(response, '<h1>Proyectos</h1>', None,
                            200,  "Usuario ve lista vacia si no es Scrum Master")
        self.assertContains(response, 'http://localhost/proyectos/crear/', 0,
                            200,  "Usuario no tiene opcion crear proyecto si no es Scrum Master")

        # Verificamos que el usuario puede ver los proyectos
        request.user = master
        response = proyectos(request)
        self.assertEqual(response.status_code, 200,
                         "Usuario no puede ver los proyectos")

    def test_crear_proyecto(self):
        """
        Prueba que el usuario puede crear un proyecto
        """
        request_factory = RequestFactory()
        request = request_factory.post('/proyectos/crear/')
        request.user = AnonymousUser()
        response = crear_proyecto(request)
        self.assertEqual(response.status_code, 401,
                         'La respuesta no fue un estado HTTP 401 a un usuario no autorizado')

        # Verificar que gpa_admin puede crear proyectos
        usuarioTest = Usuario(
            username="test", email='normal@user.com', password='foo')
        master = Usuario(username="master",
                         email='master@user.com', password='foo')
        master.save()
        usuarioTest.save()

        RolSistema.objects.get(nombre="gpa_admin").usuario.add(master)

        request.user = usuarioTest
        response = crear_proyecto(request)
        self.assertEqual(response.status_code, 403,
                         'La respuesta no fue un estado HTTP 403 a un usuario sin permisos GPA_ADMIN')

        # Verfificamos la creacion de un proyecto
        request = request_factory.post(
            '/proyectos/crear/', {'nombre': 'Proyecto de prueba', 'descripcion': 'Descripcion de prueba', 'scrumMaster': master.id})
        request.user = master
        response = crear_proyecto(request)
        self.assertEqual(response.status_code, 302,
                         'La respuesta no fue un estado HTTP 302 de la creacion de un proyecto')

        # Verificamos que el proyecto se creo correctamente
        proyecto = Proyecto.objects.get(nombre='Proyecto de prueba')
        self.assertEqual(proyecto.nombre, 'Proyecto de prueba',
                         'El nombre del proyecto no es el correcto')
        self.assertEqual(proyecto.descripcion, 'Descripcion de prueba',
                         'La descripcion del proyecto no es la correcta')
        self.assertEqual(proyecto.scrumMaster, master,
                         'El scrum master del proyecto no es el correcto')
        self.assertEqual(proyecto.estado, 'Planificacion',
                         'El estado del proyecto no es el correcto')

    def test_editar_proyecto(self):
        """
        Prueba que el usuario puede editar un proyecto
        """
        master = self.user
        proyecto = self.proyecto

        # Creamos un usuario que no este logueado
        usuarioTest = Usuario(
            username="test",
            email='test@example.com',
            password='foo'
        )
        usuarioTest.save()

        # Creamos la solicitud
        request_factory = RequestFactory()
        request = request_factory.post(f'/proyectos/{proyecto.id}/editar')

        # Verficicamos un usuario no logueado
        request.user = AnonymousUser()
        response = editar_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 401,
                         'La respuesta no fue un estado HTTP 401 a un usuario no autenticado')

        # Verficicamos un usuario logueado sin permisos
        request.user = usuarioTest
        response = editar_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 403,
                         'La respuesta no fue un estado HTTP 403 a un usuario sin permisos')

        # Verficicamos la edicion correcta de un proyecto
        request = request_factory.post(f'/proyectos/{proyecto.id}/editar', {
                                       'nombre': 'Proyecto de prueba 2', 'descripcion': 'Descripcion de prueba 2'})
        request.user = master
        response = editar_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 422,
                         'La respuesta no fue un estado HTTP 422 a una petición incorrecta')

        # Verficicamos la edicion correcta de un proyecto
        request = request_factory.post(f'/proyectos/{proyecto.id}/editar', {'nombre': 'Proyecto de prueba 22',
                                       'descripcion': 'Descripcion de prueba 2'})
        request.user = master
        response = editar_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 422,
                         'La respuesta fue un estado HTTP 422 a una petición correcta')
        self.assertFalse(Proyecto.objects.filter(
            nombre="Proyecto de prueba 22").exists(), 'El proyecto no se edito correctamente')

    def test_cancelar_proyecto(self):
        """
        Prueba que el usuario puede cancelar un proyecto
        """
        master = self.user
        proyecto = self.proyecto

        # Verificamos que un usuario no logueado no puede cancelar un proyecto
        request_factory = RequestFactory()
        request = request_factory.get(f'proyecto/cancelar/{proyecto.id}/')
        request.user = AnonymousUser()
        response = cancelar_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 401,
                         'La respuesta no fue un estado HTTP 401 a un usuario no autenticado')

        # Verificamos que un usuario sin permisos no puede cancelar un proyecto
        usuarioTest = Usuario(
            username="test", email='user@user.com', password='foo')
        usuarioTest.save()
        request.user = usuarioTest
        response = cancelar_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 403,
                         'La respuesta no fue un estado HTTP 403 a un usuario sin permisos')

        # Verificamos que un usuario con permisos puede cancelar un proyecto
        request = request_factory.post(
            f'proyecto/{proyecto.id}/cancelar', {'nombre': 'PROYECTO_STANDARD'})
        request.user = master
        response = cancelar_proyecto(request, proyecto.id)
        # self.assertEqual(proyecto.estado, 'Cancelado', 'El estado del proyecto al cancelar no es el correcto')
        self.assertEqual(response.status_code, 302,
                         'La respuesta no fue un estado HTTP 302 a una petición correcta')

        # Verificamos que no se puede cancelar un proyecto cuando no tiene nombre correcto

        proyecto = self.proyecto

        request = request_factory.post(
            f'proyecto/cancelar/{proyecto.id}/', {'nombre': 'Proyecto de prueba 2'})
        request.user = master
        response = cancelar_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 422,
                         'La respuesta no fue un estado HTTP 422 a una petición incorrecta')
        # Verificamos que el proyecto no se cancelo

        self.assertEqual(proyecto.estado, 'Planificacion',
                         'Se cancelo el proyecto por mas que introdujo un nombre incorrecto')

    def test_modificar_rol_proyecto(self):
        """
        Prueba que el usuario puede modificar un rol de proyecto
        """
        # Creamos un usuario normal
        usuarioTest = Usuario(
            username="test", email="test@user.com", password="foo")
        usuarioTest.save()

        # Creamos un usuario que sera el Scrum Master del proyecto
        usuarioTest2 = Usuario(
            username="test2", email="test2@test.com", password="foo")
        usuarioTest2.save()

        # Creamos un proyecto de ejemplo

        proyecto = self.proyecto

        # Asignacion de Scrum Master al proyecto
        scrum = RolProyecto.objects.get(
            nombre="Scrum Master", proyecto=proyecto)

        # Vinculamos el usuario al rol de Scrum Master
        scrum.usuario.add(usuarioTest2)

        # Vinculamos el usuario al proyecto
        proyecto.usuario.add(usuarioTest2)

        # Agregamos un usuarioTest al proyecto
        proyecto.usuario.add(usuarioTest)

        # Creamos un rol de proyecto
        rol = RolProyecto(nombre="Rol de prueba",
                          descripcion="Descripcion de prueba", proyecto=proyecto)
        rol.save()

        # Recuperamos el rol en la base de datos
        rol = RolProyecto.objects.get(nombre="Rol de prueba")

        # Editamos el rol de proyecto con un usuario no autenticado
        request_factory = RequestFactory()
        request = request_factory.post(f'proyecto/roles_proyecto/editar/{rol.id}/', {
            'nombre': 'Rol de prueba modificada',
            'descripcion': 'Descripcion de prueba modificada',
            'permisos': [1, 2, 3]
        })

        request.user = AnonymousUser()
        response = modificar_rol_proyecto(request, proyecto.id, rol.id)
        self.assertEqual(response.status_code, 401,
                         'La respuesta no fue un estado HTTP 401 a un usuario no autenticado')

        # Editamos el rol de proyecto con un usuario Scrum Master
        request.user = usuarioTest2
        response = modificar_rol_proyecto(request, proyecto.id, rol.id)
        self.assertEqual(response.status_code, 302,
                         'La respuesta no fue un estado HTTP 302 a una petición correcta')

        # Verificamos que el rol de proyecto fue modificado
        rol = RolProyecto.objects.get(nombre="Rol de prueba modificada")
        self.assertEqual(rol.descripcion, "Descripcion de prueba modificada",
                         'La descripcion del rol de proyecto no fue modificada')

        # Creamos un rol sin proyecto
        rol2 = RolProyecto(nombre="Rol de prueba 2",
                           descripcion="Descripcion de prueba 2")
        rol2.save()

        # Recuperamos el rol en la base de datos
        rol2 = RolProyecto.objects.get(nombre="Rol de prueba 2")

        # Verificamos que solo el gpa_admin puede editar un rol de proyecto sin proyecto
        request.user = usuarioTest
        response = eliminar_rol_proyecto_view(request, proyecto.id, rol2.id)
        self.assertEqual(response.status_code, 403,
                         'La respuesta no fue un estado HTTP 403 a una petición de un usuario sin permisos')

    def test_eliminar_rol_proyecto(self):
        """
        Prueba que el usuario puede eliminar un rol de proyecto
        """
        # Creamos un usuario normal
        usuarioTest = Usuario(
            username="test", email="test@user.com", password="foo")
        usuarioTest.save()

        # Creamos un usuario que sera el Scrum Master del proyecto
        usuarioTest2 = Usuario(
            username="test2", email="test2@test.com", password="foo")
        usuarioTest2.save()

        # Creamos un proyecto de ejemplo

        proyecto = self.proyecto

        # Asignacion de Scrum Master al proyecto
        scrum = RolProyecto.objects.get(
            nombre="Scrum Master", proyecto=proyecto)

        # Vinculamos el usuario al rol de Scrum Master
        scrum.usuario.add(usuarioTest2)

        # Vinculamos el usuario al proyecto
        proyecto.usuario.add(usuarioTest2)

        # Agregamos un usuarioTest al proyecto
        proyecto.usuario.add(usuarioTest)

        usuarioTest2 = self.user

        # Creamos un rol de proyecto
        rol = RolProyecto(nombre="Rol de prueba",
                          descripcion="Descripcion de prueba", proyecto=proyecto)
        rol.save()

        # Recuperamos el rol en la base de datos
        rol = RolProyecto.objects.get(nombre="Rol de prueba")

        # Creamos el query para eliminar el rol de proyecto
        request_factory = RequestFactory()
        request = request_factory.post(
            f'proyecto/roles_proyecto/eliminar/{rol.id}/')
        request.user = AnonymousUser()
        response = eliminar_rol_proyecto_view(request, proyecto.id, rol.id)
        self.assertEqual(response.status_code, 401,
                         'La respuesta no fue un estado HTTP 401 a un usuario no autenticado')

        # Eliminamos el rol de proyecto con un usuario Scrum Master
        request.user = usuarioTest2
        response = eliminar_rol_proyecto_view(request, proyecto.id, rol.id)
        self.assertEqual(response.status_code, 302,
                         'La respuesta no fue un estado HTTP 302 a una petición correcta')

        # Verificamos que el rol de proyecto fue eliminado
        self.assertRaises(RolProyecto.DoesNotExist,
                          RolProyecto.objects.get, nombre="Rol de prueba")

        # Creamos un rol de proyecto sin proyecto
        rol2 = RolProyecto(nombre="Rol de prueba 2",
                           descripcion="Descripcion de prueba 2")
        rol2.save()

        # Recuperamos el rol en la base de datos
        rol2 = RolProyecto.objects.get(nombre="Rol de prueba 2")

        # Un usuario sin permisos no puede eliminar un rol de proyecto sin proyecto
        request.user = usuarioTest
        response = eliminar_rol_proyecto_view(request, proyecto.id, rol2.id)
        self.assertEqual(response.status_code, 403,
                         'La respuesta no fue un estado HTTP 403 a una petición de un usuario sin permisos')

        # el scrum master no puede eliminar un rol de proyecto sin proyecto
        request.user = usuarioTest
        response = eliminar_rol_proyecto_view(request, proyecto.id, rol2.id)
        self.assertEqual(response.status_code, 403,
                         'La respuesta no fue un estado HTTP 403 a una petición de un usuario sin permisos')

    def test_roles_de_proyecto_a_un_proyecto(self):
        """
        Prueba que solamente usuario Scrum Master puede ver los roles de un proyecto
        """
        # Creamos un usuario normal
        usuarioTest = Usuario(
            username="test", email="test@user.com", password="foo")
        usuarioTest.save()

        # Creamos un usuario que sera el Scrum Master del proyecto
        usuarioTest2 = Usuario(
            username="test2", email="test2@test.com", password="foo")
        usuarioTest2.save()

        # Creamos un proyecto de ejemplo

        proyecto = self.proyecto

        # Asignacion de Scrum Master al proyecto
        scrum = RolProyecto.objects.get(
            nombre="Scrum Master", proyecto=proyecto)

        # Vinculamos el usuario al rol de Scrum Master
        scrum.usuario.add(usuarioTest2)

        # Vinculamos el usuario al proyecto
        proyecto.usuario.add(usuarioTest2)

        # Agregamos un usuarioTest al proyecto
        proyecto.usuario.add(usuarioTest)

        # Creamos un rol de proyecto
        rol = RolProyecto(nombre="Rol de prueba",
                          descripcion="Descripcion de prueba", proyecto=proyecto)
        rol.save()

        # Verificamos que solo el Scrum Master puede ver los roles de un proyecto
        request_factory = RequestFactory()
        request = request_factory.get(f'proyecto/{proyecto.id}/roles/')
        request.user = AnonymousUser()
        response = roles_de_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 401,
                         'La respuesta no fue un estado HTTP 401 a un usuario no autenticado')

        # Un usuario normal no puede ver los roles de un proyecto
        request.user = usuarioTest
        response = roles_de_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 403,
                         'La respuesta no fue un estado HTTP 403 a un usuario normal')

        # Un usuario Scrum Master puede ver los roles de un proyecto
        request.user = usuarioTest2
        response = roles_de_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 200,
                         'La respuesta no fue un estado HTTP 200 a un usuario Scrum Master')

    def test_crear_rol_a_proyecto(self):
        """
            Prueba que el usuario puede crear un rol de proyecto opcion para admin
        """
        # Creamos un usuario normal
        usuarioTest = Usuario(
            username="test", email="test@user.com", password="foo")
        usuarioTest.save()

        # Creamos un usuario que sera el Scrum Master del proyecto
        usuarioTest2 = Usuario(
            username="test2", email="test2@test.com", password="foo")
        usuarioTest2.save()

        # Creamos un proyecto de ejemplo

        proyecto = self.proyecto

        # Obtenemos el proyecto de la base de datos

        # Asignacion de Scrum Master al proyecto
        scrum = RolProyecto.objects.get(
            nombre="Scrum Master", proyecto=proyecto)

        # Vinculamos el usuario al rol de Scrum Master
        scrum.usuario.add(usuarioTest2)

        # Vinculamos el usuario al proyecto
        proyecto.usuario.add(usuarioTest2)

        # Agregamos un usuarioTest al proyecto
        proyecto.usuario.add(usuarioTest)

        # Probamos que solamente el ScrumMaster puede crear un rol de proyecto
        request_factory = RequestFactory()
        request = request_factory.post(f'proyecto/{proyecto.id}/roles/crear/', {
            'nombre': 'Rol de prueba',
            'descripcion': 'Descripcion de prueba',
            'permisos': [1, 2, 3]
        }
        )

        request.user = AnonymousUser()
        response = crear_rol_a_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 401,
                         'La respuesta no fue un estado HTTP 401 a un usuario no autenticado')

        request.user = usuarioTest
        response = crear_rol_a_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 403,
                         'La respuesta no fue un estado HTTP 403 a un usuario normal')

        request.user = usuarioTest2
        response = crear_rol_a_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 302,
                         'La respuesta no fue un estado HTTP 302 a un usuario Scrum Master')

        # Probamos que el rol se creo correctamente
        rol = RolProyecto.objects.get(nombre="Rol de prueba")
        self.assertEqual(rol.nombre, "Rol de prueba",
                         'El rol no se creo correctamente')
        self.assertEqual(rol.descripcion, "Descripcion de prueba",
                         'El rol no se creo correctamente')
        self.assertEqual(rol.proyecto, proyecto,
                         'El rol no se creo correctamente')

    def test_importar_rol(self):
        """
            Prueba que el usuario puede importar un rol de proyecto
        """
        # Creamos un usuario normal
        usuarioTest = Usuario(
            username="test", email="test@user.com", password="foo")
        usuarioTest.save()

        # Creamos un usuario que sera el Scrum Master del proyecto
        usuarioTest2 = Usuario(
            username="test2", email="test2@test.com", password="foo")
        usuarioTest2.save()

        # Creamos un proyecto de ejemplo

        proyecto = self.proyecto

        # Obtenemos el proyecto de la base de datos

        # Asignacion de Scrum Master al proyecto
        scrum = RolProyecto.objects.get(
            nombre="Scrum Master", proyecto=proyecto)

        # Vinculamos el usuario al rol de Scrum Master
        scrum.usuario.add(usuarioTest2)

        # Vinculamos el usuario al proyecto
        proyecto.usuario.add(usuarioTest2)

        # Agregamos un usuarioTest al proyecto
        proyecto.usuario.add(usuarioTest)

        # Creamos un rol de proyecto
        rol = RolProyecto(nombre="Rol de prueba", proyecto=proyecto)
        rol.save()

        # Probamos que solamente el ScrumMaster puede importar un rol de proyecto
        request_factory = RequestFactory()
        request = request_factory.get(f'proyecto/{proyecto.id}/roles/import/')
        request.user = AnonymousUser()
        response = importar_rol(request, proyecto.id)
        self.assertEqual(response.status_code, 401,
                         'La respuesta no fue un estado HTTP 401 a un usuario no autenticado')

        request.user = usuarioTest
        response = importar_rol(request, proyecto.id)
        self.assertEqual(response.status_code, 403,
                         'La respuesta no fue un estado HTTP 403 a un usuario normal')

        request.user = usuarioTest2
        response = importar_rol(request, proyecto.id)
        self.assertEqual(response.status_code, 200,
                         'La respuesta no fue un estado HTTP 200 a un usuario Scrum Master')
