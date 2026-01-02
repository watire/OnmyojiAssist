import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { compute, formatNumber, normalizeOperator } from '../lib/compute.js';
import { loadHistory, saveHistory } from '../lib/storage.js';
import './Calculator.css';

const HISTORY_KEY = 'onmyojiassist_calculator_history_v1';

function nowIso() {
  return new Date().toISOString();
}

export default function Calculator() {
  const [display, setDisplay] = useState('0');
  const [formula, setFormula] = useState('');
  const [previous, setPrevious] = useState(null);
  const [operator, setOperator] = useState(null);
  const [waitingForOperand, setWaitingForOperand] = useState(false);
  const [error, setError] = useState(null);

  const [history, setHistory] = useState(() => loadHistory(HISTORY_KEY));

  useEffect(() => {
    saveHistory(HISTORY_KEY, history);
  }, [history]);

  const buttons = useMemo(
    () => [
      { label: 'AC', kind: 'action', action: 'allClear' },
      { label: 'C', kind: 'action', action: 'clearEntry' },
      { label: '⌫', kind: 'action', action: 'backspace' },
      { label: '÷', kind: 'op', op: '÷' },

      { label: '7', kind: 'digit', value: '7' },
      { label: '8', kind: 'digit', value: '8' },
      { label: '9', kind: 'digit', value: '9' },
      { label: '×', kind: 'op', op: '×' },

      { label: '4', kind: 'digit', value: '4' },
      { label: '5', kind: 'digit', value: '5' },
      { label: '6', kind: 'digit', value: '6' },
      { label: '-', kind: 'op', op: '-' },

      { label: '1', kind: 'digit', value: '1' },
      { label: '2', kind: 'digit', value: '2' },
      { label: '3', kind: 'digit', value: '3' },
      { label: '+', kind: 'op', op: '+' },

      { label: '0', kind: 'digit', value: '0', className: 'span2' },
      { label: '.', kind: 'dot' },
      { label: '=', kind: 'equals' }
    ],
    []
  );

  const resetCalculator = useCallback(() => {
    setDisplay('0');
    setFormula('');
    setPrevious(null);
    setOperator(null);
    setWaitingForOperand(false);
    setError(null);
  }, []);

  const clearEntry = useCallback(() => {
    setDisplay('0');
    setError(null);
  }, []);

  const backspace = useCallback(() => {
    if (waitingForOperand || error) return;

    setDisplay((prev) => {
      if (prev.length <= 1) return '0';
      return prev.slice(0, -1);
    });
  }, [waitingForOperand, error]);

  const inputDigit = useCallback(
    (d) => {
      if (error) {
        resetCalculator();
        setDisplay(d);
        return;
      }

      if (waitingForOperand) {
        setDisplay(d);
        setWaitingForOperand(false);
        return;
      }

      setDisplay((prev) => {
        if (prev === '0') return d;
        return prev + d;
      });
    },
    [error, resetCalculator, waitingForOperand]
  );

  const inputDot = useCallback(() => {
    if (error) {
      resetCalculator();
      setDisplay('0.');
      return;
    }

    if (waitingForOperand) {
      setDisplay('0.');
      setWaitingForOperand(false);
      return;
    }

    setDisplay((prev) => {
      if (prev.includes('.')) return prev;
      return prev + '.';
    });
  }, [error, resetCalculator, waitingForOperand]);

  const handleOperator = useCallback(
    (opUi) => {
      if (error) return;

      const currentValue = Number.parseFloat(display);
      if (Number.isNaN(currentValue)) {
        setError('输入无效');
        return;
      }

      if (previous === null) {
        setPrevious(currentValue);
        setOperator(opUi);
        setFormula(`${display} ${opUi}`);
        setWaitingForOperand(true);
        return;
      }

      if (waitingForOperand) {
        setOperator(opUi);
        setFormula(`${formatNumber(previous)} ${opUi}`);
        return;
      }

      try {
        const result = compute(previous, operator, currentValue);
        setPrevious(result);
        setOperator(opUi);
        setDisplay(formatNumber(result));
        setFormula(`${formatNumber(result)} ${opUi}`);
        setWaitingForOperand(true);
      } catch (e) {
        setError(e?.message || '计算出错');
      }
    },
    [display, error, operator, previous, waitingForOperand]
  );

  const handleEquals = useCallback(() => {
    if (error) return;
    if (!operator || previous === null || waitingForOperand) return;

    const currentValue = Number.parseFloat(display);
    if (Number.isNaN(currentValue)) {
      setError('输入无效');
      return;
    }

    try {
      const result = compute(previous, operator, currentValue);
      const expression = `${formatNumber(previous)} ${operator} ${display}`;
      const record = {
        id: `${nowIso()}_${Math.random().toString(16).slice(2)}`,
        expression,
        result: formatNumber(result),
        at: nowIso()
      };

      setHistory((prevHist) => [record, ...prevHist]);
      setDisplay(formatNumber(result));
      setFormula('');
      setPrevious(null);
      setOperator(null);
      setWaitingForOperand(false);
    } catch (e) {
      setError(e?.message || '计算出错');
    }
  }, [display, error, operator, previous, waitingForOperand]);

  const clearHistory = useCallback(() => {
    setHistory([]);
  }, []);

  useEffect(() => {
    function onKeyDown(e) {
      const key = e.key;

      if (key >= '0' && key <= '9') {
        e.preventDefault();
        inputDigit(key);
        return;
      }

      if (key === '.') {
        e.preventDefault();
        inputDot();
        return;
      }

      if (key === 'Enter' || key === '=') {
        e.preventDefault();
        handleEquals();
        return;
      }

      if (key === 'Escape') {
        e.preventDefault();
        resetCalculator();
        return;
      }

      if (key === 'Backspace') {
        e.preventDefault();
        backspace();
        return;
      }

      const maybeOp = normalizeOperator(key);
      if (maybeOp) {
        e.preventDefault();
        handleOperator(maybeOp);
      }
    }

    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [backspace, handleEquals, handleOperator, inputDigit, inputDot, resetCalculator]);

  return (
    <div className="calcLayout">
      <section className="calcCard">
        <div className="display">
          <div className="formula" aria-label="formula">
            {formula || '\u00A0'}
          </div>
          <div className={`value ${error ? 'valueError' : ''}`} aria-label="display">
            {error ? error : display}
          </div>
        </div>

        <div className="keypad" role="group" aria-label="calculator keypad">
          {buttons.map((b) => {
            const className = [
              'btn',
              b.kind === 'op' ? 'btnOp' : '',
              b.kind === 'equals' ? 'btnEquals' : '',
              b.kind === 'action' ? 'btnAction' : '',
              b.className || ''
            ]
              .filter(Boolean)
              .join(' ');

            const onClick = () => {
              if (b.kind === 'digit') inputDigit(b.value);
              if (b.kind === 'dot') inputDot();
              if (b.kind === 'op') handleOperator(b.op);
              if (b.kind === 'equals') handleEquals();
              if (b.kind === 'action') {
                if (b.action === 'allClear') resetCalculator();
                if (b.action === 'clearEntry') clearEntry();
                if (b.action === 'backspace') backspace();
              }
            };

            return (
              <button key={b.label} className={className} onClick={onClick} type="button">
                {b.label}
              </button>
            );
          })}
        </div>

        <div className="hint">键盘支持：0-9、+ - * /、Enter、Backspace、Esc</div>
      </section>

      <aside className="historyCard">
        <div className="historyHeader">
          <div className="historyTitle">历史记录</div>
          <button className="clearHistory" type="button" onClick={clearHistory} disabled={history.length === 0}>
            清除
          </button>
        </div>

        {history.length === 0 ? (
          <div className="historyEmpty">暂无历史记录</div>
        ) : (
          <ul className="historyList">
            {history.map((h) => (
              <li key={h.id} className="historyItem">
                <div className="historyExpr">{h.expression}</div>
                <div className="historyResult">= {h.result}</div>
              </li>
            ))}
          </ul>
        )}
      </aside>
    </div>
  );
}
