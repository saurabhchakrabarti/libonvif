import os
import sys
import subprocess
import distutils.ccompiler
from pathlib import Path
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

PKG_NAME = "libonvif"
VERSION = "2.0.9"

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        extdir = os.path.join(extdir, PKG_NAME)

        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
            f"-DWITHOUT_LIBS=1",
            f"-Wno-dev",]
        
        if sys.platform == "win32":
            cmake_args.append(f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE={extdir}")
        
        # add libxml2 install dir to path so native FindLibXml2 succeeds
        directory = os.path.join(Path(__file__).parent.absolute(), "libxml2")
        os.environ['PATH'] = directory + os.pathsep + os.environ['PATH']

        build_temp = os.path.join(self.build_temp, ext.name)
        if not os.path.exists(build_temp):
            os.makedirs(build_temp)

        subprocess.run(["cmake", ext.sourcedir] + cmake_args, cwd=build_temp)
        subprocess.run(["cmake", "--build", ".", "--config", "Release"], cwd=build_temp)

def get_package_data():
    data = []
    shared_lib_extension = distutils.ccompiler.new_compiler().shared_lib_extension
    for f in os.listdir(PKG_NAME):
        _, extension = os.path.splitext(f)
        if extension == shared_lib_extension:
            data.append(f)
    return data

setup(
    name=PKG_NAME,
    version=VERSION,
    author="Stephen Rhodes",
    author_email="sr99622@gmail.com",
    description="A client side onvif library",
    long_description="",
    ext_modules=[CMakeExtension(PKG_NAME)],
    cmdclass={"build_ext": CMakeBuild},
    zip_safe=False,
    python_requires=">=3.8",
    packages=[PKG_NAME],
    package_data={ PKG_NAME : get_package_data() }
)
