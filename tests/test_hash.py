import hashlib

password = "admin123"
expected_hash = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
actual_hash = hashlib.sha256(password.encode()).hexdigest()

print(f"密码: {password}")
print(f"期望哈希: {expected_hash}")
print(f"实际哈希: {actual_hash}")
print(f"匹配: {expected_hash == actual_hash}")
