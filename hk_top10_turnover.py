import akshare as ak
import pandas as pd

def get_hk_top10_turnover():
    """
    获取港股市场今日成交量排名前10的股票
    """
    try:
        # 获取港股实时行情数据
        print("获取港股实时行情数据...")
        stock_hk_spot_em_df = ak.stock_hk_spot_em()
        
        # 确保数据已正确获取
        if stock_hk_spot_em_df is None or len(stock_hk_spot_em_df) == 0:
            print("未能获取港股数据，请检查网络连接或akshare版本")
            return None
        
        print(f"获取到的港股数据条数: {len(stock_hk_spot_em_df)}")
        
        # 设置显示所有列
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        
        # 按成交额(元)排序并获取前10位
        # 注意：根据akshare文档，成交额列名可能是'成交额'或'成交额(元)'，这里使用通用方法
        turnover_column = [col for col in stock_hk_spot_em_df.columns if '成交额' in col][0]
        
        # 确保成交额列为数值类型
        stock_hk_spot_em_df[turnover_column] = pd.to_numeric(stock_hk_spot_em_df[turnover_column], errors='coerce')
        
        # 按成交额降序排序并获取前10位
        top10_turnover = stock_hk_spot_em_df.sort_values(by=turnover_column, ascending=False).head(10)
        
        return top10_turnover
        
    except Exception as e:
        print(f"发生错误: {e}")
        return None

if __name__ == "__main__":
    # 打印akshare版本
    print(f"AKShare版本: {ak.__version__}")
    
    # 获取并打印港股成交额排名前10的数据
    top10_data = get_hk_top10_turnover()
    
    if top10_data is not None:
        print("\n今日港股成交额排名前10位:")
        print(top10_data) 