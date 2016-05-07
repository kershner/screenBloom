# -*- mode: python -*-

block_cipher = None

def extra_datas(mydir):
    def rec_glob(p, files):
        import os
        import glob
        for d in glob.glob(p):
            if os.path.isfile(d):
                files.append(d)
            rec_glob("%s/*" % d, files)
    files = []
    rec_glob("%s/*" % mydir, files)
    extra_datas = []
    for f in files:
        extra_datas.append((f, f, 'DATA'))

    return extra_datas


###############################################################################
a = Analysis(['screenbloom.py'],
             pathex=['/Users/tylerkershner/Desktop/sb_src/app'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

for directory in ('static', 'templates'):
    a.datas += extra_datas(directory)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='screenBloom',
          debug=False,
          strip=False,
          upx=True,
          console=False )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='screenbloom')

custom_plist = {
  'LSBackgroundOnly': 1
}
app = BUNDLE(coll,
             name='screenBloom.app',
             icon='static/images/icon.icns',
             bundle_identifier='screenBloom',
             info_plist=custom_plist)
