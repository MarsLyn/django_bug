/**
 * Highstock JS v11.3.0 (2024-01-10)
 *
 * Indicator series type for Highcharts Stock
 *
 * (c) 2010-2024 Daniel Studencki
 *
 * License: www.highcharts.com/license
 */!function(t){"object"==typeof module&&module.exports?(t.default=t,module.exports=t):"function"==typeof define&&define.amd?define("highcharts/indicators/keltner-channels",["highcharts","highcharts/modules/stock"],function(e){return t(e),t.Highcharts=e,t}):t("undefined"!=typeof Highcharts?Highcharts:void 0)}(function(t){"use strict";var e=t?t._modules:{};function o(t,e,o,i){t.hasOwnProperty(e)||(t[e]=i.apply(null,o),"function"==typeof CustomEvent&&window.dispatchEvent(new CustomEvent("HighchartsModuleLoaded",{detail:{path:e,module:t[e]}})))}o(e,"Stock/Indicators/MultipleLinesComposition.js",[e["Core/Series/SeriesRegistry.js"],e["Core/Utilities.js"]],function(t,e){var o,i=t.seriesTypes.sma.prototype,n=e.defined,r=e.error,s=e.merge;return function(t){var e=["bottomLine"],o=["top","bottom"],a=["top"];function p(t){return"plot"+t.charAt(0).toUpperCase()+t.slice(1)}function l(t,e){var o=[];return(t.pointArrayMap||[]).forEach(function(t){t!==e&&o.push(p(t))}),o}function h(){var t,e=this,o=e.pointValKey,a=e.linesApiNames,h=e.areaLinesNames,c=e.points,u=e.options,d=e.graph,f={options:{gapSize:u.gapSize}},y=[],m=l(e,o),g=c.length;if(m.forEach(function(e,o){for(y[o]=[];g--;)t=c[g],y[o].push({x:t.x,plotX:t.plotX,plotY:t[e],isNull:!n(t[e])});g=c.length}),e.userOptions.fillColor&&h.length){var v=y[m.indexOf(p(h[0]))],C=1===h.length?c:y[m.indexOf(p(h[1]))],A=e.color;e.points=C,e.nextPoints=v,e.color=e.userOptions.fillColor,e.options=s(c,f),e.graph=e.area,e.fillGraph=!0,i.drawGraph.call(e),e.area=e.graph,delete e.nextPoints,delete e.fillGraph,e.color=A}a.forEach(function(t,o){y[o]?(e.points=y[o],u[t]?e.options=s(u[t].styles,f):r('Error: "There is no '+t+' in DOCS options declared. Check if linesApiNames are consistent with your DOCS line names."'),e.graph=e["graph"+t],i.drawGraph.call(e),e["graph"+t]=e.graph):r('Error: "'+t+" doesn't have equivalent in pointArrayMap. To many elements in linesApiNames relative to pointArrayMap.\"")}),e.points=c,e.options=u,e.graph=d,i.drawGraph.call(e)}function c(t){var e,o=[],n=[];if(t=t||this.points,this.fillGraph&&this.nextPoints){if((e=i.getGraphPath.call(this,this.nextPoints))&&e.length){e[0][0]="L",o=i.getGraphPath.call(this,t),n=e.slice(0,o.length);for(var r=n.length-1;r>=0;r--)o.push(n[r])}}else o=i.getGraphPath.apply(this,arguments);return o}function u(t){var e=[];return(this.pointArrayMap||[]).forEach(function(o){e.push(t[o])}),e}function d(){var t,e=this,o=this.pointArrayMap,n=[];n=l(this),i.translate.apply(this,arguments),this.points.forEach(function(i){o.forEach(function(o,r){t=i[o],e.dataModify&&(t=e.dataModify.modifyValue(t)),null!==t&&(i[n[r]]=e.yAxis.toPixels(t,!0))})})}t.compose=function(t){var i=t.prototype;return i.linesApiNames=i.linesApiNames||e.slice(),i.pointArrayMap=i.pointArrayMap||o.slice(),i.pointValKey=i.pointValKey||"top",i.areaLinesNames=i.areaLinesNames||a.slice(),i.drawGraph=h,i.getGraphPath=c,i.toYData=u,i.translate=d,t}}(o||(o={})),o}),o(e,"Stock/Indicators/KeltnerChannels/KeltnerChannelsIndicator.js",[e["Stock/Indicators/MultipleLinesComposition.js"],e["Core/Series/SeriesRegistry.js"],e["Core/Utilities.js"]],function(t,e,o){var i,n=this&&this.__extends||(i=function(t,e){return(i=Object.setPrototypeOf||({__proto__:[]})instanceof Array&&function(t,e){t.__proto__=e}||function(t,e){for(var o in e)Object.prototype.hasOwnProperty.call(e,o)&&(t[o]=e[o])})(t,e)},function(t,e){if("function"!=typeof e&&null!==e)throw TypeError("Class extends value "+String(e)+" is not a constructor or null");function o(){this.constructor=t}i(t,e),t.prototype=null===e?Object.create(e):(o.prototype=e.prototype,new o)}),r=e.seriesTypes.sma,s=o.correctFloat,a=o.extend,p=o.merge,l=function(t){function o(){return null!==t&&t.apply(this,arguments)||this}return n(o,t),o.prototype.init=function(){e.seriesTypes.sma.prototype.init.apply(this,arguments),this.options=p({topLine:{styles:{lineColor:this.color}},bottomLine:{styles:{lineColor:this.color}}},this.options)},o.prototype.getValues=function(t,o){var i,n,r,a,p,l,h,c=o.period,u=o.periodATR,d=o.multiplierATR,f=o.index,y=t.yData,m=y?y.length:0,g=[],v=e.seriesTypes.ema.prototype.getValues(t,{period:c,index:f}),C=e.seriesTypes.atr.prototype.getValues(t,{period:u}),A=[],x=[];if(!(m<c)){for(h=c;h<=m;h++)p=v.values[h-c],l=C.values[h-u],a=p[0],n=s(p[1]+d*l[1]),r=s(p[1]-d*l[1]),i=p[1],g.push([a,n,i,r]),A.push(a),x.push([n,i,r]);return{values:g,xData:A,yData:x}}},o.defaultOptions=p(r.defaultOptions,{params:{index:0,period:20,periodATR:10,multiplierATR:2},bottomLine:{styles:{lineWidth:1,lineColor:void 0}},topLine:{styles:{lineWidth:1,lineColor:void 0}},tooltip:{pointFormat:'<span style="color:{point.color}">●</span><b> {series.name}</b><br/>Upper Channel: {point.top}<br/>EMA({series.options.params.period}): {point.middle}<br/>Lower Channel: {point.bottom}<br/>'},marker:{enabled:!1},dataGrouping:{approximation:"averages"},lineWidth:1}),o}(r);return a(l.prototype,{nameBase:"Keltner Channels",areaLinesNames:["top","bottom"],nameComponents:["period","periodATR","multiplierATR"],linesApiNames:["topLine","bottomLine"],pointArrayMap:["top","middle","bottom"],pointValKey:"middle"}),t.compose(l),e.registerSeriesType("keltnerchannels",l),l}),o(e,"masters/indicators/keltner-channels.src.js",[],function(){})});