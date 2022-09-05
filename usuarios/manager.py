from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    Maneja la creación de usuarios del tipo costumizado. Permite creación de usuarios normales y superusuarios.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Crear un nuevo usuario con correo y contraseña. No debería ser llamado directamente en el código.

        :param email: El email del usuario.
        :type email: str
        :param password: La contraseña del usuario.
        :type password: str
        :param extra_fields: Campos extra para el usuario, ignorados.
        :type extra_fields: dict
        """
        if not email:
            raise ValueError('Cada usuario debe tener un email')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Crear superusuario. No debería ser llamado directamente en el código.

        :param email: El email del usuario.
        :type email: str
        :param password: La contraseña del usuario.
        :type password: str
        :param extra_fields: Campos extra para el usuario, ignorados.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')
        return self.create_user(email, password, **extra_fields)
