import Calculator from './components/Calculator.jsx';

export default function App() {
  return (
    <div className="app">
      <header className="appHeader">
        <h1 className="appTitle">OnmyojiAssist 计算器</h1>
        <div className="appSubtitle">React 网页版（含历史记录）</div>
      </header>

      <main className="appMain">
        <Calculator />
      </main>

      <footer className="appFooter">
        <span>本模块仅为项目附加工具，不涉及登录/鉴权。</span>
      </footer>
    </div>
  );
}
