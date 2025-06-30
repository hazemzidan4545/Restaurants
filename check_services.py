#!/usr/bin/env python
from app.models import Service
from app import create_app

app = create_app()
with app.app_context():
    services = Service.query.all()
    print(f'Total services: {len(services)}')
    for s in services:
        print(f'- {s.name} (Active: {s.is_active})')
