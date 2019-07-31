/* ***************************************
 * Module: Tickers
 * Plattform: Controlador (Vista Cliente)
 * Framework: Angular
 * Version: 1.x.x
 * Last Date Update: 2018
 * ***************************************
 */
app.config(function ($routeProvider) {
    $routeProvider
    .when('/', {
        templateUrl: '../static/html/tickersListar.html',
        controller: 'tickerController'
    })
})

app.controller('tickerController', ["$scope", "$http", "factory_endPoints","factory_uri_websocket",function ($scope, $http, factory_endPoints,factory_uri_websocket) {//"$websocket", 


// Promesa  capturar uri de websocket del archivo config.py
factory_uri_websocket.getWebSocket().then(function(socket){

    all_Tickers = factory_endPoints.getEndPoints('getTickers');
    api_volumenCoinMarketcap=factory_endPoints.getEndPoints('getVolumen');
    //spinner
    $scope.$on('LOAD',function(){$scope.loading=true});
    $scope.$on('UNLOAD',function(){$scope.loading=false});

    //variables globales
    $scope.tickers = [];
    $scope.ticker_s = [];
    $scope.indice;
    var indice;

    //Conexion con websocket de viene del archivo config.py
    var con = io.connect(socket.data.datos)
    //
    con.on('connect',function(){
    });

    function allTickers(){
        //$scope.$emit('LOAD');
    	$http({
    		url:all_Tickers,
    		method:'GET',
    		headers:{
    			'Content-Type': 'application/json'
    		}
    	}).then(function(exito){
            $scope.$emit('UNLOAD');
                   for (i in exito.data['datos']) {
                    for(x in exito.data['datos'][i] ){
                        var dict={}
                        dict['ask'] = exito.data['datos'][i][x].ask;
                        dict['bid']=exito.data['datos'][i][x].bid;
                        dict['lastPrice']=exito.data['datos'][i][x].lastPrice;
                        dict['symbol']=exito.data['datos'][i][x].symbol.replace("_","/");
                        dict['volumen24hours']=exito.data['datos'][i][x].volumen24hours;
                    $scope.tickers.push(dict);
                   }
                } 
                
    	}, function (error){
    	    new PNotify({
                text: "Something is wrong getting this tickers information, please try again.",
                type: 'warning',
                hide: true,
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                },
            });
    })
    }

    function volumenCoinMarketcap(){
        //$scope.$emit('LOAD');
        $http({
            url:api_volumenCoinMarketcap,
            method:'GET',
            headers:{
                'Content-Type': 'application/json'
            }
        }).then(function(exito){
            if(exito.status==200){
                $scope.volumen=exito.data;
            }
        }, function (error){
          /*  new PNotify({
                text: "Something is wrong getting this volume information.",
                type: 'warning',
                hide: true,
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                },
            });*/
    })
    }

    allTickers();
    volumenCoinMarketcap(); 

    // Escuchador del evento "ticker"
    con.on('ticker',function(event){
        var pares_event=event['message'][0]['firstCurrency']+"/"+event['message'][0]['secondCurrency'];

                    var dict={}
                    for(i in $scope.tickers){
                        if(pares_event==$scope.tickers[i]['symbol']){
                            $scope.confirmaction=i;
                            
                            $scope.$apply(function(){ //revisa si hay cambio para mostrar en frond
                                $("."+i).fadeOut("fast");
                                $scope.tickers.splice(i,1,{
                                    'ask':event['message'][0]['priceSell'],
                                    'bid':event['message'][0]['priceBuy'],
                                    'lastPrice':event['message'][0]['lastPrice'],
                                    'symbol':pares_event,
                                    'volumen24hours':event['message'][0]['amount']
                                });
                                $("."+i).fadeIn(500);
                        });
                    }
                    }
                    volumenCoinMarketcap();
                });
});

}]);



angular.element(function () {
    angular.bootstrap(document, ['coreModule']);
});