import logging
import os
import platform
import shutil

import snapcraft
import snapcraft.plugins.nodejs
from snapcraft import sources

_NODEJS_ARCHES = {
    'i686': 'x86',
    'x86_64': 'x64',
    'armv7l': 'armv7l',
}
class Electronic(snapcraft.plugins.nodejs.NodePlugin):

    @classmethod
    def schema(cls):
        schema = super().schema()
        return schema

    def build(self):
        # do not run build() from snapcraft.plugins.nodejs.NodePlugin
        # we like to build the nodejs packages in build dir,
        # and use electron-packager to build the final binary.
        snapcraft.BasePlugin.build(self)

        self._nodejs_tar.provision(
            self.builddir, clean_target=False, keep_tarball=True)

        for pkg in self.options.node_packages:
            self.run(['npm', 'install', pkg])
        if os.path.exists(os.path.join(self.builddir, 'package.json')):
            self.run(['npm', 'install'])

        arch = _NODEJS_ARCHES[platform.machine()]
        env = os.environ.copy()
        env['PATH'] = self.run_output(['npm', 'bin'], self.builddir) + ":" + env['PATH']
        # FIXME: does not work for all electronic package.
        self.run(['./scripts/build.sh', 'linux', arch], self.builddir, env=env)

        if os.path.exists(self.installdir):
            shutil.rmtree(self.installdir)

        shutil.copytree(self.builddir + "/dist/" + self.name + "-linux-" + arch + "/",
            self.installdir, symlinks=True)
