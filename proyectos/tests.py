import glob
import os
from django import setup
from historias_usuario.models import SprintInfo

from historias_usuario.views import tiposHistoriaUsuario
from django.utils.timezone import get_current_timezone
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

def limpiarStaticFiles():
        files = glob.glob('app/staticfiles/temp/*')
        for f in files:
            os.remove(f)

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
        self.assertEqual(res.status_code, 200, 'La respuesta no fue un estado HTTP 200 al intentar crear un proyecto')
        self.proyecto = Proyecto.objects.get(nombre="PROYECTO_STANDARD")

    def test_ver_proyectos(self):
        """
        Prueba que el usuario puede ver los proyectos
        """
        request_factory = RequestFactory()
        request = request_factory.get('/proyecto/')
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
        response = self.client.get('/proyecto/')
        self.assertContains(response, '<h1>Proyectos</h1>', None,
                            200,  "Usuario ve lista vacia si no es Scrum Master")
        self.assertContains(response, 'http://localhost/proyectos/crear/', 0,
                            200,  "Usuario no tiene opcion crear proyecto si no es Scrum Master")

        # Verificamos que el usuario puede ver los proyectos
        response = self.client.get('/proyecto/')
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

    def test_terminar_proyecto(self):
        """
        Prueba que el usuario puede terminar un proyecto
        """
        master = self.user
        proyecto = self.proyecto

        # Verificamos que un usuario no logueado no puede terminar un proyecto
        request_factory = RequestFactory()
        request = request_factory.get(f'proyecto/terminar/{proyecto.id}/')
        request.user = AnonymousUser()
        response = terminar_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 401,
                         'La respuesta no fue un estado HTTP 401 a un usuario no autenticado')

        # Verificamos que un usuario sin permisos no puede terminar un proyecto
        usuarioTest = Usuario(
            username="test", email='user@user.com', password='foo')
        usuarioTest.save()
        request.user = usuarioTest
        response = terminar_proyecto(request, proyecto.id)
        self.assertEqual(response.status_code, 403,
                         'La respuesta no fue un estado HTTP 403 a un usuario sin permisos')

        # Verificamos que un usuario con permisos puede terminar un proyecto
        request = request_factory.post(
            f'proyecto/{proyecto.id}/terminar', {'nombre': 'PROYECTO_STANDARD'})
        request.user = master
        response = terminar_proyecto(request, proyecto.id)
        # self.assertEqual(proyecto.estado, 'Cancelado', 'El estado del proyecto al terminar no es el correcto')
        self.assertEqual(response.status_code, 302,
                         'La respuesta no fue un estado HTTP 302 a una petición correcta')

        # Verificamos que no se puede terminar un proyecto cuando no tiene nombre correcto

        proyecto = self.proyecto

        request = request_factory.post(
            f'proyecto/terminar/{proyecto.id}/', {'nombre': 'Proyecto de prueba 2'})
        request.user = master
        response = terminar_proyecto(request, proyecto.id)
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


    def test_crear_proyecto_con_feriados(self):
        """
            Prueba de crear un proyecto con feriados
        """
        res = self.client.post("/proyecto/crear/", 
            {
                'nombre': 'Proyecto Feriados', 'descripcion': 'Proyecto con feriados', 
                'minimo_dias_sprint': '15', 'maximo_dias_sprint': '30',
                'scrumMaster': self.user.id,

                'feriados-TOTAL_FORMS': '2', 
                'feriados-INITIAL_FORMS': '0',
                'feriados-MIN_NUM_FORMS': '0', 
                'feriados-MAX_NUM_FORMS': '1000', 

                'feriados-0-descripcion': "Navidad", 
                'feriados-0-fecha': '2022-12-25', 

                'feriados-1-descripcion': "Ano nuevo", 
                'feriados-1-fecha': '2022-12-30', 
            }, follow=True)
        self.assertEqual(res.status_code, 200,
                'La respuesta no fue un estado HTTP 200 a una creacion de proyecto con feriados')
            
    def test_editar_feriados_proyecto(self):
        """
            Prueba de editar un proyecto y sus feriados
        """
        res = self.client.post("/proyecto/crear/", 
            {
                'nombre': 'Proyecto Feriados', 'descripcion': 'Proyecto con feriados', 
                'minimo_dias_sprint': '15', 'maximo_dias_sprint': '30',
                'scrumMaster': self.user.id,

                'feriados-TOTAL_FORMS': '2', 
                'feriados-INITIAL_FORMS': '0',
                'feriados-MIN_NUM_FORMS': '0', 
                'feriados-MAX_NUM_FORMS': '1000', 

                'feriados-0-descripcion': "Navidad", 
                'feriados-0-fecha': '2022-12-25', 
            }, follow=True)
        self.assertEqual(res.status_code, 200,
                'La respuesta no fue un estado HTTP 200 a una creacion de proyecto con feriados')
        
        proyecto_con_feriado = Proyecto.objects.get(nombre='Proyecto Feriados')

        res = self.client.post(f"/proyecto/{proyecto_con_feriado.id}/editar/",
            {
                'descripcion': 'Proyecto con feriados modificado', 
                'minimo_dias_sprint': '10', 'maximo_dias_sprint': '35',

                'feriados-TOTAL_FORMS': '2', 
                'feriados-INITIAL_FORMS': '0',
                'feriados-MIN_NUM_FORMS': '0', 
                'feriados-MAX_NUM_FORMS': '1000', 

                'feriados-0-descripcion': "Navidad", 
                'feriados-0-fecha': '2022-12-26', 

                'feriados-1-descripcion': "Ano nuevo", 
                'feriados-1-fecha': '2022-12-30', 
            }, follow=True)
        self.assertEqual(res.status_code, 200,
                'La respuesta no fue un estado HTTP 200 a una edicion de proyecto con feriados')

class SprintTests(TestCase):
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
        self.assertEqual(res.status_code, 200, 'La respuesta no fue un estado HTTP 200 al intentar crear un proyecto')
        self.proyecto = Proyecto.objects.get(nombre="PROYECTO_STANDARD")
        self.sprint = Sprint()
        self.sprint.nombre = 'Sprint 1'
        self.sprint.proyecto = self.proyecto
        self.sprint.duracion = 3
        self.sprint.fecha_inicio = datetime.datetime.now(tz=get_current_timezone())
        self.sprint.fecha_fin = datetime.datetime.now(tz=get_current_timezone()) + datetime.timedelta(days=7)
        self.sprint.estado = "Desarrollo"
        self.sprint.save()
        self.tipoTest = TipoHistoriaUsusario.objects.get(proyecto=self.proyecto, nombre="Default")
        self.historiaTest = HistoriaUsuario.objects.create(tipo=self.tipoTest, nombre="Test US 1", descripcion="Test US 1", proyecto=self.proyecto, up=1, bv=1)
        self.historiaTest.estado = HistoriaUsuario.Estado.CANCELADO
        self.historiaTest.tipo = self.tipoTest
        self.historiaTest.save()
    
    def test_crear_sprint_vacio(self):
        """
        Prueba de crear un sprint
        """
        res = self.client.post(f"/proyecto/{self.proyecto.id}/sprints/crear/", 
            {
                'nombre': 'Sprint 1', 'descripcion': 'Sprint 1', 'duracion': '15', f'horas_trabajadas_{self.proyecto.id}': '6',
            }, follow=True)
        self.assertEqual(res.status_code, 200,
                'La respuesta no fue un estado HTTP 200 a una creacion de sprint')

    def test_crear_sprint_con_us(self):
        """
        Prueba de crear un sprint con historias iniciales
        """
        res = self.client.post(f"/proyecto/{self.proyecto.id}/sprints/crear/", 
            {
                'nombre': 'Sprint 1', 'descripcion': 'Sprint 1', 'duracion': '15', f'horas_trabajadas_{self.proyecto.id}': '6',
                f'historia_seleccionado_{self.historiaTest.id}': '1',
                f'historia_horas_{self.historiaTest.id}': '5',
                f'desarrollador_asignado_{self.historiaTest.id}': f'{self.user.id}',
            }, follow=True)
        self.assertEqual(res.status_code, 200,
                'La respuesta no fue un estado HTTP 200 a una creacion de sprint')
    
    def test_crear_sprint_con_dev(self):
        """
        Prueba de crear un sprint con historias iniciales
        """
        res = self.client.post(f"/proyecto/{self.proyecto.id}/sprints/crear/", 
            {
                'nombre': 'Sprint 1', 'descripcion': 'Sprint 1', 'duracion': '15', f'horas_trabajadas_{self.proyecto.id}': '6',
                f'desarrollador_asignado_{self.historiaTest.id}': f'{self.user.id}',
            }, follow=True)
        self.assertEqual(res.status_code, 200,
                'La respuesta no fue un estado HTTP 200 a una creacion de sprint')
    
    def test_agregar_us_backlog_sprint(self):
        """
        Prueba de agregar un US al backlog del sprint
        """
        self.sprint.estado = "Planificado"
        self.sprint.save()

        res = self.client.post(f"/proyecto/{self.proyecto.id}/sprints/{self.sprint.id}/backlog/", 
            {
                'historia_id': self.historiaTest.id
            }, follow=True)
        self.assertEqual(res.status_code, 200,
                'La respuesta no fue un estado HTTP 200 a una creacion de sprint')

        res = self.client.post(f"/proyecto/{self.proyecto.id}/sprints/{self.sprint.id}/agregar_historias/",
            {
                f'historia_seleccionado_{self.historiaTest.id}': '1',
                f'historia_horas_{self.historiaTest.id}': '5',
                f'desarrollador_asignado_{self.historiaTest.id}': f'{self.user.id}',

            }, follow=True)
        self.assertEqual(res.status_code, 200,
                'La respuesta no fue un estado HTTP 200 a una creacion de sprint')
    
    def test_cambiar_horas_desarrollador(self):
        """
        Prueba cambiar la capacidad de un desarrollador
        """
        
        self.sprint.estado = "Planificado"
        self.sprint.save()

        res = self.client.post(f"/proyecto/{self.proyecto.id}/sprints/{self.sprint.id}/editar_miembros/",
            {
                f'horas_trabajadas_{self.user.id}': '20'
            }, follow=True)
        self.assertEqual(res.status_code, 200,
                'La respuesta no fue un estado HTTP 200 a una creacion de sprint')

    def test_cambiar_horas_desarrollador_negativo(self):
        """
        Prueba cambiar la capacidad de un desarrollador
        """
        
        self.sprint.estado = "Planificado"
        self.sprint.save()
        
        res = self.client.post(f"/proyecto/{self.proyecto.id}/sprints/{self.sprint.id}/editar_miembros/",
            {
                f'horas_trabajadas_{self.user.id}': '-20'
            }, follow=True)
        self.assertEqual(res.status_code, 422,
                'La respuesta no fue un estado HTTP 422 con horas negativas')
    
    def test_prioridad_sin_previo(self):
        """
        Prueba calcular prioridad sin previo sprint
        """
        self.historiaTest.sprint = None
        self.historiaTest.estado = HistoriaUsuario.Estado.ACTIVO
        self.assertEqual(self.historiaTest.getPrioridad(), 1,
                'Con BV == UP prioridad debería ser == BV == UP')

    def test_prioridad_sin_previo_porcentajes(self):
        """
        Prueba calcular prioridad sin previo sprint y porcentajes diferentes
        """
        self.historiaTest.bv = 20
        self.historiaTest.up = 10
        self.historiaTest.sprint = None
        self.historiaTest.estado = HistoriaUsuario.Estado.ACTIVO
        self.assertEqual(self.historiaTest.getPrioridad(), self.historiaTest.bv*0.6+self.historiaTest.up*0.4,
                'BV debería ser 0.6 la prioriad')

    def test_prioridad_con_previo(self):
        """
        Prueba calcular prioridad con un sprint previo
        """
        info = SprintInfo()
        info.versionEnHistorial = self.historiaTest
        info.historia = self.historiaTest
        info.sprint = self.sprint
        info.save()
        self.historiaTest.sprint = None
        self.historiaTest.estado = HistoriaUsuario.Estado.ACTIVO
        self.assertEqual(self.historiaTest.getPrioridad(), 31,
                'Al haber estado en sprint anterior la prioridad recibe +30')

    def test_prioridad_varios_previo(self):
        """
        Prueba calcular prioridad con varios sprints previos
        """
        info = SprintInfo()
        info.versionEnHistorial = self.historiaTest
        info.historia = self.historiaTest
        info.sprint = self.sprint
        info.save()
        info2 = SprintInfo()
        info2.versionEnHistorial = self.historiaTest
        info2.historia = self.historiaTest
        info2.sprint = self.sprint
        info2.save()
        info3 = SprintInfo()
        info3.versionEnHistorial = self.historiaTest
        info3.historia = self.historiaTest
        info3.sprint = self.sprint
        info3.save()
        self.historiaTest.sprint = None
        self.historiaTest.estado = HistoriaUsuario.Estado.ACTIVO
        self.assertEqual(self.historiaTest.getPrioridad(), 31,
                'El +30 por haber estad en sprint se aplica solamente una vez')
    
    def test_prioridad_en_sprint(self):
        """
        Prueba que prioridad es -1 para historias en un Sprint
        """
        self.historiaTest.sprint = self.sprint
        self.historiaTest.estado = HistoriaUsuario.Estado.ACTIVO
        self.assertEqual(self.historiaTest.getPrioridad(), -1,
                'La historia en un sprint tiene prioridad -1')
    
    def test_prioridad_cancelado(self):
        """
        Prueba que prioridad es -1 para historias canceladas
        """
        self.historiaTest.sprint = self.sprint
        self.historiaTest.estado = HistoriaUsuario.Estado.CANCELADO
        self.assertEqual(self.historiaTest.getPrioridad(), -1,
                'La historia cancelada tiene prioridad -1')
    
    def test_prioridad_terminado(self):
        """
        Prueba que prioridad es -1 para historias terminadas
        """
        self.historiaTest.sprint = self.sprint
        self.historiaTest.estado = HistoriaUsuario.Estado.TERMINADO
        self.assertEqual(self.historiaTest.getPrioridad(), -1,
                'La historia terminada tiene prioridad -1')
    
    def test_prioridad_snapshot(self):
        """
        Prueba que prioridad es -1 para historias snapshot
        """
        self.historiaTest.sprint = self.sprint
        self.historiaTest.estado = HistoriaUsuario.Estado.SNAPSHOT
        self.assertEqual(self.historiaTest.getPrioridad(), -1,
                'La historia snapshot tiene prioridad -1')
    
    def test_terminar_sprint(self):
        """
        Prueba para terminar un sprint
        """
        
        res = self.client.post(f"/proyecto/{self.proyecto.id}/tablero/{self.historiaTest.tipo.id}/",
            {
                'terminar' : 'terminar'
            }, follow=True)
        self.assertEqual(res.status_code, 200,
                'La respuesta no fue un estado HTTP 200 al terminar un sprint')
        
        res = self.client.get(f"/proyecto/{self.proyecto.id}/sprints/list/")
        self.assertContains(res, 'Terminado', 1,
                            200, "No se cambió a estado terminado")

        limpiarStaticFiles()
            

    def test_comenzar_sprint(self):
        """
        Prueba para comenzar un sprint
        """
        
        self.sprint2 = Sprint()
        self.sprint2.nombre = 'Sprint 1'
        self.sprint2.proyecto = self.proyecto
        self.sprint2.duracion = 3
        self.sprint2.estado = "Planificado"
        self.sprint2.save()
        self.historiaTest2 = HistoriaUsuario.objects.create(tipo=self.tipoTest, nombre="Test US 2", descripcion="Test US 2", proyecto=self.proyecto, up=1, bv=1)
        self.historiaTest2.tipo = self.tipoTest
        self.historiaTest2.save()

        self.client.post(f"/proyecto/{self.proyecto.id}/tablero/{self.historiaTest.tipo.id}/",
            {
                'terminar' : 'terminar'
            }, follow=True)

        res = self.client.post(f"/proyecto/{self.proyecto.id}/sprints/{self.sprint2.id}/backlog/",
            {
                'comenzar' : 'comenzar'
            }, follow=True)

        self.assertEqual(res.status_code, 200,
                'La respuesta no fue un estado HTTP 200 al inciar un sprint')
        
        res = self.client.get(f"/proyecto/{self.proyecto.id}/sprints/list/")
        self.assertContains(res, 'Desarrollo', 1,
                            200, "No inicia el sprint correctamente")

        
    def test_ver_tablero_otros_sprints(self):
        """
        Prueba visualizar sprint terminado en tablero teniendo ya un sprint empezado
        """

        self.sprint2 = Sprint()
        self.sprint2.nombre = 'Sprint 1'
        self.sprint2.proyecto = self.proyecto
        self.sprint2.duracion = 3
        self.sprint2.estado = "Planificado"
        self.sprint2.save()
        self.historiaTest2 = HistoriaUsuario.objects.create(tipo=self.tipoTest, nombre="Test US 2", descripcion="Test US 2", proyecto=self.proyecto, up=1, bv=1)
        self.historiaTest2.tipo = self.tipoTest
        self.historiaTest2.save()
        self.historiaTest2.sprint = self.sprint2
        self.historiaTest2.etapa = self.tipoTest.etapas.all()[0]
        self.historiaTest2.save()

        self.client.post(f"/proyecto/{self.proyecto.id}/tablero/{self.historiaTest.tipo.id}/",
            {
                'terminar' : 'terminar'
            }, follow=True)

        res = self.client.post(f"/proyecto/{self.proyecto.id}/sprints/{self.sprint2.id}/backlog/",
            {
                'comenzar' : 'comenzar'
            }, follow=True)
        self.assertEqual(res.status_code, 200,
                'La respuesta no fue un estado HTTP 200 al inciar un sprint')
        
        res = self.client.post(f"/proyecto/{self.proyecto.id}/tablero/{self.historiaTest2.tipo.id}/",
                               data={'sprintId': self.sprint2.id}, follow=True)
        
        self.assertContains(res, '<span class="lead font-weight-light">Test US 2</span>', 1,
                            200, "No visualiza correctamente el sprint")
                        
    def test_cancelar_sprint(self):
        """
        Prueba para cancelar un sprint
        """
        
        self.sprint3 = Sprint()
        self.sprint3.nombre = 'Sprint 1'
        self.sprint3.proyecto = self.proyecto
        self.sprint3.duracion = 3
        self.sprint3.estado = "Planificado"
        self.sprint3.save()

        self.client.post(f"/proyecto/{self.proyecto.id}/tablero/{self.historiaTest.tipo.id}/",
            {
                'terminar' : 'terminar'
            }, follow=True)

        res = self.client.post(f"/proyecto/{self.proyecto.id}/sprints/{self.sprint3.id}/backlog/",
            {
                'cancelar' : 'Cancelar'
            }, follow=True)

        self.assertEqual(res.status_code, 200,
                'La respuesta no fue un estado HTTP 200 al inciar un sprint')
        
        res = self.client.get(f"/proyecto/{self.proyecto.id}/sprints/list/")
        self.assertContains(res, 'Cancelado', 1,
                            200, "No se cancelo el sprint correctamente")

        limpiarStaticFiles()

    def test_comenzar_sprint_mover_a_primera_etapa(self):
        """
        Prueba para comenzar un sprint
        """
        self.client.post(f"/proyecto/{self.proyecto.id}/tablero/{self.historiaTest.tipo.id}/",
            {
                'terminar' : 'terminar'
            }, follow=True)
        
        historiaTest3 = HistoriaUsuario(tipo=self.tipoTest, nombre="Test US 3", descripcion="Test US 3", proyecto=self.proyecto, up=50, bv=50)
        historiaTest3.save()

        res = self.client.post(f"/proyecto/{self.proyecto.id}/sprints/crear/", 
            {
                'nombre': 'Sprint 4', 'descripcion': 'Sprint 4', 'duracion': '15', 
                f'horas_trabajadas_{self.proyecto.id}': '6',
                f'historia_seleccionado_{historiaTest3.id}': '1',
                f'historia_horas_{historiaTest3.id}': '5',
                f'desarrollador_asignado_{historiaTest3.id}': f'{self.user.id}',
            }, follow=True)
        self.assertEqual(res.status_code, 200,
                'La respuesta no fue un estado HTTP 200 a una creacion de sprint')
        self.sprint4 = Sprint.objects.get(nombre="Sprint 4")
        self.client.post(f"/proyecto/{self.proyecto.id}/sprints/{self.sprint4.id}/backlog/",
        {
            'comenzar' : 'Comenzar'
        }, follow=True)

        self.assertEqual(HistoriaUsuario.objects.get(id=historiaTest3.id).etapa, self.tipoTest.etapas.get(orden=0),
                'La historia no se fue a la primera etapa al momento de inicar el sprint')

        limpiarStaticFiles()

    def test_ver_burndown_chart(self):
        """
        Prueba para ver si carga el burndown chart
        """
        
        res = self.client.post(f"/proyecto/{self.proyecto.id}/tablero/{self.historiaTest.tipo.id}/",
            {
                'terminar' : 'terminar'
            }, follow=True)
        self.assertEqual(res.status_code, 200,
                'La respuesta no fue un estado HTTP 200 al terminar un sprint')
        
        res = self.client.get(f"/proyecto/{self.proyecto.id}/sprints/list/", follow=True)
        self.assertContains(res, f'src="/static/bdChart_{self.proyecto.id}_{self.sprint.id}.png"', 1,
                            200, "No reconoce el path correcto")

        self.assertEqual(True, os.path.isfile(f"app/staticfiles/bdChart_{self.proyecto.id}_{self.sprint.id}.png"), "No existe archivo en path")

        limpiarStaticFiles()

    def test_descargar_burndown_chart(self):
        """
        Prueba para ver si descarga el burndown chart
        """

        res = self.client.post(f"/proyecto/{self.proyecto.id}/tablero/{self.historiaTest.tipo.id}/",
            {
                'terminar' : 'terminar'
            }, follow=True)
        self.assertEqual(res.status_code, 200,
                'La respuesta no fue un estado HTTP 200 al terminar un sprint')
        
        res = self.client.post(f"/proyecto/{self.proyecto.id}/sprints/list/",
            {
                'descargarBurndown' : self.sprint.id
            }, follow=True)
        self.assertEqual(res.status_code, 200,
                'La respuesta no fue un estado HTTP 200 al descargar el burndown chart')

        limpiarStaticFiles()

    def test_descargar_velocity_chart(self):
        """
        Prueba para ver si descarga el velocity chart
        """

        res = self.client.post(f"/proyecto/{self.proyecto.id}/tablero/{self.historiaTest.tipo.id}/",
            {
                'terminar' : 'terminar'
            }, follow=True)
        self.assertEqual(res.status_code, 200,
                'La respuesta no fue un estado HTTP 200 al terminar un sprint')

        res = self.client.post(f"/proyecto/{self.proyecto.id}/sprints/list/",
            {
                'descargarVelocity' : self.proyecto.id
            }, follow=True)
        self.assertEqual(res.status_code, 200,
                'La respuesta no fue un estado HTTP 200 al descargar el velocity chart')
    
        limpiarStaticFiles()

    def test_ver_velocity_chart(self):
        """
        Prueba para ver si carga el velocity chart
        """
        
        res = self.client.post(f"/proyecto/{self.proyecto.id}/tablero/{self.historiaTest.tipo.id}/",
            {
                'terminar' : 'terminar'
            }, follow=True)
        self.assertEqual(res.status_code, 200,
                'La respuesta no fue un estado HTTP 200 al terminar un sprint')
        
        res = self.client.get(f"/proyecto/{self.proyecto.id}/sprints/list/", follow=True)
        self.assertContains(res, f'src="/static/vlChart_{self.proyecto.id}.png"', 1,
                            200, "No reconoce el path correcto")

        self.assertEqual(True, os.path.isfile(f"app/staticfiles/vlChart_{self.proyecto.id}.png"), "No existe archivo en path")

        limpiarStaticFiles()

    def test_set_fecha_finalizacion(self):
        res = self.client.post(f"/proyecto/{self.proyecto.id}/tablero/{self.historiaTest.tipo.id}/",
        {
            'terminar' : 'terminar'
        }, follow=True)
        
        res = self.client.post(f"/proyecto/{self.proyecto.id}/sprints/crear/", 
        {
            'nombre': 'Sprint prueba fecha fin', 'descripcion': 'Sprint 1', 'duracion': '15', f'horas_trabajadas_{self.proyecto.id}': '6',
        }, follow=True)
        self.assertEqual(res.status_code, 200,
                'La respuesta no fue un estado HTTP 200 a una creacion de sprint')
                
        id = Sprint.objects.get(nombre="Sprint prueba fecha fin").id
        self.client.post(f"/proyecto/{self.proyecto.id}/sprints/{id}/backlog/",
        {
            'comenzar' : 'Comenzar'
        }, follow=True)
        
        sprint_a_finalizar = Sprint.objects.get(nombre="Sprint prueba fecha fin")
        
        res = self.client.post(f"/proyecto/{self.proyecto.id}/tablero/{self.historiaTest.tipo.id}/",
            {
                'terminar' : 'terminar'
            }, follow=True)

        sprint_finalizado = Sprint.objects.get(nombre="Sprint prueba fecha fin")
        
        self.assertNotEqual(sprint_a_finalizar.fecha_fin, sprint_finalizado.fecha_fin,"La fecha finalizacion no se establecio correctamente")

        limpiarStaticFiles()

    def test_estados_proyecto(self):
        res = self.client.post(f"/proyecto/{self.proyecto.id}/tablero/{self.historiaTest.tipo.id}/",
        {
            'terminar' : 'terminar'
        }, follow=True)
        
        self.assertEqual(self.proyecto.estado, "Planificacion")
        
        res = self.client.post(f"/proyecto/{self.proyecto.id}/sprints/crear/", 
        {
            'nombre': 'Sprint prueba estados proyecto', 'descripcion': 'Sprint 1', 'duracion': '15', f'horas_trabajadas_{self.proyecto.id}': '6',
        }, follow=True)
        self.assertEqual(res.status_code, 200,
                'La respuesta no fue un estado HTTP 200 a una creacion de sprint')
        
        id = Sprint.objects.get(nombre="Sprint prueba estados proyecto").id
        self.client.post(f"/proyecto/{self.proyecto.id}/sprints/{id}/backlog/",
        {
            'comenzar' : 'Comenzar'
        }, follow=True)
        
        proyecto1 = Proyecto.objects.get(id=self.proyecto.id)
        self.assertEqual(proyecto1.estado, "Ejecución")
    
        res = self.client.post(f"/proyecto/{self.proyecto.id}/tablero/{self.historiaTest.tipo.id}/",
        {
            'terminar' : 'terminar'
        }, follow=True)
        
        proyecto1 = Proyecto.objects.get(id=self.proyecto.id)
        self.assertEqual(proyecto1.estado, "Planificación")

        limpiarStaticFiles()
    

class ReemplazarTests(TestCase):
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
        self.assertEqual(res.status_code, 200, 'La respuesta no fue un estado HTTP 200 al intentar crear un proyecto')
        self.proyecto = Proyecto.objects.get(nombre="PROYECTO_STANDARD")
        self.sprint = Sprint()
        self.sprint.nombre = 'Sprint 1'
        self.sprint.proyecto = self.proyecto
        self.sprint.duracion = 3
        self.sprint.fecha_inicio = datetime.datetime.now(tz=get_current_timezone())
        self.sprint.fecha_fin = datetime.datetime.now(tz=get_current_timezone()) + datetime.timedelta(days=7)
        self.sprint.estado = "Desarrollo"
        self.sprint.save()
        self.tiempoEnSprint = UsuarioTiempoEnSprint()
        self.tiempoEnSprint.usuario = self.user
        self.tiempoEnSprint.sprint = self.sprint
        self.tiempoEnSprint.horas = 10
        self.tiempoEnSprint.save()
        self.tipoTest = TipoHistoriaUsusario.objects.get(proyecto=self.proyecto, nombre="Default")
        self.historiaTest = HistoriaUsuario.objects.create(tipo=self.tipoTest, nombre="Test US 1", descripcion="Test US 1", proyecto=self.proyecto, up=1, bv=1)
        self.historiaTest.tipo = self.tipoTest
        self.historiaTest.usuarioAsignado = self.user
        self.historiaTest.save()
        self.sprint.historias.add(self.historiaTest)
        self.sprint.save()
        self.assertEqual(self.historiaTest.usuarioAsignado, self.user)
    
    def test_reemplazar_no_miembro_proyecto_ui(self):
        """
        Prueba que un usuario que no es miembro del proyecto no puede ser reemplazado.
        """
        user = get_user_model().objects.create_user(email='testemail2@example.com', password='A123B456c.',
                                                    avatar_url='avatar2@example.com', direccion='Calle 1 # 2 - 3', telefono=PhoneNumber.from_string('0983 738040'))
        res = self.client.post(f"/proyecto/{self.sprint.proyecto.id}/sprints/{self.sprint.id}/reemplazar_miembro/", {"usuario_sale": self.user.id, "usuario_entra": user.id}, follow=True)
        self.assertEqual(res.status_code, 422, 'Operacion prohibida retorna un estado HTTP 422')
    
    def test_reemplazar_no_miembro_sprint_ui(self):
        """
        Prueba que un usuario que no es miembro del sprint no puede ser reemplazado.
        """
        user = get_user_model().objects.create_user(email='testemail2@example.com', password='A123B456c.',
                                                    avatar_url='avatar2@example.com', direccion='Calle 1 # 2 - 3', telefono=PhoneNumber.from_string('0983 738040'))
        self.proyecto.usuario.add(user)
        res = self.client.post(f"/proyecto/{self.sprint.proyecto.id}/sprints/{self.sprint.id}/reemplazar_miembro/", {"usuario_sale": user.id, "usuario_entra": self.user.id}, follow=True)
        self.assertEqual(res.status_code, 422, 'Operacion prohibida retorna un estado HTTP 422')
    
    def test_reemplazar_con_no_miembro_proyecto_ui(self):
        """
        Prueba que un usuario no se puede reemplazar con uno que no es miembro del proyecto no puede ser reemplazado.
        """
        user = get_user_model().objects.create_user(email='testemail2@example.com', password='A123B456c.',
                                                    avatar_url='avatar2@example.com', direccion='Calle 1 # 2 - 3', telefono=PhoneNumber.from_string('0983 738040'))
        res = self.client.post(f"/proyecto/{self.sprint.proyecto.id}/sprints/{self.sprint.id}/reemplazar_miembro/", {"usuario_sale": user.id, "usuario_entra": self.user.id}, follow=True)
        self.assertEqual(res.status_code, 422, 'Operacion prohibida retorna un estado HTTP 422')
    
    def test_reemplazar_con_miembro_sprint_ui(self):
        """
        Prueba que un usuario no se puede reemplazar con uno que no es miembro del sprint no puede ser reemplazado.
        """
        user = get_user_model().objects.create_user(email='testemail2@example.com', password='A123B456c.',
                                                    avatar_url='avatar2@example.com', direccion='Calle 1 # 2 - 3', telefono=PhoneNumber.from_string('0983 738040'))
        self.proyecto.usuario.add(user)
        nuevoTiempo = UsuarioTiempoEnSprint()
        nuevoTiempo.usuario = user
        nuevoTiempo.sprint = self.sprint
        nuevoTiempo.horas = 10
        nuevoTiempo.save()

        res = self.client.post(f"/proyecto/{self.sprint.proyecto.id}/sprints/{self.sprint.id}/reemplazar_miembro/", {"usuario_sale": self.user.id, "usuario_entra": user.id}, follow=True)
        self.assertEqual(res.status_code, 422, 'Operacion prohibida retorna un estado HTTP 422')

    def test_reemplazar_miembro_ui(self):
        """
        Prueba que un usuario se puede reemplazar por otro.
        """
        user = get_user_model().objects.create_user(email='testemail2@example.com', password='A123B456c.',
                                                    avatar_url='avatar2@example.com', direccion='Calle 1 # 2 - 3', telefono=PhoneNumber.from_string('0983 738040'))
        
        self.proyecto.usuario.add(user)

        res = self.client.post(f"/proyecto/{self.sprint.proyecto.id}/sprints/{self.sprint.id}/reemplazar_miembro/", {"usuario_sale": self.user.id, "usuario_entra": user.id}, follow=True)
        self.assertEqual(res.status_code, 200, 'Se reemplazo exitosamente al usuario')
        self.historiaTest.refresh_from_db()
        self.assertEqual(self.historiaTest.usuarioAsignado, user)
    
    def test_reemplazar_miembro_proyecto_planeado_ui(self):
        """
        Prueba que un usuario que es miembro del proyecto y sprint puede ser reemplazado en un Sprint en planificacion.
        """
        user = get_user_model().objects.create_user(email='testemail2@example.com', password='A123B456c.',
                                                    avatar_url='avatar2@example.com', direccion='Calle 1 # 2 - 3', telefono=PhoneNumber.from_string('0983 738040'))

        self.proyecto.usuario.add(user)
        self.proyecto.estado = "Planificado"

        res = self.client.post(f"/proyecto/{self.sprint.proyecto.id}/sprints/{self.sprint.id}/reemplazar_miembro/", {"usuario_sale": self.user.id, "usuario_entra": user.id}, follow=True)
        self.assertEqual(res.status_code, 200, 'Se reemplazo exitosamente al usuario')

    def test_reemplazar_miembro_proyecto_desarrollado_ui(self):
        """
        Prueba que un usuario que es miembro del proyecto y sprint puede ser reemplazado en un Sprint en desarrollo.
        """
        user = get_user_model().objects.create_user(email='testemail2@example.com', password='A123B456c.',
                                                    avatar_url='avatar2@example.com', direccion='Calle 1 # 2 - 3', telefono=PhoneNumber.from_string('0983 738040'))
        
        self.proyecto.usuario.add(user)

        res = self.client.post(f"/proyecto/{self.sprint.proyecto.id}/sprints/{self.sprint.id}/reemplazar_miembro/", {"usuario_sale": self.user.id, "usuario_entra": user.id}, follow=True)
        self.assertEqual(res.status_code, 200, 'Se reemplazo exitosamente al usuario')
