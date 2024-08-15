// UTC 时间转换为本地时区时间
function convertToLocaleTime(utcTime) {
    const date = new Date(utcTime + ' UTC');
    return date.toLocaleString();
}
function roundDownToFiveMinuteInterval(dateTime) {
    // 解析日期时间字符串
    // var date = new Date(dateTime);
    var date = new Date(dateTime.replace(' ', 'T') + 'Z');

    // 获取分钟数
    var minutes = date.getMinutes();

    // 计算向前取整的5分钟间隔
    var roundedMinutes = Math.floor(minutes / 5) * 5;

    // 设置日期对象的分钟和秒数为整5分钟
    date.setMinutes(roundedMinutes);
    date.setSeconds(0);
    date.setMilliseconds(0);

    // 格式化为 'YYYY-MM-DD HH:mm:ss'
    return date.toISOString().slice(0, 19).replace('T', ' ');
}
async function loadTradeGraph(traderId) {
    try {
        // 从API获取数据
        const response = await fetch(`/api/strategy_data/${traderId}`);
        const data = await response.json();

        const trade_response = await fetch(`/api/trading_data/${traderId}`);
        const trade_data = await trade_response.json();
        const upColor = '#ef232a';
        const downColor = '#14b143';

        // 处理数据
        var categoryData = [];
        var values = [];

        var volumes = [];
        var fastMA = []; // 新增变量，用于存储fast_ma均线数据
        var slowMA = [];
        var volume_ma = [];
        
        var buyPoints = [];  // 新增，用于存储买入点
        var sellPoints = []; // 新增，用于存储卖出点
        var lines = []; // 存储买卖点之间的连线
        
        for (var i=0; i<trade_data.length; i++){
          // let formattedDateTime = convertToLocaleTime(trade_data[i].execution_time).slice(0, 13) + ':00:00';
          // let InternaldDateTime = formatToFiveMinuteInterval(trade_data[i].execution_time);
          // let formattedDateTime = convertToLocaleTime(InternaldDateTime);
          let formattedDateTime = roundDownToFiveMinuteInterval(trade_data[i].execution_time);

          // let formattedDateTime = dateObj.toISOString().slice(0, 19).replace('T', ' ');
          // 将日期对象格式化为字符串输出
          if (trade_data[i].side == 'BUY') { // 如果buy字段有值
              // 格式化为字符串输出
              buyPoints.push({
                  name: 'Buy',
                  value: [formattedDateTime, trade_data[i].trade_price],
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
                      formatter: `时间: ${trade_data[i].execution_time}<br/>买入点位: ${trade_data[i].trade_price}<br/>买入额度: ${trade_data[i].trade_volume}`
                  }
              });
          }
          if (trade_data[i].side == 'SELL') { // 如果sell字段有值
                sellPoints.push({
                    name: 'Sell',
                    value: [formattedDateTime, trade_data[i].trade_price],
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
                        formatter: `时间: ${trade_data[i].execution_time}<br/>卖出点位: ${trade_data[i].trade_price}<br/>卖出额度: ${trade_data[i].trade_volume}`
                    }
                });
                // 添加买卖点之间的连线
                if (buyPoints.length > 0) {
                  let lastBuy = buyPoints[buyPoints.length - 1];
                  let lineColor = lastBuy.value[1] < data[i].sell ? 'green' : 'red';
                  lines.push({
                      coords: [
                          [lastBuy.value[0], lastBuy.value[1]], // 使用buy点的时间
                          [formattedDateTime, trade_data[i].trade_price]
                      ],
                      lineStyle: {
                          color: lineColor,
                          type:'dashed' //使用虚线
                      }
                  });
                }
          }
        }

        for (var i = 0; i < data.length; i++) {
            categoryData.push(data[i].timestamp);
            values.push([data[i].open, data[i].close, data[i].low, data[i].high]);

            //处理策略数据
            volumes.push([i, data[i].volume, data[i].close > data[i].open ? 1 : -1]); //为了上色
            var smaValue = parseFloat(data[i].sma_fast).toFixed(1);
            fastMA.push(smaValue == 0 ? null : smaValue); // 将0值设置为null
            var slowMaValue = parseFloat(data[i].sma_slow).toFixed(1);
            slowMA.push(slowMaValue==0? null:slowMaValue);
            var volumeMaValue = parseFloat(data[i].volume_ma).toFixed(1);
            volume_ma.push(volumeMaValue);

            // //处理买卖数据
            // if (data[i].buy) { // 如果buy字段有值
            //     buyPoints.push({
            //         name: 'Buy',
            //         value: [data[i].timestamp, data[i].buy],
            //         // value: data[i].buy,
            //         symbol: 'triangle', // 图标类型
            //         symbolSize: 15, // 图标大小
            //         itemStyle: {
            //             color: 'green' // 图标颜色
            //         },
            //         label: {
            //             show: true,
            //             formatter: 'B', // 图标内显示的文本
            //             position: 'top'
            //         },
            //         tooltip: {
            //             formatter: `时间: ${data[i].timestamp}<br/>买入点位: ${data[i].buy}<br/>买入额度: ${data[i].volume}`
            //         }
            //     });
            // }
            // if (data[i].sell) { // 如果sell字段有值
            //     sellPoints.push({
            //         name: 'Sell',
            //         value: [data[i].timestamp, data[i].sell],
            //         // value: data[i].sell,
            //         symbol: 'diamond', // 图标类型
            //         symbolSize: 15, // 图标大小
            //         itemStyle: {
            //             color: 'red' // 图标颜色
            //         },
            //         label: {
            //             show: true,
            //             formatter: 'S', // 图标内显示的文本
            //             position: 'bottom'
            //         },
            //         tooltip: {
            //             formatter: `时间: ${data[i].timestamp}<br/>卖出点位: ${data[i].sell}<br/>卖出额度: ${data[i].volume}`
            //         }
            //     });
            //     // 添加买卖点之间的连线
            //     if (buyPoints.length > 0) {
            //         let lastBuy = buyPoints[buyPoints.length - 1];
            //         let lineColor = lastBuy.value[1] < data[i].sell ? 'green' : 'red';
            //         lines.push({
            //             coords: [
            //                 [lastBuy.value[0], lastBuy.value[1]], // 使用buy点的时间
            //                 [categoryData[i], data[i].sell]
            //             ],
            //             lineStyle: {
            //                 color: lineColor,
            //                 type:'dashed' //使用虚线
            //             }
            //         });
            //     }
            // }

        }

        
        // categoryData = categoryData.map(convertToLocaleTime); //把时间转换成local时间
       
        // 主图表选项
        var mainOption = {
            title: {
              text: '策略数据图形化展示',
              left: 'center',  // 将标题居中
              top: '1%',         // 距离顶部的距离
              textStyle: {
                    fontWeight: 'bold',  // 设置为黑体
                    color: '#000'        // 设置标题文字颜色为黑色
                  }
            },
            tooltip: {
                trigger: 'axis',
                backgroundColor: 'rgba(0, 0, 0, 0.5)',  // 半透明黑色背景
                borderWidth: 1,                        // 边框宽度
                borderColor: 'rgba(200, 200, 200, 0.7)', // 半透明灰色边框
                textStyle: {
                    color: '#ffffff',                  // 白色文字
                    fontSize: 12,                      // 字体大小
                    fontWeight: 'normal'               // 字体粗细
                },
                padding: 10,                           // 内边距
                extraCssText: 'box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);' ,// 添加阴影
                axisPointer: {
                    type: 'cross'
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
            dataZoom: [ //滑动条设置
                {
                  type: 'slider',
                  xAxisIndex: [0,1,2],
                  realtime: false,
                  start: 80,  // 例如从最后20%处开始显
                  end: 100,   // 显示最新的数据
                  top: 'bottom',
                  height: 30,
                  handleSize: '120%'
                },
                {
                  type: 'inside',
                  xAxisIndex: [0,1,2],
                  start: 80,
                  end: 100,
                  top: 30,
                  height: 20
                }
              ],
            xAxis: [
                {
                  type: 'category',
                  data: categoryData,
                  axisLine: {  //横坐标线的属性 
                    show: true,
                    lineStyle: { type:'dashed',width:2 } 
                  },
             
                  min: 'dataMin',
                  max: 'dataMax',
                  axisPointer: {  //显示轨迹，但不显示浮动坐标
                    show: true,
                    label:{show:false}
                  },
                  boundaryGap: false,
                  splitLine: { show: true }, //横向坐标轴表格
                  axisLabel: { show: false },
                  axisTick: { show: false }
                },
                {
                  gridIndex: 1,
                  type: 'category',
                  data: categoryData,
                  axisLine: {
                    show: true,
                    lineStyle:{ type:'dashed',width:2 }
                  },

                  min: 'dataMin',
                  max: 'dataMax',
                  axisPointer:{
                    show:true,
                    label:{show:false}
                    },
                  boundaryGap: true,
                  splitLine: { show: true },
                  axisLabel: { show: false },//是否显示坐标
                  axisTick: { show: false }
                },
                {
                  gridIndex: 2,
                  type: 'category',
                  data: categoryData,
                  axisLine: {
                    show: true,
                    lineStyle:{ type:'solid',width:2 }
                  },

                  min: 'dataMin',
                  max: 'dataMax',
                  axisPointer:{
                    show:true,
                    label:{show:true}
                    },
                  boundaryGap: true,
                  splitLine: { show: true },
                  axisLabel: { show: true },
                  axisTick: { show: false },
                  
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
                  splitNumber: 5,
                  axisLine: {
                    show:true, 
                    lineStyle: { type: 'solid' } 
                  },
                  splitLine: { show: true }, //坐标轴表格
                  axisTick: { show: false }, //刻度
                  axisLabel: {  //标签
                    inside: false,
                    formatter: '{value}\n'
                  }
                },
                {
                  gridIndex: 1,
                  scale: true,
                  splitNumber: 3,
                  axisLine: { 
                    show: true,
                    lineStyle:{type: 'solid'}
                  }, //用来做显示y轴坐标
                  splitLine:{show: true},
                  axisTick: { show: false },
                  axisLabel: { 
                    inside: false,
                    formatter: '{value}\n' 
                  }
                },
                {
                  gridIndex: 2,
                  scale: true,
                  splitNumber: 3,
                  axisLine: {
                    show: true,
                    lineStyle:{type: 'solid'}
                  },
                  splitLine: { show: true},
                  axisTick: { show: false },
                  axisLabel: { 
                    inside: false,
                    formatter: '{value}\n'},
                }
              ],
            grid: [  //改成百分数后，尺寸可以动态调整
                {
                  left: '7%',
                  right: '7%',
                  height: '50%',
                  top: '9%'
                },
                {
                  left: '7%',
                  right: '7%',
                  top: '62%',
                  height: '16%'
                },
                {
                  left: '7%',
                  right: '7%',
                  top: '80%',
                  height: '16%'
                }

              ],
            
            series: [
              {
                type: 'candlestick',
                name: 'K线',
                data: values,
                itemStyle: {
                  color: upColor,
                  color0: downColor,
                  borderColor: upColor,
                  borderColor0: downColor
                },
              },
                
                
              
              ]
        };

        var stra_ma_series = [
          {
            type: 'line', // 新增，用于显示fast_ma均线
            name: 'Fast MA',
            data: fastMA,
            smooth: true,
            showSymbol: false,  //不显示数据点只显示线条
            itemStyle: {
                color: '#FF9900',    // 数据点颜色设置为黄色（也可以是其他颜色）
                borderWidth: 1,      // 点的边框宽度
                borderColor: '#FF9900' // 点的边框颜色设置为蓝色
            },
            lineStyle:{
              color: '#FF9900', //橙红色,
              width: 1
            }
          },
          {
            type: `line`,
            name: 'Slow MA',
            data: slowMA,
            smooth: true,
            showSymbol: false,  //不显示数据点只显示线条
            itemStyle: {
                color: '#1E90FF',    // 数据点颜色设置为黄色（也可以是其他颜色）
                borderWidth: 1,      // 点的边框宽度
                borderColor: '#1E90FF' // 点的边框颜色设置为蓝色
            },
            lineStyle:{
              color: '#1E90FF', //蓝色,
              width: 1
            }
          },
          {
            name: 'Volume',
            type: 'bar',
            xAxisIndex: 1,
            yAxisIndex: 1,
            data: volumes,
            itemStyle: {
              color: function(params) {
                  // 根据 params.data[2] (即 1 或 -1) 来设置颜色
                  return params.data[2] > 0 ? upColor : downColor;
              }
          }
          },
          {
            name: 'VolumeMa',
            type: 'line',
            xAxisIndex: 2,
            yAxisIndex: 2,
            data: volume_ma,
            smooth: true,
            lineStyle:{
              color: '#585eaa'
            },
            markLine: {
              symbol: 'none', // 不显示箭头
              data: [
                {
                  name: '第一条线',
                  yAxis: 10000, // 固定在y轴50的位置
                  lineStyle: {
                    type: 'dashed', // 虚线
                    color: 'blue', // 第一条线的颜色
                    width: 1
                  }
                },
                {
                  name: '第二条线',
                  yAxis: 30000, // 固定在y轴100的位置
                  lineStyle: {
                    type: 'dashed', // 虚线
                    color: 'red', // 第一条线的颜色
                    width: 1
                  }
                }
              ]
            }
          },
        ];

        var trade_series = [
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
        ];

        // var stra_ma_legend = {  
        //   // right: 30,
        //   orient: 'vertical',  // 设置图例的排列方向为垂直
        //   right: '-20px',       // 将图例挪到屏幕右边
        //   top: '20%',       // 将图例垂直居中
        //   // right: 10,
        //   // top: 20,
        //   // bottom: 20,
        //   data: ['K线', 'Fast MA','Slow MA','Buy Points','Sell Points','Buy-Sell Lines','Volume','VolumeMa']
        // };

        var stra_ma_legend = {  
          type: 'scroll',            // 设置图例类型为可滑动
          orient: 'horizontal',      // 水平排列
          left: 'center',            // 水平居中
          top: '4%',                 // 放置在标题下方
          data: ['K线', 'Fast MA', 'Slow MA', 'Buy Points', 'Sell Points', 'Buy-Sell Lines', 'Volume', 'VolumeMa'],
          pageIconColor: '#aaa',     // 滑动控制按钮颜色
          pageTextStyle: {
              color: '#333'          // 滑动控制按钮文字颜色
          }
       };
        mainOption.legend = stra_ma_legend;
        mainOption.series = mainOption.series.concat(trade_series);
        mainOption.series = mainOption.series.concat(stra_ma_series);



        // 获取图表的容器
        var mainChartDom = document.getElementById('main');

        // 初始化图表实例
        var mainChart = echarts.init(mainChartDom);

        // 设置图表选项
        mainChart.setOption(mainOption);

        // 窗口大小变化时调整图表大小
        window.addEventListener('resize', function () {
            mainChart.resize();
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
