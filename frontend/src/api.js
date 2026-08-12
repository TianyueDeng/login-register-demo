/**
 * api.js —— 统一管理所有对Flask后端的接口调用
 * 对应《接口与数据库设计文档》第二章：接口设计
 */

import axios from 'axios';

// Base URL：Flask后端的地址
const BASE_URL = 'http://localhost:5000';

/**
 * 注册接口
 * @param {Object} data - { username, password, confirm_password }
 * @returns Promise，resolve后能拿到 { status, message } 或 { status, message, data }
 */
export const registerUser = (data) => {
  return axios.post(`${BASE_URL}/api/register`, data);
};

/**
 * 登录接口
 * @param {Object} data - { username, password }
 */
export const loginUser = (data) => {
  return axios.post(`${BASE_URL}/api/login`, data);
};

// TODO：如果后续需要处理请求失败（比如后端没启动、网络错误），
// 可以在这里用 axios 的拦截器（interceptor）统一处理，暂时先不用管这个，
// 页面组件里用 try/catch 包住调用即可。
