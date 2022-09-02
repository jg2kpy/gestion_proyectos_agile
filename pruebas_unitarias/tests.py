import email
from django.test import TestCase
from phonenumber_field.modelfields import PhoneNumber

# Create your tests here.
from django.contrib.auth import get_user_model
from requests import delete
from django import setup
import os

from usuarios.models import RolSistema
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gestion_proyectos_agile.settings")
setup()


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
        self.assertEqual(Usuario.objects.all().count(), 0,
                         "No se pudo limpiar la base de datos")
        Usuario.objects.create_user(email='normal@user.com', password='foo')
        rol_admin, _ = RolSistema.objects.get_or_create(nombre='gpa_admin')
        self.assertEqual(Usuario.objects.filter(roles_sistema__id=rol_admin.id).count(), 1)


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
        res = self.client.post("/perfil/", {'email': 'testemails@example.com',
                                            'avatar_url': 'avatar2@example.com', 'direccion': 'Calle 2 # 3 - 4', 'telefono': '0983 738041'})
        print(res)
        res = self.client.get('/perfil/')
        self.assertContains(res, 'testemail2@example.com', 1, 200, "Usuario loguedao puede ver su perfil con email")
        self.assertContains(res, '0983 738041', 1, 200, "Usuario loguedao puede ver su perfil con número de telefono")
        self.assertContains(res, 'Calle 2 # 3 - 4', 1, 200, "Usuario loguedao puede ver su perfil con direccion")
        self.assertContains(res, 'avatar2@example.com', None, 200, "Usuario loguedao puede ver su perfil con foto")
