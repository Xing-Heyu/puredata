#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(os.path.dirname(script_dir), 'platform', 'backend')

users_path = os.path.join(backend_dir, 'users.json')
sessions_path = os.path.join(backend_dir, 'sessions.json')

users_size = os.path.getsize(users_path) if os.path.exists(users_path) else 0
sessions_size = os.path.getsize(sessions_path) if os.path.exists(sessions_path) else 0

print(f'users.json: {users_size} bytes ({users_size/1024:.1f} KB)')
print(f'sessions.json: {sessions_size} bytes ({sessions_size/1024:.1f} KB)')
