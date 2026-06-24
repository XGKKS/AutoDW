# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('app', 'app'), ('custom_prompt.txt', '.'), ('word_roots.json', '.'), ('dev_standards.json', '.'), ('standards', 'standards'), ('builtin', 'builtin'), ('..\\frontend\\dist', 'frontend')]
binaries = []
hiddenimports = ['uvicorn', 'fastapi', 'httpx', 'openpyxl', 'docx', 'pydantic', 'multipart', 'langchain', 'langchain_community', 'cryptography', 'pymysql', 'psycopg', 'oracledb', 'app', 'app.models', 'app.native_db_executor', 'app.validators', 'app.validators.ddl_validator', 'app.config', 'app.config.db_examples']
tmp_ret = collect_all('uvicorn')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('fastapi')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('starlette')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['start.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AI-WarHouse',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AI-WarHouse',
)