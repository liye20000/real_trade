async function loadTradeGraph(traderId) {
    try {
        // 从API获取数据
        const response = await fetch(`/api/strategy_data/${traderId}`);
        const data = await response.json();
        const upColor = '#00da3c';
        const downColor = '#ec0000';

        // 处理数据
        var categoryData = [];
        var values = [];
        var volumes = [];
        var fastMA = []; // 新增变量，用于存储fast_ma均线数据
        var slowMA = [];
        var buyPoints = [];  // 新增，用于存储买入点
        var sellPoints = []; // 新增，用于存储卖出点
        var lines = []; // 存储买卖点之间的连线
        var volume_ma = [];
    


        for (var i = 0; i < data.length; i++) {
            categoryData.push(data[i].timestamp);
            values.push([data[i].open, data[i].close, data[i].low, data[i].high]);
            // volumes.push(data[i].volume);
            volumes.push([i, data[i].volume, data[i].close > data[i].open ? 1 : -1]); //为了上色

            // fastMA.push(data[i].fast_ma); // 新增，将fast_ma数据推入数组
            // fastMA.push(parseFloat(data[i].sma_fast).toFixed(1));
            var smaValue = parseFloat(data[i].sma_fast).toFixed(1);
            fastMA.push(smaValue == 0 ? null : smaValue); // 将0值设置为null

            var slowMaValue = parseFloat(data[i].sma_slow).toFixed(1);
            slowMA.push(slowMaValue==0? null:slowMaValue);

            var volumeMaValue = parseFloat(data[i].volume_ma).toFixed(1);
            volume_ma.push(volumeMaValue);

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
              left: 'center',  // 将标题居中
              top: 30,         // 距离顶部的距离
              textStyle: {
                    fontWeight: 'bold',  // 设置为黑体
                    color: '#000'        // 设置标题文字颜色为黑色
                  }
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross'
                },
                borderWidth: 1,
                borderColor: '#ccc',
                padding: 10,
                textStyle: {
                  color: '#000'
                },
                position: function (pos, params, el, elRect, size) {
                          const obj = {
                              top: 10
                            };
                          obj[['left', 'right'][+(pos[0] < size.viewSize[0] / 2)]] = 30;
                          return obj;
                }
            },
            axisPointer: {   //增加后，可以在tooltip里面展示所有的分子栏的信息
              link: [
                    {
                      xAxisIndex: 'all'
                    }
                    ],
              label: {
                    backgroundColor: '#777'
                    }
            },
            visualMap: {  //先加上，后面volume上色用
                  show: false,
                  seriesIndex: 0,
                  dimension: 2,
                  pieces: [
                        {
                          value: 1,
                          color: downColor
                        },
                        {
                          value: -1,
                          color: upColor
                        }
                  ]
            },
            legend: {
                // right: 30,
                orient: 'vertical',  // 设置图例的排列方向为垂直
                right: '10px',       // 将图例挪到屏幕右边
                top: '10%',       // 将图例垂直居中
                // right: 10,
                // top: 20,
                // bottom: 20,
                data: ['K线', 'Fast MA','Slow MA','Buy Points','Sell Points','Buy-Sell Lines','Volume','VolumeMa']
            },
            dataZoom: [
                {
                  type: 'slider',
                  xAxisIndex: [0, 2],
                  realtime: false,
                  start: 20,
                  end: 70,
                  top: 'bottom',
                  height: 20,
                  handleSize: '120%'
                },
                {
                  type: 'inside',
                  xAxisIndex: [0, 2],
                  start: 40,
                  end: 70,
                  top: 30,
                  height: 20
                }
              ],
              xAxis: [
                {
                  type: 'category',
                  data: categoryData,
                  boundaryGap: false,
                  axisLine: { lineStyle: { color: '#777' } },
                //   axisLabel: {
                //     formatter: function (value) {
                //       return echarts.format.formatTime('MM-dd', value);
                //     }
                //   },
                  min: 'dataMin',
                  max: 'dataMax',
                  axisPointer: {
                    show: true
                  },
                  boundaryGap: false,
                  splitLine: { show: false },
                  axisLabel: { show: false },
                  axisTick: { show: false }
                },
                {
                  type: 'category',
                  gridIndex: 1,
                  data: categoryData,
                  boundaryGap: true,
                  splitLine: { show: true },
                  axisLabel: { show: true },
                  axisTick: { show: true },
                  axisLine: { lineStyle: { color: '#777' } },
                  min: 'dataMin',
                  max: 'dataMax',
                //   axisPointer: {  //辅助图标，不需要
                //     type: 'shadow',
                //     label: { show: false },
                //     triggerTooltip: true,
                //     handle: {
                //       show: true,
                //       margin: 30,
                //       color: '#B80C00'
                //     }
                //   }
                },
                {
                  type: 'category',
                  gridIndex: 2,
                  data: categoryData,
                  boundaryGap: true,
                  splitLine: { show: true },
                  axisLabel: { show: true },
                  axisTick: { show: true },
                  axisLine: { lineStyle: { color: '#777' } },
                  min: 'dataMin',
                  max: 'dataMax',
                //   axisPointer: {  //辅助图标，不需要
                //     type: 'shadow',
                //     label: { show: false },
                //     triggerTooltip: true,
                //     handle: {
                //       show: true,
                //       margin: 30,
                //       color: '#B80C00'
                //     }
                //   }
                }
              ],
              yAxis: [
                {
                  scale: true,
                  splitNumber: 3,
                  axisLine: { lineStyle: { color: '#777' } },
                  splitLine: { show: true },
                  axisTick: { show: false },
                  axisLabel: {
                    inside: true,
                    formatter: '{value}\n'
                  }
                },
                {
                  scale: true,
                  gridIndex: 1,
                  splitNumber: 3,
                  axisLabel: { show: false },
                  axisLine: { show: false }, //用来做显示y轴坐标
                  axisTick: { show: false },
                  splitLine: { show: false }
                },
                {
                  scale: true,
                  gridIndex: 2,
                  splitNumber: 3,
                  axisLabel: { show: false },
                  axisLine: { show: false }, //用来做显示y轴坐标
                  axisTick: { show: false },
                  splitLine: { show: false }
                }
              ],
              grid: [  //改成百分数后，尺寸可以动态调整
                {
                  left: '10%',
                  right: '8%',
                  // top: 110,
                  height: '50%'
                },
                {
                  left: '10%',
                  right: '8%',
                  top: '55%',
                  // height: 60,
                  height: '16%'
                },
                {
                  left: '10%',
                  right: '8%',
                  top: '75%',
                  // height: 60,
                  height: '16%'
                }

              ],
            
              series: [
                {
                  name: 'Volume',
                  type: 'bar',
                  xAxisIndex: 1,
                  yAxisIndex: 1,
                  // itemStyle: {
                  //   color: '#7fbe9e'
                  // },
                  // emphasis: {
                  //   itemStyle: {
                  //     color: '#140'
                  //   }
                  // },
                  data: volumes
                },
                {
                  name: 'VolumeMa',
                  type: 'line',
                  xAxisIndex: 2,
                  yAxisIndex: 2,
                  // itemStyle: {
                  //   color: '#7fbe9e'
                  // },
                  // emphasis: {
                  //   itemStyle: {
                  //     color: '#140'
                  //   }
                  // },
                  data: volume_ma
                },

                {
                  type: 'candlestick',
                  name: 'K线',
                  data: values,
                  itemStyle: {
                    color: '#ef232a',
                    color0: '#14b143',
                    borderColor: '#ef232a',
                    borderColor0: '#14b143'
                  },
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
                    type: `line`,
                    name: 'Slow MA',
                    data: slowMA,
                    smooth: false,
                    lineStyle:{
                      color: '#FF9922'
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

     

        // 获取图表的容器
        var mainChartDom = document.getElementById('main');
        // var volumeChartDom = document.getElementById('volume');

        // 初始化图表实例
        var mainChart = echarts.init(mainChartDom);
        // var volumeChart = echarts.init(volumeChartDom);

        // 设置图表选项
        mainChart.setOption(mainOption);
        // volumeChart.setOption(volumeOption);

        // 窗口大小变化时调整图表大小
        window.addEventListener('resize', function () {
            mainChart.resize();
            // volumeChart.resize();
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
