def generate_stats_html(stats: dict) -> str:
    if not stats:
        return "<p>No valid trades in selected period.</p>"

    max_loss = stats["max_loss"] if stats["max_loss"] < 0 else 0.0

    html = f"""
    <ul class="metrics-list">
        <li><span class="stat-title">💼 Trades</span><span class="stat-value">{stats['total']}</span></li>
        <li><span class="stat-title">✅ Wins</span><span class="stat-value">{stats['wins']}</span></li>
        <li><span class="stat-title">❌ Losses</span><span class="stat-value">{stats['losses']}</span></li>
        <li><span class="stat-title">📈 Max Win</span><span class="stat-value">${stats['max_win']:.2f}</span></li>
        <li><span class="stat-title">📉 Max Loss</span><span class="stat-value">${max_loss:.2f}</span></li>
        <li><span class="stat-title">🏆 Win Rate</span><span class="stat-value">{stats['win_rate']:.1f}%</span></li>
        <li><span class="stat-title">📊 Avg Win</span><span class="stat-value">${stats['avg_win']:.2f}</span></li>
        <li><span class="stat-title">📊 Avg Loss</span><span class="stat-value">${stats['avg_loss']:.2f}</span></li>
        <li><span class="stat-title">💡 Expectancy</span><span class="stat-value">{stats['expectancy']:.2f}</span></li>
        <li><span class="stat-title">💰 Total PnL</span><span class="stat-value">${stats['profit']:.2f}</span></li>
        <li><span class="stat-title">📊 Total Return (%)</span>
            <span class="stat-value">
                <span style="color:{'limegreen' if stats.get('pnl_pct', 0) > 0 else 'tomato'};">{stats.get('pnl_pct', 0):.2f}%</span>
            </span>
        </li>
    </ul>
    """
    return html