#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Webcamoid Deploy Tools.
# Copyright (C) 2022  Gonzalo Exequiel Pedone
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
import subprocess
import sys

from . import DTBinary
from . import DTUtils


def copyPipeWireModules(globs,
                        targetPlatform,
                        targetArch,
                        dataDir,
                        outputPipeWireModulesDir,
                        pipeWireModules,
                        pipeWireModulesDir,
                        sysLibDir,
                        stripCmd='strip'):
    solver = DTBinary.BinaryTools(DTUtils.hostPlatform(),
                                  targetPlatform,
                                  targetArch,
                                  sysLibDir,
                                  stripCmd)

    for dep in solver.scanDependencies(dataDir):
        libName = solver.name(dep)

        if libName == 'pipewire-0.3':
            for root, _, files in os.walk(pipeWireModulesDir):
                relpath = os.path.relpath(root, pipeWireModulesDir)

                if relpath != '.' \
                    and pipeWireModules != [] \
                    and not (relpath in pipeWireModules):
                    continue

                for f in files:
                    sysPluginPath = os.path.join(root, f)

                    if relpath == '.':
                        pluginPath = os.path.join(outputPipeWireModulesDir, f)
                    else:
                        pluginPath = os.path.join(outputPipeWireModulesDir,
                                                  relpath,
                                                  f)

                    if not os.path.exists(sysPluginPath):
                        continue

                    print('    {} -> {}'.format(sysPluginPath, pluginPath))
                    DTUtils.copy(sysPluginPath, pluginPath)
                    globs['dependencies'].add(sysPluginPath)

            break

def copySpaPlugins(globs,
                   targetPlatform,
                   targetArch,
                   dataDir,
                   outputSpaPluginsDir,
                   spaPlugins,
                   spaPluginsDir,
                   sysLibDir,
                   stripCmd='strip'):
    solver = DTBinary.BinaryTools(DTUtils.hostPlatform(),
                                  targetPlatform,
                                  targetArch,
                                  sysLibDir,
                                  stripCmd)

    for dep in solver.scanDependencies(dataDir):
        libName = solver.name(dep)

        if libName == 'pipewire-0.3':
            for root, _, files in os.walk(spaPluginsDir):
                relpath = os.path.relpath(root, spaPluginsDir)

                if relpath != '.' \
                    and spaPlugins != [] \
                    and not (relpath in spaPlugins):
                    continue

                for f in files:
                    sysPluginPath = os.path.join(root, f)

                    if relpath == '.':
                        pluginPath = os.path.join(outputSpaPluginsDir, f)
                    else:
                        pluginPath = os.path.join(outputSpaPluginsDir,
                                                  relpath,
                                                  f)

                    if not os.path.exists(sysPluginPath):
                        continue

                    print('    {} -> {}'.format(sysPluginPath, pluginPath))
                    DTUtils.copy(sysPluginPath, pluginPath)
                    globs['dependencies'].add(sysPluginPath)

            break

def preRun(globs, configs, dataDir):
    targetPlatform = configs.get('Package', 'targetPlatform', fallback='').strip()
    targetArch = configs.get('Package', 'targetArch', fallback='').strip()
    outputPipeWireModulesDir = configs.get('PipeWire', 'outputModulesDir', fallback='pipewire-modules').strip()
    outputPipeWireModulesDir = os.path.join(dataDir, outputPipeWireModulesDir)
    pipeWireModulesDir = configs.get('PipeWire', 'modulesDir', fallback='').strip()

    if pipeWireModulesDir == '':
        if 'PIPEWIRE_MODULE_DIR' in os.environ:
            pipeWireModulesDir = os.environ['PIPEWIRE_MODULE_DIR']

    pipeWireModules = configs.get('PipeWire', 'modules', fallback='')

    if pipeWireModules == '':
        pipeWireModules = []
    else:
        pipeWireModules = [plugin.strip() for plugin in pipeWireModules.split(',')]

    outputSpaPluginsDir = configs.get('PipeWire', 'outputSpaPluginsDir', fallback='spa-plugins').strip()
    outputSpaPluginsDir = os.path.join(dataDir, outputSpaPluginsDir)
    spaPluginsDir = configs.get('PipeWire', 'spaPluginsDir', fallback='').strip()

    if spaPluginsDir == '':
        if 'SPA_PLUGIN_DIR' in os.environ:
            spaPluginsDir = os.environ['SPA_PLUGIN_DIR']

    spaPlugins = configs.get('PipeWire', 'spaPlugins', fallback='')

    if spaPlugins == '':
        spaPlugins = []
    else:
        spaPlugins = [plugin.strip() for plugin in spaPlugins.split(',')]

    sysLibDir = configs.get('System', 'libDir', fallback='')
    libs = set()

    for lib in sysLibDir.split(','):
        libs.add(lib.strip())

    sysLibDir = list(libs)
    stripCmd = configs.get('System', 'stripCmd', fallback='strip').strip()
    verbose = configs.get('PipeWire', 'verbose', fallback='false').strip()
    verbose = DTUtils.toBool(verbose)

    print('PipeWire information')
    print()
    print('PipeWire modules directory: {}'.format(pipeWireModulesDir))
    print('PipeWire modules output directory: {}'.format(outputPipeWireModulesDir))
    print()
    print('Copying required PipeWire modules')
    print()
    copyPipeWireModules(globs,
                        targetPlatform,
                        targetArch,
                        dataDir,
                        outputPipeWireModulesDir,
                        pipeWireModules,
                        pipeWireModulesDir,
                        sysLibDir,
                        stripCmd)
    print()
    print('PipeWire SPA information')
    print()
    print('PipeWire SPA plugins directory: {}'.format(spaPluginsDir))
    print('PipeWire SPA plugins output directory: {}'.format(outputSpaPluginsDir))
    print()
    print('Copying required PipeWire SPA plugins')
    print()
    copySpaPlugins(globs,
                   targetPlatform,
                   targetArch,
                   dataDir,
                   outputSpaPluginsDir,
                   spaPlugins,
                   spaPluginsDir,
                   sysLibDir,
                   stripCmd)

def postRun(globs, configs, dataDir):
    pass
