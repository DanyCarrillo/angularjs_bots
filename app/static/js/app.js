var app = angular.module('coreModule', ['ngRoute',"ui.bootstrap"])
app.value('routes',{
        "apisIP": location.protocol + "//" + location.hostname,
        "portApi": location.port,
        "socketIP": "ws://127.0.0.1",
        "socketPort": "9095",
        "endPoints": {
            "user": "/user",
            "botConfig": "/botConfig",
            "getPrice": "/getPricesCripFiat",
            "apiUser": "/exchanges",
            "listPlayBot": "/modPlay/obtListPlayBot",
            "webSocket": "/ws",
            "trading":"/trading" ,
            "coins": "/modCoins/coins",
            "countryCripto": '/packagesCoins/getCountryCriptocoins',
            "getPackages": "/packagesCoins/getPackages",
            "getTransaction": "/getTransaction",
            "packagesCoins": "/packagesCoins",
            "blockUser": "/modUser/suspend",
            "login": "/modUser/login",
            "country": "/modCountrys/country",
            "loadLinks": "/loadLinks",
            "delLink": "/delLink",
            "updLinks": "/modCoins/updLinks",
            "home":"/home",
            "getPairs": "/modPairs/getPairslist",
            "botPlay": "/modPlays/play",
            "botStop": "/modPlays/stop",
            "getTypesBot": "/modBots/getTypesBot",
            "getPricesExchange": "/getPriceLink",
            "getMarketPrice": "/getMarketPrice",
            "getTypesTrading": "/getTypesTrading",
            "getFormatNames": "/exchanges/getFormatNamesExchange",
            "addExchange" : "/exchange/add",
            "updExchange" : "/exchange/upd",
            "delExchange" : "/exchange/del",
            "selExchange" : "/exchange/sel",
            "showExchange" : "/exchange/show",
            "viewAllExchange" : "/exchange/all/view",
            "showPair" : "/pair/show",
            "showBotType" : "/bot/type/show",
            "showTradingType" : "/trading/type/show",
            "showBot" : "/bot/show",
            "selMarketPricesExchange":"/trading/exchange/marketprices",
            "addExchangeUserApilink" : "/exchange/users/apilinks/add",
            "updExchangeUserApilink" : "/exchange/users/apilinks/upd",
            "showFormat": "/exchange/format/show",
            "selUsersExchange":"/exchange/user/sel",
            "selPairsUserExchange":"/exchange/user/pair/sel",
            "addBot":"/bot/add",
            "updBot":"/bot/upd",
            "delBot":"/bot/del",
            "addPlay" : "/bot/play/add",
            "updPlay" : "/bot/play/upd",
            "showPlay": "/bot/play/show",
            "showBotYPlay" : "/botYplay/show",
            "getApiResponse": "/modCoins/getApiResponse",
            "verifyExchangeBitinka": "/exchange/verify/bitinka",
            "verifyTypesBotAndTrading":"/bot/verify/bottypeYtradingtype",
            "getIdUserByUsername":"/user/sel/id",
            "getTickers":"/ticker",
            "getUserLogs":"/logUser",
            "getListPairs": "/pairs",
            "blockPair": "/pairs/modPair",
            "getHistorialOrders": "/trading/orders/active/bot",
            "sendOrdersToCancel": "/trading/orders/cancel",
            "getVolumen":"/ticker/volum/merketcap",
            "getAllOrdersUri":"/orders/active/bot",
            "selPair":"/pair/selpornombre",
            "selFormatExchange": "/exchange/format/sel",
            "selOrderBookByPair":"/orderBook/pair/sel",
            "serPairTypeCoins":"/pairs/seltype",
            "uriwebsocket":"/uriWebsocket"
        }
    }
);
app.factory("factory_coins", function($http, factory_endPoints){
    apiGetCoins = factory_endPoints.getEndPoints('coins');
    return {
        getAllCoins: function(){
            var responseHttp = $http({
                url:apiGetCoins + '/A',
                method: 'GET',
            }).then(function (response){
                return response.data.datos;
            }, function(error){
                new PNotify({ text: error.data.mensaje, type: 'error', hide: true, styling: 'bootstrap3'});
            });
            return responseHttp;
        },
    }
});

// Factory
app.factory("factory_uri_websocket", function($http, factory_endPoints){
    apiWebSocket = factory_endPoints.getEndPoints('uriwebsocket');
    return {
        getWebSocket: function(){
            var responseHttp = $http({
                url:apiWebSocket,
                method: 'GET',
            }).then(function (response){
                return response
            }, function(error){
                new PNotify({ text: 'Error in uri websocket', type: 'error', hide: true, styling: 'bootstrap3'});
            });
            return responseHttp;
        },
    }
});

app.factory("factory_endPoints", function(routes){
    return {
        getEndPoints: function(name){
            return routes.apisIP+':'+routes.portApi+routes.endPoints[name];
        },
        getUrlWS: function(){
            return routes.socketIP + ':' + routes.socketPort + routes.endPoints.webSocket
        }
    }
});

