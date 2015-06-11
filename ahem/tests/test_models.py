
from django.test import TestCase
from django.db import IntegrityError

from model_mommy import mommy

from ahem.models import UserBackendRegistry


class UserBackendRegistryTests(TestCase):

	def test_user_and_backend_unique_together(self):
		mommy.make('ahem.UserBackendRegistry',
			user__id=1, backend='test_backend')
		with self.assertRaises(IntegrityError):
			mommy.make('ahem.UserBackendRegistry',
				user__id=1, backend='test_backend')
