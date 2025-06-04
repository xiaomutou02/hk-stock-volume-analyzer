# 港股成交量筛选分析系统

## 📈 项目简介

一个基于Streamlit的港股成交量异常增长分析工具，帮助投资者快速发现成交额大幅增长的港股股票。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ 功能特点

### 🎯 两阶段分析策略
- **第一阶段**：筛选成交额大于设定门槛的港股
- **第二阶段**：分析成交额增长情况（对比前两个完整交易日）

### 📊 可视化展示
- **增长率图表**：显示TOP15股票的成交额增长率
- **成交额对比**：对比前后两日成交额的柱状图
- **详细数据表**：分类显示不同增长区间的股票
- **数据下载**：支持CSV格式导出

### 🔧 交互式参数调整
- **成交额门槛**：10-100百万港元可调
- **增长阈值**：支持50%、100%、200%等多级筛选

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Windows 10+

### 安装依赖
```bash
git clone https://github.com/yourusername/hk-stock-volume-analyzer.git
cd hk-stock-volume-analyzer
pip install -r requirements.txt
```

### 启动应用
```bash
streamlit run streamlit_app.py
```

### 访问应用
打开浏览器访问：http://localhost:8501

## 📂 项目结构
```
hk_stock/
├── streamlit_app.py          # Streamlit主应用
├── hk_volume_filter.py       # 核心分析逻辑
├── requirements.txt          # 项目依赖
├── README.md                # 项目说明
├── .gitignore               # Git忽略文件
├── 启动说明.md               # 详细启动说明
├── 启动应用.bat             # Windows批处理启动脚本
└── 程序修改说明.md           # 程序修改历史
```

## 💡 使用流程

1. **设置参数**：在左侧面板调整筛选条件
2. **开始分析**：点击"🚀 开始分析"按钮
3. **查看结果**：
   - 📊 分析结果统计
   - 📈 增长率图表 
   - 💰 成交额对比
   - 📋 详细数据表
   - 💾 数据下载

## 📈 数据说明

### 数据源
- **AKShare港股行情数据**
- **实时数据**：用于初步筛选
- **历史数据**：用于准确对比分析

### 计算公式
```
成交额 = 成交量 × 收盘价
增长率 = (最近交易日成交额 / 前一交易日成交额 - 1) × 100%
```

## ⚡ 性能优化

- **执行效率**：从几小时优化到几分钟
- **数据准确性**：基于完整交易日数据对比
- **实时反馈**：进度条显示分析进度

## ⚠️ 注意事项

1. **运行时间**：建议在交易日收盘后运行，确保数据完整性
2. **网络连接**：需要稳定的网络连接获取股票数据
3. **数据延迟**：实时数据可能有几分钟延迟
4. **投资建议**：结果仅供参考，投资需谨慎

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

如果您有任何问题或建议，请创建 Issue 或联系项目维护者。

---

⭐ 如果这个项目对您有帮助，请给个星标支持一下！ 