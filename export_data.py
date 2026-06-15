"""
数据导出脚本：读取Excel文件 → 计算指标 → 导出为 preloaded_data.json
运行方式：在本地终端执行 `python export_data.py`
输出文件：preloaded_data.json（约 20-50KB，可直接纳入 Git 仓库）
"""

import pandas as pd
import json
import os
import sys
import warnings
warnings.filterwarnings('ignore')

# ===================== 配置参数 =====================
CUTOFF_MONTH = 202605
current_year = CUTOFF_MONTH // 100
current_month = CUTOFF_MONTH % 100
last_year = current_year - 1
last_year_cutoff = last_year * 100 + current_month

# ===================== 工具函数 =====================
def safe_divide(numerator, denominator):
    if denominator == 0 or pd.isna(denominator):
        return 0.0
    return float(numerator / denominator)

def to_serializable(obj):
    """将 pandas/numpy 类型转为 JSON 可序列化的 Python 原生类型"""
    if isinstance(obj, (pd.DataFrame, pd.Series)):
        return json.loads(obj.to_json(orient='records', force_ascii=False))
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_serializable(v) for v in obj]
    if hasattr(obj, 'item'):  # numpy scalar
        return obj.item()
    if pd.isna(obj):
        return None
    return obj

def load_all_data(sales_path, profit_path, expense_path):
    """加载并处理所有数据"""
    results = {}
    try:
        sales_current_df = pd.read_excel(sales_path, sheet_name=f'{current_year}年')
        sales_last_df = pd.read_excel(sales_path, sheet_name=f'{last_year}年')
        if '月份' not in sales_last_df.columns:
            sales_last_df.rename(columns={sales_last_df.columns[-1]: '月份'}, inplace=True)

        sales_current_filtered = sales_current_df[sales_current_df['月份'] <= CUTOFF_MONTH].copy()
        sales_last_filtered = sales_last_df[sales_last_df['月份'] <= last_year_cutoff].copy()
        results['sales_current'] = sales_current_filtered
        results['sales_last'] = sales_last_filtered

        profit_df = pd.read_excel(profit_path, sheet_name='单票利润核算单')
        profit_df = profit_df[profit_df['部门'].str.contains('医化', na=False)].copy()
        profit_df['发货年月'] = profit_df['发货日期'].dt.to_period('M').astype(int)
        results['profit_current'] = profit_df[(profit_df['归属年度'] == current_year) & (profit_df['发货年月'] <= CUTOFF_MONTH)].copy()
        results['profit_last'] = profit_df[(profit_df['归属年度'] == last_year) & (profit_df['发货年月'] <= last_year_cutoff)].copy()
        results['profit_all'] = profit_df

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

    cur_income = float(sales_cur['抵消后收入'].sum())
    cur_cost = float(sales_cur['抵消后成本'].sum())
    cur_profit = float(sales_cur['利润'].sum())
    cur_margin = safe_divide(cur_profit, cur_income)
    last_income = float(sales_last['抵消后收入'].sum())
    last_cost = float(sales_last['抵消后成本'].sum())
    last_profit = float(sales_last['利润'].sum())
    last_margin = safe_divide(last_profit, last_income)

    indicators['current'] = {'income': cur_income, 'cost': cur_cost, 'profit': cur_profit, 'margin': cur_margin}
    indicators['last'] = {'income': last_income, 'cost': last_cost, 'profit': last_profit, 'margin': last_margin}
    indicators['yoy'] = {
        'income_growth': safe_divide(cur_income - last_income, last_income),
        'cost_growth': safe_divide(cur_cost - last_cost, last_cost),
        'profit_growth': safe_divide(cur_profit - last_profit, last_profit),
        'margin_change': cur_margin - last_margin
    }

    cust_sum = sales_cur.groupby('实际客户', dropna=False).agg(收入=('抵消后收入','sum'), 利润=('利润','sum')).reset_index()
    indicators['customer_top5'] = cust_sum.sort_values('收入', ascending=False).head(5).fillna(0)

    supp_sum = sales_cur.groupby('实际供应商', dropna=False).agg(采购成本=('抵消后成本','sum')).reset_index()
    indicators['supplier_top5'] = supp_sum.sort_values('采购成本', ascending=False).head(5).fillna(0)

    prod_sum = sales_cur.groupby('商品中文品名', dropna=False).agg(收入=('抵消后收入','sum'), 利润=('利润','sum')).reset_index()
    prod_sum = prod_sum[prod_sum['商品中文品名'] != '其他']
    indicators['product_top5'] = prod_sum.sort_values('利润', ascending=False).head(5).fillna(0)

    sp_cur = profit_cur.groupby('业务员', dropna=False).agg(销售收入=('销售收入','sum'), 利润=('利润','sum')).reset_index()
    sp_last = profit_last.groupby('业务员', dropna=False).agg(上年利润=('利润','sum')).reset_index()
    sp_summary = pd.merge(sp_cur, sp_last, on='业务员', how='left').fillna(0)
    sp_summary['利润率'] = sp_summary.apply(lambda x: safe_divide(x['利润'], x['销售收入']), axis=1)
    sp_summary['同比利润变化'] = sp_summary['利润'] - sp_summary['上年利润']
    indicators['salesperson_top5'] = sp_summary.sort_values('利润', ascending=False).head(5).reset_index(drop=True)

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

    person_df = exp_cur[exp_cur['费用类别'].isin(['业务招待费', '差旅费'])].copy()
    person_df = person_df[person_df['人员'].notna() & (person_df['人员'].str.strip() != '') & (person_df['人员'].str.strip() != '其他')]
    person_summary = person_df.groupby('人员').agg(
        业务招待费=('借方', lambda x: x[person_df['费用类别'] == '业务招待费'].sum()),
        差旅费=('借方', lambda x: x[person_df['费用类别'] == '差旅费'].sum())
    ).reset_index()
    person_summary['总费用'] = person_summary['业务招待费'] + person_summary['差旅费']
    indicators['person_expense_top5'] = person_summary.sort_values('总费用', ascending=False).head(5).reset_index(drop=True)

    monthly = sales_cur.groupby('月份').agg(收入=('抵消后收入','sum'), 利润=('利润','sum')).reset_index().sort_values('月份')
    indicators['monthly_trend'] = monthly

    indicators['_meta'] = {
        'CUTOFF_MONTH': CUTOFF_MONTH,
        'current_year': current_year,
        'current_month': current_month,
        'last_year': last_year
    }
    return indicators

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 用户的实际文件路径
    sales_path = r'D:\1、工作\1、普洛\13、分析\医化4部销售数据.xlsx'
    profit_path = r'D:\1、工作\1、普洛\13、分析\单票利润核算单.xlsx'
    expense_path = r'D:\1、工作\1、普洛\13、分析\医化4部费用明细-202605.xlsx'

    for name, path in [('销售数据', sales_path), ('利润核算单', profit_path), ('费用明细', expense_path)]:
        if not os.path.exists(path):
            print(f"❌ 未找到 {name} 文件：{path}")
            sys.exit(1)

    print("📖 正在读取 Excel 文件...")
    print(f"  - {sales_path}")
    print(f"  - {profit_path}")
    print(f"  - {expense_path}")

    data = load_all_data(sales_path, profit_path, expense_path)
    if not data['success']:
        print(f"❌ 数据加载失败：{data.get('error', '未知错误')}")
        sys.exit(1)

    print("⚙️ 正在计算分析指标...")
    indicators = calculate_indicators(data)

    print("💾 正在序列化并导出...")
    serialized = to_serializable(indicators)
    
    output_path = os.path.join(script_dir, 'preloaded_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(serialized, f, ensure_ascii=False, indent=2)

    file_size = os.path.getsize(output_path)
    print(f"✅ 导出成功！")
    print(f"  📄 输出文件：{output_path}")
    print(f"  📏 大小：{file_size / 1024:.1f} KB")
    print(f"  现在请将 preloaded_data.json 提交到 Git 仓库并推送。")

if __name__ == '__main__':
    main()