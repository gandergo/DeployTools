#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Webcamoid Deploy Tools.
# Copyright (C) 2020  Gonzalo Exequiel Pedone
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Web-Site: http://github.com/webcamoid/DeployTools/

import os
import sys
import platform
import shutil

from . import DTUtils


class DeployBase(DTUtils.Utils):
    def __init__(self):
        super().__init__()
        self.setRootDir()

    def __str__(self):
        deployInfo = 'Python version: {}\n' \
                     'Root directory: {}\n' \
                     'Build directory: {}\n' \
                     'Install directory: {}\n' \
                     'Packages directory: {}\n' \
                     'System: {}\n' \
                     'Architecture: {}\n' \
                     'Target system: {}\n' \
                     'Target architecture: {}\n' \
                     'Number of threads: {}\n' \
                     'Program version: {}'. \
                        format(platform.python_version(),
                               self.rootDir,
                               self.buildDir,
                               self.installDir,
                               self.pkgsDir,
                               self.system,
                               self.arch,
                               self.targetSystem,
                               self.targetArch,
                               self.njobs,
                               self.programVersion())

        return deployInfo

    def setRootDir(self, rootDir=''):
        self.rootDir = rootDir
        self.buildDir = os.environ['BUILD_PATH'] if 'BUILD_PATH' in os.environ else self.rootDir
        self.installDir = os.environ['INSTALL_PATH'] if 'INSTALL_PATH' in os.environ else \
            os.path.join(self.buildDir, 'ports/deploy/temp_priv/root')
        self.rootInstallDir = ''
        self.pkgsDir = os.path.join(self.rootDir,
                                    'ports/deploy/packages_auto',
                                    sys.platform if os.name == 'posix' else os.name)
        self.qmake = ''

    def run(self):
        print('Deploy info\n')
        print(self)
        print('\nPreparing for software packaging\n')
        self.prepare()

        if not 'NO_SHOW_PKG_DATA_INFO' in os.environ \
            or os.environ['NO_SHOW_PKG_DATA_INFO'] != '1':
            print('\nPackaged data info\n')
            self.printPackageDataInfo()

        if 'PACKAGES_PREPARE_ONLY' in os.environ \
            and os.environ['PACKAGES_PREPARE_ONLY'] == '1':
            print('\nPackage data is ready for merging\n')
        else:
            print('\nCreating packages\n')
            self.package()
            print('\nCleaning up')
            self.cleanup()
            print('Deploy finnished\n')

    def printPackageDataInfo(self):
        packagedFiles = []

        for root, _, files in os.walk(self.rootInstallDir):
            for f in files:
                packagedFiles.append(os.path.join(root, f))

        packagedFiles = sorted(packagedFiles)

        for f in packagedFiles:
            print('    ' + f)

    def prepare(self):
        pass

    def package(self):
        pass

    def cleanup(self):
        shutil.rmtree(self.installDir, True)
