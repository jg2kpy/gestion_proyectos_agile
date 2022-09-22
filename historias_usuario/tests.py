from phonenumber_field.modelfields import PhoneNumber
from historias_usuario.views import tiposHistoriaUsuario
from usuarios.models import RolProyecto, Usuario
from proyectos.models import Proyecto
from usuarios.models import RolSistema
from .models import TipoHistoriaUsusario
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

        