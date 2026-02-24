@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================================
echo 全链路测试 - 直接API调用
echo ============================================================
echo.

echo [步骤1] 测试登录
echo.
curl -X POST http://localhost:8000/api/login -H "Content-Type: application/json" -d "{\"username\":\"test_fullchain\",\"password\":\"Test123456\"}" -s
echo.

echo [步骤2] 测试生成 - 30条纯净模式
echo.
curl -X POST http://localhost:8000/generate -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_TOKEN_HERE" -d "{\"domain\":\"旅游\",\"count\":30,\"format\":\"json\",\"mode\":\"clean\",\"noise_level\":0,\"quality_mode\":\"standard\"}" -s
echo.

echo [步骤3] 测试生成 - 40条混合模式
echo.
curl -X POST http://localhost:8000/generate -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_TOKEN_HERE" -d "{\"domain\":\"旅游\",\"count\":40,\"format\":\"json\",\"mode\":\"hybrid\",\"noise_level\":30,\"quality_mode\":\"high\"}" -s
echo.

echo [步骤4] 测试生成 - 30条噪音模式
echo.
curl -X POST http://localhost:8000/generate -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_TOKEN_HERE" -d "{\"domain\":\"旅游\",\"count\":30,\"format\":\"json\",\"mode\":\"noisy\",\"noise_level\":30,\"quality_mode\":\"standard\"}" -s
echo.

echo ============================================================
echo 测试说明:
echo 1. 先执行步骤1登录，复制返回的token
echo 2. 将YOUR_TOKEN_HERE替换为实际token
echo 3. 执行步骤2-4测试生成
echo 4. 观察服务器日志确认25个模块是否被调用
echo ============================================================
pause
