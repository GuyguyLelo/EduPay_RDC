"""
Tests pour l'app core
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import User, UserRole

User = get_user_model()


class UserModelTest(TestCase):
    """Tests pour le modèle User"""
    
    def setUp(self):
        """Configuration initiale"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role=UserRole.ETUDIANT
        )
    
    def test_user_creation(self):
        """Test de création d'un utilisateur"""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.role, UserRole.ETUDIANT)
        self.assertTrue(self.user.is_active)
    
    def test_user_str(self):
        """Test de la représentation string"""
        self.assertEqual(str(self.user), 'test@example.com')
    
    def test_superuser_creation(self):
        """Test de création d'un super utilisateur"""
        superuser = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        self.assertEqual(superuser.role, UserRole.SUPER_ADMIN)
    
    def test_user_properties(self):
        """Test des propriétés de l'utilisateur"""
        self.assertTrue(self.user.is_etudiant)
        self.assertFalse(self.user.is_super_admin)
        self.assertFalse(self.user.is_etablissement_admin)
