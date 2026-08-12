/**
 * RegisterPage.jsx —— 注册页
 * 对应《前端页面原型说明》注册页布局 + 需求规格说明书 F-03/F-04/F-05/F-07
 */

import { useState } from 'react';
import { Input, Button } from 'antd';
import { Link, useNavigate } from 'react-router-dom';
import { registerUser } from '../api';

function RegisterPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const navigate = useNavigate();

  const handleRegister = async () => {
    try {
      const response = await registerUser({
        username,
        password,
        confirm_password: confirmPassword
      });

      if (response.data.status === 'success') {
        navigate('/login')
      } else {
        setErrorMsg(response.data.message);
      }
    } catch (err) {
      if (err.response) {
        setErrorMsg(err.response.data.message);
      } else {
          setErrorMsg('网络异常，请稍后重试')
      }
    }
  };

  return (
    <div style={{ maxWidth: 360, margin: '80px auto' }}>
      <h2>注册</h2>

      <Input
        placeholder="用户名（至少6位）"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        style={{ marginBottom: 12 }}
      />

      <Input.Password
        placeholder="密码"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        style={{ marginBottom: 12 }}
      />

      <Input.Password
        placeholder="确认密码"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        style={{ marginBottom: 12 }}
      />

      {/* 错误提示：对应线框图里输入框下方的红字 */}
      {errorMsg && <p style={{ color: 'red', marginBottom: 12 }}>{errorMsg}</p>}

      <Button type="primary" block onClick={handleRegister}>
        注册
      </Button>

      <p style={{ textAlign: 'center', marginTop: 16 }}>
        已有账号？<Link to="/login">去登录</Link>
      </p>
    </div>
  );
}

export default RegisterPage;
