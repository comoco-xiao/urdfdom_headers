import os
import subprocess
import sys
import shutil
from pathlib import Path
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

PROJECT_DIR = Path(__file__).parent
VERSION = "1.0.5"

class CMakeBuildExt(build_ext):
    """集成 CMake 编译流程"""
    user_options = build_ext.user_options + [
        ('build-type=', None, 'CMake build type [Release|Debug]'),
    ]

    def initialize_options(self):
        super().initialize_options()
        self.build_type = "Release"

    def finalize_options(self):
        super().finalize_options()

    def run(self):
        self._check_dependencies()
        self._configure_and_build()

    def _check_dependencies(self):
        """检查编译依赖"""
        required_commands = {
            'cmake': 'CMake >= 3.10',
            'make': 'Make/Ninja'
        }
        missing = []
        for cmd, desc in required_commands.items():
            try:
                subprocess.check_output([cmd, '--version'], stderr=subprocess.DEVNULL)
            except OSError:
                missing.append(desc)
        if missing:
            sys.stderr.write(f"Error: Missing required tools: {', '.join(missing)}\n")
            sys.exit(1)
    def copy_data(self, install_dir):
        # include
        include_path = os.path.join(self.build_lib, "cmeel.prefix", "include")
        source_include_path = os.path.join(install_dir, "include")
        if os.path.exists(include_path):
            shutil.rmtree(include_path)
        shutil.copytree(source_include_path, include_path)
        
        # lib
        lib_path = os.path.join(self.build_lib, "cmeel.prefix", "lib")
        source_lib_path = os.path.join(install_dir, "lib")
        if os.path.exists(lib_path):
            shutil.rmtree(lib_path)
        shutil.copytree(source_lib_path, lib_path)
        
    def _configure_and_build(self):
        """执行 CMake 构建"""
        build_dir = os.path.join(PROJECT_DIR, "cmake_build")
        install_dir = os.path.join(PROJECT_DIR, "urdfdom_headers_install")

        # 创建构建目录
        os.makedirs(build_dir, exist_ok=True)
        os.makedirs(install_dir, exist_ok=True)

        # CMake 配置参数
        cmake_args = [
            f"-DCMAKE_INSTALL_PREFIX={install_dir}",
            f"-DCMAKE_BUILD_TYPE={self.build_type}",
        ]

        # 生成构建系统
        subprocess.check_call(
            ["cmake", str(PROJECT_DIR)] + cmake_args,
            cwd=str(build_dir), env=os.environ.copy()
        )

        # 编译并安装
        build_args = ["--config", "Release", "-j2"]
        subprocess.check_call(
            ["cmake", "--build", ".", "--target", "install"] + build_args,
            cwd=build_dir,
        )
        
        # copy data
        self.copy_data(install_dir)

setup(
    name="urdfdom_headers",
    version=VERSION,
    description="Efficient Rigid Body Dynamics Library",
    author="Xiao",
    license="BSD-2-Clause",
    packages=[],
    python_requires=">=3.9",
    ext_modules=[Extension("urdfdom_headers_dummy", [])],  # 触发扩展构建
    cmdclass={"build_ext": CMakeBuildExt},
    zip_safe=False,
)