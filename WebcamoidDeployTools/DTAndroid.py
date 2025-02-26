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
import platform
import shutil
import xml.etree.ElementTree as ET

from . import DTBinary
from . import DTGit
from . import DTSystemPackages
from . import DTUtils


def sysInfo():
    info = ''

    for f in os.listdir('/etc'):
        if f.endswith('-release'):
            with open(os.path.join('/etc' , f)) as releaseFile:
                info += releaseFile.read()

    if len(info) < 1:
        info = ' '.join(platform.uname())

    return info

def writeBuildInfo(globs, buildInfoFile, sourcesDir, androidCompileSdkVersion):
    outputDir = os.path.dirname(buildInfoFile)

    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    # Write repository info.

    with open(buildInfoFile, 'w') as f:
        # Write repository info.

        commitHash = DTGit.commitHash(sourcesDir)

        if len(commitHash) < 1:
            commitHash = 'Unknown'

        print('    Commit hash: ' + commitHash)
        f.write('Commit hash: ' + commitHash + '\n')

        buildLogUrl = ''

        if 'TRAVIS_BUILD_WEB_URL' in os.environ:
            buildLogUrl = os.environ['TRAVIS_BUILD_WEB_URL']
        elif 'APPVEYOR_ACCOUNT_NAME' in os.environ \
            and 'APPVEYOR_PROJECT_NAME' in os.environ \
            and 'APPVEYOR_JOB_ID' in os.environ:
            buildLogUrl = 'https://ci.appveyor.com/project/{}/{}/build/job/{}'.format(os.environ['APPVEYOR_ACCOUNT_NAME'],
                                                                                      os.environ['APPVEYOR_PROJECT_SLUG'],
                                                                                      os.environ['APPVEYOR_JOB_ID'])
        elif 'GITHUB_SERVER_URL' in os.environ and os.environ['GITHUB_SERVER_URL'] != '' \
            and 'GITHUB_REPOSITORY' in os.environ and os.environ['GITHUB_REPOSITORY'] != '' \
            and 'GITHUB_RUN_ID' in os.environ and os.environ['GITHUB_RUN_ID'] != '':
            buildLogUrl = '{}/{}/actions/runs/{}'.format(os.environ['GITHUB_SERVER_URL'],
                                                         os.environ['GITHUB_REPOSITORY'],
                                                         os.environ['GITHUB_RUN_ID'])

        if len(buildLogUrl) > 0:
            print('    Build log URL: ' + buildLogUrl)
            f.write('Build log URL: ' + buildLogUrl + '\n')

        print()
        f.write('\n')

        # Write host info.

        info = sysInfo()

        for line in info.split('\n'):
            if len(line) > 0:
                print('    ' + line)
                f.write(line + '\n')

        print()
        f.write('\n')

        # Write SDK and NDK info.

        androidSDK = ''

        if 'ANDROID_HOME' in os.environ:
            androidSDK = os.environ['ANDROID_HOME']

        androidNDK = ''

        if 'ANDROID_NDK_ROOT' in os.environ:
            androidNDK = os.environ['ANDROID_NDK_ROOT']
        elif 'ANDROID_NDK' in os.environ:
            androidNDK = os.environ['ANDROID_NDK']

        sdkInfoFile = os.path.join(androidSDK, 'tools', 'source.properties')
        ndkInfoFile = os.path.join(androidNDK, 'source.properties')

        print('    Android Platform: {}'.format(androidCompileSdkVersion))
        f.write('Android Platform: {}\n'.format(androidCompileSdkVersion))
        print('    SDK Info: \n')
        f.write('SDK Info: \n\n')

        with open(sdkInfoFile) as sdkf:
            for line in sdkf:
                if len(line) > 0:
                    print('        ' + line.strip())
                    f.write('    ' + line)

        print('\n    NDK Info: \n')
        f.write('\nNDK Info: \n\n')

        with open(ndkInfoFile) as ndkf:
            for line in ndkf:
                if len(line) > 0:
                    print('        ' + line.strip())
                    f.write('    ' + line)

        print()
        f.write('\n')

        # Write binary dependencies info.

        packages = set()

        if 'dependencies' in globs:
            for dep in globs['dependencies']:
                packageInfo = DTSystemPackages.searchPackageFor(dep)

                if len(packageInfo) > 0:
                    packages.add(packageInfo)

        packages = sorted(packages)

        for packge in packages:
            print('    ' + packge)
            f.write(packge + '\n')

def removeUnneededFiles(path):
    afiles = set()

    for root, _, files in os.walk(path):
        for f in files:
            if f.endswith('.jar'):
                afiles.add(os.path.join(root, f))

    for afile in afiles:
        os.remove(afile)

def preRun(globs, configs, dataDir):
    targetPlatform = configs.get('Package', 'targetPlatform', fallback='').strip()
    targetArch = configs.get('Package', 'targetArch', fallback='').strip()
    mainExecutable = configs.get('Package', 'mainExecutable', fallback='').strip()
    mainExecutable = os.path.join(dataDir, mainExecutable)
    libDir = configs.get('Package', 'libDir', fallback='').strip()
    libDir = os.path.join(dataDir, libDir)
    defaultSysLibDir = '/opt/android-libs/{}/lib'.format(targetArch)
    sysLibDir = configs.get('System', 'libDir', fallback=defaultSysLibDir)
    stripCmd = configs.get('System', 'stripCmd', fallback='strip').strip()
    libs = set()

    if sysLibDir != '':
        for lib in sysLibDir.split(','):
            libs.add(lib.strip())

    sysLibDir = list(libs)
    extraLibs = configs.get('System', 'extraLibs', fallback='')
    elibs = set()

    if extraLibs != '':
        for lib in extraLibs.split(','):
            elibs.add(lib.strip())

    extraLibs = list(elibs)
    solver = DTBinary.BinaryTools(DTUtils.hostPlatform(),
                                  targetPlatform,
                                  targetArch,
                                  sysLibDir,
                                  stripCmd)

    print('Copying required libs')
    print()
    DTUtils.solvedepsLibs(globs,
                          mainExecutable,
                          targetPlatform,
                          targetArch,
                          dataDir,
                          libDir,
                          sysLibDir,
                          extraLibs,
                          stripCmd)
    print()
    print('Stripping symbols')
    solver.stripSymbols(dataDir)
    print('Removing unnecessary files')
    removeUnneededFiles(libDir)
    print()

def postRun(globs, configs, dataDir):
    sourcesDir = configs.get('Package', 'sourcesDir', fallback='.').strip()
    buildInfoFile = configs.get('Package', 'buildInfoFile', fallback='build-info.txt').strip()
    buildInfoFile = os.path.join(dataDir, buildInfoFile)
    androidCompileSdkVersion = configs.get('System', 'androidCompileSdkVersion', fallback='24').strip()

    print('Writting build system information')
    print()
    writeBuildInfo(globs, buildInfoFile, sourcesDir, androidCompileSdkVersion)
