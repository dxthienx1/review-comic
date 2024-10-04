import requests
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Đọc khóa bí mật để ký
def load_private_key():
    with open("private_key.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=b"your_password",  # Mật khẩu của khóa bí mật
            backend=default_backend()
        )
    return private_key

# Ký nội dung file
def sign_data(data, private_key):
    signature = private_key.sign(
        data,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode('utf-8')

# Đọc nội dung file start.py
def read_file(file_path):
    with open(file_path, 'rb') as f:
        return f.read()

# Gửi nội dung file và chữ ký lên máy chủ
def send_file_to_server(file_data, signature, otp):
    url = "https://yourserver.com/api/verify_start"
    payload = {
        "file_content": base64.b64encode(file_data).decode('utf-8'),
        "signature": signature,
        "otp": otp
    }
    response = requests.post(url, json=payload)
    return response

def main():
    # Đọc nội dung file start.py
    file_path = 'start.py'
    file_data = read_file(file_path)

    # Tải và ký file bằng khóa bí mật
    private_key = load_private_key()
    signature = sign_data(file_data, private_key)

    # Nhập mã OTP được gửi qua Telegram
    otp = input("Nhập OTP đã nhận qua Telegram: ")

    # Gửi file, chữ ký và OTP lên server
    response = send_file_to_server(file_data, signature, otp)

    if response.status_code == 200:
        # Nhận dữ liệu từ server (các file .pyc) và khởi chạy chúng
        pyc_files = response.json().get('pyc_files')
        if pyc_files:
            run_pyc_files(pyc_files)
    else:
        print(f"Server returned error: {response.status_code}")

# Hàm khởi chạy các file .pyc mà không lưu ra đĩa
def run_pyc_files(pyc_files):
    import importlib.util
    import marshal
    import types
    for file_name, file_data in pyc_files.items():
        pyc_code = marshal.loads(base64.b64decode(file_data))
        module = types.ModuleType(file_name)
        exec(pyc_code, module.__dict__)
        print(f"Executed {file_name}")

if __name__ == '__main__':
    main()
