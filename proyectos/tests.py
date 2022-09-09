import os
from django import setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gestion_proyectos_agile.settings")
setup()

from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.test.client import RequestFactory
from usuarios.views import *
from usuarios.models import RolSistema
from proyectos.models import Proyecto
from usuarios.views import vista_equipo
from usuarios.models import RolProyecto, Usuario

from proyectos.views import cancelar_proyecto, crear_rol_a_proyecto, importar_rol, modificar_rol_proyecto, proyectos,crear_proyecto, editar_proyecto, roles_proyecto, crear_rol_proyecto,ver_rol_proyecto, ver_roles_asignados
from proyectos.views import eliminar_rol_proyecto as eliminar_rol_proyecto_view

# Create your tests here.

class ProyectoTests(TestCase):

    fixtures = [
       "databasedump.json",
    ]

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
        self.assertContains(response, '<h1>Proyectos</h1>', None, 200,  "Usuario ve lista vacia si no es Scrum Master")
        self.assertContains(response, 'http://localhost/proyectos/crear/', 0, 200,  "Usuario no tiene opcion crear proyecto si no es Scrum Master")

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
        self.assertEqual(response.status_code, 302, 'La respuesta no fue un estado HTTP 302 a una petición correcta')

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
        rol2 = RolProyecto.objects.get(nombre='Rol de prueba modificada', proyecto=None)
        self.assertEqual(rol2.descripcion, 'Descripcion de prueba modificada', 'La descripcion del rol de proyecto no fue modificada')

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
        self.assertEqual(response.status_code, 302, 'La respuesta no fue un estado HTTP 302 a una petición correcta')

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
        self.assertEqual(response.status_code, 302, 'La respuesta no fue un estado HTTP 302 a un usuario Scrum Master')

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
        self.assertEqual(response.status_code, 302, 'La respuesta no fue un estado HTTP 302 a un usuario Scrum Master')