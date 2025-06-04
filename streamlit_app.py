import streamlit as st
import pandas as pd
import datetime
import time
import plotly.express as px
import plotly.graph_objects as go
from hk_volume_filter import get_high_volume_stocks, analyze_volume_growth

# 设置页面配置
st.set_page_config(
    page_title="港股成交量筛选分析",
    page_icon="📈",
    layout="wide"
)

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

def main():
    """主应用函数"""
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
                    delta="增长>50%"
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
    main() 