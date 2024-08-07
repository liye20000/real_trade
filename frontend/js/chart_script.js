async function loadTradeGraph(traderId) {
    try {
        // 从API获取数据
        const response = await fetch(`/api/strategy_data/${traderId}`);
        const data = await response.json();

        // 处理数据
        var categoryData = [];
        var values = [];
        var volumes = [];
        var fastMA = []; // 新增变量，用于存储fast_ma均线数据
        var buyPoints = [];  // 新增，用于存储买入点
        var sellPoints = []; // 新增，用于存储卖出点
        var lines = []; // 存储买卖点之间的连线
    


        for (var i = 0; i < data.length; i++) {
            categoryData.push(data[i].timestamp);
            values.push([data[i].open, data[i].close, data[i].low, data[i].high]);
            volumes.push(data[i].volume);
            // fastMA.push(data[i].fast_ma); // 新增，将fast_ma数据推入数组
            // fastMA.push(parseFloat(data[i].sma_fast).toFixed(1));
            var smaValue = parseFloat(data[i].sma_fast).toFixed(1);
            fastMA.push(smaValue == 0 ? null : smaValue); // 将0值设置为null
            if (data[i].buy) { // 如果buy字段有值
                buyPoints.push({
                    name: 'Buy',
                    value: [data[i].timestamp, data[i].buy],
                    // value: data[i].buy,
                    symbol: 'triangle', // 图标类型
                    symbolSize: 15, // 图标大小
                    itemStyle: {
                        color: 'green' // 图标颜色
                    },
                    label: {
                        show: true,
                        formatter: 'B', // 图标内显示的文本
                        position: 'top'
                    },
                    tooltip: {
                        formatter: `时间: ${data[i].timestamp}<br/>买入点位: ${data[i].buy}<br/>买入额度: ${data[i].volume}`
                    }
                });
            }
            if (data[i].sell) { // 如果sell字段有值
                sellPoints.push({
                    name: 'Sell',
                    value: [data[i].timestamp, data[i].sell],
                    // value: data[i].sell,
                    symbol: 'diamond', // 图标类型
                    symbolSize: 15, // 图标大小
                    itemStyle: {
                        color: 'red' // 图标颜色
                    },
                    label: {
                        show: true,
                        formatter: 'S', // 图标内显示的文本
                        position: 'bottom'
                    },
                    tooltip: {
                        formatter: `时间: ${data[i].timestamp}<br/>卖出点位: ${data[i].sell}<br/>卖出额度: ${data[i].volume}`
                    }
                });
                // 添加买卖点之间的连线
                if (buyPoints.length > 0) {
                    let lastBuy = buyPoints[buyPoints.length - 1];
                    let lineColor = lastBuy.value[1] < data[i].sell ? 'green' : 'red';
                    lines.push({
                        coords: [
                            [lastBuy.value[0], lastBuy.value[1]], // 使用buy点的时间
                            [categoryData[i], data[i].sell]
                        ],
                        lineStyle: {
                            color: lineColor,
                            type:'dashed' //使用虚线
                        }
                    });
                }
            }

        }

        // 主图表选项
        var mainOption = {
            title: {
                text: 'K线图',
                left: 0
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross'
                }
            },
             legend: {
                data: ['K线', 'Fast MA','Buy Points','Sell Points','Buy-Sell Lines']
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
            dataZoom: [  //TODO: 后续修改统一滑块
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
                },
                {
                    type: 'line', // 新增，用于显示fast_ma均线
                    name: 'Fast MA',
                    data: fastMA,
                    smooth: true,
                    lineStyle: {
                        color: '#FF9900' // fast_ma均线颜色
                    }
                },
                {
                    type: 'scatter',
                    name: 'Buy Points',
                    data: buyPoints,
                    tooltip: {
                        trigger: 'item',
                        formatter: function (params) {
                            return params.data.tooltip.formatter;
                        }
                    }
                },
                {
                    type: 'scatter',
                    name: 'Sell Points',
                    data: sellPoints,
                    tooltip: {
                        trigger: 'item',
                        formatter: function (params) {
                            return params.data.tooltip.formatter;
                        }
                    }
                },
                {
                    type: 'lines',
                    name: 'Buy-Sell Lines',
                    coordinateSystem: 'cartesian2d',
                    data: lines,
                    lineStyle: {
                        type:'dashed',
                        width: 2
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
