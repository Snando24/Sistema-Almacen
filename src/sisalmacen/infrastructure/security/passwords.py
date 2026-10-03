"""Hash y verificación de contraseñas con Argon2id."""

from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from sisalmacen.application.auth import PasswordHasherPort


class Argon2PasswordHasher(PasswordHasherPort):
    """Adaptador de hash de contraseñas para la aplicación."""

    def __init__(self) -> None:
        self._hasher = PasswordHasher()

    def hash(self, plain_password: str) -> str:
        return self._hasher.hash(plain_password)

    def verify(self, password_hash: str, plain_password: str) -> bool:
        try:
            return self._hasher.verify(password_hash, plain_password)
        except (InvalidHashError, VerificationError):
            return False
