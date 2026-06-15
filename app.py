"""
财务分析报告 Web 版 - Streamlit 应用
基于医化4部销售数据自动生成美观的网页分析报告
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ===================== 页面配置 =====================
st.set_page_config(
    page_title="医化4部 - 财务分析报告",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== 自定义CSS样式 =====================
def load_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
        
        * {
            font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
        }
        
        .main {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 0;
        }
        
        /* 报告容器 */
        .report-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        /* 标题区域 */
        .report-header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            padding: 3rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            position: relative;
            overflow: hidden;
        }
        .report-header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
            animation: pulse 8s ease-in-out infinite;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.2); }
        }
        .report-header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0;
            position: relative;
            letter-spacing: 4px;
            text-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        .report-header p {
            font-size: 1.1rem;
            opacity: 0.85;
            margin-top: 0.5rem;
            position: relative;
            letter-spacing: 2px;
        }
        .report-header .badge {
            display: inline-block;
            background: rgba(255,255,255,0.15);
            padding: 0.3rem 1.5rem;
            border-radius: 20px;
            font-size: 0.85rem;
            margin-top: 1rem;
            position: relative;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        /* 板块标题 */
        .section-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #1a1a2e;
            margin: 2rem 0 1.5rem 0;
            padding-left: 1rem;
            border-left: 4px solid #0f3460;
            line-height: 1.4;
        }
        .section-subtitle {
            font-size: 1.1rem;
            font-weight: 500;
            color: #333;
            margin: 1.2rem 0 0.8rem 0;
            padding-left: 0.8rem;
            border-left: 3px solid #e94560;
        }
        
        /* KPI 卡片 */
        .kpi-card {
            background: white;
            padding: 1.5rem;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
            text-align: center;
            transition: all 0.3s ease;
            border: 1px solid rgba(0,0,0,0.03);
            height: 100%;
        }
        .kpi-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.1);
        }
        .kpi-card .kpi-label {
            font-size: 0.9rem;
            color: #888;
            margin-bottom: 0.5rem;
            font-weight: 500;
            letter-spacing: 1px;
        }
        .kpi-card .kpi-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #1a1a2e;
        }
        .kpi-card .kpi-change {
            font-size: 0.9rem;
            margin-top: 0.4rem;
            font-weight: 500;
        }
        .kpi-card .kpi-change.positive { color: #22c55e; }
        .kpi-card .kpi-change.negative { color: #ef4444; }
        .kpi-card .kpi-change.neutral { color: #f59e0b; }
        
        /* 数据卡片 */
        .data-card {
            background: white;
            padding: 1.5rem;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
            margin-bottom: 1.5rem;
            border: 1px solid rgba(0,0,0,0.03);
        }
        .data-card .card-title {
            font-size: 1rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #f0f0f0;
        }
        
        /* 总结卡片 */
        .summary-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 20px;
            color: white;
            margin: 2rem 0;
            box-shadow: 0 20px 60px rgba(102,126,234,0.3);
        }
        .summary-card h3 {
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 1rem;
            letter-spacing: 2px;
        }
        .summary-card p {
            font-size: 1rem;
            line-height: 1.8;
            opacity: 0.95;
        }
        .summary-card .highlight-positive { color: #86efac; font-weight: 600; }
        .summary-card .highlight-negative { color: #fca5a5; font-weight: 600; }
        .summary-card .highlight-neutral { color: #fde68a; font-weight: 600; }
        
        /* 数据表格美化 */
        .dataframe {
            width: 100%;
            border-collapse: collapse;
        }
        .dataframe thead th {
            background: #f8fafc;
            padding: 0.75rem 1rem;
            text-align: center;
            font-weight: 600;
            font-size: 0.85rem;
            color: #475569;
            border-bottom: 2px solid #e2e8f0;
        }
        .dataframe tbody td {
            padding: 0.7rem 1rem;
            text-align: center;
            border-bottom: 1px solid #f1f5f9;
            font-size: 0.9rem;
        }
        .dataframe tbody tr:hover {
            background: #f8fafc;
        }
        .dataframe tbody tr.total-row {
            background: #f1f5f9;
            font-weight: 600;
        }
        
        /* 状态指示器 */
        .status-tag {
            display: inline-block;
            padding: 0.2rem 0.8rem;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        .status-tag.up { background: #dcfce7; color: #16a34a; }
        .status-tag.down { background: #fce4ec; color: #d32f2f; }
        .status-tag.flat { background: #fef3c7; color: #d97706; }
        
        /* 隐藏 Streamlit 默认元素 */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stApp {background: transparent;}
        .stApp > header {display: none;}
        
        /* 按钮样式 */
        .stButton > button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 0.5rem 2rem;
            border-radius: 12px;
            font-weight: 500;
            transition: all 0.3s;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102,126,234,0.4);
        }
        
        /* 文件上传区域 */
        .upload-section {
            background: white;
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
            margin-bottom: 2rem;
            border: 2px dashed #c3cfe2;
        }
        
        /* 指标网格 */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        @media (max-width: 768px) {
            .report-header h1 { font-size: 1.8rem; }
            .kpi-card .kpi-value { font-size: 1.4rem; }
            .metrics-grid { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
    """, unsafe_allow_html=True)

# ===================== 配置 =====================
DEPARTMENT_NAME = '医化4部'
CUTOFF_MONTH = 202605
current_year = CUTOFF_MONTH // 100
current_month = CUTOFF_MONTH % 100
last_year = current_year - 1
last_year_cutoff = last_year * 100 + current_month

MONTH_NAMES = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月']

# ===================== 辅助函数 =====================
def safe_divide(numerator, denominator):
    if pd.isna(denominator) or denominator == 0:
        return 0
    return numerator / denominator

def format_currency(value):
    """金额格式化为万元，带千分位"""
    if pd.isna(value):
        return '0.00'
    return f'{value / 10000:,.2f}'

def format_percent(value):
    if pd.isna(value):
        return '0.00%'
    return f'{value * 100:.2f}%'

def format_growth(value):
    if pd.isna(value):
        return '0.00%'
    return f'{value * 100:+,.2f}%'

def get_color_for_change(value):
    if value > 0.05:
        return 'positive'
    elif value < -0.05:
        return 'negative'
    return 'neutral'

def get_change_tag(value):
    if value > 0.05:
        return '📈 增长'
    elif value < -0.05:
        return '📉 下降'
    return '➡️ 持平'

def highlight_class(value, higher_is_better=True):
    """返回CSS类名"""
    if pd.isna(value):
        return 'neutral'
    if higher_is_better:
        if value > 0:
            return 'positive'
        elif value < 0:
            return 'negative'
    else:
        if value < 0:
            return 'positive'
        elif value > 0:
            return 'negative'
    return 'neutral'

# ===================== 数据加载 =====================
@st.cache_data(ttl=3600)
def load_all_data(sales_path, profit_path, expense_path):
    """加载并处理所有数据"""
    results = {}
    
    try:
        # 1. 销售数据
        sales_current_df = pd.read_excel(sales_path, sheet_name=f'{current_year}年')
        sales_last_df = pd.read_excel(sales_path, sheet_name=f'{last_year}年')
        if '月份' not in sales_last_df.columns:
            sales_last_df.rename(columns={sales_last_df.columns[-1]: '月份'}, inplace=True)
        
        sales_current_filtered = sales_current_df[sales_current_df['月份'] <= CUTOFF_MONTH].copy()
        sales_last_filtered = sales_last_df[sales_last_df['月份'] <= last_year_cutoff].copy()
        
        results['sales_current'] = sales_current_filtered
        results['sales_last'] = sales_last_filtered
        
        # 2. 利润数据
        profit_df = pd.read_excel(profit_path, sheet_name='单票利润核算单')
        profit_df = profit_df[profit_df['部门'].str.contains('医化', na=False)].copy()
        profit_df['发货年月'] = profit_df['发货日期'].dt.to_period('M').astype(int)
        
        results['profit_current'] = profit_df[(profit_df['归属年度'] == current_year) & (profit_df['发货年月'] <= CUTOFF_MONTH)].copy()
        results['profit_last'] = profit_df[(profit_df['归属年度'] == last_year) & (profit_df['发货年月'] <= last_year_cutoff)].copy()
        results['profit_all'] = profit_df
        
        # 3. 费用数据
        expense_category_df = pd.read_excel(expense_path, sheet_name='费用分类')
        expense_current_df = pd.read_excel(expense_path, sheet_name=f'{current_year}年')
        expense_last_df = pd.read_excel(expense_path, sheet_name=f'{last_year}年')
        
        results['expense_category'] = expense_category_df
        results['expense_current'] = expense_current_df
        results['expense_last'] = expense_last_df
        
        results['success'] = True
    except Exception as e:
        results['success'] = False
        results['error'] = str(e)
    
    return results

def calculate_indicators(data):
    """计算所有分析指标"""
    indicators = {}
    
    sales_cur = data['sales_current']
    sales_last = data['sales_last']
    profit_cur = data['profit_current']
    profit_last = data['profit_last']
    exp_cur = data['expense_current']
    exp_last = data['expense_last']
    exp_cat = data['expense_category']
    
    # === 核心经营指标 ===
    cur_income = sales_cur['抵消后收入'].sum()
    cur_cost = sales_cur['抵消后成本'].sum()
    cur_profit = sales_cur['利润'].sum()
    cur_margin = safe_divide(cur_profit, cur_income)
    
    last_income = sales_last['抵消后收入'].sum()
    last_cost = sales_last['抵消后成本'].sum()
    last_profit = sales_last['利润'].sum()
    last_margin = safe_divide(last_profit, last_income)
    
    indicators['current'] = {
        'income': cur_income,
        'cost': cur_cost,
        'profit': cur_profit,
        'margin': cur_margin
    }
    indicators['last'] = {
        'income': last_income,
        'cost': last_cost,
        'profit': last_profit,
        'margin': last_margin
    }
    indicators['yoy'] = {
        'income_growth': safe_divide(cur_income - last_income, last_income),
        'cost_growth': safe_divide(cur_cost - last_cost, last_cost),
        'profit_growth': safe_divide(cur_profit - last_profit, last_profit),
        'margin_change': cur_margin - last_margin
    }
    
    # === 客户TOP5 ===
    cust_sum = sales_cur.groupby('实际客户', dropna=False).agg(
        收入=('抵消后收入','sum'), 利润=('利润','sum')
    ).reset_index()
    indicators['customer_top5'] = cust_sum.sort_values('收入', ascending=False).head(5).fillna(0)
    
    # === 供应商TOP5 ===
    supp_sum = sales_cur.groupby('实际供应商', dropna=False).agg(
        采购成本=('抵消后成本','sum')
    ).reset_index()
    indicators['supplier_top5'] = supp_sum.sort_values('采购成本', ascending=False).head(5).fillna(0)
    
    # === 商品TOP5 ===
    prod_sum = sales_cur.groupby('商品中文品名', dropna=False).agg(
        收入=('抵消后收入','sum'), 利润=('利润','sum')
    ).reset_index()
    prod_sum = prod_sum[prod_sum['商品中文品名'] != '其他']
    indicators['product_top5'] = prod_sum.sort_values('利润', ascending=False).head(5).fillna(0)
    
    # === 业务员TOP5 ===
    sp_cur = profit_cur.groupby('业务员', dropna=False).agg(
        销售收入=('销售收入','sum'), 利润=('利润','sum')
    ).reset_index()
    sp_last = profit_last.groupby('业务员', dropna=False).agg(
        上年利润=('利润','sum')
    ).reset_index()
    
    sp_summary = pd.merge(sp_cur, sp_last, on='业务员', how='left').fillna(0)
    sp_summary['利润率'] = sp_summary.apply(lambda x: safe_divide(x['利润'], x['销售收入']), axis=1)
    sp_summary['同比利润变化'] = sp_summary['利润'] - sp_summary['上年利润']
    indicators['salesperson_top5'] = sp_summary.sort_values('利润', ascending=False).head(5).reset_index(drop=True)
    
    # === 费用分析 ===
    cat_map = dict(zip(exp_cat.iloc[:, 0], exp_cat.iloc[:, 1]))
    target_cats = ['业务招待费', '差旅费', '展会费', '保险费']
    
    exp_cur['费用类别'] = exp_cur['科目'].map(cat_map)
    exp_last['费用类别'] = exp_last['科目'].map(cat_map)
    
    exp_cur_sum = exp_cur[exp_cur['费用类别'].isin(target_cats)].groupby('费用类别')['借方'].sum().reset_index()
    exp_cur_sum.columns = ['费用类别', '本年累计']
    exp_last_sum = exp_last[exp_last['费用类别'].isin(target_cats)].groupby('费用类别')['借方'].sum().reset_index()
    exp_last_sum.columns = ['费用类别', '上年同期']
    
    expense_df = pd.merge(exp_cur_sum, exp_last_sum, on='费用类别', how='left').fillna(0)
    expense_df['同比增减额'] = expense_df['本年累计'] - expense_df['上年同期']
    expense_df['同比增幅'] = expense_df.apply(lambda x: safe_divide(x['同比增减额'], x['上年同期']), axis=1)
    indicators['expense_summary'] = expense_df
    
    # === 人员费用TOP5 ===
    person_df = exp_cur[exp_cur['费用类别'].isin(['业务招待费', '差旅费'])].copy()
    person_df = person_df[
        person_df['人员'].notna() & 
        (person_df['人员'].str.strip() != '') & 
        (person_df['人员'].str.strip() != '其他')
    ]
    
    person_summary = person_df.groupby('人员').agg(
        业务招待费=('借方', lambda x: x[person_df['费用类别'] == '业务招待费'].sum()),
        差旅费=('借方', lambda x: x[person_df['费用类别'] == '差旅费'].sum())
    ).reset_index()
    person_summary['总费用'] = person_summary['业务招待费'] + person_summary['差旅费']
    indicators['person_expense_top5'] = person_summary.sort_values('总费用', ascending=False).head(5).reset_index(drop=True)
    
    # === 月度趋势数据 ===
    monthly = sales_cur.groupby('月份').agg(
        收入=('抵消后收入','sum'), 利润=('利润','sum')
    ).reset_index().sort_values('月份')
    indicators['monthly_trend'] = monthly
    
    return indicators

# ===================== 图表生成 =====================
def create_monthly_chart(monthly_df):
    """创建月度收入利润趋势图"""
    months = monthly_df['月份'].astype(str).str[-2:] + '月'
    
    fig = make_subplots(specs=[[{"secondary_y": False}]])
    
    fig.add_trace(
        go.Bar(name='月度收入', x=months, y=monthly_df['收入']/10000,
               marker_color='#5470C6', text=monthly_df['收入']/10000,
               texttemplate='%{text:.1f}', textposition='outside',
               hovertemplate='%{x}<br>收入: %{text:.2f}万元<extra></extra>'),
    )
    fig.add_trace(
        go.Bar(name='月度利润', x=months, y=monthly_df['利润']/10000,
               marker_color='#91CC75', text=monthly_df['利润']/10000,
               texttemplate='%{text:.1f}', textposition='outside',
               hovertemplate='%{x}<br>利润: %{text:.2f}万元<extra></extra>'),
    )
    
    fig.update_layout(
        title=dict(text=f'{current_year}年1-{current_month}月 月度收入 & 利润趋势', 
                   font=dict(size=16, color='#1a1a2e'), x=0.5),
        barmode='group',
        bargap=0.25,
        bargroupgap=0.1,
        xaxis=dict(title='月份', tickfont=dict(size=12)),
        yaxis=dict(title='金额（万元）', gridcolor='#f0f0f0'),
        plot_bgcolor='white',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=40, r=40, t=60, b=40),
        height=400,
    )
    
    fig.update_yaxes(gridcolor='#e8e8e8')
    return fig

def create_pie_chart(data, names_col, values_col, title, color_scheme=None):
    """创建饼图"""
    colors = color_scheme or px.colors.qualitative.Set2
    
    fig = px.pie(
        data, names=names_col, values=values_col,
        title=title,
        color_discrete_sequence=colors,
        hole=0.4
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='%{label}<br>%{value:.2f}万元<br>占比: %{percent}<extra></extra>'
    )
    fig.update_layout(
        showlegend=False,
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='white',
        font=dict(size=12)
    )
    return fig

# ===================== 渲染函数 =====================
def render_kpi_cards(indicators):
    """渲染核心KPI卡片"""
    cur = indicators['current']
    last = indicators['last']
    yoy = indicators['yoy']
    
    cols = st.columns(4)
    kpis = [
        ('累计收入', cur['income'], yoy['income_growth'],
         f"上年同期: {format_currency(last['income'])}万元"),
        ('累计成本', cur['cost'], yoy['cost_growth'],
         f"上年同期: {format_currency(last['cost'])}万元", False),
        ('累计利润', cur['profit'], yoy['profit_growth'],
         f"上年同期: {format_currency(last['profit'])}万元"),
        ('利润率', cur['margin'], yoy['margin_change'],
         f"上年同期: {format_percent(last['margin'])}", True, True),
    ]
    
    for i, (col, kpi) in enumerate(zip(cols, kpis)):
        label = kpi[0]
        value = kpi[1]
        change = kpi[2]
        sub_text = kpi[3]
        is_higher_better = kpi[4] if len(kpi) > 4 else True
        is_percent = kpi[5] if len(kpi) > 5 else False
        
        if is_percent:
            display_value = format_percent(value)
        else:
            display_value = f"{format_currency(value)}万元"
        
        color_class = get_color_for_change(change) if is_higher_better else \
                      get_color_for_change(-change)
        
        change_text = format_growth(change) if not is_percent else \
                      f"{change:+.2f}pp" if not pd.isna(change) else "0.00pp"
        
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{display_value}</div>
            <div class="kpi-change {color_class}">
                同比 {change_text}
            </div>
            <div style="font-size:0.75rem;color:#aaa;margin-top:0.3rem;">{sub_text}</div>
        </div>
        """, unsafe_allow_html=True)

def render_operation_table(indicators):
    """渲染经营情况对比表"""
    cur = indicators['current']
    last = indicators['last']
    yoy = indicators['yoy']
    
    data = {
        '指标': ['抵消后收入', '抵消后成本', '利润', '利润率'],
        f'{current_year}年': [
            f"{format_currency(cur['income'])}万元",
            f"{format_currency(cur['cost'])}万元",
            f"{format_currency(cur['profit'])}万元",
            format_percent(cur['margin'])
        ],
        f'{last_year}年': [
            f"{format_currency(last['income'])}万元",
            f"{format_currency(last['cost'])}万元",
            f"{format_currency(last['profit'])}万元",
            format_percent(last['margin'])
        ],
        '同比增减额': [
            f"{format_currency(cur['income'] - last['income'])}万元",
            f"{format_currency(cur['cost'] - last['cost'])}万元",
            f"{format_currency(cur['profit'] - last['profit'])}万元",
            f"{format_percent(cur['margin'] - last['margin'])}"
        ],
        '同比增幅': [
            format_growth(yoy['income_growth']),
            format_growth(yoy['cost_growth']),
            format_growth(yoy['profit_growth']),
            format_growth(yoy['margin_change']) if yoy['margin_change'] != 0 else '0.00%'
        ]
    }
    
    change_tags = [
        get_change_tag(yoy['income_growth']),
        get_change_tag(yoy['cost_growth']),
        get_change_tag(yoy['profit_growth']),
        get_change_tag(yoy['margin_change'])
    ]
    
    df = pd.DataFrame(data)
    
    # 用HTML渲染表格
    html = '<table class="dataframe" style="width:100%;">'
    html += '<thead><tr>'
    for col in df.columns:
        html += f'<th>{col}</th>'
    html += '<th>状态</th></tr></thead><tbody>'
    
    for i, (_, row) in enumerate(df.iterrows()):
        is_total = (i == len(df) - 1)
        row_class = 'total-row' if is_total else ''
        html += f'<tr class="{row_class}">'
        for j, col in enumerate(df.columns):
            html += f'<td>{row[col]}</td>'
        html += f'<td><span class="status-tag {get_color_for_change(float(yoy[list(yoy.keys())[i]] if i < len(yoy) else 0))}">{change_tags[i]}</span></td>'
        html += '</tr>'
    
    html += '</tbody></table>'
    return html

def render_top5_table(data, columns, rank_col=None):
    """通用的TOP5表格渲染"""
    headers = list(columns.keys())
    html = '<table class="dataframe" style="width:100%;">'
    html += '<thead><tr>'
    for h in headers:
        html += f'<th>{h}</th>'
    html += '</tr></thead><tbody>'
    
    for i, (_, row) in enumerate(data.iterrows()):
        is_total = rank_col and (row.get(rank_col, '') == '合计' or i == len(data) - 1)
        row_class = 'total-row' if is_total else ''
        html += f'<tr class="{row_class}">'
        for h in headers:
            val = row[columns[h]]
            if isinstance(val, float):
                if abs(val) > 100:  # 金额
                    val = format_currency(val)
                else:  # 比例
                    val = format_percent(val) if val < 1 else f'{val:.2f}'
            html += f'<td>{val}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html

def render_summary(indicators):
    """渲染总结"""
    cur = indicators['current']
    yoy = indicators['yoy']
    expense = indicators['expense_summary']
    
    profit_growth = yoy['profit_growth']
    if profit_growth > 0.1:
        profit_judge = "大幅增长，经营质量持续向好"
        profit_cls = "highlight-positive"
    elif profit_growth > -0.1:
        profit_judge = "基本持平，经营整体平稳"
        profit_cls = "highlight-neutral"
    else:
        profit_judge = "同比下滑，经营存在一定压力"
        profit_cls = "highlight-negative"
    
    total_expense = expense['本年累计'].sum()
    total_expense_last = expense['上年同期'].sum()
    exp_growth = safe_divide(total_expense - total_expense_last, total_expense_last)
    
    if exp_growth > 0.1:
        expense_judge = "费用同比增长较快，需重点管控"
        exp_cls = "highlight-negative"
    elif exp_growth > -0.1:
        expense_judge = "费用规模基本稳定，整体可控"
        exp_cls = "highlight-neutral"
    else:
        expense_judge = "费用同比下降，管控效果良好"
        exp_cls = "highlight-positive"
    
    income_growth_text = format_growth(yoy['income_growth'])
    profit_growth_text = format_growth(yoy['profit_growth'])
    exp_growth_text = format_growth(exp_growth)
    
    st.markdown(f"""
    <div class="summary-card">
        <h3>📋 总结</h3>
        <p>
            截至{current_year}年{current_month}月，{DEPARTMENT_NAME}累计实现收入 
            <strong>{format_currency(cur['income'])}万元</strong>，
            同比 <span class="{highlight_class(yoy['income_growth'])}">{income_growth_text}</span>；<br>
            累计实现利润 <strong>{format_currency(cur['profit'])}万元</strong>，
            同比 <span class="{profit_cls}">{profit_growth_text}</span>，
            利润{profit_judge}。
        </p>
        <p>
            核心业务方面，收入、成本、利润高度集中于头部客户、供应商及商品，
            核心业务结构稳定，头部贡献突出；业务员绩效分化明显，核心业务员贡献了主要利润。
        </p>
        <p>
            费用方面，当期累计总费用 <strong>{format_currency(total_expense)}万元</strong>，
            同比 <span class="{exp_cls}">{exp_growth_text}</span>，
            {expense_judge}；费用主要集中于头部人员。
        </p>
        <p>
            整体来看，部门经营{profit_judge}，核心业务稳定，费用整体可控，
            后续需持续优化客户与商品结构，严控成本费用，进一步提升盈利水平。
        </p>
    </div>
    """, unsafe_allow_html=True)

def highlight_class(value):
    if value > 0.05:
        return 'highlight-positive'
    elif value < -0.05:
        return 'highlight-negative'
    return 'highlight-neutral'

# ===================== 主页面 =====================
def main():
    load_css()
    
    # 侧边栏配置
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:1rem 0;">
            <div style="font-size:2.5rem;margin-bottom:0.5rem;">📊</div>
            <div style="font-weight:700;font-size:1.1rem;color:#1a1a2e;">财务分析报告</div>
            <div style="font-size:0.8rem;color:#888;">自动生成工具 v2.0</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown("### 📁 上传数据文件")
        
        st.markdown(
            '<div style="font-size:0.85rem;color:#666;margin-bottom:0.5rem;">请上传以下3个Excel文件：</div>',
            unsafe_allow_html=True
        )
        
        sales_file = st.file_uploader(
            "① 销售数据（医化4部销售数据.xlsx）", 
            type=['xlsx'],
            key="sales"
        )
        profit_file = st.file_uploader(
            "② 利润核算单（单票利润核算单.xlsx）", 
            type=['xlsx'],
            key="profit"
        )
        expense_file = st.file_uploader(
            "③ 费用明细（医化4部费用明细.xlsx）", 
            type=['xlsx'],
            key="expense"
        )
        
        all_uploaded = all([sales_file, profit_file, expense_file])
        
        if all_uploaded:
            st.success("✅ 3个文件已全部上传")
        
        st.divider()
        
        st.markdown("### ℹ️ 报告信息")
        st.markdown(f"""
        - **部门**: {DEPARTMENT_NAME}
        - **报告期间**: {current_year}年1-{current_month}月
        - **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """)
        
        st.divider()
        
        st.markdown("""
        <div style="font-size:0.75rem;color:#999;text-align:center;padding:1rem 0;">
            📌 数据不会上传到服务器外部<br>
            仅用于本次报告生成，请放心使用<br>
            技术支持：Streamlit + Plotly
        </div>
        """, unsafe_allow_html=True)
    
    # 主内容区
    st.markdown('<div class="report-container">', unsafe_allow_html=True)
    
    # 标题
    st.markdown(f"""
    <div class="report-header">
        <h1>{DEPARTMENT_NAME} 财务分析报告</h1>
        <p>{current_year}年1月 - {current_month}月 · 经营数据全景分析</p>
        <div class="badge">
            📅 报告生成: {datetime.now().strftime('%Y年%m月%d日')} &nbsp;|&nbsp; 
            📊 数据截止: {current_year}年{current_month}月
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 检查文件是否已上传
    if not all_uploaded:
        st.info("👈 请在左侧侧边栏上传3个Excel文件后，报告将自动生成。")
        
        st.markdown("""
        <div style="text-align:center;padding:3rem 1rem;background:white;border-radius:16px;border:2px dashed #c3cfe2;">
            <div style="font-size:3rem;margin-bottom:1rem;">📂</div>
            <h3 style="color:#333;">等待数据上传</h3>
            <p style="color:#888;">请上传以下3个Excel底稿文件：</p>
            <div style="display:inline-block;text-align:left;color:#666;line-height:2;">
                📄 <strong>医化4部销售数据.xlsx</strong>（含当年和上年sheet）<br>
                📄 <strong>单票利润核算单.xlsx</strong>（含单票利润sheet）<br>
                📄 <strong>医化4部费用明细.xlsx</strong>（含费用分类、当年、上年sheet）
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # 加载数据
    with st.spinner('正在读取并分析数据...'):
        data = load_all_data(sales_file, profit_file, expense_file)
    
    if not data['success']:
        st.error(f"❌ 数据加载失败：{data.get('error', '未知错误')}")
        st.info("💡 请检查上传的Excel文件格式是否正确，确认包含所需的sheet名称。")
        return
    
    # 计算指标
    indicators = calculate_indicators(data)
    
    # ========== 一、核心经营指标 ==========
    st.markdown('<div class="section-title">📈 一、整体经营情况</div>', unsafe_allow_html=True)
    
    # KPI 卡片
    render_kpi_cards(indicators)
    
    # 经营情况表格
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📋 经营指标对比表</div>', unsafe_allow_html=True)
    st.markdown(render_operation_table(indicators), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 月度趋势图
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📊 月度收入 & 利润趋势</div>', unsafe_allow_html=True)
    fig = create_monthly_chart(indicators['monthly_trend'])
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== 二、利润贡献结构 ==========
    st.markdown('<div class="section-title">🏆 二、利润贡献结构（TOP5）</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["客户TOP5", "供应商TOP5", "商品TOP5"])
    
    with tab1:
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">收入TOP5客户</div>', unsafe_allow_html=True)
            
            cust_data = indicators['customer_top5'].copy()
            cust_data['排名'] = range(1, len(cust_data) + 1)
            cust_display = cust_data[['排名', '实际客户', '收入', '利润']].copy()
            
            # 格式化金额
            cust_display['收入(万元)'] = cust_display['收入'].apply(lambda x: f"{x/10000:,.2f}")
            cust_display['利润(万元)'] = cust_display['利润'].apply(lambda x: f"{x/10000:,.2f}")
            
            st.dataframe(
                cust_display[['排名', '实际客户', '收入(万元)', '利润(万元)']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    '排名': st.column_config.NumberColumn("排名", width=50),
                    '实际客户': st.column_config.TextColumn("客户名称"),
                    '收入(万元)': st.column_config.TextColumn("累计收入(万元)"),
                    '利润(万元)': st.column_config.TextColumn("累计利润(万元)"),
                }
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            fig = create_pie_chart(
                indicators['customer_top5'], '实际客户', '收入',
                '收入占比分布',
                px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with tab2:
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">采购成本TOP5供应商</div>', unsafe_allow_html=True)
            
            supp_data = indicators['supplier_top5'].copy()
            supp_data['排名'] = range(1, len(supp_data) + 1)
            supp_display = supp_data[['排名', '实际供应商', '采购成本']].copy()
            supp_display['采购成本(万元)'] = supp_display['采购成本'].apply(lambda x: f"{x/10000:,.2f}")
            
            st.dataframe(
                supp_display[['排名', '实际供应商', '采购成本(万元)']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    '排名': st.column_config.NumberColumn("排名", width=50),
                    '实际供应商': st.column_config.TextColumn("供应商名称"),
                    '采购成本(万元)': st.column_config.TextColumn("累计采购成本(万元)"),
                }
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            fig = create_pie_chart(
                indicators['supplier_top5'], '实际供应商', '采购成本',
                '采购成本占比分布',
                px.colors.qualitative.Pastel1
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with tab3:
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">利润TOP5商品（不含其他）</div>', unsafe_allow_html=True)
            
            prod_data = indicators['product_top5'].copy()
            prod_data['排名'] = range(1, len(prod_data) + 1)
            prod_display = prod_data[['排名', '商品中文品名', '收入', '利润']].copy()
            prod_display['收入(万元)'] = prod_display['收入'].apply(lambda x: f"{x/10000:,.2f}")
            prod_display['利润(万元)'] = prod_display['利润'].apply(lambda x: f"{x/10000:,.2f}")
            
            st.dataframe(
                prod_display[['排名', '商品中文品名', '收入(万元)', '利润(万元)']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    '排名': st.column_config.NumberColumn("排名", width=50),
                    '商品中文品名': st.column_config.TextColumn("商品名称"),
                    '收入(万元)': st.column_config.TextColumn("累计收入(万元)"),
                    '利润(万元)': st.column_config.TextColumn("累计利润(万元)"),
                }
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            fig = create_pie_chart(
                indicators['product_top5'], '商品中文品名', '利润',
                '利润占比分布',
                px.colors.qualitative.Set2
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # ========== 三、业务员绩效 ==========
    st.markdown('<div class="section-title">👤 三、业务员绩效（TOP5）</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    sp_data = indicators['salesperson_top5'].copy()
    sp_data['排名'] = range(1, len(sp_data) + 1)
    sp_display = sp_data[['排名', '业务员', '销售收入', '利润', '利润率', '上年利润', '同比利润变化']].copy()
    sp_display['销售收入(万元)'] = sp_display['销售收入'].apply(lambda x: f"{x/10000:,.2f}")
    sp_display['利润(万元)'] = sp_display['利润'].apply(lambda x: f"{x/10000:,.2f}")
    sp_display['利润率'] = sp_display['利润率'].apply(format_percent)
    sp_display['上年利润(万元)'] = sp_display['上年利润'].apply(lambda x: f"{x/10000:,.2f}")
    sp_display['同比变化(万元)'] = sp_display['同比利润变化'].apply(lambda x: f"{x/10000:+,.2f}")
    
    st.dataframe(
        sp_display[['排名', '业务员', '销售收入(万元)', '利润(万元)', '利润率', '上年利润(万元)', '同比变化(万元)']],
        use_container_width=True,
        hide_index=True,
        column_config={
            '排名': st.column_config.NumberColumn("排名", width=50),
            '业务员': st.column_config.TextColumn("业务员"),
            '销售收入(万元)': st.column_config.TextColumn("销售收入(万元)"),
            '利润(万元)': st.column_config.TextColumn("累计利润(万元)"),
            '利润率': st.column_config.TextColumn("利润率"),
            '上年利润(万元)': st.column_config.TextColumn("上年同期(万元)"),
            '同比变化(万元)': st.column_config.TextColumn("同比变化(万元)"),
        }
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 业务员横向柱状图
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    sp_chart_data = indicators['salesperson_top5'].copy()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=sp_chart_data['业务员'][::-1],
        x=sp_chart_data['利润'][::-1]/10000,
        orientation='h',
        marker_color='#5470C6',
        text=sp_chart_data['利润'][::-1]/10000,
        texttemplate='%{text:.1f}万元',
        textposition='outside',
        name='利润'
    ))
    fig.update_layout(
        title=dict(text='业务员利润TOP5', font=dict(size=14), x=0.5),
        xaxis=dict(title='利润（万元）', gridcolor='#f0f0f0'),
        yaxis=dict(title='', automargin=True),
        plot_bgcolor='white',
        height=350,
        margin=dict(l=20, r=60, t=40, b=20),
        hovermode='y unified'
    )
    fig.update_xaxes(gridcolor='#e8e8e8')
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== 四、费用情况 ==========
    st.markdown('<div class="section-title">💰 四、费用情况</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">费用同比分析</div>', unsafe_allow_html=True)
        
        exp_data = indicators['expense_summary'].copy()
        exp_display = exp_data[['费用类别', '本年累计', '上年同期', '同比增减额', '同比增幅']].copy()
        exp_display['本年累计(万元)'] = exp_display['本年累计'].apply(lambda x: f"{x/10000:,.2f}")
        exp_display['上年同期(万元)'] = exp_display['上年同期'].apply(lambda x: f"{x/10000:,.2f}")
        exp_display['同比增减(万元)'] = exp_display['同比增减额'].apply(lambda x: f"{x/10000:+,.2f}")
        exp_display['同比增幅'] = exp_display['同比增幅'].apply(format_growth)
        
        st.dataframe(
            exp_display[['费用类别', '本年累计(万元)', '上年同期(万元)', '同比增减(万元)', '同比增幅']],
            use_container_width=True,
            hide_index=True,
            column_config={
                '费用类别': st.column_config.TextColumn("费用类别"),
                '本年累计(万元)': st.column_config.TextColumn(f"{current_year}年"),
                '上年同期(万元)': st.column_config.TextColumn(f"{last_year}年"),
                '同比增减(万元)': st.column_config.TextColumn("同比增减"),
                '同比增幅': st.column_config.TextColumn("同比增幅"),
            }
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">费用结构分布</div>', unsafe_allow_html=True)
        fig = create_pie_chart(
            indicators['expense_summary'], '费用类别', '本年累计',
            '',
            ['#5470C6', '#91CC75', '#FAC858', '#EE6666']
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 人员费用TOP5
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">费用TOP5人员（差旅费+业务招待费）</div>', unsafe_allow_html=True)
    
    person_data = indicators['person_expense_top5'].copy()
    person_display = person_data[['人员', '业务招待费', '差旅费', '总费用']].copy()
    person_display['业务招待费(万元)'] = person_display['业务招待费'].apply(lambda x: f"{x/10000:,.2f}")
    person_display['差旅费(万元)'] = person_display['差旅费'].apply(lambda x: f"{x/10000:,.2f}")
    person_display['总费用(万元)'] = person_display['总费用'].apply(lambda x: f"{x/10000:,.2f}")
    
    st.dataframe(
        person_display[['人员', '业务招待费(万元)', '差旅费(万元)', '总费用(万元)']],
        use_container_width=True,
        hide_index=True,
        column_config={
            '人员': st.column_config.TextColumn("人员"),
            '业务招待费(万元)': st.column_config.TextColumn("业务招待费(万元)"),
            '差旅费(万元)': st.column_config.TextColumn("差旅费(万元)"),
            '总费用(万元)': st.column_config.TextColumn("总费用(万元)"),
        }
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 人员费用横向柱状图
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    person_chart = indicators['person_expense_top5'].copy()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=person_chart['人员'][::-1],
        x=person_chart['业务招待费'][::-1]/10000,
        orientation='h',
        marker_color='#FAC858',
        text=person_chart['业务招待费'][::-1]/10000,
        texttemplate='%{text:.1f}',
        textposition='inside',
        name='业务招待费'
    ))
    fig.add_trace(go.Bar(
        y=person_chart['人员'][::-1],
        x=person_chart['差旅费'][::-1]/10000,
        orientation='h',
        marker_color='#91CC75',
        text=person_chart['差旅费'][::-1]/10000,
        texttemplate='%{text:.1f}',
        textposition='inside',
        name='差旅费'
    ))
    fig.update_layout(
        title=dict(text='人员费用TOP5 构成分析', font=dict(size=14), x=0.5),
        barmode='stack',
        xaxis=dict(title='费用（万元）', gridcolor='#f0f0f0'),
        yaxis=dict(title='', automargin=True),
        plot_bgcolor='white',
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='y unified'
    )
    fig.update_xaxes(gridcolor='#e8e8e8')
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== 总结 ==========
    render_summary(indicators)
    
    st.markdown('</div>', unsafe_allow_html=True)  # 关闭 report-container


if __name__ == '__main__':
    main()