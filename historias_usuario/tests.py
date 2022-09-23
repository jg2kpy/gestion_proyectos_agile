from phonenumber_field.modelfields import PhoneNumber
from historias_usuario.views import tiposHistoriaUsuario
from usuarios.models import RolProyecto, Usuario
from proyectos.models import Proyecto
from usuarios.models import RolSistema
from .models import HistoriaUsuario, TipoHistoriaUsusario
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.auth import get_user_model
from django.test.client import RequestFactory
from django.test import TestCase
import os
from django import setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gestion_proyectos_agile.settings")
setup()

class TiposHistoriasUsuarioTest(TestCase):
    """
    Pruebas unitarias relacionadas al manejo de tipos de historias de usuario.
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

    def test_crearTipoHistoriaUsuario(self):
        """
        Crea una historia de usuario para realizar las pruebas.
        """
        res = self.client.post(f"/proyecto/{self.proyecto.id}/tipo-historia-usuario/crear/", {'nombre': 'Test', 'descripcion': 'etapa prueba', 'etapas-TOTAL_FORMS': '1', 'etapas-INITIAL_FORMS': '0',
                        'etapas-MIN_NUM_FORMS': '0', 'etapas-MAX_NUM_FORMS': '1000', 'etapas-0-nombre': 'Etapa 1', 'etapas-0-descripcion': "descripcion1"}, follow=True)
        self.assertEqual(res.status_code, 200)
        creado = TipoHistoriaUsusario.objects.get(nombre='Test')
        self.assertIsNotNone(creado)
        self.assertEqual(creado.nombre, 'Test')
        self.assertEqual(creado.descripcion, 'etapa prueba')
        self.assertEqual(creado.etapas.all()[0].descripcion, 'descripcion1')
        self.assertEqual(creado.etapas.all()[0].nombre, 'Etapa 1')

    def test_editarTipoHistoriaUsuario(self):
        """
        Edita un tipo de historia de usuario pero no sus etapas.
        """
        self.client.post(f"/proyecto/{self.proyecto.id}/tipo-historia-usuario/crear/", {'nombre': 'Test', 'descripcion': 'etapa prueba', 'etapas-TOTAL_FORMS': '1', 'etapas-INITIAL_FORMS': '0',
                        'etapas-MIN_NUM_FORMS': '0', 'etapas-MAX_NUM_FORMS': '1000', 'etapas-0-nombre': 'Etapa 1', 'etapas-0-descripcion': "descripcion1"}, follow=True)
        creado = TipoHistoriaUsusario.objects.get(nombre='Test')
        res = self.client.post(f"/proyecto/{self.proyecto.id}/tipo-historia-usuario/{creado.id}/editar/", {'nombre': 'Testedit', 'descripcion': 'etapa prueba edit', 'etapas-TOTAL_FORMS': '1', 'etapas-INITIAL_FORMS': '0',
                        'etapas-MIN_NUM_FORMS': '0', 'etapas-MAX_NUM_FORMS': '1000', 'etapas-0-nombre': 'Etapa 1', 'etapas-0-descripcion': "descripcion1"}, follow=True)
        self.assertEqual(res.status_code, 200)
        creado.refresh_from_db()
        self.assertEqual(creado.nombre, 'Testedit')
        self.assertEqual(creado.descripcion, 'etapa prueba edit')
        self.assertEqual(creado.etapas.all()[0].descripcion, 'descripcion1')
        self.assertEqual(creado.etapas.all()[0].nombre, 'Etapa 1')
        
    def test_agregarEtapaTipoHistoriaUsuario(self):
        """
        Edita un tipo de historia de usuario pero no sus etapas.
        """
        self.client.post(f"/proyecto/{self.proyecto.id}/tipo-historia-usuario/crear/", {'nombre': 'Test', 'descripcion': 'etapa prueba', 'etapas-TOTAL_FORMS': '1', 'etapas-INITIAL_FORMS': '0',
                        'etapas-MIN_NUM_FORMS': '0', 'etapas-MAX_NUM_FORMS': '1000', 'etapas-0-nombre': 'Etapa 1', 'etapas-0-descripcion': "descripcion1"}, follow=True)
        creado = TipoHistoriaUsusario.objects.get(nombre='Test')
        res = self.client.post(f"/proyecto/{self.proyecto.id}/tipo-historia-usuario/{creado.id}/editar/", {'nombre': 'Test', 'descripcion': 'etapa prueba', 'etapas-TOTAL_FORMS': '2', 'etapas-INITIAL_FORMS': '0',
                        'etapas-MIN_NUM_FORMS': '0', 'etapas-MAX_NUM_FORMS': '1000', 'etapas-0-nombre': 'Etapa 1', 'etapas-0-descripcion': "descripcion1", 'etapas-1-nombre': 'Etapa 2', 'etapas-1-descripcion': "descripcion2"}, follow=True)
        self.assertEqual(res.status_code, 200)
        creado = TipoHistoriaUsusario.objects.get(nombre='Test')
        self.assertIsNotNone(creado)
        self.assertEqual(creado.nombre, 'Test')
        self.assertEqual(creado.descripcion, 'etapa prueba')
        self.assertEqual(creado.etapas.all()[0].descripcion, 'descripcion1')
        self.assertEqual(creado.etapas.all()[0].nombre, 'Etapa 1')
        self.assertEqual(creado.etapas.all()[1].descripcion, 'descripcion2')
        self.assertEqual(creado.etapas.all()[1].nombre, 'Etapa 2')

    def test_eliminarEtapaTipoHistoriaUsuario(self):
        """
        Edita un tipo de historia de usuario pero no sus etapas.
        """
        self.client.post(f"/proyecto/{self.proyecto.id}/tipo-historia-usuario/crear/", {'nombre': 'Test', 'descripcion': 'etapa prueba', 'etapas-TOTAL_FORMS': '1', 'etapas-INITIAL_FORMS': '0',
                        'etapas-MIN_NUM_FORMS': '0', 'etapas-MAX_NUM_FORMS': '1000', 'etapas-0-nombre': 'Etapa 1', 'etapas-0-descripcion': "descripcion1"}, follow=True)
        creado = TipoHistoriaUsusario.objects.get(nombre='Test')
        res = self.client.post(f"/proyecto/{self.proyecto.id}/tipo-historia-usuario/{creado.id}/editar/", {'nombre': 'Test', 'descripcion': 'etapa prueba', 'etapas-TOTAL_FORMS': '0', 'etapas-INITIAL_FORMS': '0',
                        'etapas-MIN_NUM_FORMS': '0', 'etapas-MAX_NUM_FORMS': '1000'}, follow=True)
        self.assertEqual(res.status_code, 200)
        creado = TipoHistoriaUsusario.objects.get(nombre='Test')
        self.assertIsNotNone(creado)
        self.assertEqual(creado.nombre, 'Test')
        self.assertEqual(creado.descripcion, 'etapa prueba')
        self.assertEqual(creado.etapas.count(), 0)


class HistoriasUsuarioTest(TestCase):
    """
    Pruebas unitarias relacionadas al manejo de historias de usuario.
    """

    fixtures = [
       "databasedump.json",
    ]

    def setUp(self):
        """
        Crea dos usuarios, un proyecto y un tipo de historia de usuario para realizar las pruebas.
        """

        self.user = get_user_model().objects.create_user(email='testemail@example.com', password='A123B456c.',
                                                         avatar_url='avatar@example.com', direccion='Calle 1 # 2 - 3', telefono=PhoneNumber.from_string('0983 738040'))
                                                        
        get_user_model().objects.create_user(email='testemail2@example.com', password='A123B456c.',
                                                         avatar_url='avatar@example.com', direccion='Calle 1 # 2 - 3', telefono=PhoneNumber.from_string('0983 738041'))


        self.client.login(email='testemail@example.com', password='A123B456c.')
        res = self.client.post("/proyecto/crear/", {"nombre": "PROYECTO_STANDARD", "descripcion": "Existe en todas las pruebas", "scrum_master": self.user.id})
        self.assertEqual(res.status_code, 200)
        self.proyecto = Proyecto.objects.get(nombre="PROYECTO_STANDARD")
        self.assertTrue(self.proyecto.roles.filter(usuario=self.user, nombre="Scrum Master").exists())

        res = self.client.post(f"/proyecto/{self.proyecto.id}/tipo-historia-usuario/crear/", {'nombre': 'Test tipo 1', 'descripcion': 'Des de Test tipo 1', 'etapas-TOTAL_FORMS': '3', 'etapas-INITIAL_FORMS': '0',
                        'etapas-MIN_NUM_FORMS': '0', 'etapas-MAX_NUM_FORMS': '1000', 'etapas-0-nombre': 'Etapa 1', 'etapas-0-descripcion': "descripcion1", 'etapas-1-nombre': 'Etapa 2', 'etapas-1-descripcion': "descripcion2", 'etapas-2-nombre': 'Etapa 3', 'etapas-2-descripcion': "descripcion3"}, follow=True)
        self.assertEqual(res.status_code, 200)

        creado = TipoHistoriaUsusario.objects.get(nombre='Test tipo 1')
        self.assertIsNotNone(creado, 'El tipo de historia de usuario no existe')
        self.assertEqual(creado.nombre, 'Test tipo 1', 'El tipo de historia de usuario no tiene el nombre correspondiente')
        self.assertEqual(creado.descripcion, 'Des de Test tipo 1', 'El tipo de historia de usuario no tiene la descripcion correspondiente')
    

    def test_crearHistoriaUsuario(self):
        """
        Prueba de crear una historia de usuario.
        """
        res = self.client.post(f"/proyecto/{self.proyecto.id}/historia-usuario/crear/", 
            {
                'nombre': 'Test US 1', 'descripcion': 'Des de Test US 1', 'bv': '10', 'up': '10',
                'tipo': TipoHistoriaUsusario.objects.get(nombre='Test tipo 1').id,
                'usuarioAsignado': Usuario.objects.get(email='testemail@example.com').id
            }, follow=True)
        self.assertEqual(res.status_code, 200)

        creado = HistoriaUsuario.objects.get(nombre='Test US 1')
        self.assertIsNotNone(creado, 'La historia de usuario no existe')
        self.assertEqual(creado.nombre, 'Test US 1', 'La historia de usuario recien creada no tiene el nombre correspondiente')
        self.assertEqual(creado.descripcion, 'Des de Test US 1', 'La historia de usuario recien creada no tiene la descripcion correspondiente')
        self.assertEqual(creado.bv, 10, 'La historia de usuario recien creada no tiene el BV correspondiente')
        self.assertEqual(creado.up, 10, 'La historia de usuario recien creada no tiene el UP correspondiente')
        self.assertEqual(creado.tipo, TipoHistoriaUsusario.objects.get(nombre='Test tipo 1'), 'La historia de usuario recien creada no tiene el tipo de US correspodiente')
        self.assertEqual(creado.usuarioAsignado, Usuario.objects.get(email='testemail@example.com'), 'La historia de usuario recien creada no el usuario asignado correspondiente')
    

    def test_editarHistoriaUsuario(self):
        """
        Prueba de editar una historia de usuario.
        """
        res = self.client.post(f"/proyecto/{self.proyecto.id}/historia-usuario/crear/", 
            {
                'nombre': 'Test US 1', 'descripcion': 'Des de Test US 1', 'bv': '10', 'up': '10',
                'tipo': TipoHistoriaUsusario.objects.get(nombre='Test tipo 1').id,
                'usuarioAsignado': Usuario.objects.get(email='testemail@example.com').id
            }, follow=True)

        creado = HistoriaUsuario.objects.get(nombre='Test US 1')
        res = self.client.post(f"/proyecto/{self.proyecto.id}/historia-usuario/{creado.id}/editar/", 
            {
                'descripcion': 'Des de Test US 1 actualizado', 'bv': '5', 'up': '15',
                'usuarioAsignado': Usuario.objects.get(email='testemail2@example.com').id
            }, follow=True)
        self.assertEqual(res.status_code, 200)

        actualizado = HistoriaUsuario.objects.get(nombre='Test US 1')
        self.assertIsNotNone(actualizado, 'La historia de usuario modificada no existe')
        self.assertEqual(actualizado.descripcion, 'Des de Test US 1 actualizado', 'La descripcion de la historia de usuario no fue actualizada')
        self.assertEqual(actualizado.bv, 5, 'Los BV de la historia de usuario no fue actualizada')
        self.assertEqual(actualizado.up, 15, 'Los UP de la historia de usuario no fue actualizada')
        self.assertEqual(actualizado.usuarioAsignado, Usuario.objects.get(email='testemail2@example.com'), 'El usuario asignado de la historia de usuario no fue actualizada')

    def test_cancelarHistoriaUsuario(self):
        """
        Prueba de cancelar una historia de usuario.
        """
        res = self.client.post(f"/proyecto/{self.proyecto.id}/historia-usuario/crear/", 
            {
                'nombre': 'Test US 1', 'descripcion': 'Des de Test US 1', 'bv': '10', 'up': '10',
                'tipo': TipoHistoriaUsusario.objects.get(nombre='Test tipo 1').id,
                'usuarioAsignado': Usuario.objects.get(email='testemail@example.com').id
            }, follow=True)

        creado = HistoriaUsuario.objects.get(nombre='Test US 1')
        res = self.client.post(f"/proyecto/{self.proyecto.id}/historia-usuario/{creado.id}/borrar", follow=True)
        self.assertEqual(res.status_code, 200)
        
        cancelado = HistoriaUsuario.objects.get(nombre='Test US 1')
        self.assertIsNotNone(cancelado)
        self.assertEqual(cancelado.estado, 'A', 'La historia de usuario no se paso a estado cancelado')
    
## TODO: Test de verificar si llego a la etapa de terminado
