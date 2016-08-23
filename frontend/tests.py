from django.test import TestCase
from django.test import Client


class TestResponses(TestCase):
	def setUp(self):
		self.c = Client()

	def test_index(self):
		resp = self.c.get('/')
		self.assertEqual(resp.status_code, 200)

	def test_settings(self):
		resp = self.c.get('/settings')
		self.assertEqual(resp.status_code, 200)

	def test_docs(self):
		resp = self.c.get('/docs')
		self.assertEqual(resp.status_code, 200)

	def test_logout(self):
		resp = self.c.get('/logout')
		self.assertEqual(resp.status_code, 200)

	def test_login(self):
		resp = self.c.get('/login')
		self.assertEqual(resp.status_code, 200)

	def test_welcome(self):
		resp = self.c.get('/welcome')
		self.assertEqual(resp.status_code, 200)

	def test_stats(self):
		resp = self.c.get('/stats')
		self.assertEqual(resp.status_code, 200)

	def test_upload(self):
		resp = self.c.get('/upload')
		self.assertEqual(resp.status_code, 200)

	def test_view_file(self):
		resp = self.c.get('/0000')
		self.assertEqual(resp.status_code, 200)

