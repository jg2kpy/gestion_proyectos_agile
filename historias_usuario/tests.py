import email
import os
from django import setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gestion_proyectos_agile.settings")
setup()


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
        res = self.client.post("/proyecto/crear/", {"nombre": "PROYECTO_STANDARD", "descripcion": "Existe en todas las pruebas", "scrumMaster": self.user.id}, follow=True)
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
        res = self.client.post("/proyecto/crear/", {"nombre": "PROYECTO_STANDARD", "descripcion": "Existe en todas las pruebas", "scrumMaster": self.user.id}, follow=True)
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

        actualizado = HistoriaUsuario.objects.get(nombre='Test US 1', descripcion='Des de Test US 1 actualizado')
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
    
    def test_visualiarHistorial(self):
        """
        Prueba de visualizar una historia de usuario en el historial
        """
        res = self.client.post(f"/proyecto/{self.proyecto.id}/historia-usuario/crear/", 
            {
                'nombre': 'Test US 1', 'descripcion': 'Des de Test US 1', 'bv': '10', 'up': '10',
                'tipo': TipoHistoriaUsusario.objects.get(nombre='Test tipo 1').id,
                'usuarioAsignado': Usuario.objects.get(email='testemail@example.com').id
            }, follow=True)
        self.assertEqual(res.status_code, 200)

        creado = HistoriaUsuario.objects.get(nombre='Test US 1')

        res = self.client.get(f"/proyecto/{self.proyecto.id}/historial/{creado.id}", follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, '<td>Test US 1</td>', 1, 200, "No se puede visualizar el rol en el historial")

    def test_terminarHistoriaUsuario(self):
        """
        Prueba de terminar una historia de usuario.
        """
        res = self.client.post(f"/proyecto/{self.proyecto.id}/historia-usuario/crear/", 
            {
                'nombre': 'Test US 1', 'descripcion': 'Des de Test US 1', 'bv': '10', 'up': '10',
                'tipo': TipoHistoriaUsusario.objects.get(nombre='Test tipo 1').id,
                'usuarioAsignado': Usuario.objects.get(email='testemail@example.com').id
            }, follow=True)

        for _ in range(4):
            actual = HistoriaUsuario.objects.get(nombre='Test US 1', estado='A')
            res = self.client.post(f"/proyecto/{self.proyecto.id}/historias/{actual.id}/", {'siguiente':'siguiente'} ,follow=True)
            self.assertEqual(res.status_code, 200)

        terminado = HistoriaUsuario.objects.get(nombre='Test US 1', estado='T')
        self.assertIsNotNone(terminado)

    def test_moverHistoriaSigEtapa(self):
        """
        Prueba de mover una historia de usuario a su siguiente etapa.
        """
        res = self.client.post(f"/proyecto/{self.proyecto.id}/historia-usuario/crear/", 
            {
                'nombre': 'Test US 1', 'descripcion': 'Des de Test US 1', 'bv': '10', 'up': '10',
                'tipo': TipoHistoriaUsusario.objects.get(nombre='Test tipo 1').id,
                'usuarioAsignado': Usuario.objects.get(email='testemail@example.com').id
            }, follow=True)

        creado = HistoriaUsuario.objects.get(nombre='Test US 1', estado='A')
        res = self.client.post(f"/proyecto/{self.proyecto.id}/historias/{creado.id}/", {'siguiente':'siguiente'}, follow=True)
        self.assertEqual(res.status_code, 200)
        res = self.client.post(f"/proyecto/{self.proyecto.id}/historias/{creado.id}/", {'siguiente':'siguiente'}, follow=True)

        movidoSig = HistoriaUsuario.objects.get(nombre='Test US 1', estado='A')
        self.assertEqual(movidoSig.etapa.nombre, 'Etapa 2', f'La historia de usuario no se movió. Está en etapa: {movidoSig.etapa.nombre}')

        res = self.client.post(f"/proyecto/{self.proyecto.id}/historias/{creado.id}/", {'anterior':'anterior'}, follow=True)
        self.assertEqual(res.status_code, 200)

        movidoAnt = HistoriaUsuario.objects.get(nombre='Test US 1', estado='A')
        self.assertEqual(movidoAnt.etapa.nombre, 'Etapa 1', f'La historia de usuario no se movió. Está en etapa: {movidoAnt.etapa.nombre}')

    def test_visualizarHistoriaUsuarioAsignada(self):
        """
        Prueba de visualizar una historia de usuario asignada a dicho usuario.
        """
        res = self.client.post(f"/proyecto/{self.proyecto.id}/historia-usuario/crear/", 
            {
                'nombre': 'Test US 1', 'descripcion': 'Des de Test US 1', 'bv': '10', 'up': '10',
                'tipo': TipoHistoriaUsusario.objects.get(nombre='Test tipo 1').id,
                'usuarioAsignado': Usuario.objects.get(email='testemail@example.com').id
            }, follow=True)
        self.assertEqual(res.status_code, 200)

        creado = HistoriaUsuario.objects.get(nombre='Test US 1', estado='A')
        self.assertEqual(self.user, creado.usuarioAsignado)

        res = self.client.get(f"/proyecto/{self.proyecto.id}/mis-historias/", follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, '<td>Test US 1</td>', 1, 200, "No se puede visualizar la historia asignada")

class TableroTest(TestCase):
    """
    Pruebas de tablero.
    """

    fixtures = [
       "databasedump.json",
    ]

    def setUp(self):
        """
        Configuración de pruebas.
        """
        self.user = get_user_model().objects.create_user(email='testemail@example.com', password='A123B456c.',
                                                         avatar_url='avatar@example.com', direccion='Calle 1 # 2 - 3', telefono=PhoneNumber.from_string('0983 738040'))

        self.client.login(email='testemail@example.com', password='A123B456c.')
        res = self.client.post("/proyecto/crear/", {"nombre": "PROYECTO_STANDARD", "descripcion": "Existe en todas las pruebas", "scrumMaster": self.user.id}, follow=True)
        self.assertEqual(res.status_code, 200)
        self.proyecto = Proyecto.objects.get(nombre="PROYECTO_STANDARD")
        self.assertIsNotNone(self.proyecto)
        self.assertTrue(self.proyecto.roles.filter(usuario=self.user, nombre="Scrum Master").exists())

        res = self.client.post(f"/proyecto/{self.proyecto.id}/tipo-historia-usuario/crear/", {'nombre': 'Test tipo 1', 'descripcion': 'Des de Test tipo 1', 'etapas-TOTAL_FORMS': '3', 'etapas-INITIAL_FORMS': '0',
                        'etapas-MIN_NUM_FORMS': '0', 'etapas-MAX_NUM_FORMS': '1000', 'etapas-0-nombre': 'Etapa 1', 'etapas-0-descripcion': "descripcion1", 'etapas-1-nombre': 'Etapa 2', 'etapas-1-descripcion': "descripcion2", 'etapas-2-nombre': 'Etapa 3', 'etapas-2-descripcion': "descripcion3"}, follow=True)
        self.assertEqual(res.status_code, 200)

        self.creado = TipoHistoriaUsusario.objects.get(nombre='Test tipo 1')
        self.assertIsNotNone(self.creado, 'El tipo de historia de usuario no existe')
        self.assertEqual(self.creado.nombre, 'Test tipo 1', 'El tipo de historia de usuario no tiene el nombre correspondiente')
        self.assertEqual(self.creado.descripcion, 'Des de Test tipo 1', 'El tipo de historia de usuario no tiene la descripcion correspondiente')
    
    def test_visualizarTablero(self):
        """
        Prueba de visualizar el tablero de un proyecto.
        """
        res = self.client.get(f"/proyecto/{self.proyecto.id}/tablero/{self.creado.id}", follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, f'<h3>{self.creado.nombre}</h3>', 1, 200, "Se puede visualizar el tablero")
    
    def test_visualizarTableroNoExistente(self):
        """
        Prueba de visualizar el tablero de un proyecto no existente.
        """
        res = self.client.get(f"/proyecto/{self.proyecto.id}/tablero/{self.creado.id+2}", follow=True)
        self.assertEqual(res.status_code, 404, "Se redirecciona a la página de error 404 para tableros no existentes")
    
    def test_visualizarTableroVacio(self):
        """
        Prueba de visualizar el tablero de un proyecto sin historias de usuario.
        """
        res = self.client.get(f"/proyecto/{self.proyecto.id}/tablero/{self.creado.id}", follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'class="card shadow-sm"', 0, 200, "Se puede visualizar el tablero vacío")
    
    def test_tableroNoMuestraEtapaNull(self):
        """
        Prueba de visualizar el tablero de un proyecto sin historias de usuario, pero existen historias en backlog.
        """
        res = self.client.get(f"/proyecto/{self.proyecto.id}/tablero/{self.creado.id}", follow=True)
        self.assertEqual(res.status_code, 200)
        historia = HistoriaUsuario.objects.create(tipo=self.creado, nombre="Test US 1", descripcion="Test US 1", proyecto=self.proyecto, up=1, bv=1, usuarioAsignado=self.user)
        historia.save()
        self.assertContains(res, 'class="card shadow-sm"', 0, 200, "Se puede visualizar el tablero vacío")
    
    def test_tableroMuestraHistoriaEnEtapa1(self):
        """
        Prueba de visualizar el tablero con historias de usuario activo.
        """
        historia = HistoriaUsuario.objects.create(tipo=self.creado, nombre="Test US 1", descripcion="Test US 1", proyecto=self.proyecto, up=1, bv=1, usuarioAsignado=self.user)
        historia.etapa = self.creado.etapas.all()[0]
        historia.estado = HistoriaUsuario.Estado.ACTIVO
        historia.save()
        res = self.client.get(f"/proyecto/{self.proyecto.id}/tablero/{self.creado.id}", follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'class="card shadow-sm"', 1, 200, "Se puede visualizar el tablero con una historia en la etapa 1")

    def test_tableroNoMuestraEtapaCancelado(self):
        """
        Prueba de visualizar el tablero de un proyecto sin historias de usuario, pero existen historias canceladas.
        """
        res = self.client.get(f"/proyecto/{self.proyecto.id}/tablero/{self.creado.id}", follow=True)
        self.assertEqual(res.status_code, 200)
        historia = HistoriaUsuario.objects.create(tipo=self.creado, nombre="Test US 1", descripcion="Test US 1", proyecto=self.proyecto, up=1, bv=1, usuarioAsignado=self.user)
        historia.etapa = self.creado.etapas.all()[0]
        historia.estado = HistoriaUsuario.Estado.CANCELADO
        historia.save()
        self.assertContains(res, 'class="card shadow-sm"', 0, 200, "Se puede visualizar el tablero vacío")

    def test_tableroNoMuestraEtapaTerminado(self):
        """
        Prueba de visualizar el tablero de un proyecto sin historias de usuario, pero existen historias canceladas.
        """
        res = self.client.get(f"/proyecto/{self.proyecto.id}/tablero/{self.creado.id}", follow=True)
        self.assertEqual(res.status_code, 200)
        historia = HistoriaUsuario.objects.create(tipo=self.creado, nombre="Test US 1", descripcion="Test US 1", proyecto=self.proyecto, up=1, bv=1, usuarioAsignado=self.user)
        historia.etapa = self.creado.etapas.all()[0]
        historia.estado = HistoriaUsuario.Estado.TERMINADO
        historia.save()
        self.assertContains(res, 'class="card shadow-sm"', 0, 200, "Se puede visualizar el tablero vacío")

class HistorialTest(TestCase):
    """
    Pruebas de historial.
    """

    fixtures = [
       "databasedump.json",
    ]

    def setUp(self):
        """
        Configuración de pruebas.
        """
        self.user = get_user_model().objects.create_user(email='testemail@example.com', password='A123B456c.',
                                                         avatar_url='avatar@example.com', direccion='Calle 1 # 2 - 3', telefono=PhoneNumber.from_string('0983 738040'))
                                                        
        get_user_model().objects.create_user(email='testemail2@example.com', password='A123B456c.',
                                                         avatar_url='avatar@example.com', direccion='Calle 1 # 2 - 3', telefono=PhoneNumber.from_string('0983 738041'))


        self.client.login(email='testemail@example.com', password='A123B456c.')
        res = self.client.post("/proyecto/crear/", {"nombre": "PROYECTO_STANDARD", "descripcion": "Existe en todas las pruebas", "scrumMaster": self.user.id}, follow=True)
        self.assertEqual(res.status_code, 200)
        self.proyecto = Proyecto.objects.get(nombre="PROYECTO_STANDARD")
        self.assertTrue(self.proyecto.roles.filter(usuario=self.user, nombre="Scrum Master").exists())

        res = self.client.post(f"/proyecto/{self.proyecto.id}/tipo-historia-usuario/crear/", {'nombre': 'Test tipo 1', 'descripcion': 'Des de Test tipo 1', 'etapas-TOTAL_FORMS': '3', 'etapas-INITIAL_FORMS': '0',
                        'etapas-MIN_NUM_FORMS': '0', 'etapas-MAX_NUM_FORMS': '1000', 'etapas-0-nombre': 'Etapa 1', 'etapas-0-descripcion': "descripcion1", 'etapas-1-nombre': 'Etapa 2', 'etapas-1-descripcion': "descripcion2", 'etapas-2-nombre': 'Etapa 3', 'etapas-2-descripcion': "descripcion3"}, follow=True)
        self.assertEqual(res.status_code, 200)

        self.tipoTest = TipoHistoriaUsusario.objects.get(nombre='Test tipo 1')
        self.assertIsNotNone(self.tipoTest, 'El tipo de historia de usuario no existe')
        self.assertEqual(self.tipoTest.nombre, 'Test tipo 1', 'El tipo de historia de usuario no tiene el nombre correspondiente')
        self.assertEqual(self.tipoTest.descripcion, 'Des de Test tipo 1', 'El tipo de historia de usuario no tiene la descripcion correspondiente')
        self.historiaTest = HistoriaUsuario.objects.create(tipo=self.tipoTest, nombre="Test US 1", descripcion="Test US 1", proyecto=self.proyecto, up=1, bv=1, usuarioAsignado=self.user)
        self.historiaTest.estado = HistoriaUsuario.Estado.CANCELADO
        self.historiaTest.save()
        self.assertEqual(HistoriaUsuario.objects.filter(tipo=self.tipoTest).count(), 1, 'Se creo la historia de usuario')

    def test_guardarConHistorial(self):
        """
        Prueba de guardar un tipo de historia de usuario con historial.
        """
        self.historiaTest.guardarConHistorial()
        self.assertEqual(HistoriaUsuario.objects.filter(tipo=self.tipoTest).count(), 2, 'Se creo una copia de la historia de usuario')
        historiaHistorial = HistoriaUsuario.objects.filter(tipo=self.tipoTest).get(estado=HistoriaUsuario.Estado.HISTORIAL)
        self.assertIsNotNone(historiaHistorial, 'Se creo la historia de usuario historial')
        self.assertEqual(self.historiaTest.nombre, historiaHistorial.nombre, 'El nombre de la historia de usuario historial es igual al original')
        self.assertEqual(self.historiaTest.descripcion, historiaHistorial.descripcion, 'La descripcion de la historia de usuario historial es igual al original')
        self.assertEqual(self.historiaTest.proyecto, historiaHistorial.proyecto, 'El proyecto de la historia de usuario historial es igual al original')
        self.assertEqual(self.historiaTest.usuarioAsignado, historiaHistorial.usuarioAsignado, 'El usuario asignado de la historia de usuario historial es igual al original')
    
    def test_restaurarHistorial(self):
        """
        Prueba de restaurar un tipo de historia de usuario con historial.
        """
        self.historiaTest.guardarConHistorial()
        self.historiaTest.nombre = self.historiaTest.nombre + " modificado"
        self.historiaTest.save()
        historiaHistorial = HistoriaUsuario.objects.filter(tipo=self.tipoTest).get(estado=HistoriaUsuario.Estado.HISTORIAL)
        self.assertNotEqual(self.historiaTest.nombre, historiaHistorial.nombre, 'El nombre de la historia de usuario es diferente al historial')
        self.historiaTest.restaurarDelHistorial(historiaHistorial)
        self.assertEqual(HistoriaUsuario.objects.filter(tipo=self.tipoTest).count(), 3, 'Restaurar la historia de usuario a su vez se guarda en el historial')
        self.assertEqual(self.historiaTest.nombre, historiaHistorial.nombre, 'El nombre de la historia de usuario es igual al historial restaurado')
