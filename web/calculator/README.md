# React 网页版计算器（OnmyojiAssist 模块）

本目录是 OnmyojiAssist 项目中的一个独立 React 网页模块：基础四则运算 + 计算历史记录。

## 功能

- 加（+）、减（-）、乘（×）、除（÷）
- 计算历史记录展示（本地浏览器 localStorage 持久化）
- 一键清除历史记录
- 输入校验与错误处理（例如：除以 0）

## 开发与运行

> 需要 Node.js 18+。

```bash
cd web/calculator
npm install
npm run dev
```

然后打开终端输出的本地地址（通常是 http://localhost:5173）。

## 测试

```bash
npm test
```

## 键盘快捷键

- 数字：`0-9`
- 运算：`+ - * /`
- 等于：`Enter`
- 退格：`Backspace`
- 清空：`Esc`
