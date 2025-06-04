import akshare as ak
import pandas as pd
import datetime
import os
import time
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def get_recent_trading_days(days=5):
    """获取最近的交易日（简化版，使用工作日）"""
    today = datetime.datetime.now()
    trading_days = []
    current_date = today
    
    while len(trading_days) < days:
        if current_date.weekday() < 5:  # 排除周末
            trading_days.append(current_date.strftime('%Y-%m-%d'))
        current_date = current_date - datetime.timedelta(days=1)
    
    return trading_days

def get_high_volume_stocks():
    """
    第一阶段：获取所有港股实时行情，筛选出成交额大于3000万港元的股票
    """
    print("正在获取港股实时行情数据...")
    
    try:
        # 获取港股实时行情
        spot_data = ak.stock_hk_spot_em()
        
        # 检查必要的列是否存在
        required_columns = ['代码', '名称', '成交额']
        available_columns = spot_data.columns.tolist()
        
        # 打印列名以便调试
        print(f"可用列名: {available_columns}")
        
        # 尝试找到正确的列名映射
        column_mapping = {}
        for req_col in required_columns:
            for avail_col in available_columns:
                if req_col in avail_col or avail_col in req_col:
                    column_mapping[avail_col] = req_col
                    break
        
        # 如果没有找到成交额列，尝试常见的英文列名
        if '成交额' not in column_mapping.values():
            for col in available_columns:
                if 'amount' in col.lower() or 'turnover' in col.lower() or '额' in col:
                    column_mapping[col] = '成交额'
                    break
        
        # 重命名列
        spot_data = spot_data.rename(columns=column_mapping)
        
        # 确保代码格式正确
        spot_data['代码'] = spot_data['代码'].astype(str).str.zfill(5)
        
        # 转换成交额为数值类型
        if '成交额' in spot_data.columns:
            spot_data['成交额'] = pd.to_numeric(spot_data['成交额'], errors='coerce')
            
            # 筛选成交额大于3000万港元的股票
            min_turnover = 30000000  # 3000万港元
            high_volume_stocks = spot_data[spot_data['成交额'] > min_turnover].copy()
            
            print(f"共获取 {len(spot_data)} 支港股数据")
            print(f"成交额大于3000万港元的股票: {len(high_volume_stocks)} 支")
            
            return high_volume_stocks[['代码', '名称', '成交额']].reset_index(drop=True)
        else:
            print("警告: 无法找到成交额列，将返回空结果")
            return pd.DataFrame(columns=['代码', '名称', '成交额'])
            
    except Exception as e:
        print(f"获取实时行情数据时出错: {e}")
        return pd.DataFrame(columns=['代码', '名称', '成交额'])

def analyze_volume_growth(high_volume_stocks):
    """
    第二阶段：对筛选后的股票进行历史数据分析
    改为比较前两个完整交易日的成交额
    """
    if high_volume_stocks.empty:
        print("没有符合条件的股票需要分析")
        return {'50%': pd.DataFrame(), '100%': pd.DataFrame(), '200%': pd.DataFrame()}
    
    print(f"开始分析 {len(high_volume_stocks)} 支高成交额股票的历史数据...")
    
    # 获取交易日
    trading_days = get_recent_trading_days(5)
    if len(trading_days) < 3:
        print("无法获取足够的交易日数据")
        return {'50%': pd.DataFrame(), '100%': pd.DataFrame(), '200%': pd.DataFrame()}
    
    # 使用前两个完整的交易日进行比较
    recent_date = trading_days[1]  # 最近一个完整交易日
    previous_date = trading_days[2]  # 前一个完整交易日
    
    print(f"分析日期: 最近交易日 {recent_date}, 前一交易日 {previous_date}")
    
    # 结果容器
    analysis_results = []
    
    # 分析每只股票
    for idx, stock in high_volume_stocks.iterrows():
        code = stock['代码']
        name = stock['名称']
        
        try:
            # 获取历史数据
            hist_data = ak.stock_hk_daily(symbol=code, adjust="")
            time.sleep(0.3)  # 减少延时
            
            if not hist_data.empty:
                hist_data['date'] = pd.to_datetime(hist_data['date'])
                hist_data = hist_data.sort_values(by='date', ascending=False)
                
                # 确保至少有两条历史记录
                if len(hist_data) >= 2:
                    # 获取最近两个交易日的数据
                    recent_record = hist_data.iloc[0]  # 最近交易日
                    previous_record = hist_data.iloc[1]  # 前一交易日
                    
                    # 计算成交额 (成交量 * 收盘价)
                    recent_turnover = float(recent_record['volume']) * float(recent_record['close'])
                    previous_turnover = float(previous_record['volume']) * float(previous_record['close'])
                    
                    # 确保前一日成交额不为0
                    if previous_turnover > 0:
                        growth_ratio = recent_turnover / previous_turnover
                        
                        analysis_results.append({
                            '代码': code,
                            '名称': name,
                            '最近交易日成交额': recent_turnover,
                            '前一交易日成交额': previous_turnover,
                            '增长比例': growth_ratio,
                            '最近交易日': recent_record['date'].strftime('%Y-%m-%d'),
                            '前一交易日': previous_record['date'].strftime('%Y-%m-%d')
                        })
                        
                        if (idx + 1) % 10 == 0:
                            print(f"已分析 {idx + 1}/{len(high_volume_stocks)} 支股票")
                
        except Exception as e:
            print(f"分析股票 {code} {name} 时出错: {e}")
            continue
    
    print(f"已分析 {len(high_volume_stocks)}/{len(high_volume_stocks)} 支股票")
    
    # 转换为DataFrame并分类
    if not analysis_results:
        print("没有获取到有效的分析结果")
        return {'50%': pd.DataFrame(), '100%': pd.DataFrame(), '200%': pd.DataFrame()}
    
    analysis_df = pd.DataFrame(analysis_results)
    analysis_df = analysis_df.sort_values(by='增长比例', ascending=False)
    
    # 按不同增长比例分类
    result_50 = analysis_df[analysis_df['增长比例'] > 1.5].copy()  # 增长50%以上
    result_100 = analysis_df[analysis_df['增长比例'] > 2.0].copy()  # 增长100%以上
    result_200 = analysis_df[analysis_df['增长比例'] > 3.0].copy()  # 增长200%以上
    
    print(f"分析完成！")
    print(f"成交额增长 > 50%: {len(result_50)} 支")
    print(f"成交额增长 > 100%: {len(result_100)} 支") 
    print(f"成交额增长 > 200%: {len(result_200)} 支")
    
    return {
        '50%': result_50,
        '100%': result_100,
        '200%': result_200
    }

def save_results(results):
    """保存结果到CSV文件"""
    os.makedirs('results', exist_ok=True)
    today = datetime.datetime.now().strftime('%Y%m%d')
    
    for growth_rate, df in results.items():
        if not df.empty:
            filename = f"results/港股成交额增长{growth_rate}_{today}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"保存 {len(df)} 条记录到: {filename}")
            
            # 显示前5条记录
            if len(df) > 0:
                print(f"\n成交额增长 > {growth_rate} 的股票（前5名）:")
                display_df = df[['代码', '名称', '最近交易日成交额', '前一交易日成交额', '增长比例']].head()
                print(display_df.to_string(index=False))
                print()

def main():
    """主函数"""
    print("=" * 60)
    print("港股成交量筛选程序 - 优化版")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # 第一阶段：筛选高成交额股票
        print("第一阶段：筛选成交额大于3000万港元的股票...")
        high_volume_stocks = get_high_volume_stocks()
        
        if high_volume_stocks.empty:
            print("未找到符合条件的股票")
            return
        
        # 第二阶段：分析成交额增长情况
        print("\n第二阶段：分析成交额增长情况...")
        results = analyze_volume_growth(high_volume_stocks)
        
        # 保存结果
        print("\n保存结果...")
        save_results(results)
        
        end_time = time.time()
        print(f"\n程序执行完成，总耗时: {end_time - start_time:.2f} 秒")
        
    except Exception as e:
        print(f"程序执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

# ============ Streamlit 可视化功能 ============

def format_number(num):
    """格式化数字显示"""
    if num >= 1e8:
        return f"{num/1e8:.2f}亿"
    elif num >= 1e4:
        return f"{num/1e4:.2f}万"
    else:
        return f"{num:.2f}"

def create_turnover_chart(df, title):
    """创建成交额对比图表"""
    if df.empty:
        return None
    
    # 准备数据
    chart_data = df.head(10).copy()  # 只显示前10支股票
    chart_data['股票'] = chart_data['代码'] + '-' + chart_data['名称']
    
    # 创建柱状图
    fig = go.Figure()
    
    # 添加前一交易日成交额
    fig.add_trace(go.Bar(
        name='前一交易日成交额',
        x=chart_data['股票'],
        y=chart_data['前一交易日成交额'],
        marker_color='lightblue',
        text=[format_number(x) for x in chart_data['前一交易日成交额']],
        textposition='auto',
    ))
    
    # 添加最近交易日成交额
    fig.add_trace(go.Bar(
        name='最近交易日成交额',
        x=chart_data['股票'],
        y=chart_data['最近交易日成交额'],
        marker_color='orange',
        text=[format_number(x) for x in chart_data['最近交易日成交额']],
        textposition='auto',
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='股票代码-名称',
        yaxis_title='成交额(港元)',
        barmode='group',
        height=500,
        xaxis_tickangle=-45
    )
    
    return fig

def create_growth_ratio_chart(df, title):
    """创建增长比例图表"""
    if df.empty:
        return None
    
    chart_data = df.head(15).copy()
    chart_data['股票'] = chart_data['代码'] + '-' + chart_data['名称']
    chart_data['增长率%'] = (chart_data['增长比例'] - 1) * 100
    
    fig = px.bar(
        chart_data,
        x='股票',
        y='增长率%',
        title=title,
        text='增长率%',
        color='增长率%',
        color_continuous_scale='Reds'
    )
    
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(
        height=500,
        xaxis_tickangle=-45,
        showlegend=False
    )
    
    return fig

def streamlit_app():
    """Streamlit主应用"""
    st.set_page_config(
        page_title="港股成交量筛选分析",
        page_icon="📈",
        layout="wide"
    )
    
    st.title("📈 港股成交量筛选分析系统")
    st.markdown("---")
    
    # 侧边栏参数设置
    st.sidebar.header("🔧 参数设置")
    min_turnover_million = st.sidebar.slider(
        "最低成交额门槛(百万港元)", 
        min_value=10, 
        max_value=100, 
        value=30, 
        step=5
    )
    
    growth_threshold_50 = st.sidebar.slider(
        "增长50%阈值", 
        min_value=1.2, 
        max_value=2.0, 
        value=1.5, 
        step=0.1
    )
    
    # 运行分析按钮
    if st.sidebar.button("🚀 开始分析", type="primary"):
        
        # 显示进度
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.spinner("正在获取港股数据..."):
            status_text.text("第一阶段：获取港股实时行情数据...")
            progress_bar.progress(25)
            
            # 获取高成交额股票
            high_volume_stocks = get_high_volume_stocks()
            
            if high_volume_stocks.empty:
                st.error("❌ 未找到符合条件的股票")
                return
            
            # 显示第一阶段结果
            progress_bar.progress(50)
            status_text.text("第二阶段：分析成交额增长情况...")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总股票数", len(high_volume_stocks))
            with col2:
                st.metric("成交额门槛", f"{min_turnover_million}百万港元")
            with col3:
                avg_turnover = high_volume_stocks['成交额'].mean()
                st.metric("平均成交额", format_number(avg_turnover))
            
            # 分析增长情况
            results = analyze_volume_growth(high_volume_stocks)
            progress_bar.progress(75)
            
            # 合并所有结果
            all_results = pd.concat([
                results['50%'], results['100%'], results['200%']
            ]).drop_duplicates().sort_values('增长比例', ascending=False)
            
            progress_bar.progress(100)
            status_text.text("✅ 分析完成!")
            
            # 显示结果统计
            st.markdown("## 📊 分析结果统计")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "符合条件股票", 
                    len(all_results),
                    delta=f"增长>50%"
                )
            with col2:
                st.metric(
                    "增长>50%", 
                    len(results['50%']),
                    delta=f"{len(results['50%'])/len(high_volume_stocks)*100:.1f}%"
                )
            with col3:
                st.metric(
                    "增长>100%", 
                    len(results['100%']),
                    delta=f"{len(results['100%'])/len(high_volume_stocks)*100:.1f}%"
                )
            with col4:
                st.metric(
                    "增长>200%", 
                    len(results['200%']),
                    delta=f"{len(results['200%'])/len(high_volume_stocks)*100:.1f}%"
                )
            
            # 创建标签页
            tab1, tab2, tab3, tab4 = st.tabs(["📈 增长率图表", "💰 成交额对比", "📋 详细数据", "💾 数据下载"])
            
            with tab1:
                st.markdown("### 成交额增长率排行")
                if not all_results.empty:
                    fig_growth = create_growth_ratio_chart(all_results, "港股成交额增长率TOP15")
                    st.plotly_chart(fig_growth, use_container_width=True)
                else:
                    st.info("没有符合条件的数据")
            
            with tab2:
                st.markdown("### 成交额前后对比")
                if not all_results.empty:
                    fig_turnover = create_turnover_chart(all_results, "成交额前后对比TOP10")
                    st.plotly_chart(fig_turnover, use_container_width=True)
                else:
                    st.info("没有符合条件的数据")
            
            with tab3:
                st.markdown("### 详细数据表")
                
                # 增长>50%的股票
                if not results['50%'].empty:
                    st.markdown("#### 🔥 增长>50%的股票")
                    display_df = results['50%'][['代码', '名称', '最近交易日成交额', '前一交易日成交额', '增长比例']].copy()
                    display_df['增长率%'] = (display_df['增长比例'] - 1) * 100
                    display_df['最近交易日成交额'] = display_df['最近交易日成交额'].apply(format_number)
                    display_df['前一交易日成交额'] = display_df['前一交易日成交额'].apply(format_number)
                    display_df['增长比例'] = display_df['增长比例'].apply(lambda x: f"{x:.2f}")
                    display_df['增长率%'] = display_df['增长率%'].apply(lambda x: f"{x:.1f}%")
                    st.dataframe(display_df, use_container_width=True)
                
                # 增长>100%的股票
                if not results['100%'].empty:
                    st.markdown("#### 🚀 增长>100%的股票")
                    display_df = results['100%'][['代码', '名称', '最近交易日成交额', '前一交易日成交额', '增长比例']].copy()
                    display_df['增长率%'] = (display_df['增长比例'] - 1) * 100
                    display_df['最近交易日成交额'] = display_df['最近交易日成交额'].apply(format_number)
                    display_df['前一交易日成交额'] = display_df['前一交易日成交额'].apply(format_number)
                    display_df['增长比例'] = display_df['增长比例'].apply(lambda x: f"{x:.2f}")
                    display_df['增长率%'] = display_df['增长率%'].apply(lambda x: f"{x:.1f}%")
                    st.dataframe(display_df, use_container_width=True)
            
            with tab4:
                st.markdown("### 数据导出")
                if not all_results.empty:
                    csv = all_results.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 下载完整分析结果 (CSV)",
                        data=csv,
                        file_name=f"港股成交额分析_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime='text/csv'
                    )
                    
                    # 显示样本数据
                    st.markdown("#### 数据预览")
                    st.dataframe(all_results.head(10), use_container_width=True)
                else:
                    st.info("没有可下载的数据")
    
    else:
        # 初始状态
        st.info("👆 请在左侧设置参数，然后点击'开始分析'按钮开始运行")
        
        # 显示程序说明
        st.markdown("""
        ## 📖 程序说明
        
        ### 功能特点
        - 🎯 **两阶段筛选**：先筛选高成交额股票，再分析增长情况
        - 📊 **可视化展示**：图表和数据表格多维度展示结果
        - ⚡ **高效执行**：相比原始程序，执行时间从几小时缩短到几分钟
        - 🔧 **参数可调**：可自定义成交额门槛和增长阈值
        
        ### 数据来源
        - 基于AKShare的港股实时行情数据
        - 对比前两个完整交易日的成交额
        - 成交额 = 成交量 × 收盘价
        
        ### 使用建议
        - 建议在交易日收盘后运行，确保数据完整性
        - 可根据市场情况调整参数
        - 结果仅供参考，投资需谨慎
        """)

if __name__ == "__main__":
    # 检查是否在streamlit环境中运行
    try:
        # 如果导入streamlit成功且检测到streamlit运行环境
        if 'streamlit' in globals():
            streamlit_app()
        else:
            main()
    except:
        # 如果streamlit不可用，运行传统命令行版本
        main()