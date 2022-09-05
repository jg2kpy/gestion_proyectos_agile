from django.test import TestCase

# Create your tests here.
from django.contrib.auth import get_user_model
from requests import delete
from django import setup
import os
from django.contrib.auth.models import AnonymousUser, User
from django.test.client import RequestFactory
from usuarios.views import *
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gestion_proyectos_agile.settings")
setup()


# class UsuariosTests(TestCase):
#     """
#     Pruebas unitarias relacionadas a la creacion de usuarios.
#     """

#     def test_create_user(self):
#         """
#         Prueba la creación de usuarios normales
#         """
#         User = get_user_model()
#         user = User.objects.create_user(
#             email='normal@user.com', password='foo')
#         self.assertEqual(user.email, 'normal@user.com')
#         self.assertTrue(user.is_active)

#         # Verificamos que se trata de un usuario normal
#         self.assertFalse(user.is_staff)
#         self.assertFalse(user.is_superuser)

#         # Verificamos que se exige correo y contraseña
#         with self.assertRaises(TypeError):
#             User.objects.create_user()
#         with self.assertRaises(TypeError):
#             User.objects.create_user(email='')
#         with self.assertRaises(ValueError):
#             User.objects.create_user(email='', password="foo")

#     def test_create_superuser(self):
#         """
#         Prueba la creación de superusuarios
#         """
#         User = get_user_model()
#         admin_user = User.objects.create_superuser(
#             email='super@user.com', password='foo')
#         self.assertEqual(admin_user.email, 'super@user.com')
#         self.assertTrue(admin_user.is_active)
#         self.assertTrue(admin_user.is_staff)
#         self.assertTrue(admin_user.is_superuser)

#         with self.assertRaises(ValueError):
#             User.objects.create_superuser(
#                 email='super@user.com', password='foo', is_superuser=False)

#     def test_crear_primer_admin(self):
#         """
#         Prueba que el primer usuario creado se vuelve admin
#         """
#         Usuario = get_user_model()
#         Usuario.objects.all().delete()
#         self.assertEqual(Usuario.objects.all().count(), 0,
#                          "No se pudo limpiar la base de datos")
#         Usuario.objects.create_user(email='normal@user.com', password='foo')
#         self.assertEqual(Usuario.objects.filter(
#             groups__name='gpa_admin').count(), 1)


class RolesGlobalesTests(TestCase):
    """
    Pruebas unitarias relacionadas al manejo de Roles Globales.
    """
    def test_crear_rol(self):
        """
        Prueba que se pueda crear el rol
        """
        self.user = get_user_model().objects.create_user(email='testemail@example.com', password='A123B456c.', username='test')
        self.client.login(email='testemail@example.com', password='A123B456c.', username='test')
        res = self.client.post('/rolesglobales/crear/', data={'nombre': 'rol_global_test', 'descripcion': 'Esto es un test'}, follow=True)
        self.assertContains(res, 'rol_global_test', 1, 200, "No recibe el nombre del rol correctamente")
        self.assertContains(res, 'Esto es un test', 1, 200, "No recibe la descripcion del rol correctamente")

    def test_visualizar_roles(self):
        """
        Prueba que visualicen correctamente los roles globales
        """
        self.user = get_user_model().objects.create_user(email='testemail@example.com', password='A123B456c.', username='test')
        print(f"Login es: {self.client.login(email='testemail@example.com', password='A123B456c.', username='test')}")
        res = self.client.get('/rolesglobales/')
        self.assertContains(res, 'Roles Disponibles', 1, 200, "Carga de forma correcta")

    def test_eliminar_rol(self):
        """
        Prueba que se pueda eliminar un rol
        """
        self.user = get_user_model().objects.create_user(email='testemail@example.com', password='A123B456c.', username='test')
        self.client.login(email='testemail@example.com', password='A123B456c.', username='test')
        rolTest = RolSistema(nombre='test', descripcion='descripcion test')
        rolTest.save()
        res = self.client.post(f'/rolesglobales/{rolTest.id}/eliminar/', follow=True)
        self.assertContains(res, 'test', 0, 200, "No se elimina el rol")

    def test_editar_rol(self):
        """
        Prueba que se pueda editar un rol
        """
        self.user = get_user_model().objects.create_user(email='testemail@example.com', password='A123B456c.', username='test')
        self.client.login(email='testemail@example.com', password='A123B456c.', username='test')
        rolTest = RolSistema(nombre='test', descripcion='descripcion test')
        rolTest.save()
        res = self.client.post(f'/rolesglobales/{rolTest.id}/editar/', data={'nombre': 'rol_global_test_editado', 'descripcion': 'Esto es un test editado'}, follow=True)
        self.assertContains(res, 'rol_global_test_editado', 1, 200, "No recibe el nombre del rol editado correctamente")
        self.assertContains(res, 'Esto es un test editado', 1, 200, "No recibe la descripcion del rol editado correctamente")

    # ARRLEGAR LINEA 126 EL POS (res = self.client.post)
    def test_vincular_rol(self):
        """
        Prueba que se pueda vincular un usuario a un rol
        """
        self.user = get_user_model().objects.create_user(email='testemail@example.com', password='A123B456c.', username='test')
        self.client.login(email='testemail@example.com', password='A123B456c.', username='test')
        rolTest = RolSistema(nombre='test', descripcion='descripcion test')
        rolTest.save()
        res = self.client.post(f'/rolesglobales/{rolTest.id}/usuarios/', follow=True)
        self.assertContains(res, 'Se ha vinculado el rol', 1, 200, "No se vincula correctamente el rol")
    
    # ARRLEGAR LINEA 138 EL POS (res = self.client.post)
    def test_desvincular_rol(self):
        """
        Prueba que se pueda desvincular un usuario a un rol
        """
        self.user = get_user_model().objects.create_user(email='testemail@example.com', password='A123B456c.', username='test')
        self.client.login(email='testemail@example.com', password='A123B456c.', username='test')
        rolTest = RolSistema(nombre='test', descripcion='descripcion test')
        rolTest.save()
        res = self.client.post(f'/rolesglobales/{rolTest.id}/usuarios/', follow=True)
        self.assertContains(res, 'Se ha desvinculado el rol', 1, 200, "No se desvincula correctamente el rol")