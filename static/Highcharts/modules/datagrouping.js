/**
 * Highstock JS v11.3.0 (2024-01-10)
 *
 * Data grouping module
 *
 * (c) 2010-2024 Torstein Hønsi
 *
 * License: www.highcharts.com/license
 */!function(t){"object"==typeof module&&module.exports?(t.default=t,module.exports=t):"function"==typeof define&&define.amd?define("highcharts/modules/datagrouping",["highcharts"],function(i){return t(i),t.Highcharts=i,t}):t("undefined"!=typeof Highcharts?Highcharts:void 0)}(function(t){"use strict";var i=t?t._modules:{};function o(t,i,o,e){t.hasOwnProperty(i)||(t[i]=e.apply(null,o),"function"==typeof CustomEvent&&window.dispatchEvent(new CustomEvent("HighchartsModuleLoaded",{detail:{path:i,module:t[i]}})))}o(i,"Extensions/DataGrouping/ApproximationRegistry.js",[],function(){return{}}),o(i,"Extensions/DataGrouping/ApproximationDefaults.js",[i["Extensions/DataGrouping/ApproximationRegistry.js"],i["Core/Utilities.js"]],function(t,i){let{arrayMax:o,arrayMin:e,correctFloat:a,extend:n,isNumber:s}=i;function r(t){let i=t.length,o=l(t);return s(o)&&i&&(o=a(o/i)),o}function l(t){let i=t.length,o;if(!i&&t.hasNulls)o=null;else if(i)for(o=0;i--;)o+=t[i];return o}let p={average:r,averages:function(){let t=[];return[].forEach.call(arguments,function(i){t.push(r(i))}),void 0===t[0]?void 0:t},close:function(t){return t.length?t[t.length-1]:t.hasNulls?null:void 0},high:function(t){return t.length?o(t):t.hasNulls?null:void 0},hlc:function(i,o,e){if(i=t.high(i),o=t.low(o),e=t.close(e),s(i)||s(o)||s(e))return[i,o,e]},low:function(t){return t.length?e(t):t.hasNulls?null:void 0},ohlc:function(i,o,e,a){if(i=t.open(i),o=t.high(o),e=t.low(e),a=t.close(a),s(i)||s(o)||s(e)||s(a))return[i,o,e,a]},open:function(t){return t.length?t[0]:t.hasNulls?null:void 0},range:function(i,o){return(i=t.low(i),o=t.high(o),s(i)||s(o))?[i,o]:null===i&&null===o?null:void 0},sum:l};return n(t,p),p}),o(i,"Extensions/DataGrouping/DataGroupingDefaults.js",[],function(){return{common:{groupPixelWidth:2,dateTimeLabelFormats:{millisecond:["%A, %e %b, %H:%M:%S.%L","%A, %e %b, %H:%M:%S.%L","-%H:%M:%S.%L"],second:["%A, %e %b, %H:%M:%S","%A, %e %b, %H:%M:%S","-%H:%M:%S"],minute:["%A, %e %b, %H:%M","%A, %e %b, %H:%M","-%H:%M"],hour:["%A, %e %b, %H:%M","%A, %e %b, %H:%M","-%H:%M"],day:["%A, %e %b %Y","%A, %e %b","-%A, %e %b %Y"],week:["Week from %A, %e %b %Y","%A, %e %b","-%A, %e %b %Y"],month:["%B %Y","%B","-%B %Y"],year:["%Y","%Y","-%Y"]}},seriesSpecific:{line:{},spline:{},area:{},areaspline:{},arearange:{},column:{groupPixelWidth:10},columnrange:{groupPixelWidth:10},candlestick:{groupPixelWidth:10},ohlc:{groupPixelWidth:5},hlc:{groupPixelWidth:5},heikinashi:{groupPixelWidth:10}},units:[["millisecond",[1,2,5,10,20,25,50,100,200,500]],["second",[1,2,5,10,15,30]],["minute",[1,2,5,10,15,30]],["hour",[1,2,3,4,6,8,12]],["day",[1]],["week",[1]],["month",[1,3,6]],["year",null]]}}),o(i,"Extensions/DataGrouping/DataGroupingAxisComposition.js",[i["Extensions/DataGrouping/DataGroupingDefaults.js"],i["Core/Globals.js"],i["Core/Utilities.js"]],function(t,i,o){let e;let{composed:a}=i,{addEvent:n,extend:s,merge:r,pick:l,pushUnique:p}=o;function u(t){let i=this,o=i.series;o.forEach(function(t){t.groupPixelWidth=void 0}),o.forEach(function(o){o.groupPixelWidth=i.getGroupPixelWidth&&i.getGroupPixelWidth(),o.groupPixelWidth&&(o.hasProcessed=!0),o.applyGrouping(!!t.hasExtremesChanged)})}function h(){let i=this.series,o=i.length,e=0,a=!1,n,s;for(;o--;)(s=i[o].options.dataGrouping)&&(e=Math.max(e,l(s.groupPixelWidth,t.common.groupPixelWidth)),n=(i[o].processedXData||i[o].data).length,(i[o].groupPixelWidth||n>this.chart.plotSizeX/e||n&&s.forced)&&(a=!0));return a?e:0}function g(){this.series.forEach(function(t){t.hasProcessed=!1})}function d(t,i){let o;if(i=l(i,!0),t||(t={forced:!1,units:null}),this instanceof e)for(o=this.series.length;o--;)this.series[o].update({dataGrouping:t},!1);else this.chart.options.series.forEach(function(i){i.dataGrouping="boolean"==typeof t?t:r(t,i.dataGrouping)});this.ordinal&&(this.ordinal.slope=void 0),i&&this.chart.redraw()}return{compose:function t(i){e=i,p(a,t)&&(n(i,"afterSetScale",g),n(i,"postProcessData",u),s(i.prototype,{applyGrouping:u,getGroupPixelWidth:h,setDataGrouping:d}))}}}),o(i,"Extensions/DataGrouping/DataGroupingSeriesComposition.js",[i["Extensions/DataGrouping/ApproximationRegistry.js"],i["Extensions/DataGrouping/DataGroupingDefaults.js"],i["Core/Axis/DateTimeAxis.js"],i["Core/Defaults.js"],i["Core/Globals.js"],i["Core/Series/SeriesRegistry.js"],i["Core/Utilities.js"]],function(t,i,o,e,a,n,s){let{composed:r}=a,{series:{prototype:l}}=n,{addEvent:p,defined:u,error:h,extend:g,isNumber:d,merge:c,pick:f,pushUnique:m}=s,x=l.generatePoints;function D(t){var e;let a,n;let s=this.chart,r=this.options,p=r.dataGrouping,g=!1!==this.allowDG&&p&&f(p.enabled,s.options.isStock),c=this.reserveSpace(),m=this.currentDataGrouping,x,D,G=!1;g&&!this.requireSorting&&(this.requireSorting=G=!0);let y=!1==!(this.isCartesian&&!this.isDirty&&!this.xAxis.isDirty&&!this.yAxis.isDirty&&!t)||!g;if(G&&(this.requireSorting=!1),y)return;this.destroyGroupedData();let M=p.groupAll?this.xData:this.processedXData,A=p.groupAll?this.yData:this.processedYData,S=s.plotSizeX,j=this.xAxis,b=j.options.ordinal,P=this.groupPixelWidth;if(P&&M&&M.length&&S){n=!0,this.isDirty=!0,this.points=null;let t=j.getExtremes(),r=t.min,g=t.max,f=b&&j.ordinal&&j.ordinal.getGroupIntervalFactor(r,g,this)||1,m=P*(g-r)/S*f,G=j.getTimeTicks(o.Additions.prototype.normalizeTimeTickInterval(m,p.units||i.units),Math.min(r,M[0]),Math.max(g,M[M.length-1]),j.options.startOfWeek,M,this.closestPointRange),y=l.groupData.apply(this,[M,A,G,p.approximation]),E=y.groupedXData,v=y.groupedYData,C=0;for(p&&p.smoothed&&E.length&&(p.firstAnchor="firstPoint",p.anchor="middle",p.lastAnchor="lastPoint",h(32,!1,s,{"dataGrouping.smoothed":"use dataGrouping.anchor"})),a=1;a<G.length;a++)G.info.segmentStarts&&-1!==G.info.segmentStarts.indexOf(a)||(C=Math.max(G[a]-G[a-1],C));(x=G.info).gapSize=C,this.closestPointRange=G.info.totalRange,this.groupMap=y.groupMap,this.currentDataGrouping=x,function(t,i,o){let e=t.options,a=e.dataGrouping,n=t.currentDataGrouping&&t.currentDataGrouping.gapSize;if(!(a&&t.xData&&n&&t.groupMap))return;let s=i.length-1,r=a.anchor,l=a.firstAnchor,p=a.lastAnchor,u=i.length-1,h=0;if(l&&t.xData[0]>=i[0]){let o;h++;let e=t.groupMap[0].start,a=t.groupMap[0].length;d(e)&&d(a)&&(o=e+(a-1)),i[0]=({start:i[0],middle:i[0]+.5*n,end:i[0]+n,firstPoint:t.xData[0],lastPoint:o&&t.xData[o]})[l]}if(s>0&&p&&n&&i[s]>=o-n){u--;let o=t.groupMap[t.groupMap.length-1].start;i[s]=({start:i[s],middle:i[s]+.5*n,end:i[s]+n,firstPoint:o&&t.xData[o],lastPoint:t.xData[t.xData.length-1]})[p]}if(r&&"start"!==r){let t=n*({middle:.5,end:1})[r];for(;u>=h;)i[u]+=t,u--}}(this,E,g),c&&(u((e=E)[0])&&d(j.min)&&d(j.dataMin)&&e[0]<j.min&&((!u(j.options.min)&&j.min<=j.dataMin||j.min===j.dataMin)&&(j.min=Math.min(e[0],j.min)),j.dataMin=Math.min(e[0],j.dataMin)),u(e[e.length-1])&&d(j.max)&&d(j.dataMax)&&e[e.length-1]>j.max&&((!u(j.options.max)&&d(j.dataMax)&&j.max>=j.dataMax||j.max===j.dataMax)&&(j.max=Math.max(e[e.length-1],j.max)),j.dataMax=Math.max(e[e.length-1],j.dataMax))),p.groupAll&&(this.allGroupedData=v,E=(D=this.cropData(E,v,j.min,j.max)).xData,v=D.yData,this.cropStart=D.start),this.processedXData=E,this.processedYData=v}else this.groupMap=null;this.hasGroupedData=n,this.preventGraphAnimation=(m&&m.totalRange)!==(x&&x.totalRange)}function G(){this.groupedData&&(this.groupedData.forEach(function(t,i){t&&(this.groupedData[i]=t.destroy?t.destroy():null)},this),this.groupedData.length=0,delete this.allGroupedData)}function y(){x.apply(this),this.destroyGroupedData(),this.groupedData=this.hasGroupedData?this.points:null}function M(){return this.is("arearange")?"range":this.is("ohlc")?"ohlc":this.is("hlc")?"hlc":this.is("column")||this.options.cumulative?"sum":"average"}function A(i,o,e,a){let n=this,s=n.data,r=n.options&&n.options.data,l=[],p=[],h=[],g=i.length,f=!!o,m=[],x=n.pointArrayMap,D=x&&x.length,G=["x"].concat(x||["y"]),y=this.options.dataGrouping&&this.options.dataGrouping.groupAll,M,A,S,j=0,b=0,P="function"==typeof a?a:a&&t[a]?t[a]:t[n.getDGApproximation&&n.getDGApproximation()||"average"];if(D){let t=x.length;for(;t--;)m.push([])}else m.push([]);let E=D||1;for(let t=0;t<=g;t++)if(!(i[t]<e[0])){for(;void 0!==e[j+1]&&i[t]>=e[j+1]||t===g;){M=e[j],n.dataGroupInfo={start:y?b:n.cropStart+b,length:m[0].length,groupStart:M},S=P.apply(n,m),n.pointClass&&!u(n.dataGroupInfo.options)&&(n.dataGroupInfo.options=c(n.pointClass.prototype.optionsToObject.call({series:n},n.options.data[n.cropStart+b])),G.forEach(function(t){delete n.dataGroupInfo.options[t]})),void 0!==S&&(l.push(M),p.push(S),h.push(n.dataGroupInfo)),b=t;for(let t=0;t<E;t++)m[t].length=0,m[t].hasNulls=!1;if(j+=1,t===g)break}if(t===g)break;if(x){let i;let o=n.options.dataGrouping&&n.options.dataGrouping.groupAll?t:n.cropStart+t,e=s&&s[o]||n.pointClass.prototype.applyOptions.apply({series:n},[r[o]]);for(let t=0;t<D;t++)d(i=e[x[t]])?m[t].push(i):null===i&&(m[t].hasNulls=!0)}else d(A=f?o[t]:null)?m[0].push(A):null===A&&(m[0].hasNulls=!0)}return{groupedXData:l,groupedYData:p,groupMap:h}}function S(t){let o=t.options,a=this.type,n=this.chart.options.plotOptions,s=this.useCommonDataGrouping&&i.common,r=i.seriesSpecific,l=e.defaultOptions.plotOptions[a].dataGrouping;if(n&&(r[a]||s)){let t=this.chart.rangeSelector;l||(l=c(i.common,r[a])),o.dataGrouping=c(s,l,n.series&&n.series.dataGrouping,n[a].dataGrouping,this.userOptions.dataGrouping,!o.isInternal&&t&&d(t.selected)&&t.buttonOptions[t.selected].dataGrouping)}}return{compose:function t(i){let o=i.prototype.pointClass;m(r,t)&&(p(o,"update",function(){if(this.dataGroup)return h(24,!1,this.series.chart),!1}),p(i,"afterSetOptions",S),p(i,"destroy",G),g(i.prototype,{applyGrouping:D,destroyGroupedData:G,generatePoints:y,getDGApproximation:M,groupData:A}))},groupData:A}}),o(i,"Extensions/DataGrouping/DataGrouping.js",[i["Extensions/DataGrouping/DataGroupingAxisComposition.js"],i["Extensions/DataGrouping/DataGroupingDefaults.js"],i["Extensions/DataGrouping/DataGroupingSeriesComposition.js"],i["Core/Templating.js"],i["Core/Globals.js"],i["Core/Utilities.js"]],function(t,i,o,e,a,n){let{format:s}=e,{composed:r}=a,{addEvent:l,extend:p,isNumber:u,pick:h,pushUnique:g}=n;function d(t){let o=this.chart,e=o.time,a=t.labelConfig,n=a.series,r=a.point,l=n.options,g=n.tooltipOptions,d=l.dataGrouping,c=n.xAxis,f=g.xDateFormat,m,x,D,G,y,M=g[t.isFooter?"footerFormat":"headerFormat"];if(c&&"datetime"===c.options.type&&d&&u(a.key)){x=n.currentDataGrouping,D=d.dateTimeLabelFormats||i.common.dateTimeLabelFormats,x?(G=D[x.unitName],1===x.count?f=G[0]:(f=G[1],m=G[2])):!f&&D&&c.dateTime&&(f=c.dateTime.getXDateFormat(a.x,g.dateTimeLabelFormats));let l=h(n.groupMap?.[r.index].groupStart,a.key),u=l+x?.totalRange-1;y=e.dateFormat(f,l),m&&(y+=e.dateFormat(m,u)),n.chart.styledMode&&(M=this.styledModeFormat(M)),t.text=s(M,{point:p(a.point,{key:y}),series:n},o),t.preventDefault()}}let c={compose:function i(e,a,n){t.compose(e),o.compose(a),n&&g(r,i)&&l(n,"headerFormatter",d)},groupData:o.groupData};return c}),o(i,"masters/modules/datagrouping.src.js",[i["Core/Globals.js"],i["Extensions/DataGrouping/ApproximationDefaults.js"],i["Extensions/DataGrouping/ApproximationRegistry.js"],i["Extensions/DataGrouping/DataGrouping.js"]],function(t,i,o,e){t.dataGrouping={approximationDefaults:i,approximations:o},e.compose(t.Axis,t.Series,t.Tooltip)})});