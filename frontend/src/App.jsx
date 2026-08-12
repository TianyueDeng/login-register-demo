/**
 * App.jsx —— 根组件，负责路由：根据网址决定显示哪个页面
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import RegisterPage from './pages/RegisterPage';
import LoginPage from './pages/LoginPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* TODO：网址是 /register 时，显示注册页 */}
        <Route path="/register" element={<RegisterPage />} />

        {/* TODO：网址是 /login 时，显示登录页 */}
        <Route path="/login" element={<LoginPage />} />

        {/* 默认打开网站时（网址是根路径 / ），跳转到登录页 */}
        <Route path="/" element={<Navigate to="/login" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
