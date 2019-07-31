/* ***************************************
 * Module: Exchanges
 * Plattform: Controlador (Vista Cliente)
 * Framework: Angular
 * Version: 1.x.x
 * Last Date Update: August, 03 2018
 * ***************************************
 */
botsId = [];
app.config(function ($routeProvider) {
    $routeProvider
        .when('/', {
            templateUrl: '../static/html/orders.html',
            controller: 'ordersController'
        })
}).directive('myPostRepeatDirective', function () {
    return function (scope, element, attrs) {
        botsId[attrs.bot] = parseInt(attrs.repeatDone);
        if (scope.$last) {}
    };
}).controller('ordersController', ["$scope", "$http", "$q","factory_coins", "factory_endPoints",
    function ($scope, $http, $q,factory_coins, factory_endPoints) {

     $scope.$on('LOAD',function(){$scope.loading=true});
    $scope.$on('UNLOAD',function(){$scope.loading=false});

    // Rutas HTTP (app.js):
    getAllOrdersUri = factory_endPoints.getEndPoints("getAllOrdersUri");
    selUsersExchangeUri = factory_endPoints.getEndPoints('selUsersExchange');
    selExchangeUri = factory_endPoints.getEndPoints('selExchange');
    verifyExchangeBitinkaUri = factory_endPoints.getEndPoints('verifyExchangeBitinka');
    showPairUri = factory_endPoints.getEndPoints('showPair');
    sendOrdersToCancelUri = factory_endPoints.getEndPoints("sendOrdersToCancel");

    // Variables Globales:
    $scope.cabeceras = ['#','idOrder','Type','Price','Amount','Total','Status','Datetime','Check'];
    $scope.usersExchange = [];
    $scope.pairs = [];
    $scope.orders = [];
    $scope.waiting_orders = false;
    $scope.data_orders = false;
    $scope.canceler = $q.defer();
    $scope.time_orders = '';

    // Funciones:

    /* Function: findExchangeBitinka
     * Arguments: -
     * Output: $scope.exchange {,,[],,}
     * Method: GET
     * Summary: Verify if exchange Bitinka exists and prevent if it not exists
     */
    function findExchangeBitinka(){
        $http({
            url: verifyExchangeBitinkaUri,
            method:'GET',
            headers: {
                'Content-Type':'application/json'
            }
        }).then(function(exito) {
            $scope.ID_BITINKA = exito.data['data'];
            selExchangeBitinka($scope.ID_BITINKA);
        },function(error) {
            NotifyFailConnection();
        })
    }

    /* Function: selExchangeBitinka
     * Arguments: -
     * Output: $scope.exchange {,,[],,}
     * Method: GET
     * Summary: Lists data Exchange items according by idExchange from ngPriceMarket - pair selected
     */
    function selExchangeBitinka(id_bitinka){
        $http({
            url:selExchangeUri,
            method:'POST',
            headers: {
                'Content-Type':'application/json'
            },
            data: {'idExchange':id_bitinka}
        }).then(function(exito) {
            var exch = exito.data['data'];
            var items = ['idExchange','name','type','status','priority'];
            dic = {};
            for (var i=0; i<items.length; i++) {
                dic[items[i]] = exch[i];
            }
            $scope.exchange = {'general' : dic};
            $scope.ngExchange = $scope.exchange;
            showAllUsersByExchange(exito.data['data'][0]);
            showAllPairs();
        },function(error) {
            Notify('Error in find Exchange Bitinka by default.','warning'); 
        })
    }

    /* Function: showAllUsersByExchange 
     * Arguments: idExchange
     * Output: -
     * Method: GET
     * Summary: Lists all Exchange items created by Administrator
     */
     function showAllUsersByExchange(id_exchange){
        $http({
            url: selUsersExchangeUri,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            data: {'idExchange':id_exchange}
        })
        .then(function (exito) {
            $scope.usersExchange = [];
            var items = ['idUser','idExchange','username','credentials','status'];
            for (var i=0;i<exito.data['data'].length;i++) {
                var dic = {};
                for (var j=0; j<items.length; j++) dic[items[j]] = exito.data['data'][i][j+1];
                $scope.usersExchange.push(dic);
            }
        }, function (error) {
            Notify('Error in show users by exchange.','warning'); 
        })
     }

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
                $scope.pairs.push(dic);
            }
        },function(error) {
            Notify('Error in show pairs.','warning');   
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

     /* Function: NotifyFailConnection (Error/Success)
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: show a message with error in proccess
     */
     function NotifyFailConnection() {
        var form = ('<div class="failConnMysql">'
                    +   '<center>'
                    +       'There was a connection error!<br>'
                    +       'Please Refresh the web page!'
                    +   '</center>'
                    +'</div>'
                    +'<br>'
                    );
        var stack_center = {
                            "dir1": "down", 
                            "dir2": "right", 
                            "firstpos1": ($(window).height() / 2) - 100, 
                            "firstpos2": ($(window).width() / 2) - (Number(PNotify.prototype.options.width.replace(/\D/g, '')) / 2)
                            };
        tooltip = new PNotify({
            title: '<br><center><label>Error Connection</label></div>',
            text: form,
            icon: 'fa fa-question',
            hide: false,
            type: 'success',
            addclass: 'customWeb pnotify-center',
            styling: 'bootstrap3',
            confirm: {
                confirm: true,
                buttons: [{text: 'Accept', addClass: 'btn btn-success btn-md'},
                          {text: 'Cancel', addClass: 'btn btn-danger btn-md hide'}]
            },
            buttons: {
                closer: false,
                sticker: false
            },
            history: {
                history: false
            },
            stack: stack_center,
            animate_speed: "fast",
            opacity: .5,
            icon: "fa fa-calculator",
            auto_display: false
        });

        tooltip.open();

        tooltip.get().on('pnotify.confirm',function(){
            window.location.reload(true); 
        });
     }

     /* Function: NotifyFailConnection (Error/Success)
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: show a message with error in proccess
     */
     $scope.showOrdersByUserYPair = function(id_username_exchange, id_pair, id_bot_type) {
        if(id_username_exchange==null){
            Notify('Please choose user exchange.','success'); 
        } else {
            if(id_pair==null){
                Notify('Please choose pair.','success'); 
            } else {
                $scope.waiting_orders = true;

                var username_exchange = "";
                $scope.usersExchange.forEach(function(element){
                    username_exchange = (element.idUser==id_username_exchange)? element.username:username_exchange;
                });

                var pair = "";
                $scope.pairs.forEach(function(element){
                    pair = (element.idPair==id_pair)? element.pair:pair;
                });

                var post_order = {'usernameExchange':username_exchange,
                                  'pair':pair,
                                  'idBotType':id_bot_type,
                                  'tipo':1};

                if($http.pendingRequests.length<=0){
                    $http({
                            url: getAllOrdersUri,
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            data: post_order,
                            timeout: $scope.canceler.promise
                        })
                        .then(function (exito) {
                            distributionOrders(exito.data);
                        }, function (error) {
                            var r = $scope.canceler.promise.$$state['status'];
                            if(r==1){
                                Notify('Error in show History of Active Orders.','warning'); 
                            }
                        })        
                } else {
                    $scope.canceler.resolve();
                    var r_1 = $scope.canceler.promise.$$state['status'];
                    $scope.canceler = $q.defer();
                    var r_2 = $scope.canceler.promise.$$state['status'];
                    $http({
                            url: getAllOrdersUri,
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            data: post_order,
                            timeout: $scope.canceler.promise
                        })
                        .then(function (exito) {
                            distributionOrders(exito.data);
                        }, function (error) {
                            if(r_1==r_2){
                                Notify('Error in show History of Active Orders.','warning'); 
                            }
                        })        
                }

            }
        }
     }

     /* Function: distributionOrders
     * Arguments: 0 (todos) / 1 (solo los mios)
     * Output: $scope.orders {,,[],,}
     * Method: 
     * Summary: Lists all Exchange items created by Administrator
     */
     function distributionOrders(vec_orders){
        var resp = vec_orders;
        $scope.orders = [];
        $scope.orders_all = [];
        if(resp['code']==201){
            resp['data']['history'].forEach(function(h){
                if(h['order_id']!=null){
                    var order = h;
                    $scope.orders.push(order);
                    $scope.orders_all.push(order);
                }
            });
        }
        $scope.waiting_orders = false;
        $scope.data_orders = ($scope.orders.length>0)?true:false;
     }

     /* Function: check_decheck_all
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: checking all checkbox
     */
    $scope.check_decheck_all = function() {
        var checks = document.getElementsByClassName("check_orders");
        if(event.target.checked==true){
            for(var i=0;i<checks.length;i++){
                checks[i].checked = true;
            }
        } else {
            for(var i=0;i<checks.length;i++){
                checks[i].checked = false;
            }
        }
    }

    /* Function: cancelOrders 
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: send to cancel orders
     */
     $scope.cancelOrders = function() {
        var usernameExchange = '';
        $scope.usersExchange.forEach(function(element){
          usernameExchange = (element.idUser==$scope.ngUsernameExchange)? element.username : usernameExchange;
        });

        var select_orders = $('.check_orders:checked');
        var active_orders = [];
        for(i=0;i<select_orders.length;i++){
            var aux = ((select_orders[i].id).replace("check_order_",""));
            active_orders.push(parseInt(aux));   
        }

        var pair = "";
        $scope.pairs.forEach(function(element){
          pair = (element.idPair==$scope.ngPairExchange)? element.pair:pair;
        });

        if (active_orders.length == 0) {
            Notify('Checkbox can\'t be empty.','warning');
        } else {
            $http({
                url: sendOrdersToCancelUri,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                data: {
                        "idOrders": active_orders,
                        "usernameExchange":usernameExchange,
                        "pair":pair
                      }
            })
            .then(function (exito) {
                (exito.data['code']==200) ? Notify('Orders cancelled successfully.','success') : Notify('Error in send cancel order request.','warning'); 
                $scope.showOrdersByUserYPair($scope.ngUsernameExchange, $scope.ngPairExchange, 'D');
            }, function (error) {
                Notify('Error in send cancel order request.','warning'); 
            })
        }
    }

    /* Function: filtroTiempos
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: 
     */
    $scope.filtroTiempos = function(tiempo_ordenes){
        var datetime_now = new Date().toISOString();
        var aux = [];
        $scope.orders_all.forEach(function(element){
            var m1 = (moment(element.datetime, 'YYYY-MM-DD HH:mm:ss'));  
            var m2 = (moment(moment().format(), 'YYYY-MM-DD HH:mm:ss'));                 
            var milisegundos = m2.diff(m1);
            var segundos = milisegundos/1000;
            (segundos>=tiempo_ordenes) ? aux.push(element) : 0;
        });
        $scope.orders = aux;
    }


     // Al cargar el documento inicial:
     findExchangeBitinka();
     

}]);

angular.element(function () {
    angular.bootstrap(document, ['coreModule']);
});