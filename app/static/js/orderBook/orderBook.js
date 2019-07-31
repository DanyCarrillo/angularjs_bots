/* ***************************************
 * Module: orderBook
 * Plattform: Controlador (Vista Cliente)
 * Framework: Angular
 * Version: 1.x.x
 * Last Date Update: Mayo, 2019
 * ***************************************
 */
botsId = [];
app.config(function ($routeProvider) {
    $routeProvider
        .when('/', {
            templateUrl: '../static/html/orderBook.html',
            controller: 'orderBookController'
        })
}).directive('myPostRepeatDirective', function () {
    return function (scope, element, attrs) {
        botsId[attrs.bot] = parseInt(attrs.repeatDone);
        if (scope.$last) {}
    };
}).controller('orderBookController', ["$scope", "$http", "$q","factory_coins", "factory_endPoints","factory_uri_websocket",
    function ($scope, $http, $q,factory_coins, factory_endPoints,factory_uri_websocket) {

// Promesa captura uri de webSocket del archivo condig.py
factory_uri_websocket.getWebSocket().then(function(socket){
     $scope.$on('LOAD',function(){$scope.loading=true});
    $scope.$on('UNLOAD',function(){$scope.loading=false});

    // BEGIN BLOQUE 1: AVG - Variables Globales:
    showPairUri = factory_endPoints.getEndPoints('showPair');
    showOrderBookByPairUri = factory_endPoints.getEndPoints('selOrderBookByPair');
    selectFormatExchangeUri =  factory_endPoints.getEndPoints("selFormatExchange");


    $scope.ngPair = {};
    $scope.dictPair = {};
    $scope.pairs = [];          // showAllPairs()
    $scope.ngORDERS = [];
    $scope.waiting_orders = false;
    $scope.uriwebsocket='';

    /* Function: showAllPairs
     * Arguments: -
     * Output: $scope.exchange {,,[],,}
     * Method: GET
     * Summary: Lists all Exchange items created by Administrator
     */
    function showAllPairs(){
        $http({
            url:showPairUri,
            method:'GET',
            headers: {
                'Content-Type':'application/json'
            },
        }).then(function(exito) {
            $scope.pairs = [];
            for (var i=0; i<exito.data['data'].length; i++) {
                var exch = exito.data['data'][i];
                var dic = {};
                var items = ['idPair','firstCurrency','secondCurrency','pair','status'];
                for (var j=0; j<items.length; j++) {
                    dic[items[j]] = exch[j];
                }
                //$scope.pairs.push({'pair' : dic});
                $scope.pairs.push(dic);
            }
        },function(error) {
            Notify('Error in show pairs.','warning');   
        })
    }

    /* Function: showAllPairs
     * Arguments: -
     * Output: $scope.exchange {,,[],,}
     * Method: GET
     * Summary: Lists all Exchange items created by Administrator
     */
    function selectUrlOrderBook (){
        $http({
            url: selectFormatExchangeUri,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            data: {
                'idExchange' : 1
            }
        }).then(function(exito) {
            uris = exito.data['data'];
            uris.forEach(function(element){
                $scope.urlOrderBook = (element[3]=='BB') ? element[4] : $scope.urlOrderBook;
            });
        },function(error) {
            Notify('Error in select url order book.','warning');
        })

    }

    /* Autor: dcarrillo
     * Fecha: 17/05/2019
     * Parametro: stringDate="2019-01-28 22:48:01"
     * Descripcion: Resta 5 horas a la fecha ingresada
     */
    function substractFiveHours(stringDate){
        if (stringDate!='--'){
            var b_setDate = new Date(stringDate);
            b_setDate.setHours(b_setDate.getHours()-5);
            var dateTime = moment(b_setDate).format("YYYY-MM-DD HH:mm:ss");
            return dateTime
        }else{
            return stringDate
        }
    }


    /* Function: showAllPairs
     * Arguments: -
     * Output: $scope.exchange {,,[],,}
     * Method: GET
     * Summary: Lists all Exchange items created by Administrator
     */

    $scope.showOrderBookByPair = function (id_pair){
        var dict_pair = null;
        // id de par seleccionado para evento "cancelOrdersBatch"
        $scope.id_pair_global = id_pair;
        $scope.dictPair = {};
        $scope.pairs.forEach(function(element) {
            dict_pair = (element['idPair']==id_pair) ? element : dict_pair;
        })
        $scope.ngORDERS = [];
        $scope.waiting_orders = true;
        $scope.dictPair['firstCurrency'] = dict_pair['firstCurrency'];
        $scope.dictPair['secondCurrency'] = dict_pair['secondCurrency'];
        $http({
            url: showOrderBookByPairUri,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            data: {
                'firstCurrency': dict_pair['firstCurrency'],
                'secondCurrency': dict_pair['secondCurrency']
            }
        }).then(function(exito) {
            if (exito.data.code==200){
                $scope.waiting_orders = false;
                    if (exito.data['data'][0]['buy']){
                        for(i in exito.data['data'][0]['buy']){
                            exito.data['data'][0]['buy'][i]['hora'] = substractFiveHours(exito.data['data'][0]['buy'][i]['hora'])
                        }
                    }
                    if (exito.data['data'][0]['sell']){
                        for (i in exito.data['data'][0]['sell']){
                        exito.data['data'][0]['sell'][i]['hora'] = substractFiveHours(exito.data['data'][0]['sell'][i]['hora'])
                        }
                    }
                $scope.ngORDERS = exito.data['data'][0]
            }else{
                $scope.waiting_orders = false;
                $scope.ngORDERS = {'buy':[],'sell':[]}
                Notify(exito.data.data,'warning');
            }
        },function(error) {
            $scope.waiting_orders = false;
            $scope.ngORDERS = {'buy':[],'sell':[]}
            Notify('Error in show order book.','warning');
        })
    }

    /* Function: Notify (Error/Success)
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: show a message with error in proccess
     */
     function Notify(msg,tipo){
        new PNotify({ 
                        text: msg,
                        hide: true,
                        type: tipo,
                        styling: 'bootstrap3',
                        buttons: {
                            closer: false,
                            sticker: false
                        }
                    });
     }

    // BEGIN BLOQUE 3: AVG - FUNCIONES INI 

    // Funciones al cargar WebPage:();
    showAllPairs();
    selectUrlOrderBook();

    // Conexion con websocket
    var con = io.connect(socket.data.datos)
    con.on('connect',function(){
    });


    // Escuchador de evento "orderCreated"
    con.on('orderCreated',function(event){
        /*
        Descripcion: Captura el evento de orderCreated para mostrar en front
        Nota: BUY emitido se convierte en SELL para mostrar,
              SELL emitido se convierte en BUY para mostrar,
              Hora se convierte a hora peruana.
        */
        if (event.message.firstCurrency == $scope.dictPair['firstCurrency'] && event.message.secondCurrency == $scope.dictPair['secondCurrency']){
            var dataDictbuy = {}
            var dataDictsell = {}
            if(event.message.typeOrder == "BUY"){
                dataDictbuy['amount'] = (event.message.amount);
                dataDictbuy['amount'] = (event.message.amount).toFixed(8);
                dataDictbuy['hora'] = substractFiveHours(event.message.date);
                dataDictbuy['price'] = event.message.price;
                dataDictbuy['pair'] = event.message.firstCurrency+"_"+event.message.secondCurrency;
                dataDictbuy['username'] = event.message.username;
                dataDictbuy['idOrder'] = event.message.idOrder;
                dataDictbuy['flag'] = event.message.flag;
                $scope.ngORDERS.buy.push(dataDictbuy);
            }
            if(event.message.typeOrder == "SELL"){
                dataDictsell['amount'] = (event.message.amount).toFixed(8);
                dataDictsell['hora'] = substractFiveHours(event.message.date);
                dataDictsell['price'] = event.message.price;
                dataDictsell['pair'] = event.message.firstCurrency+"_"+event.message.secondCurrency;
                dataDictsell['username'] = event.message.username;
                dataDictsell['idOrder'] = event.message.idOrder;
                dataDictsell['flag'] = event.message.flag;
                $scope.ngORDERS.sell.push(dataDictsell);
            }
            
            $scope.$apply(function(){ // Escuchador de cambios

            });
            
        }
     
        });

    // Escucador de evento "mapping"
    con.on('mapping',function(event){
        /*
        Descripcion: captura evento mapping
        Nota: Si status es FI se elimina orden de la tabla
              Si status es PA se resta el amount 

        */
        if (event.message.firstCurrency == $scope.dictPair['firstCurrency'] && event.message.secondCurrency == $scope.dictPair['secondCurrency']){
            var dataDictbuy = {}
            var dataDictsell = {}
            if (event.message.status == "FI"){
                if(event.message.type == "BUY"){
                    for(i in $scope.ngORDERS.buy){
                        if (event.message.idOrder == $scope.ngORDERS.buy[i]['idOrder']){
                            $scope.$apply(function(){ // Escuchador de cambios
                                $scope.ngORDERS.buy.splice(i,1);
                            });
                        }
                    }
                }
                if(event.message.type == "SELL"){
                    for(i in $scope.ngORDERS.sell){
                        if (event.message.idOrder == $scope.ngORDERS.sell[i]['idOrder']){
                            $scope.$apply(function(){ // Escuchador de cambios
                                $scope.ngORDERS.sell.splice(i,1);
                            });
                        }
                    }
                }
            }

            if (event.message.status == "PA"){
                if(event.message.type == "BUY"){
                    for(i in $scope.ngORDERS.buy){
                        if (event.message.idOrder == $scope.ngORDERS.buy[i]['idOrder']){
                            $scope.$apply(function(){ // Escuchador de cambios
                                $scope.ngORDERS.buy.splice(i,1,
                                    {
                                        'amount':parseFloat($scope.ngORDERS.buy[i]['amount'] - event.message.amount).toFixed(8),
                                        'hora':substractFiveHours(event.message.datetime),
                                        'price':event.message.priceOrder,
                                        'pair':event.message.firstCurrency+"_"+event.message.secondCurrency,
                                        'username':event.message.username,
                                        'idOrder':event.message.idOrder,
                                        'flag':$scope.ngORDERS.buy[i]['flag']
                                });
                            });
                            
                        }
                    }
                }
                if(event.message.type == "SELL"){
                    for(i in $scope.ngORDERS.sell){
                        if (event.message.idOrder == $scope.ngORDERS.sell[i]['idOrder']){
                            $scope.$apply(function(){ // Escuchador de cambios
                                $scope.ngORDERS.sell.splice(i,1,
                                    {
                                        'amount':parseFloat($scope.ngORDERS.sell[i]['amount'] - event.message.amount).toFixed(8),
                                        'hora':substractFiveHours(event.message.datetime),
                                        'price':event.message.priceOrder,
                                        'pair':event.message.firstCurrency+"_"+event.message.secondCurrency,
                                        'username':event.message.username,
                                        'idOrder':event.message.idOrder,
                                        'flag':$scope.ngORDERS.sell[i]['flag']
                                });
                            });
                        }
                    }
                }
            }
        }
                });

    // Escuchador de evento "cancelOrder"
    con.on('cancelOrder',function(event){
        /*
        Descripcion: Captura evento cancelOrder, si oden cancelada existe en la tabla lo elimina de la tabla
        */
        if (event.message.firstCurrency == $scope.dictPair['firstCurrency'] && event.message.secondCurrency == $scope.dictPair['secondCurrency']){
            var dataDictbuy = {}
            var dataDictsell = {}
            if(event.message.typeOrder == "BUY"){
                for(i in $scope.ngORDERS.buy){
                    if (event.message.idOrder == $scope.ngORDERS.buy[i]['idOrder']){
                        $scope.$apply(function(){ // Escuchador de cambios
                            $scope.ngORDERS.buy.splice(i,1);
                         });
                    }
                }
            }
            if(event.message.typeOrder == "SELL"){
                for(i in $scope.ngORDERS.sell){
                    if (event.message.idOrder == $scope.ngORDERS.sell[i]['idOrder']){
                        $scope.$apply(function(){ // Escuchador de cambios
                            $scope.ngORDERS.sell.splice(i,1);
                        });
                    }
                }

            }
        }
                });

    // Escuchador de evento "cancelOrdersBatch"
    con.on('cancelOrdersBatch',function(event){
        /*
        Descripcion: Refresca la data del par seleccionado
        */
        $scope.showOrderBookByPair($scope.id_pair_global);
        });


});

}]);

angular.element(function () {
    angular.bootstrap(document, ['coreModule']);
});