async function loadTradeGraph(traderId) {
    try {
        // 从API获取数据
        const response = await fetch(`/api/strategy_data/${traderId}`);
        const data = await response.json();

        // 处理数据
        var categoryData = [];
        var values = [];
        var volumes = [];
        var sma_fast = [];

        for (var i = 0; i < data.length; i++) {
            categoryData.push(data[i].timestamp);
            values.push([data[i].open, data[i].close, data[i].low, data[i].high]);
            sma_fast.push([data[i].sma_fast]);
            volumes.push(data[i].volume);
        }

        // 主图表选项
        var mainOption = {
            title: {
                text: 'K线图hehe',
                left: 0
            },

            grid: {
                left: '10%',
                right: '10%',
                bottom: '15%'
              },
            xAxis: {
                type: 'category',
                data: categoryData,
                scale: true,
                boundaryGap: false,
                axisLine: { onZero: false },
                splitLine: { show: false },
                min: 'dataMin',
                max: 'dataMax'
            },
            yAxis: {
                scale: true,
                splitArea: {
                    show: true
                }
            },
            dataZoom: [
                {
                    type: 'inside',
                    xAxisIndex: [0, 1], // 指定两个图表共享同一个dataZoom
                    start: 70,
                    end: 100
                },
                {
                    show: true,
                    xAxisIndex: [0, 1], // 指定两个图表共享同一个dataZoom
                    type: 'slider',
                    top: '85%', // 滑块的位置
                    start: 70,
                    end: 100
                }
            ],
            series: [
                {
                    type: 'candlestick',
                    name: 'K线',
                    data: values,
                    itemStyle: {
                        color: '#FD1050', // 下跌颜色
                        color0: '#0CF49B', // 上涨颜色
                        borderColor: '#FD1050',
                        borderColor0: '#0CF49B'
                    }
                }
            ]
        };

        // 成交量图表选项
        var volumeOption = {
            title: {
                text: '成交量',
                left: 0
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'shadow'
                }
            },
            xAxis: {
                type: 'category',
                data: categoryData,
                scale: true,
                boundaryGap: false,
                axisLine: { onZero: false },
                splitLine: { show: false },
                min: 'dataMin',
                max: 'dataMax'
            },
            yAxis: {
                scale: true,
                splitArea: {
                    show: true
                }
            },
            dataZoom: [
                {
                    type: 'inside',
                    xAxisIndex: [0, 1], // 与主图表共享
                    start: 70,
                    end: 100
                },
                {
                    show: true,
                    xAxisIndex: [0, 1], // 与主图表共享
                    type: 'slider',
                    top: '85%', // 滑块的位置
                    start: 70,
                    end: 100
                }
            ],
            series: [
                {
                    type: 'bar',
                    name: '成交量',
                    data: volumes,
                    itemStyle: {
                        color: '#7fbe9e'
                    }
                }
            ]
        };

        // 获取图表的容器
        var mainChartDom = document.getElementById('main');
        var volumeChartDom = document.getElementById('volume');

        // 初始化图表实例
        var mainChart = echarts.init(mainChartDom);
        var volumeChart = echarts.init(volumeChartDom);

        // 设置图表选项
        mainChart.setOption(mainOption);
        volumeChart.setOption(volumeOption);

        // 窗口大小变化时调整图表大小
        window.addEventListener('resize', function () {
            mainChart.resize();
            volumeChart.resize();
        });

    } catch (error) {
        console.error('Failed to load trade data:', error);
    }
}

// 从URL获取trader_id
const urlParams = new URLSearchParams(window.location.search);
const traderId = urlParams.get('trader_id');

// 加载图表
loadTradeGraph(traderId);
