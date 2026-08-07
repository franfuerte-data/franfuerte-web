"""
Generate SVG visualizations for blog articles.
Run from project root: python scripts/gen_charts.py
"""
import os, math, textwrap

OUT = os.path.join(os.path.dirname(__file__), '..', 'public', 'charts')
os.makedirs(OUT, exist_ok=True)

# ── 1. Radar chart: Lakehouse vs Data Warehouse ──────────────────────────────

def radar_lakehouse_vs_dw():
    dims = [
        ("SQL / T-SQL",      9, 4),
        ("Python / Spark",   2, 9),
        ("Power BI directo", 9, 6),
        ("Streaming",        3, 8),
        ("Time travel",      2, 9),
        ("ML / Ciencia dato",2, 8),
        ("Aprendizaje",      8, 5),
        ("Flex. formatos",   4, 9),
    ]
    n = len(dims)
    labels  = [d[0] for d in dims]
    dw_vals = [d[1] for d in dims]
    lh_vals = [d[2] for d in dims]

    cx, cy, R = 260, 215, 150
    angles = [2*math.pi*i/n - math.pi/2 for i in range(n)]

    def pt(val, angle, rmax=R):
        r = val/10*rmax
        return cx + r*math.cos(angle), cy + r*math.sin(angle)

    def polygon(vals, angle_list):
        return " ".join(f"{pt(v,a)[0]:.1f},{pt(v,a)[1]:.1f}" for v,a in zip(vals, angle_list))

    grid_lines = ""
    for level in [2,4,6,8,10]:
        pts = " ".join(f"{pt(level,a)[0]:.1f},{pt(level,a)[1]:.1f}" for a in angles)
        grid_lines += f'<polygon points="{pts}" fill="none" stroke="rgba(255,255,255,0.07)" stroke-width="1"/>\n'

    spokes = ""
    label_els = ""
    for i,(lbl,_,_) in enumerate(dims):
        a = angles[i]
        x2,y2 = pt(10,a)
        spokes += f'<line x1="{cx}" y1="{cy}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="rgba(255,255,255,0.07)" stroke-width="1"/>\n'
        lx, ly = pt(11.5, a)
        anchor = "middle"
        if lx < cx-10: anchor = "end"
        elif lx > cx+10: anchor = "start"
        wrapped = textwrap.wrap(lbl, 12)
        dy_start = -0.5*(len(wrapped)-1)*14
        txt_els = ""
        for j,line in enumerate(wrapped):
            dy = dy_start + j*14
            txt_els += f'<tspan x="{lx:.1f}" dy="{dy:.0f}">{line}</tspan>'
        label_els += f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" fill="#94a3b8" font-size="11" font-family="Arial,sans-serif">{txt_els}</text>\n'

    dw_poly  = polygon(dw_vals, angles)
    lh_poly  = polygon(lh_vals, angles)

    svg = f"""<svg viewBox="0 0 520 430" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:520px;display:block">
  <rect width="520" height="430" fill="rgba(255,255,255,0.02)" rx="16"/>
  {grid_lines}
  {spokes}
  <polygon points="{dw_poly}" fill="rgba(245,158,11,0.18)" stroke="#f59e0b" stroke-width="2.5" stroke-linejoin="round"/>
  <polygon points="{lh_poly}" fill="rgba(99,102,241,0.18)" stroke="#6366f1" stroke-width="2.5" stroke-linejoin="round"/>
  {label_els}
  <!-- Legend -->
  <rect x="310" y="30" width="12" height="12" fill="#f59e0b" rx="3"/>
  <text x="330" y="41" fill="#e2e8f0" font-size="12" font-family="Arial,sans-serif" font-weight="600">Data Warehouse</text>
  <rect x="310" y="52" width="12" height="12" fill="#6366f1" rx="3"/>
  <text x="330" y="63" fill="#e2e8f0" font-size="12" font-family="Arial,sans-serif" font-weight="600">Lakehouse</text>
  <text x="260" y="410" text-anchor="middle" fill="#475569" font-size="10" font-family="Arial,sans-serif">Valoración relativa 1–10. Ambas herramientas son complementarias, no excluyentes.</text>
</svg>"""
    with open(os.path.join(OUT, 'radar-lakehouse-vs-dw.svg'), 'w', encoding='utf-8') as f:
        f.write(svg)
    print("OK radar-lakehouse-vs-dw.svg")


# ── 2. Token cost bar chart for Claude/MCP article ───────────────────────────

def bar_token_cost():
    data = [
        ("Prompt acotado\n(tabla específica)", 21_000, 0.06),
        ("Sesión media\n(modelo completo)", 105_000, 0.30),
        ("Modelo grande\n(26k líneas)", 210_000, 0.60),
    ]

    max_tokens = 210_000
    W, H = 560, 260
    pad_l, pad_r, pad_t, pad_b = 40, 30, 40, 70
    chart_w = W - pad_l - pad_r
    chart_h = H - pad_t - pad_b
    bar_w   = chart_w / len(data) * 0.45
    gap     = chart_w / len(data)

    colors = ["#22c55e", "#f59e0b", "#ef4444"]
    bars_svg = ""
    labels_svg = ""

    for i, (lbl, tokens, cost) in enumerate(data):
        bh = (tokens / max_tokens) * chart_h
        bx = pad_l + gap*i + gap*0.275
        by = pad_t + chart_h - bh

        bars_svg += f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w:.1f}" height="{bh:.1f}" fill="{colors[i]}" rx="6" opacity="0.85"/>\n'
        bars_svg += f'<text x="{bx + bar_w/2:.1f}" y="{by - 8:.1f}" text-anchor="middle" fill="{colors[i]}" font-size="13" font-weight="700" font-family="Arial,sans-serif">{int(tokens/1000)}k tokens</text>\n'
        bars_svg += f'<text x="{bx + bar_w/2:.1f}" y="{by - 24:.1f}" text-anchor="middle" fill="white" font-size="14" font-weight="900" font-family="Arial,sans-serif">${cost:.2f}</text>\n'

        # x-axis label (multi-line)
        lines = lbl.split('\n')
        for j,line in enumerate(lines):
            ly = pad_t + chart_h + 18 + j*14
            labels_svg += f'<text x="{bx + bar_w/2:.1f}" y="{ly:.1f}" text-anchor="middle" fill="#94a3b8" font-size="10.5" font-family="Arial,sans-serif">{line}</text>\n'

    baseline_y = pad_t + chart_h

    svg = f"""<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:{W}px;display:block">
  <rect width="{W}" height="{H}" fill="rgba(255,255,255,0.02)" rx="16"/>
  <text x="{W//2}" y="24" text-anchor="middle" fill="#e2e8f0" font-size="13" font-weight="700" font-family="Arial,sans-serif">Coste estimado por sesión — Claude Sonnet + Power BI MCP</text>
  <!-- Grid lines -->
  <line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{baseline_y}" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>
  <line x1="{pad_l}" y1="{baseline_y}" x2="{W-pad_r}" y2="{baseline_y}" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>
  {bars_svg}
  {labels_svg}
</svg>"""
    with open(os.path.join(OUT, 'bar-token-cost.svg'), 'w', encoding='utf-8') as f:
        f.write(svg)
    print("OK bar-token-cost.svg")


# ── 3. Dashboard layers visual (powerbi article) ──────────────────────────────

def dashboard_layers():
    W, H = 580, 200
    layers = [
        ("#7c3aed", "#a78bfa", "NIVEL 1 — Dirección", "1 página · 6 KPIs · Semáforo · Tendencia", 0),
        ("#1d4ed8", "#60a5fa", "NIVEL 2 — Mandos intermedios", "2–3 páginas · Desglose · Rankings · Drill-through", 1),
        ("#065f46", "#34d399", "NIVEL 3 — Equipo analítico", "Tablas detalladas · Transacciones · Metodología", 2),
    ]

    rects = ""
    texts = ""
    for bg, acc, title, desc, i in layers:
        y = 20 + i*56
        rects += f'<rect x="20" y="{y}" width="{W-40}" height="48" rx="10" fill="{bg}" opacity="0.15"/>\n'
        rects += f'<rect x="20" y="{y}" width="6" height="48" rx="3" fill="{acc}" opacity="0.8"/>\n'
        texts += f'<text x="42" y="{y+18}" fill="{acc}" font-size="11" font-weight="700" font-family="Arial,sans-serif">{title}</text>\n'
        texts += f'<text x="42" y="{y+34}" fill="#94a3b8" font-size="10" font-family="Arial,sans-serif">{desc}</text>\n'

    svg = f"""<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:{W}px;display:block">
  <rect width="{W}" height="{H}" fill="rgba(255,255,255,0.02)" rx="14"/>
  <text x="{W//2}" y="18" text-anchor="middle" fill="#64748b" font-size="11" font-family="Arial,sans-serif" font-weight="600" letter-spacing="0.1em">MODELO DE TRES CAPAS DE REPORTE</text>
  {rects}
  {texts}
  <text x="{W//2}" y="{H-10}" text-anchor="middle" fill="#334155" font-size="9.5" font-family="Arial,sans-serif">La dirección opera en Nivel 1. El equipo analítico accede a todos los niveles.</text>
</svg>"""
    with open(os.path.join(OUT, 'dashboard-3-layers.svg'), 'w', encoding='utf-8') as f:
        f.write(svg)
    print("OK dashboard-3-layers.svg")


# ── 4. MCP flow diagram ────────────────────────────────────────────────────────

def mcp_comparison():
    W, H = 560, 180
    items = [
        ("#7c3aed","#a78bfa","Local (stdio)","Power BI Modeling MCP","Power BI Desktop + VS Code","Modelo semántico: medidas, relaciones, DAX"),
        ("#0284c7","#38bdf8","Cloud (HTTP)","Power BI Remote MCP","Fabric F2+ o Premium P1","Consultar datos del servicio publicado"),
    ]
    rects = ""
    for i,(bg,acc,tipo,name,req,desc) in enumerate(items):
        x = 20 + i*270
        rects += f'<rect x="{x}" y="30" width="250" height="135" rx="12" fill="{bg}" opacity="0.1"/>\n'
        rects += f'<rect x="{x}" y="30" width="250" height="4" rx="2" fill="{acc}" opacity="0.8"/>\n'
        rects += f'<text x="{x+125}" y="56" text-anchor="middle" fill="{acc}" font-size="10" font-weight="700" font-family="Arial,sans-serif" letter-spacing="0.08em">{tipo.upper()}</text>\n'
        rects += f'<text x="{x+125}" y="76" text-anchor="middle" fill="#e2e8f0" font-size="12" font-weight="700" font-family="Arial,sans-serif">{name}</text>\n'
        rects += f'<text x="{x+125}" y="96" text-anchor="middle" fill="#64748b" font-size="9.5" font-family="Arial,sans-serif">Requisitos: {req}</text>\n'
        wrapped = textwrap.wrap(desc, 30)
        for j,line in enumerate(wrapped):
            rects += f'<text x="{x+125}" y="{116+j*14}" text-anchor="middle" fill="#94a3b8" font-size="9.5" font-family="Arial,sans-serif">{line}</text>\n'

    svg = f"""<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:{W}px;display:block">
  <rect width="{W}" height="{H}" fill="rgba(255,255,255,0.02)" rx="14"/>
  <text x="{W//2}" y="20" text-anchor="middle" fill="#64748b" font-size="10.5" font-family="Arial,sans-serif" font-weight="600" letter-spacing="0.1em">DOS SERVIDORES MCP PARA POWER BI — SON DISTINTOS</text>
  {rects}
  <text x="280" y="170" text-anchor="middle" fill="#334155" font-size="9" font-family="Arial,sans-serif">Este artículo cubre el servidor Local. No requiere Fabric ni licencia Premium.</text>
</svg>"""
    with open(os.path.join(OUT, 'mcp-comparison.svg'), 'w', encoding='utf-8') as f:
        f.write(svg)
    print("OK mcp-comparison.svg")


radar_lakehouse_vs_dw()
bar_token_cost()
dashboard_layers()
mcp_comparison()
print("\nAll charts generated in src/assets/charts/")
