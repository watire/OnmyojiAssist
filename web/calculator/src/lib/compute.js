const UI_TO_INTERNAL_OPERATOR = {
  '+': '+',
  '-': '-',
  '×': '*',
  '÷': '/',
  '*': '*',
  '/': '/'
};

export function normalizeOperator(key) {
  if (key === '*') return '×';
  if (key === '/') return '÷';
  if (key === '+' || key === '-') return key;
  return null;
}

export function compute(a, operatorUi, b) {
  const operator = UI_TO_INTERNAL_OPERATOR[operatorUi];
  const left = Number(a);
  const right = Number(b);

  if (!operator) throw new Error('未知操作符');
  if (Number.isNaN(left) || Number.isNaN(right)) throw new Error('输入无效');

  switch (operator) {
    case '+':
      return left + right;
    case '-':
      return left - right;
    case '*':
      return left * right;
    case '/':
      if (right === 0) throw new Error('不能除以 0');
      return left / right;
    default:
      throw new Error('未知操作符');
  }
}

export function formatNumber(n) {
  if (typeof n !== 'number' || Number.isNaN(n)) return '0';
  if (!Number.isFinite(n)) return 'Error';

  const str = String(n);
  if (!str.includes('e') && str.length <= 14) return str;

  return n.toPrecision(12).replace(/\.0+$/u, '').replace(/(\.\d*?)0+$/u, '$1');
}
