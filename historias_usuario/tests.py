import datetime
import email
import os
from django.utils.timezone import get_current_timezone
from django import setup

from gestion_proyectos_agile.templatetags.gpa_tags import cantidad_tareas_en_etapa, horas_trabajadas_en_sprint, horas_trabajadas_en_sprint_total, trabajo_realizado_en_sprint
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gestion_proyectos_agile.settings")
setup()


from phonenumber_field.modelfields import PhoneNumber
from historias_usuario.views import tiposHistoriaUsuario
from usuarios.models import RolProyecto, Usuario
from proyectos.models import Proyecto, Sprint
from usuarios.models import RolSistema
from .models import EtapaHistoriaUsuario, HistoriaUsuario, Tarea, TipoHistoriaUsusario
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
        self.assertEqual(res.status_code, 200, 'La respuesta no fue un estado HTTP 200 al intentar crear un proyecto')
        self.proyecto = Proyecto.objects.get(nombre="PROYECTO_STANDARD")
        self.assertTrue(self.proyecto.roles.filter(usuario=self.user, nombre="Scrum Master").exists(),'No se creo el rol Scrum Master en un proyecto nuevo')

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
                'tipo': TipoHistoriaUsusario.objects.get(nombre='Test tipo 1').id
            }, follow=True)
        self.assertEqual(res.status_code, 200)

        creado = HistoriaUsuario.objects.get(nombre='Test US 1')
        self.assertIsNotNone(creado, 'La historia de usuario no existe')
        self.assertEqual(creado.nombre, 'Test US 1', 'La historia de usuario recien creada no tiene el nombre correspondiente')
        self.assertEqual(creado.descripcion, 'Des de Test US 1', 'La historia de usuario recien creada no tiene la descripcion correspondiente')
        self.assertEqual(creado.bv, 10, 'La historia de usuario recien creada no tiene el BV correspondiente')
        self.assertEqual(creado.up, 10, 'La historia de usuario recien creada no tiene el UP correspondiente')
        self.assertEqual(creado.tipo, TipoHistoriaUsusario.objects.get(nombre='Test tipo 1'), 'La historia de usuario recien creada no tiene el tipo de US correspodiente')
    

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
                'descripcion': 'Des de Test US 1 actualizado', 'bv': '5', 'up': '15'
            }, follow=True)
        self.assertEqual(res.status_code, 200)

        actualizado = HistoriaUsuario.objects.get(nombre='Test US 1', descripcion='Des de Test US 1 actualizado')
        self.assertIsNotNone(actualizado, 'La historia de usuario modificada no existe')
        self.assertEqual(actualizado.descripcion, 'Des de Test US 1 actualizado', 'La descripcion de la historia de usuario no fue actualizada')
        self.assertEqual(actualizado.bv, 5, 'Los BV de la historia de usuario no fue actualizada')
        self.assertEqual(actualizado.up, 15, 'Los UP de la historia de usuario no fue actualizada')

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
        
        creado = HistoriaUsuario.objects.get(nombre='Test US 1', estado='A')
        creado.etapa = EtapaHistoriaUsuario.objects.get(TipoHistoriaUsusario=TipoHistoriaUsusario.objects.get(nombre='Test tipo 1'), orden=1)
        creado.sprint = Sprint(proyecto=self.proyecto, fecha_inicio=datetime.datetime.now(tz=get_current_timezone()), fecha_fin=datetime.datetime.now(tz=get_current_timezone()) + datetime.timedelta(days=7), duracion=7)
        creado.usuarioAsignado = Usuario.objects.get(email='testemail@example.com')
        creado.sprint.save()
        creado.save()

        for _ in range(4):
            tarea = Tarea()
            tarea.descripcion = 'Test tarea 1'
            tarea.sprint = creado.sprint
            tarea.etapa = creado.etapa
            tarea.historia = creado
            tarea.sprint = creado.sprint
            tarea.usuario = creado.usuarioAsignado
            tarea.horas = 1
            tarea.save()
            creado.tareas.add(tarea)
            creado.save()
            res = self.client.post(f"/proyecto/{self.proyecto.id}/historias/{creado.id}/", {'siguiente':'siguiente'} ,follow=True)
            self.assertEqual(res.status_code, 200)

        terminado = HistoriaUsuario.objects.all().count()
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
        creado.etapa = EtapaHistoriaUsuario.objects.get(TipoHistoriaUsusario=TipoHistoriaUsusario.objects.get(nombre='Test tipo 1'), orden=1)
        creado.sprint = Sprint(proyecto=self.proyecto, fecha_inicio=datetime.datetime.now(tz=get_current_timezone()), fecha_fin=datetime.datetime.now(tz=get_current_timezone()) + datetime.timedelta(days=7), duracion=7)
        creado.usuarioAsignado = Usuario.objects.get(email='testemail@example.com')
        creado.sprint.save()
        tarea = Tarea()
        tarea.descripcion = 'Test tarea 1'
        tarea.sprint = creado.sprint
        tarea.etapa = creado.etapa
        tarea.historia = creado
        tarea.sprint = creado.sprint
        tarea.usuario = creado.usuarioAsignado
        tarea.horas = 1
        tarea.save()
        creado.tareas.add(tarea)
        creado.save()

        self.assertGreater(creado.tareas.filter(etapa=creado.etapa).count(), 0, 'No se pudo crear la tarea')
        res = self.client.post(f"/proyecto/{self.proyecto.id}/historias/{creado.id}/", {'siguiente':'siguiente'}, follow=True)
        self.assertEqual(res.status_code, 200)
        tarea = Tarea()
        tarea.descripcion = 'Test tarea 1'
        tarea.sprint = creado.sprint
        tarea.etapa = creado.etapa
        tarea.historia = creado
        tarea.sprint = creado.sprint
        tarea.usuario = creado.usuarioAsignado
        tarea.horas = 1
        tarea.save()
        creado.tareas.add(tarea)
        creado.save()
        res = self.client.post(f"/proyecto/{self.proyecto.id}/historias/{creado.id}/", {'siguiente':'siguiente'}, follow=True)

        movidoSig = HistoriaUsuario.objects.get(nombre='Test US 1', estado='A')
        self.assertEqual(movidoSig.etapa.nombre, 'Etapa 3', 'La historia de usuario no se movió.')

        res = self.client.post(f"/proyecto/{self.proyecto.id}/historias/{creado.id}/", {'anterior':'anterior'}, follow=True)
        self.assertEqual(res.status_code, 200)

        movidoAnt = HistoriaUsuario.objects.get(nombre='Test US 1', estado='A')
        self.assertEqual(movidoAnt.etapa.nombre, 'Etapa 2', f'La historia de usuario no se movió. Está en etapa: {movidoAnt.etapa.nombre}')
    
    def test_moverSinTareaBloqueado(self):
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
        creado.etapa = EtapaHistoriaUsuario.objects.get(TipoHistoriaUsusario=TipoHistoriaUsusario.objects.get(nombre='Test tipo 1'), orden=1)
        creado.sprint = Sprint(proyecto=self.proyecto, fecha_inicio=datetime.datetime.now(tz=get_current_timezone()), fecha_fin=datetime.datetime.now(tz=get_current_timezone()) + datetime.timedelta(days=7), duracion=7)
        creado.usuarioAsignado = Usuario.objects.get(email='testemail@example.com')
        creado.sprint.save()
        tarea = Tarea()
        tarea.descripcion = 'Test tarea 1'
        tarea.sprint = creado.sprint
        tarea.etapa = creado.etapa
        tarea.historia = creado
        tarea.sprint = creado.sprint
        tarea.usuario = creado.usuarioAsignado
        tarea.horas = 1
        tarea.save()
        creado.tareas.add(tarea)
        creado.save()

        self.assertGreater(creado.tareas.filter(etapa=creado.etapa).count(), 0, 'No se pudo crear la tarea')
        res = self.client.post(f"/proyecto/{self.proyecto.id}/historias/{creado.id}/", {'siguiente':'siguiente'}, follow=True)
        self.assertEqual(res.status_code, 200)
        res = self.client.post(f"/proyecto/{self.proyecto.id}/historias/{creado.id}/", {'siguiente':'siguiente'}, follow=True)
        self.assertNotEquals(res.status_code, 200)

        movidoAnt = HistoriaUsuario.objects.get(nombre='Test US 1', estado='A')
        self.assertEqual(movidoAnt.etapa.nombre, 'Etapa 3', f'La historia de usuario no se movió.')

    def test_visualizarHistoriaUsuarioAsignada(self):
        """
        Prueba de visualizar una historia de usuario asignada a dicho usuario.
        """
        res = self.client.post(f"/proyecto/{self.proyecto.id}/historia-usuario/crear/", 
            {
                'nombre': 'Test US 1', 'descripcion': 'Des de Test US 1', 'bv': '10', 'up': '10',
                'tipo': TipoHistoriaUsusario.objects.get(nombre='Test tipo 1').id
            }, follow=True)
        self.assertEqual(res.status_code, 200)

        creado = HistoriaUsuario.objects.get(nombre='Test US 1', estado='A')
        creado.usuarioAsignado = self.user
        creado.save()
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
        self.sprint = Sprint()
        self.sprint.nombre = 'Sprint 1'
        self.sprint.proyecto = self.proyecto
        self.sprint.duracion = 3
        self.sprint.fecha_inicio = datetime.datetime.now(tz=get_current_timezone())
        self.sprint.fecha_fin = datetime.datetime.now(tz=get_current_timezone()) + datetime.timedelta(days=7)
        self.sprint.estado = "Desarrollo"
        self.sprint.save()
    
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
        historia.sprint = self.sprint
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
        historia.sprint = self.sprint
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

class TareasTest(TestCase):
    """
    Pruebas de la clase Tarea.
    """
    def setUp(self):
        """
        Configuracion inicial de las pruebas.
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
        self.historiaTest = HistoriaUsuario.objects.create(tipo=self.tipoTest, nombre="Test US 1", descripcion="Test US 1", proyecto=self.proyecto, up=1, bv=1, usuarioAsignado=self.user, horasAsignadas=10)
        self.historiaTest.sprint = Sprint(proyecto=self.proyecto, fecha_inicio=datetime.datetime.now(tz=get_current_timezone()), fecha_fin=datetime.datetime.now(tz=get_current_timezone()) + datetime.timedelta(days=7), duracion=7)
        self.historiaTest.sprint.save()
        self.historiaTest.etapa = EtapaHistoriaUsuario.objects.get(TipoHistoriaUsusario=TipoHistoriaUsusario.objects.get(nombre='Test tipo 1'), orden=1)
        self.historiaTest.save()
        self.assertEqual(HistoriaUsuario.objects.filter(tipo=self.tipoTest).count(), 1, 'Se creo la historia de usuario')

    fixtures = [
       "databasedump.json",
    ]

    def test_crearTarea(self):
        """
        Prueba de crear una tarea.
        """
        self.assertEqual(Tarea.objects.filter(historia=self.historiaTest).count(), 0, 'No hay tareas')
        tarea1 = Tarea()
        tarea1.descripcion = 'Test tarea 1'
        tarea1.sprint = self.historiaTest.sprint
        tarea1.etapa = self.historiaTest.etapa
        tarea1.historia = self.historiaTest
        tarea1.sprint = self.historiaTest.sprint
        tarea1.usuario = self.historiaTest.usuarioAsignado
        tarea1.horas = 1
        tarea1.save()
        self.assertIsNotNone(tarea1, 'Se creo la tarea')
        self.assertEqual(Tarea.objects.filter(historia=self.historiaTest).count(), 1, 'Se creo la tarea')
    
    def test_trabajoRealizadoEnSprintVacio(self):
        """
        Prueba calcular horas de trabajo realizado en Sprint vacio
        """
        self.assertEqual(horas_trabajadas_en_sprint_total(self.historiaTest.sprint), 0, 'No hay horas de trabajo en el sprint')

    def test_trabajoRealizadoEnSprintVacio(self):
        """
        Prueba calcular horas de trabajo realizado en Sprint
        """
        tarea1 = Tarea()
        tarea1.descripcion = 'Test tarea 1'
        tarea1.sprint = self.historiaTest.sprint
        tarea1.etapa = self.historiaTest.etapa
        tarea1.historia = self.historiaTest
        tarea1.sprint = self.historiaTest.sprint
        tarea1.usuario = self.historiaTest.usuarioAsignado
        tarea1.horas = 1
        tarea1.save()
        tarea2 = Tarea()
        tarea2.descripcion = 'Test tarea 2'
        tarea2.sprint = self.historiaTest.sprint
        tarea2.etapa = self.historiaTest.etapa
        tarea2.historia = self.historiaTest
        tarea2.sprint = self.historiaTest.sprint
        tarea2.usuario = self.historiaTest.usuarioAsignado
        tarea2.horas = 4
        tarea2.save()
        self.assertEqual(horas_trabajadas_en_sprint_total(self.historiaTest.sprint), 5, 'No hay horas de trabajo en el sprint')

    def test_trabajoRealizadoEnSprintVacio(self):
        """
        Prueba calcular horas de trabajo realizado en Sprint
        """
        self.user2 = get_user_model().objects.create_user(email='testemail3@example.com', password='A123B456c.2',
                                                         avatar_url='avatar3@example.com', direccion='Calle 1 # 2 - 3', telefono=PhoneNumber.from_string('0984 738040'))
        self.user2.save()
        tarea1 = Tarea()
        tarea1.descripcion = 'Test tarea 1'
        tarea1.sprint = self.historiaTest.sprint
        tarea1.etapa = self.historiaTest.etapa
        tarea1.historia = self.historiaTest
        tarea1.sprint = self.historiaTest.sprint
        tarea1.usuario = self.user2
        tarea1.horas = 1
        tarea1.save()
        tarea2 = Tarea()
        tarea2.descripcion = 'Test tarea 2'
        tarea2.sprint = self.historiaTest.sprint
        tarea2.etapa = self.historiaTest.etapa
        tarea2.historia = self.historiaTest
        tarea2.sprint = self.historiaTest.sprint
        tarea2.usuario = self.historiaTest.usuarioAsignado
        tarea2.horas = 4
        tarea2.save()
        self.assertEqual(horas_trabajadas_en_sprint_total(self.historiaTest.sprint), 5, 'Se suman todas las tareas')

    def test_trabajoRealizadoEnSprintPorUsuario(self):
        """
        Prueba calcular horas de trabajo realizado en Sprint por usuario
        """
        self.user2 = get_user_model().objects.create_user(email='testemail3@example.com', password='A123B456c.2',
                                                         avatar_url='avatar3@example.com', direccion='Calle 1 # 2 - 3', telefono=PhoneNumber.from_string('0984 738040'))
        self.user2.save()
        tarea1 = Tarea()
        tarea1.descripcion = 'Test tarea 1'
        tarea1.sprint = self.historiaTest.sprint
        tarea1.etapa = self.historiaTest.etapa
        tarea1.historia = self.historiaTest
        tarea1.sprint = self.historiaTest.sprint
        tarea1.usuario = self.user2
        tarea1.horas = 1
        tarea1.save()
        tarea2 = Tarea()
        tarea2.descripcion = 'Test tarea 2'
        tarea2.sprint = self.historiaTest.sprint
        tarea2.etapa = self.historiaTest.etapa
        tarea2.historia = self.historiaTest
        tarea2.sprint = self.historiaTest.sprint
        tarea2.usuario = self.historiaTest.usuarioAsignado
        tarea2.horas = 4
        tarea2.save()
        self.assertEqual(horas_trabajadas_en_sprint(self.user2, self.historiaTest.sprint), 1, 'Horas trabajadas son del usuario correcto')
        self.assertEqual(horas_trabajadas_en_sprint(self.user, self.historiaTest.sprint), 4, 'Horas trabajadas son del usuario correcto')

    def test_tareasNoConsideradasEnEtapa(self):
        """
        Prueba contar las tareas en una etapa que no se consideran para mover la historia
        """
        tarea1 = Tarea()
        tarea1.descripcion = 'Test tarea 1'
        tarea1.sprint = self.historiaTest.sprint
        tarea1.etapa = self.historiaTest.etapa
        tarea1.historia = self.historiaTest
        tarea1.sprint = self.historiaTest.sprint
        tarea1.usuario = self.user2
        tarea1.horas = 1
        tarea1.considerado = True
        tarea1.save()
        tarea2 = Tarea()
        tarea2.descripcion = 'Test tarea 2'
        tarea2.sprint = self.historiaTest.sprint
        tarea2.etapa = self.historiaTest.etapa
        tarea2.historia = self.historiaTest
        tarea2.sprint = self.historiaTest.sprint
        tarea2.usuario = self.historiaTest.usuarioAsignado
        tarea2.horas = 4
        tarea2.save()
        self.assertEqual(cantidad_tareas_en_etapa(self.historiaTest), 1, 'Se conto la tarea no considerada y no se conto la tarea ya considerada, por defecto')
        self.assertEqual(cantidad_tareas_en_etapa(self.historiaTest, False), 1, 'Se conto la tarea no considerada y no se conto la tarea ya considerada')

    def test_tareasNoConsideradasEnEtapa(self):
        """
        Prueba contar las tareas en una etapa que no se consideran para mover la historia
        """
        tarea1 = Tarea()
        tarea1.descripcion = 'Test tarea 1'
        tarea1.sprint = self.historiaTest.sprint
        tarea1.etapa = self.historiaTest.etapa
        tarea1.historia = self.historiaTest
        tarea1.sprint = self.historiaTest.sprint
        tarea1.usuario = self.user
        tarea1.horas = 1
        tarea1.considerado = True
        tarea1.save()
        tarea2 = Tarea()
        tarea2.descripcion = 'Test tarea 2'
        tarea2.sprint = self.historiaTest.sprint
        tarea2.etapa = self.historiaTest.etapa
        tarea2.historia = self.historiaTest
        tarea2.sprint = self.historiaTest.sprint
        tarea2.usuario = self.historiaTest.usuarioAsignado
        tarea2.horas = 4
        tarea2.save()
        self.assertEqual(cantidad_tareas_en_etapa(self.historiaTest, True), 2, 'Se contaron todas las tareas')
