#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统兼容性检查器
确保：不需要UAC权限、跨平台兼容、错误友好提示
"""

import os
import sys
import platform
import tempfile
import json

class SystemChecker:
    """系统兼容性检查器"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.info = {}
    
    def check_all(self):
        """检查所有兼容性问题"""
        print("\n" + "="*60)
        print("系统兼容性检查")
        print("="*60)
        
        self._check_os()
        self._check_python()
        self._check_permissions()
        self._check_ports()
        self._check_disk()
        
        self._print_results()
        
        return len(self.issues) == 0
    
    def _check_os(self):
        """检查操作系统"""
        print("\n[1] 操作系统检查...")
        
        self.info["os"] = platform.system()
        self.info["os_version"] = platform.version()
        
        print(f"    系统: {self.info['os']}")
        print(f"    版本: {self.info['os_version'][:50]}...")
        
        if self.info["os"] == "Windows":
            print("    ✅ Windows系统兼容")
        elif self.info["os"] == "Linux":
            print("    ✅ Linux系统兼容")
        elif self.info["os"] == "Darwin":
            print("    ✅ macOS系统兼容")
        else:
            self.warnings.append(f"未知系统: {self.info['os']}")
    
    def _check_python(self):
        """检查Python版本"""
        print("\n[2] Python环境检查...")
        
        self.info["python"] = sys.version
        self.info["python_version"] = f"{sys.version_info.major}.{sys.version_info.minor}"
        
        print(f"    Python版本: {self.info['python_version']}")
        
        if sys.version_info.major < 3:
            self.issues.append("需要Python 3.x")
        elif sys.version_info.minor < 7:
            self.warnings.append("建议使用Python 3.7+")
        else:
            print("    ✅ Python版本符合要求")
    
    def _check_permissions(self):
        """检查文件权限 - 关键：不需要UAC"""
        print("\n[3] 文件权限检查...")
        
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        
        test_dirs = [
            backend_dir,
            os.path.join(backend_dir, "outputs"),
            os.path.join(backend_dir, "checkpoints"),
        ]
        
        for test_dir in test_dirs:
            try:
                os.makedirs(test_dir, exist_ok=True)
                
                test_file = os.path.join(test_dir, ".write_test")
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                
                print(f"    ✅ 可写入: {os.path.basename(test_dir) or '根目录'}")
                
            except PermissionError:
                self.issues.append(f"无法写入目录: {test_dir}")
                print(f"    ❌ 权限不足: {test_dir}")
            except Exception as e:
                self.warnings.append(f"目录检查异常: {e}")
        
        if not self.issues:
            print("    ✅ 不需要UAC管理员权限")
    
    def _check_ports(self):
        """检查端口可用性"""
        print("\n[4] 端口检查...")
        
        import socket
        
        test_ports = [8000, 8080, 3000]
        
        for port in test_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    print(f"    ⚠️ 端口 {port} 已被占用")
                else:
                    print(f"    ✅ 端口 {port} 可用")
            except Exception as e:
                self.warnings.append(f"端口检查异常: {e}")
    
    def _check_disk(self):
        """检查磁盘空间"""
        print("\n[5] 磁盘空间检查...")
        
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        
        try:
            if platform.system() == "Windows":
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(backend_dir), 
                    None, None, ctypes.pointer(free_bytes)
                )
                free_gb = free_bytes.value / (1024**3)
            else:
                stat = os.statvfs(backend_dir)
                free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
            
            print(f"    可用空间: {free_gb:.1f} GB")
            
            if free_gb < 0.1:
                self.issues.append("磁盘空间不足100MB")
            elif free_gb < 1:
                self.warnings.append("磁盘空间较少")
            else:
                print("    ✅ 磁盘空间充足")
                
        except Exception as e:
            self.warnings.append(f"磁盘检查异常: {e}")
    
    def _print_results(self):
        """打印检查结果"""
        print("\n" + "="*60)
        print("检查结果")
        print("="*60)
        
        if self.issues:
            print("\n❌ 严重问题:")
            for issue in self.issues:
                print(f"   - {issue}")
        
        if self.warnings:
            print("\n⚠️ 警告:")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        if not self.issues and not self.warnings:
            print("\n✅ 系统完全兼容，无需UAC权限！")
        elif not self.issues:
            print("\n✅ 系统基本兼容，可以运行")
        else:
            print("\n❌ 存在兼容性问题，需要解决")
        
        print("="*60)


class SafeFileHandler:
    """安全文件处理器 - 避免权限问题"""
    
    @staticmethod
    def get_safe_dir():
        """获取安全的存储目录"""
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        
        if os.access(backend_dir, os.W_OK):
            return backend_dir
        
        user_dir = os.path.expanduser("~")
        app_dir = os.path.join(user_dir, ".datagenpro")
        os.makedirs(app_dir, exist_ok=True)
        
        return app_dir
    
    @staticmethod
    def safe_write(filename, data):
        """安全写入文件"""
        safe_dir = SafeFileHandler.get_safe_dir()
        filepath = os.path.join(safe_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True, filepath
        except PermissionError:
            return False, "权限不足，请检查文件夹权限"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def safe_read(filename):
        """安全读取文件"""
        safe_dir = SafeFileHandler.get_safe_dir()
        filepath = os.path.join(safe_dir, filename)
        
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return True, json.load(f)
            return True, {}
        except Exception as e:
            return False, str(e)


def ensure_compatibility():
    """确保兼容性 - 启动前检查"""
    checker = SystemChecker()
    is_ok = checker.check_all()
    
    if not is_ok:
        print("\n" + "="*60)
        print("⚠️  兼容性问题解决方案")
        print("="*60)
        print("\n如果遇到权限问题，请尝试：")
        print("1. 将程序放在用户目录下（如桌面、文档）")
        print("2. 不要放在C:\\Program Files等系统目录")
        print("3. 不需要以管理员身份运行")
        print("="*60)
    
    return is_ok


if __name__ == "__main__":
    ensure_compatibility()
