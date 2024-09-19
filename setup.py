from setuptools import setup
from Cython.Build import cythonize
import os

# Xác định các module cần chuyển đổi sang Cython
modules = [
    "common_function",
    "common_function_CTK",
    "Common",
    "facebook",
    "youtube",
    "tiktok"
]

# Tạo danh sách các file .pyx tương ứng
cython_files = [f"{module}.pyx" for module in modules]

setup(
    name="MyApplication",
    version="0.1",
    description="My Application Description",
    ext_modules=cythonize(cython_files, language_level=3),
    zip_safe=False,
)

# Sau khi chạy setup.py, bạn sẽ cần đóng gói ứng dụng bằng PyInstaller

# Tạo file bytecode
os.system('python -m compileall .')

# Chạy lệnh PyInstaller để đóng gói ứng dụng
os.system('pyinstaller --onefile '
          '--add-data "icon.ico;." '
          '--add-data "__pycache__/common_function.cpython-38.pyc;." '
          '--add-data "__pycache__/common_function_CTK.cpython-38.pyc;." '
          '--add-data "__pycache__/Common.cpython-38.pyc;." '
          '--add-data "__pycache__/facebook.cpython-38.pyc;." '
          '--add-data "__pycache__/youtube.cpython-38.pyc;." '
          '--add-data "__pycache__/tiktok.cpython-38.pyc;." '
          '--collect-data selenium_stealth '
          '--hidden-import=imageio_ffmpeg.binaries '
          '--icon "icon.ico" '
          'app.py')
