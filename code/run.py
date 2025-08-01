#!/usr/bin/env python3
"""
Script de lancement simple pour NBA Analytics
"""

import os
import sys

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importer et lancer l'application
from main import main

if __name__ == '__main__':
    main() 