/**
 * LoginPage.jsx —— 登录页
 * 对应《前端页面原型说明》登录页布局 + 需求规格说明书 F-02/F-06
 */

import { useState } from 'react';
import { Input, Button } from 'antd';
import { Link, useNavigate } from 'react-router-dom';
import { loginUser } from '../api';

function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [welcomeName, setWelcomeName] = useState(''); // 登录成功后显示"欢迎，xxx"用
  const navigate = useNavigate();

  const handleLogin = async () => {
    try {
      const response = await loginUser({username, password});
      
      if (response.data.status === 'success') {
        setWelcomeName(response.data.data.username);
        setErrorMsg('')
      }else {
        setErrorMsg(response.data.message);
      }
    } catch (err) {
      if (err.response) {
        setErrorMsg(err.response.data.message);
      } else {
        setErrorMsg('网络异常，请稍后重试');
      }
    }
  };

  return (
    <div style={{ maxWidth: 360, margin: '80px auto' }}>
      <h2>登录</h2>

      <Input
        placeholder="用户名"
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

      {/* 错误提示：F-06要求用户名不存在/密码错误提示语必须一致 */}
      {errorMsg && <p style={{ color: 'red', marginBottom: 12 }}>{errorMsg}</p>}

      {/* 登录成功后的欢迎信息（简化版，先不单独做首页） */}
      {welcomeName && <p style={{ color: 'green', marginBottom: 12 }}>欢迎，{welcomeName}</p>}

      <Button type="primary" block onClick={handleLogin}>
        登录
      </Button>

      <p style={{ textAlign: 'center', marginTop: 16 }}>
        没有账号？<Link to="/register">去注册</Link>
      </p>
    </div>
  );
}

export default LoginPage;
