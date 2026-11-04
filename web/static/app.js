// Portfolio Analyzer: renders the JSON from /api/analyze into hash-routed views (#/overview, #/holding/AAPL, ...).
(() => {
  const canvas = document.getElementById('canvas');
  const MINUS = '−';
  const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);

  // ---------- formatting: true minus, a sign on every change, tabular figures in CSS ----------
  const nf = (min, max = min) => new Intl.NumberFormat('en-US', { minimumFractionDigits: min, maximumFractionDigits: max });
  const sign = (v) => (v < 0 ? MINUS : '');
  const plus = (v) => (v > 0 ? '+' : '');
  const money = (v, d = 2) => `${sign(v)}$${nf(d).format(Math.abs(v))}`;
  const compactMoney = (v) => `${sign(v)}$${new Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 }).format(Math.abs(v))}`;
  const pct = (v, d = 1) => (v == null ? '–' : `${sign(v)}${nf(d).format(Math.abs(v * 100))}%`);
  const signedPct = (v, d = 1) => (v == null ? '–' : plus(v) + pct(v, d));
  const signedMoney = (v) => plus(v) + money(v);
  const dec = (v, d = 2) => (v == null ? '–' : sign(v) + nf(d).format(Math.abs(v)));
  const pts = (v) => `${plus(v)}${sign(v)}${nf(1).format(Math.abs(v * 100))} pts`;
  const shares = (v) => nf(0, 4).format(v);
  const tone = (v) => (v > 0.00005 ? 'up' : v < -0.00005 ? 'down' : '');
  const day = (iso, year = false) => new Date(`${iso}T12:00:00`).toLocaleDateString('en-US', { month: 'short', day: 'numeric', ...(year ? { year: 'numeric' } : {}) });
  const cents = (v) => Math.round(v * 100) / 100;
  const listing = (items) => (items.length < 2 ? items.join('') : `${items.slice(0, -1).join(', ')} and ${items.at(-1)}`);

  // ---------- state ----------
  const DEFAULT_HOLDINGS = [
    { ticker: 'AAPL', shares: 10, purchase_price: 230 },
    { ticker: 'MSFT', shares: 5, purchase_price: 400 },
    { ticker: 'NVDA', shares: 8, purchase_price: 180 },
  ];
  // the holdings are a per-browser convenience; the page works without storage
  const saved = (() => { try { return JSON.parse(localStorage.getItem('portfolio-holdings')); } catch { return null; } })();
  const state = { holdings: Array.isArray(saved) && saved.length ? saved : DEFAULT_HOLDINGS, data: null, error: null, loading: false, news: {}, target: 'maximum_sharpe', simBusy: false };
  const MAX_PATH_YEARS = 10000; // matches web/api.py: about 20 MB of paths per run
  const maxPaths = (years) => Math.min(10000, Math.floor(MAX_PATH_YEARS / years / 100) * 100);
  const save = () => { try { localStorage.setItem('portfolio-holdings', JSON.stringify(state.holdings)); } catch { /* storage blocked: keep in memory */ } };

  async function request(url, body) {
    let res;
    try {
      res = await fetch(url, body ? { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) } : {});
    } catch {
      throw new Error('The analyzer server could not be reached. Check that it is running, then try again.');
    }
    const json = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(json.error || `The request failed (${res.status}).`);
    return json;
  }

  async function analyze() {
    state.loading = true; state.error = null; state.news = {};
    render();
    try { state.data = await request('/api/analyze', { holdings: state.holdings }); }
    catch (e) { state.error = e.message; state.data = null; }
    state.loading = false;
    render();
  }

  // ---------- derived figures, computed from rows as displayed so totals agree ----------
  function rows(d) {
    return Object.entries(d.holdings)
      .map(([ticker, h]) => ({ ticker, ...h, current_value: cents(h.current_value), cost_basis: cents(h.cost_basis) }))
      .map((h) => ({ ...h, gain_loss: cents(h.current_value - h.cost_basis) }))
      .sort((a, b) => b.current_value - a.current_value);
  }
  function totals(list) {
    const value = cents(list.reduce((s, h) => s + h.current_value, 0));
    const cost = cents(list.reduce((s, h) => s + h.cost_basis, 0));
    return { value, cost, gain: cents(value - cost), ret: cost ? (value - cost) / cost : 0 };
  }
  const drawdownOf = (values) => { let peak = -Infinity; return values.map((v) => { peak = Math.max(peak, v); return v / peak - 1; }); };
  const belowZeroTicks = (values) => Charts.ticks(Math.min(...values), 0, 4).filter((v) => v <= 1e-9);
  const holdingsWord = (n) => `${n} holding${n === 1 ? '' : 's'}`;

  // ---------- markup helpers ----------
  const title = (h1, sub, extra = '') => `<div class="title-row s12"><div><h1>${h1}</h1>${sub ? `<p class="sub">${sub}</p>` : ''}</div>${extra}</div>`;
  const kpi = (label, value, sub = '', cls = '') => `<div class="kpi"><div class="kpi-label">${label}</div><div class="kpi-value num ${cls}">${value}</div>${sub ? `<div class="delta">${sub}</div>` : ''}</div>`;
  const kpis = (cells) => `<div class="kpis s12">${cells.join('')}</div>`;
  const panel = (cls, h2, body, meta = '', id = '') => `<section class="panel ${cls}"${id ? ` id="${id}"` : ''}><header><h2>${h2}</h2>${meta}</header>${body}</section>`;
  const toned = (v, text) => `<span class="${tone(v)}">${text}</span>`;
  const empty = (msg, action = '') => `<section class="panel s12"><div class="empty"><div class="notice" style="justify-items:center">${msg}${action}</div></div></section>`;

  // ---------- views ----------
  function overview(d) {
    const list = rows(d), t = totals(list), c = d.comparison, top = d.attribution[0];
    const ahead = c.excess_return >= 0 ? 'ahead of' : 'behind';
    // last session: each holding's move between the two most recent closes
    const prev = list.reduce((sum, h) => sum + h.shares * d.stocks[h.ticker].prices.values.at(-2), 0);
    const last = list.reduce((sum, h) => sum + h.shares * d.stocks[h.ticker].prices.values.at(-1), 0);
    const session = { change: cents(last - prev), ret: prev ? last / prev - 1 : 0 };
    const byReturn = Object.keys(d.stocks).sort((a, b) => d.stocks[b].metrics.cumulative_return - d.stocks[a].metrics.cumulative_return);
    const best = byReturn[0], worstStock = byReturn.at(-1);
    const lead = list.length > 1 && top.Contribution > 0 ? ` ${esc(top.Ticker)} added the most, ${pts(top.Contribution)} of it.` : '';
    canvas.innerHTML = [
      title('Overview', `Over the past year at today's weights, the portfolio returned ${signedPct(c.portfolio_return)}, ${nf(1).format(Math.abs(c.excess_return * 100))} pts ${ahead} the S&amp;P 500 (${signedPct(c.benchmark_return)}).${lead}`),
      kpis([
        kpi('Market value', money(t.value), `${holdingsWord(list.length)} at the ${day(d.as_of, true)} close`),
        kpi('Cost basis', money(t.cost), 'What you paid'),
        kpi('Unrealized gain', toned(t.gain, signedMoney(t.gain)), 'Market value less cost basis'),
        kpi('Return since purchase', toned(t.ret, signedPct(t.ret)), 'On cost basis'),
      ]),
      panel('s8', 'Past year: portfolio against the S&amp;P 500', '<div class="chart" id="growth-chart"></div>', '<div id="growth-legend"></div>'),
      panel('s4', 'Allocation', `<div id="weights"></div><dl class="facts">
        <div><dt>Last session</dt><dd>${toned(session.change, `${signedMoney(session.change)} (${signedPct(session.ret)})`)}</dd></div>
        <div><dt>Best 1-year stock</dt><dd>${esc(best)} ${signedPct(d.stocks[best].metrics.cumulative_return)}</dd></div>
        <div><dt>Worst 1-year stock</dt><dd>${esc(worstStock)} ${signedPct(d.stocks[worstStock].metrics.cumulative_return)}</dd></div>
      </dl>`, '<span class="meta">Share of market value</span>'),
      panel('s12', 'Holdings', `<div class="table-wrap"><table>
        <thead><tr><th>Ticker</th><th class="n">Shares</th><th class="n">Avg cost</th><th class="n">Price</th><th class="n">Market value</th><th class="n">Gain / loss</th><th class="n">Return</th><th class="n">Weight</th></tr></thead>
        <tbody>${list.map((h) => `<tr>
          <td><a href="#/holding/${encodeURIComponent(h.ticker)}">${esc(h.ticker)}</a></td>
          <td class="n">${shares(h.shares)}</td><td class="n">${money(h.purchase_price)}</td><td class="n">${money(h.current_price)}</td>
          <td class="n">${money(h.current_value)}</td><td class="n">${toned(h.gain_loss, signedMoney(h.gain_loss))}</td>
          <td class="n">${toned(h.return_percentage, signedPct(h.return_percentage / 100))}</td><td class="n">${pct(h.weight / 100)}</td></tr>`).join('')}</tbody>
        <tfoot><tr><td>Total</td><td></td><td></td><td></td><td class="n">${money(t.value)}</td><td class="n">${toned(t.gain, signedMoney(t.gain))}</td><td class="n">${toned(t.ret, signedPct(t.ret))}</td><td class="n">${pct(1)}</td></tr></tfoot>
      </table></div>`, `<a class="card-link" href="#/edit">Edit holdings</a>`),
    ].join('');
    Charts.line(document.getElementById('growth-chart'), {
      labels: d.growth.dates.map((x) => day(x)),
      series: [{ name: 'Portfolio', values: d.growth.portfolio.map((g) => g - 1) }, { name: `S&P 500 (${d.benchmark})`, values: d.growth.benchmark.map((g) => g - 1) }],
      format: signedPct, tickFormat: (v) => pct(v, 0), height: 264, endLabel: true, legend: '#growth-legend',
    });
    Charts.barList(document.getElementById('weights'), list.map((h) => ({ label: h.ticker, value: h.weight / 100 })), { format: (v) => pct(v) });
  }

  function performance(d) {
    const c = d.comparison, dd = d.drawdown.values, worst = dd.indexOf(Math.min(...dd));
    const spyDd = drawdownOf(d.growth.benchmark);
    const attr = d.attribution, span = Math.max(...attr.map((r) => Math.abs(r.Contribution))) || 1;
    canvas.innerHTML = [
      title('Performance', `One year of daily closes, weighted by today's holdings and compared with the S&amp;P 500 (${d.benchmark}). The Sharpe ratio assumes a 0% risk-free rate.`),
      kpis([
        kpi('1-year return', toned(c.portfolio_return, signedPct(c.portfolio_return)), `${pts(c.excess_return)} against S&amp;P 500 at ${signedPct(c.benchmark_return)}`),
        kpi('Volatility', pct(c.portfolio_volatility), `S&amp;P 500 ${pct(c.benchmark_volatility)}, annualized`),
        kpi('Sharpe ratio', dec(c.portfolio_sharpe), `S&amp;P 500 ${dec(c.benchmark_sharpe)}`),
        kpi('Max drawdown', pct(c.portfolio_max_drawdown), `S&amp;P 500 ${pct(c.benchmark_max_drawdown)}`),
      ]),
      panel('s7', 'Drawdown from the running peak', '<div class="chart" id="dd-chart"></div>', '<div id="dd-legend"></div>'),
      panel('s5', 'Return attribution', `<div class="rows">${attr.map((r) => {
        const w = (Math.abs(r.Contribution) / span) * 50;
        return `<div class="contrib"><span>${esc(r.Ticker)}<span class="sub">${pct(r.Weight / 100)} weight</span></span>
          <span class="track" aria-hidden="true"><span class="bar ${r.Contribution < 0 ? 'neg' : ''}" style="${r.Contribution < 0 ? `right:50%;width:${w}%` : `left:50%;width:${w}%`}"></span></span>
          <span class="value">${pts(r.Contribution)}<span class="sub">stock ${signedPct(r['Stock Return'])}</span></span></div>`;
      }).join('')}</div>`, '<span class="meta">Weight × the stock’s 1-year return</span>'),
    ].join('');
    Charts.line(document.getElementById('dd-chart'), {
      labels: d.drawdown.dates.map((x) => day(x)),
      series: [{ name: 'Portfolio', values: dd }, { name: `S&P 500 (${d.benchmark})`, values: spyDd }],
      format: (v) => pct(v), tickFormat: (v) => pct(v, 0), height: 248, yTicks: belowZeroTicks([...dd, ...spyDd]), legend: '#dd-legend',
      annotations: [{ at: worst, label: `Deepest ${pct(dd[worst])} on ${day(d.drawdown.dates[worst])}` }],
    });
  }

  function diversification(d) {
    const v = d.diversification;
    if (!v) { canvas.innerHTML = title('Diversification', '') + empty('Diversification needs at least two holdings to compare.', '<a class="btn" href="#/edit">Add a holding</a>'); return; }
    const m = v.correlation_matrix, n = m.tickers.length, pairs = [];
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) pairs.push({ a: m.tickers[i], b: m.tickers[j], r: m.values[i][j] });
    pairs.sort((x, y) => y.r - x.r);
    const shown = pairs.slice(0, 6), close = pairs.filter((p) => p.r > 0.7).length;
    const cell = (r, diag) => `<td style="background:${diag ? 'var(--raised)' : `color-mix(in srgb, var(--accent) ${Math.round(Math.max(0, r) * 55)}%, var(--surface))`}">${dec(r)}</td>`;
    canvas.innerHTML = [
      title('Diversification', `${esc(v.largest_position.ticker)} is ${pct(v.largest_position.weight / 100)} of the portfolio. By concentration, your ${n} holdings behave like ${dec(v.effective_holdings, 1)} equal-sized positions.`),
      kpis([
        kpi('Holdings', String(v.number_of_holdings)),
        kpi('Largest position', esc(v.largest_position.ticker), `${pct(v.largest_position.weight / 100)} of market value`),
        kpi('Top 3 concentration', pct(v.top_3_concentration / 100), n <= 3 ? 'All holdings' : `Of ${n} holdings`),
        kpi('Effective holdings', dec(v.effective_holdings), `1 ÷ HHI of ${dec(v.hhi, 3)}`),
        kpi('Average correlation', dec(v.average_correlation), 'Daily returns, past year'),
      ]),
      panel('s7', 'Correlation of daily returns', `<div class="table-wrap"><table class="matrix">
        <thead><tr><th></th>${m.tickers.map((t) => `<th scope="col">${esc(t)}</th>`).join('')}</tr></thead>
        <tbody>${m.tickers.map((t, i) => `<tr><th scope="row">${esc(t)}</th>${m.values[i].map((r, j) => cell(r, i === j)).join('')}</tr>`).join('')}</tbody>
      </table></div>`, '<span class="meta">1 moves together, 0 unrelated</span>'),
      panel('s5', 'Most correlated pairs', `<dl class="facts" style="margin-top:0">${shown.map((p) => `<div><dt>${esc(p.a)} and ${esc(p.b)}</dt><dd>${dec(p.r)}</dd></div>`).join('')}</dl>
        <p class="meta" style="margin-top:14px">${close ? `${close} of ${pairs.length} pair${pairs.length === 1 ? '' : 's'} move closely together (above 0.70), so they add little diversification.` : 'No pair moves closely together (above 0.70).'}</p>`,
        `<span class="meta">${shown.length} of ${pairs.length} pair${pairs.length === 1 ? '' : 's'}</span>`),
    ].join('');
  }

  function optimization(d) {
    const o = d.optimization;
    if (!o) { canvas.innerHTML = title('Optimization', '') + empty(d.diversification ? 'The optimizer could not find a solution for these holdings.' : 'Optimization needs at least two holdings to reweight.', '<a class="btn" href="#/edit">Edit holdings</a>'); return; }
    const pick = o[state.target], cur = o.current, names = { current: 'Current weights', minimum_volatility: 'Minimum volatility', maximum_sharpe: 'Maximum Sharpe' };
    const lower = { minimum_volatility: 'minimum-volatility', maximum_sharpe: 'maximum-Sharpe' }[state.target];
    const value = totals(rows(d)).value;
    const tickers = Object.keys(cur.weights).sort((a, b) => cur.weights[b] - cur.weights[a]);
    canvas.innerHTML = [
      title('Optimization', `On the past year's returns, the ${lower} mix would have returned ${pct(pick.expected_return)} a year at ${pct(pick.volatility)} volatility, against ${pct(cur.expected_return)} at ${pct(cur.volatility)} for your current weights.`,
        `<div class="segmented" role="group" aria-label="Target allocation">${['maximum_sharpe', 'minimum_volatility'].map((k) => `<button type="button" data-target="${k}" aria-pressed="${state.target === k}">${names[k]}</button>`).join('')}</div>`),
      panel('s7', `Current weight against the ${lower} target`, `<div id="bullets"></div><dl class="facts">${tickers.map((t) => {
        const change = (pick.weights[t] - cur.weights[t]) * value, qty = change / d.holdings[t].current_price;
        return `<div><dt>${esc(t)} to reach target</dt><dd>${Math.abs(qty) < 0.005 ? 'No change' : `${toned(change, signedMoney(cents(change)))} <span class="meta">${plus(qty)}${dec(qty)} shares</span>`}</dd></div>`;
      }).join('')}</dl>`, '<span class="meta">Tick marks the target</span>'),
      panel('s5', 'Allocations compared', `<div class="table-wrap"><table>
        <thead><tr><th>Allocation</th><th class="n">Return</th><th class="n">Volatility</th><th class="n">Sharpe</th></tr></thead>
        <tbody>${['current', 'minimum_volatility', 'maximum_sharpe'].map((k) => `<tr aria-selected="${k === state.target}"><td>${names[k]}</td><td class="n">${pct(o[k].expected_return)}</td><td class="n">${pct(o[k].volatility)}</td><td class="n">${dec(o[k].sharpe_ratio)}</td></tr>`).join('')}</tbody>
      </table></div><p class="meta" style="margin-top:14px">Annualized from the past year of daily returns. Long only, fully invested, 0% risk-free rate. A backward look, not a forecast.</p>`),
    ].join('');
    Charts.bullet(document.getElementById('bullets'), tickers.map((t) => ({ label: t, value: cur.weights[t], target: pick.weights[t] })), { format: (v) => pct(v), max: 1 });
    // drift here is the point of the comparison, not an alarm, so it stays grey
    canvas.querySelectorAll('#bullets li > span:last-child > span').forEach((el) => { el.style.color = 'var(--muted)'; });
    canvas.querySelectorAll('[data-target]').forEach((b) => b.addEventListener('click', () => { state.target = b.dataset.target; optimization(d); }));
  }

  function simulation(d) {
    const s = d.simulation, init = s.initial_value, years = s.years;
    const edges = s.histogram.edges, mids = s.histogram.counts.map((_, i) => (edges[i] + edges[i + 1]) / 2);
    const losing = mids.map((m, i) => (m < init ? i : -1)).filter((i) => i >= 0);
    const horizon = `${years} year${years === 1 ? '' : 's'}`;
    const label = (dd) => (dd === 0 ? 'Today' : years <= 2 ? `${Math.round(dd / 21)} mo` : `Year ${nf(0, 1).format(dd / 252)}`);
    canvas.innerHTML = [
      title('Monte Carlo simulation', `Across ${nf(0).format(s.simulations)} simulated paths over ${horizon}, the portfolio ends below today's ${money(init)} in ${pct(s.probability_of_loss)} of them. The median path ends at ${money(s.summary.median)}.`),
      `<div class="controls s12">
        <div class="range"><label for="sims">Paths</label><input id="sims" type="range" min="100" max="${maxPaths(years)}" step="100" value="${s.simulations}" aria-describedby="sims-cap"><output for="sims">${nf(0).format(s.simulations)}</output><span class="meta" id="sims-cap">Up to ${nf(0).format(maxPaths(years))} at this horizon</span></div>
        <div class="range"><label for="years">Horizon</label><input id="years" type="range" min="1" max="10" step="1" value="${years}"><output for="years">${horizon}</output></div>
        <button class="btn" type="button" id="rerun">Run again</button>
      </div>`,
      kpis([
        kpi('Median ending value', money(s.summary.median), `${toned(s.summary.median - init, signedMoney(s.summary.median - init))} from today`),
        kpi('5th percentile', money(s.summary.percentile_5), '1 path in 20 ends lower'),
        kpi('95th percentile', money(s.summary.percentile_95), '1 path in 20 ends higher'),
        kpi('Probability of loss', pct(s.probability_of_loss), `Ends below ${money(init, 0)}`),
        kpi('95% value at risk', money(s.value_at_risk), 'Loss at the 5th percentile'),
      ]),
      panel('s8 sim', `Range of outcomes over ${horizon}`, '<div class="chart" id="fan"></div>', '<div id="fan-legend"></div>'),
      panel('s4 sim', 'Ending values', '<div class="chart" id="hist"></div>', `<span class="meta">Below today in ${pct(s.probability_of_loss, 0)}</span>`),
    ].join('');
    Charts.line(document.getElementById('fan'), {
      labels: s.days.map(label),
      series: [{ name: 'Median', values: s.bands.p50 }, { name: '95th percentile', values: s.bands.p95 }, { name: '5th percentile', values: s.bands.p5 }],
      format: (v) => money(v, 0), tickFormat: compactMoney, height: 264, min: Math.min(...s.bands.p5, init), reference: { value: init, label: `Today ${money(init, 0)}` }, legend: '#fan-legend',
    });
    const negative = getComputedStyle(document.documentElement).getPropertyValue('--negative').trim();
    Charts.bars(document.getElementById('hist'), {
      labels: mids.map(compactMoney), values: s.histogram.counts, format: (v) => `${nf(0).format(v)} paths`, tickFormat: (v) => nf(0).format(v),
      height: 264, highlight: losing, colour: negative, xAt: [0, Math.floor(mids.length / 2), mids.length - 1],
    });

    const sims = document.getElementById('sims'), yrs = document.getElementById('years');
    let timer;
    const rerun = () => { clearTimeout(timer); timer = setTimeout(() => runSimulation(+sims.value, +yrs.value), 250); };
    sims.addEventListener('input', () => { sims.nextElementSibling.textContent = nf(0).format(+sims.value); rerun(); });
    yrs.addEventListener('input', () => {
      yrs.nextElementSibling.textContent = `${yrs.value} year${yrs.value === '1' ? '' : 's'}`;
      // a lower max clamps the slider's value, so the run stays inside the server's budget
      sims.max = maxPaths(+yrs.value);
      sims.nextElementSibling.textContent = nf(0).format(+sims.value);
      document.getElementById('sims-cap').textContent = `Up to ${nf(0).format(maxPaths(+yrs.value))} at this horizon`;
      rerun();
    });
    document.getElementById('rerun').addEventListener('click', () => runSimulation(+sims.value, +yrs.value));
  }

  async function runSimulation(simulations, years) {
    const d = state.data;
    canvas.querySelectorAll('.sim').forEach((p) => p.classList.add('busy'));
    try {
      // the same annualized mean and volatility the server estimated from the daily portfolio returns
      d.simulation = await request('/api/simulate', { ...d.simulation_params, initial_value: d.simulation.initial_value, simulations, years });
      if (route().name === 'simulation') simulation(d);
    } catch (e) {
      canvas.querySelectorAll('.sim').forEach((el) => el.classList.remove('busy'));
      alertBox(e.message);
    }
  }

  function holding(d, ticker) {
    const list = rows(d), h = list.find((x) => x.ticker === ticker) || list[0];
    const s = d.stocks[h.ticker], m = s.metrics, dd = s.drawdown, worst = dd.indexOf(Math.min(...dd));
    canvas.innerHTML = [
      `<nav class="tabs s12" aria-label="Holdings">${list.map((x) => `<a href="#/holding/${encodeURIComponent(x.ticker)}" aria-selected="${x.ticker === h.ticker}">${esc(x.ticker)}</a>`).join('')}</nav>`,
      title(esc(h.ticker), `${shares(h.shares)} shares bought at ${money(h.purchase_price)}, now ${pct(h.weight / 100)} of the portfolio.`),
      kpis([
        kpi('Price', money(h.current_price), `${day(d.as_of, true)} close`),
        kpi('Position value', money(h.current_value), `Cost ${money(h.cost_basis)}`),
        kpi('Gain / loss', toned(h.gain_loss, signedMoney(h.gain_loss)), 'Since purchase'),
        kpi('Return since purchase', toned(h.return_percentage, signedPct(h.return_percentage / 100)), 'On cost basis'),
        kpi('1-year return', toned(m.cumulative_return, signedPct(m.cumulative_return)), 'Price change'),
      ]),
      panel('s8', 'Price, past year', '<div class="chart" id="price-chart"></div>'),
      panel('s4', 'Risk, past year', `<dl class="facts">
        <div><dt>Volatility, annualized</dt><dd>${pct(m.annualized_volatility)}</dd></div>
        <div><dt>Sharpe ratio</dt><dd>${dec(m.sharpe_ratio)}</dd></div>
        <div><dt>Max drawdown</dt><dd>${pct(m.max_drawdown)}</dd></div>
        <div><dt>Past-year high</dt><dd>${money(Math.max(...s.prices.values))}</dd></div>
        <div><dt>Below the high</dt><dd>${pct(dd.at(-1))}</dd></div>
        <div><dt>Past-year low</dt><dd>${money(Math.min(...s.prices.values))}</dd></div>
      </dl>`),
      panel('s5', 'Drawdown from the running peak', '<div class="chart" id="stock-dd"></div>'),
      panel('s7', 'Recent news', '<div id="news-body"><div class="skeleton line"></div><div class="skeleton line"></div><div class="skeleton line" style="width:70%"></div></div>', '<span class="meta" id="news-meta">Scored with VADER sentiment</span>', 'news'),
    ].join('');
    Charts.line(document.getElementById('price-chart'), {
      labels: s.prices.dates.map((x) => day(x)), series: [{ name: h.ticker, values: s.prices.values }],
      format: (v) => money(v), tickFormat: (v) => money(v, 0), height: 264, min: Math.min(...s.prices.values, h.purchase_price) * 0.95, endLabel: true,
      reference: { value: h.purchase_price, label: `Bought at ${money(h.purchase_price)}` },
    });
    Charts.line(document.getElementById('stock-dd'), {
      labels: s.prices.dates.map((x) => day(x)), series: [{ name: `${h.ticker} drawdown`, values: dd }],
      format: (v) => pct(v), tickFormat: (v) => pct(v, 0), height: 220, yTicks: belowZeroTicks(dd),
      annotations: [{ at: worst, label: `Deepest ${pct(dd[worst])}` }],
    });
    document.getElementById('news').dataset.ticker = h.ticker;
    loadNews(h.ticker);
  }

  async function loadNews(ticker) {
    if (!state.news[ticker]) {
      state.news[ticker] = request('/api/news', { ticker }).catch((e) => ({ error: e.message }));
    }
    const n = await state.news[ticker];
    const body = document.getElementById('news-body');
    // the visitor may have moved to another holding while this was loading
    if (!body || document.getElementById('news').dataset.ticker !== ticker) return;
    if (n.error) { body.innerHTML = `<div class="empty">News for ${esc(ticker)} is unavailable right now. Prices and analysis above are unaffected.</div>`; return; }
    if (!n.articles.length) { body.innerHTML = `<div class="empty">No recent articles found for ${esc(ticker)}.</div>`; return; }
    const pill = (label) => `<span class="pill ${label === 'Positive' ? 'pos' : label === 'Negative' ? 'neg' : ''}">${esc(label)}</span>`;
    document.getElementById('news-meta').innerHTML = `${pill(n.summary.overall_sentiment)} <span style="margin-left:6px">Average ${dec(n.summary.average_score)} across ${n.summary.article_count}</span>`;
    body.innerHTML = `<ul class="news">${n.articles.map((a) => `<li>
      ${a.url ? `<a href="${esc(a.url)}" target="_blank" rel="noopener noreferrer">${esc(a.title)}</a>` : `<span>${esc(a.title)}</span>`}
      ${pill(a.sentiment_label)}
      <span class="meta">${esc(a.publisher)} · score ${dec(a.sentiment_score)}</span></li>`).join('')}</ul>`;
  }

  function edit() {
    const row = (h = {}) => `<tr>
      <td><input class="input ticker" name="ticker" aria-label="Ticker" placeholder="Ticker, e.g. AAPL" value="${esc(h.ticker)}" maxlength="12" autocomplete="off" spellcheck="false"></td>
      <td><input class="input num" name="shares" aria-label="Shares" type="number" min="0" step="any" inputmode="decimal" placeholder="Shares" value="${esc(h.shares)}"></td>
      <td><input class="input num" name="purchase_price" aria-label="Purchase price per share in dollars" type="number" min="0" step="any" inputmode="decimal" placeholder="Price paid" value="${esc(h.purchase_price)}"></td>
      <td><button class="btn ghost icon-btn remove" type="button" aria-label="Remove holding"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M4 4l8 8M12 4l-8 8"/></svg></button></td></tr>`;
    canvas.innerHTML = [
      title('Holdings', 'Enter each position as the number of shares and the price you paid per share. Prices, history and news come from Yahoo Finance.'),
      `<section class="panel s8"><form id="holdings-form" novalidate>
        <table class="editor"><thead><tr><th>Ticker</th><th>Shares</th><th>Price paid per share</th><th></th></tr></thead>
        <tbody>${state.holdings.map(row).join('')}</tbody></table>
        <div class="form-actions"><button class="btn" type="button" id="add-row">Add holding</button><span style="flex:1"></span><button class="btn primary" type="submit">Analyze portfolio</button></div>
        <p class="form-error" id="form-error" role="alert"></p>
      </form></section>`,
      `<section class="panel s4"><header><h2>How it is analyzed</h2></header><dl class="facts">
        <div><dt>History</dt><dd>1 year of daily closes</dd></div>
        <div><dt>Benchmark</dt><dd>S&amp;P 500 (SPY)</dd></div>
        <div><dt>Risk-free rate</dt><dd>0%</dd></div>
        <div><dt>Simulation</dt><dd>1,000 paths, 1 year</dd></div>
        <div><dt>Saved</dt><dd>In this browser only</dd></div>
      </dl><p class="meta" style="margin-top:14px">The server uses your holdings only to compute the analysis and keeps no copy. Ticker symbols are looked up on Yahoo Finance.</p>
      <button class="btn" type="button" id="forget" style="margin-top:14px">Forget saved holdings</button></section>`,
    ].join('');
    const form = document.getElementById('holdings-form'), tbody = form.querySelector('tbody'), error = document.getElementById('form-error');
    document.getElementById('forget').addEventListener('click', () => {
      try { localStorage.removeItem('portfolio-holdings'); } catch { /* storage blocked: nothing was saved */ }
      state.holdings = DEFAULT_HOLDINGS;
      edit();
      const note = document.getElementById('form-error');
      note.style.color = 'var(--muted)';
      note.textContent = 'Saved holdings removed from this browser. The sample portfolio is shown.';
    });
    document.getElementById('add-row').addEventListener('click', () => { tbody.insertAdjacentHTML('beforeend', row()); tbody.lastElementChild.querySelector('input').focus(); });
    tbody.addEventListener('click', (e) => { const b = e.target.closest('.remove'); if (b) b.closest('tr').remove(); });
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const holdings = [...tbody.rows].map((tr) => ({ ticker: tr.querySelector('[name=ticker]').value.trim().toUpperCase(), shares: parseFloat(tr.querySelector('[name=shares]').value), purchase_price: parseFloat(tr.querySelector('[name=purchase_price]').value) }))
        .filter((h) => h.ticker || !Number.isNaN(h.shares) || !Number.isNaN(h.purchase_price));
      const bad = holdings.find((h) => !/^[A-Z0-9.\-^=]{1,12}$/.test(h.ticker) || !(h.shares > 0) || !(h.purchase_price > 0));
      if (!holdings.length) { error.textContent = 'Add at least one holding.'; return; }
      if (bad) { error.textContent = `Check ${bad.ticker || 'the row without a ticker'}: it needs a ticker, shares above 0 and a price above 0.`; return; }
      state.holdings = holdings; save();
      location.hash = '#/overview';
      analyze();
    });
  }

  function loading() {
    const tickers = state.holdings.map((h) => esc(String(h.ticker).toUpperCase()));
    canvas.innerHTML = [
      `<div class="title-row s12"><div><h1>Analyzing portfolio</h1><p class="sub">Fetching a year of prices for ${listing(tickers)} and the S&amp;P 500. This takes a few seconds.</p></div></div>`,
      kpis([0, 1, 2, 3].map(() => '<div class="kpi"><div class="skeleton line" style="width:40%"></div><div class="skeleton big"></div></div>')),
      `<section class="panel s8"><div class="skeleton" style="height:264px"></div></section><section class="panel s4"><div class="skeleton" style="height:264px"></div></section>`,
    ].join('');
  }

  function failed() {
    canvas.innerHTML = title('This portfolio could not be analyzed', esc(state.error)) +
      `<div class="form-actions s12" style="margin-top:0"><button class="btn primary" type="button" id="retry">Try again</button><a class="btn" href="#/edit">Edit holdings</a></div>`;
    document.getElementById('retry').addEventListener('click', analyze);
  }

  function alertBox(msg) {
    canvas.insertAdjacentHTML('afterbegin', `<p class="form-error s12" role="alert">${esc(msg)}</p>`);
  }

  // ---------- shell ----------
  const VIEWS = { overview, performance, diversification, optimization, simulation, holding, edit };
  function route() {
    const [name, arg] = location.hash.replace(/^#\/?/, '').split('/');
    // the holdings editor is the landing page, so a first visit starts where the portfolio is set up
    return { name: VIEWS[name] ? name : 'edit', arg: arg ? decodeURIComponent(arg) : null };
  }

  function render() {
    const { name, arg } = route(), d = state.data;
    document.querySelectorAll('.nav-item').forEach((a) => (a.dataset.view === name ? a.setAttribute('aria-current', 'page') : a.removeAttribute('aria-current')));
    const summary = document.getElementById('summary');
    if (d) {
      const t = totals(rows(d));
      summary.innerHTML = `<strong class="num">${money(t.value)}</strong><span class="num ${tone(t.ret)}">${signedPct(t.ret)}</span><span class="stamp">${holdingsWord(rows(d).length)} · ${day(d.as_of, true)} close</span>`;
    } else summary.innerHTML = state.loading ? '<span class="stamp">Loading prices…</span>' : '';
    document.title = `${name === 'holding' && d ? (arg || rows(d)[0].ticker) : name[0].toUpperCase() + name.slice(1)} · Portfolio Analyzer`;
    if (name === 'edit') edit();
    else if (state.loading) loading();
    else if (state.error) failed();
    else if (d) VIEWS[name](d, arg);
    window.scrollTo(0, 0);
  }

  const sidebar = document.getElementById('sidebar');
  document.querySelector('.menu-toggle').addEventListener('click', () => sidebar.classList.add('open'));
  sidebar.addEventListener('click', (e) => { if (e.target.closest('.close, .nav-item')) sidebar.classList.remove('open'); });
  window.addEventListener('hashchange', render);
  analyze();
})();
