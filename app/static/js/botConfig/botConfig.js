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
            templateUrl: '../static/html/botConfListar.html',
            controller: 'botConfigController'
        })
}).directive('myPostRepeatDirective', function () {
    return function (scope, element, attrs) {
        botsId[attrs.bot] = parseInt(attrs.repeatDone);
        if (scope.$last) {}
    };
}).controller('botConfigController', ["$scope", "$http", "$q","factory_coins", "factory_endPoints",
    function ($scope, $http, $q,factory_coins, factory_endPoints) {

     $scope.$on('LOAD',function(){$scope.loading=true});
    $scope.$on('UNLOAD',function(){$scope.loading=false});

    apiBotConfig = factory_endPoints.getEndPoints('botConfig');
    apiGetPrice = factory_endPoints.getEndPoints('getPrice'); 
    apiApiUser = factory_endPoints.getEndPoints('apiUser');
    urlWebSocket = factory_endPoints.getUrlWS();
    apiTrading = factory_endPoints.getEndPoints('trading');
    listPlayBot = factory_endPoints.getEndPoints('listPlayBot');
    botPlay = factory_endPoints.getEndPoints('botPlay');
    botStop = factory_endPoints.getEndPoints('botStop');
    getTypesBot = factory_endPoints.getEndPoints('getTypesBot');
    getPricesExchange = factory_endPoints.getEndPoints('getPricesExchange');
    getMarketPrice = factory_endPoints.getEndPoints('getMarketPrice');
    getTypesTrading = factory_endPoints.getEndPoints('getTypesTrading');
    selPairPorNombre = factory_endPoints.getEndPoints('selPair');
    selPairTypeCoins = factory_endPoints.getEndPoints('serPairTypeCoins');

    $scope.timeIds = {};
    $scope.bots = [];
    $scope.listarActiveOrder = [];
    $scope.botsO = [];
    $scope.config = {};
    $scope.botsId = [];
    $scope.current = 1;
    $scope.totalresult = 8;
    $scope.waiting_modal=false;
    $scope.pricesBtc = true;
    $scope.switchStatus = false;
    $scope.switchVerTodo = false;
    $scope.idsBots = [];
    $scope.dataFiltros = [];

    // BEGIN BLOQUE 1: AVG - Variables Globales:
    selExchangeUri = factory_endPoints.getEndPoints('selExchange');
    showPairUri = factory_endPoints.getEndPoints('showPair');
    showBotTypesUri = factory_endPoints.getEndPoints('showBotType');
    showTradingTypesUri = factory_endPoints.getEndPoints('showTradingType');
    selMarketPricesExchangeUri = factory_endPoints.getEndPoints('selMarketPricesExchange');
    selUsersExchangeUri = factory_endPoints.getEndPoints('selUsersExchange');
    showBotYPlayUri = factory_endPoints.getEndPoints('showBotYPlay'); 
    addBotUri = factory_endPoints.getEndPoints('addBot');    
    updBotUri = factory_endPoints.getEndPoints('updBot');     
    delBotUri = factory_endPoints.getEndPoints('delBot');
    addPlayUri = factory_endPoints.getEndPoints('addPlay');
    updPlayUri = factory_endPoints.getEndPoints('updPlay');
    verifyExchangeBitinkaUri = factory_endPoints.getEndPoints('verifyExchangeBitinka');
    verifyTypesBotAndTradingUri = factory_endPoints.getEndPoints("verifyTypesBotAndTrading");
    getIdUserByUsernameUri = factory_endPoints.getEndPoints("getIdUserByUsername");
    getHistorialOrdersUri = factory_endPoints.getEndPoints("getHistorialOrders");
    sendOrdersToCancelUri = factory_endPoints.getEndPoints("sendOrdersToCancel");
    
    $scope.ID_BITINKA = null;
    $scope.idUser = localStorage.getItem("idUserSession");
    $scope.usernameByExchange = '';
    $scope.cabeceraTabla_1 = ['#','Username','Pairs'];
    $scope.cabeceraTabla_2 = ['Min / Max','Order Type','Exec. Time, %Buy & %Sell','Play / Stop','Cycle','Active Orders','Options'];

    $scope.ngExchange = {};     
    $scope.ngPair = {}     
    $scope.ngPriceMarket = {};     
    $scope.ngBot = {};
    $scope.ngPlay = {};     
    $scope.ngTiempo = {};

    $scope.exchanges = [];      // showAllExchanges()
    $scope.users = [];          // showAllUsersByExchange()
    $scope.pairs = [];          // showAllPairs()
    $scope.bottypes = [];       // showAllBotTypes()
    $scope.tradingtypes = [];   // showAllTradingTypes()
    $scope.bots = [];           // showAllBot()
    $scope.botsplays = [];      // showAllBotPlay()
    $scope.bots_filtrados = [];
    $scope.canceler = $q.defer();
    $scope.stateBots = '';
    $scope.botType = '';
    $scope.headerOrder = '';
    $scope.headOrders = [{'value':'#','width':'40px'},{'value':'idOrder','width':'90px'},{'value':'Pair','width':'70px'},{'value':'Type','width':'70px'},{'value':'Price','width':'95px'},{'value':'Amount','width':'100px'},{'value':'Total','width':'105px'},{'value':'Status','width':'85px'},{'value':'Datetime','width':'130px'},{'value':'Check','width':'20px'}];
    $scope.order_reverse = {'#':false,'idOrder':false,'Pair':false,'Type':false,'Price':false,'Amount':false,'Total':false,'Status':false,'Datetime':false,'Check':false};
    $scope.order_reverse_flag = false;
    $scope.inac_pagIzq = true;
    $scope.inac_pagDer = false;
    $scope.current_type_coins = "";
    $scope.PairByBot = '';

    $scope.minutos = [];
    $scope.segundos = [];
    $scope.waiting = true;
    $scope.waiting_play = [];
    $scope.waiting_cycle = [];
    $scope.waiting_editar = [];
    $scope.waiting_bots = true;
    $scope.styleWeb = {"background-color":'#2A3F54'};
    $scope.styleTextWeb = {"color":'#2A3F54'};
    $scope.bgInvalid = '#FCD6D6';
    $scope.bgValid = '#F7FCEE';
    $scope.paginas_bots = 0;
    $scope.bots_all = [];
    // END BLOQUE 1: AVG - Variables Globales:


    // BEGIN BLOQUE 2: AVG - FUNCIONES 

    /* Function: showAllBot
     * Arguments: 0 (todos) / 1 (solo los mios)
     * Output: $scope.exchange {,,[],,}
     * Method: GET
     * Summary: Lists all Exchange items created by Administrator
     */
    function showAllBotYPlay(tipo,status_bot,status_play,username_exchange, page){
        $scope.waiting_bots = true;
        id_user = (tipo==0)?0:parseInt($scope.idUser);
        if($http.pendingRequests.length<=0){
            $http({
                url:showBotYPlayUri,
                method:'POST',
                headers: {
                    'Content-Type':'application/json'
                },
                data: {
                        'idUser': id_user,
                        'statusBot': status_bot,
                        'statusPlay' : status_play,
                        'exchangeUsername' : username_exchange,
                        'start':page
                      },
                timeout: $scope.canceler.promise
            }).then(function(exito) {
                distributionBots(exito.data);
            },function(error) {
                var r = $scope.canceler.promise.$$state['status'];
                if(r==1){
                    NotifyFailConnection();
                }
            })
        } else {
            $scope.canceler.resolve();
            var r_1 = $scope.canceler.promise.$$state['status'];
            $scope.canceler = $q.defer();
            var r_2 = $scope.canceler.promise.$$state['status'];
            $http({
                url:showBotYPlayUri,
                method:'POST',
                headers: {
                    'Content-Type':'application/json'
                },
                data: {
                        'idUser': id_user,
                        'statusBot': status_bot,
                        'statusPlay' : status_play,
                        'exchangeUsername' : username_exchange,
                        'start':page
                      },
                timeout: $scope.canceler.promise
            }).then(function(exito) {
                distributionBots(exito.data);
            },function(error) {
                if(r_1==r_2){
                    NotifyFailConnection();
                }
            })
        }
    }

    /* Function: distributionBots
     * Arguments: 0 (todos) / 1 (solo los mios)
     * Output: $scope.bots {,,[],,}
     * Method: 
     * Summary: Lists all Exchange items created by Administrator
     */
     function distributionBots(data_bots){
        data_bots['data'].forEach(function(element){
            for (var i=0; i<$scope.bottypes.length; i++){
                element['general']['nameBotType'] = (element['general']['idBotType'] == $scope.bottypes[i]['idBotType'])? $scope.bottypes[i]['name'] : element['general']['nameBotType'];
            }
        });

        $scope.response_showBots = data_bots;
        var vec_bots = data_bots['data'];
        vec_bots.forEach(function(element){     
            $scope.bots_all.push(element);
        });

        (vec_bots.length%$scope.response_showBots['bots_per_page']==0 && vec_bots.length!=0) ? vec_bots.slice(0, -1) : 0;
        vec_bots.forEach(function(element){     
            $scope.bots.push(element);
        }); 
        
        $scope.waiting_bots = false;
        setWaitings($scope.bots);

        $scope.bots_played = [];
        $scope.bots_stopped = [];
        var cont = 0;
        $scope.bots.forEach(function (element){
            if(element.hasOwnProperty('play')){
                if(element.play.hasOwnProperty('idBotPlay')){
                    if(element.play['idBotPlay']!=null && element.play['status']!=2){
                        $scope.bots_played.push(element);
                        $scope.bots[cont]['play_status'] = true;       
                    } else {
                        $scope.bots_stopped.push(element);   
                        $scope.bots[cont]['play_status'] = false;
                    }
                }else {
                    $scope.bots_stopped.push(element);    
                    $scope.bots[cont]['play_status'] = false;
                }
            }else {
                $scope.bots_stopped.push(element);
                $scope.bots[cont]['play_status'] = false;
            }
            cont = cont +1;
        });

        (data_bots['data'].length!=0)?httpRequestOrder():0;
        
     }

    /* Function: httpRequestOrder
     * Arguments: -
     * Output: 
     * Method: -
     * Summary: Permite realizar una consulta de 'Orders' sin eliminar los requests de visualizacion de bots
     */
     function httpRequestOrder(){
        if($scope.bots_all.length%$scope.response_showBots['bots_per_page']==0 && $scope.bots_all.length!=0){
            $scope.paginas_bots = $scope.paginas_bots+1; 
            ($scope.switchVerTodos) ? showAllBotYPlay(0,1,'active',$scope.usernameByExchange,$scope.paginas_bots) : showAllBotYPlay(1,1,'active',$scope.usernameByExchange,$scope.paginas_bots);
        } else {
            if($scope.response_showBots['continue']==true){
                $scope.paginas_bots = $scope.paginas_bots+1; 
                ($scope.switchVerTodos) ? showAllBotYPlay(0,1,'active',$scope.usernameByExchange,$scope.paginas_bots) : showAllBotYPlay(1,1,'active',$scope.usernameByExchange,$scope.paginas_bots);
            }
        }
     }

    /* Function: find id user from USERS model
     * Arguments: -
     * Output: $scope.exchange {,,[],,}
     * Method: GET
     * Summary: -
     */
     function findIdUserByUsername(var_result,username){
        $http({
            url:getIdUserByUsernameUri,
            method:'POST',
            headers: {
                'Content-Type':'application/json'
            },
            data: {
                    'username':username
                  }
        }).then(function(exito) {
            var_result = parseInt(exito.data['data']['idUser']);
        },function(error) {
            Notify('Error in get User Id.','warning');               
        })
     }

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
            showAllUsersByExchange($scope.ID_BITINKA);
            showAllBotTypes();
            showAllTradingTypes();
            showAllPairs();
            showAllBotYPlay(1,1,'active',$scope.usernameByExchange,$scope.paginas_bots);
            findBotAndTradingType_By_Default();
            getPriceBTCinUSD();
        },function(error) {
            NotifyFailConnection();
        })
    }

    /* Function: findBotAndTradingType_By_Default
     * Arguments: -
     * Output: $scope.exchange {,,[],,}
     * Method: GET
     * Summary: Verify if bot type is 'Depth' and trading type is 'limit order'
     */
    function findBotAndTradingType_By_Default(){
        $http({
            url: verifyTypesBotAndTradingUri,
            method:'GET',
            headers: {
                'Content-Type':'application/json'
            }
        }).then(function(exito) {
            // Values by default:
            $scope.ngBot['idBotType'] = exito.data['data']['idBotType'];
            $scope.ngBot['idTradingType'] = exito.data['data']['idTradingType'];  
        },function(error) {
            Notify('Error in find Bot Type and Trading Type by default.','warning');  
        })
    }

    /* Function: selExchange
     * Arguments: id_exchange
     * Output: $scope.exchange {,,[],,}
     * Method: GET
     * Summary: Lists data Exchange items according by idExchange from ngPriceMarket - pair selected
     */
    function selExchange(id_exchange){
        $http({
            url:selExchangeUri,
            method:'POST',
            headers: {
                'Content-Type':'application/json'
            },
            data: {'idExchange':id_exchange}
        }).then(function(exito) {
            var exch = exito.data['data'];
            var items = ['idExchange','name','type','status','priority'];
            dic = {};
            for (var i=0; i<items.length; i++){
                dic[items[i]] = exch[i];
            }
            $scope.exchange = {'general' : dic};
            $scope.ngExchangeByPair = $scope.exchange;
        },function(error) {
            Notify('Error in find Exchange.','warning');  
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
            $scope.users = []
            var items = ['idUser','idExchange','username','credentials','status'];
            for (var i=0;i<exito.data['data'].length;i++) {
                var dic = {};
                for (var j=0; j<items.length; j++) dic[items[j]] = exito.data['data'][i][j+1];
                $scope.users.push(dic);
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
                //$scope.pairs.push({'pair' : dic});
                $scope.pairs.push(dic);
            }
        },function(error) {
            Notify('Error in show pairs.','warning');   
        })
    }

    /* Function: showAllBotTypes
     * Arguments: -
     * Output: $scope.exchange {,,[],,}
     * Method: GET
     * Summary: Lists all Exchange items created by Administrator
     */
    function showAllBotTypes(){
        $http({
            url:showBotTypesUri,
            method:'GET',
            headers: {
                'Content-Type':'application/json'
            },
        }).then(function(exito) {
            $scope.bottypes = exito.data['data'];
        },function(error) {
            Notify('Error in show Bot Types.','warning'); 
        })
    }

    /* Function: showAllTradingTypes
     * Arguments: -
     * Output: $scope. {,,[],,}
     * Method: GET
     * Summary: Lists all Exchange items created by Administrator
     */
    function showAllTradingTypes(){
        $http({
            url:showTradingTypesUri,
            method:'GET',
            headers: {
                'Content-Type':'application/json'
            },
        }).then(function(exito) {
            $scope.tradingtypes = exito.data['data'];
        },function(error) {
            Notify('Error in show Trading Types.','warning'); 
        })
    }

    /* Function: botModal
     * Arguments: 'A'/'M'/'D' (Add/Modify/Delete)
     * Output: -
     * Method: -
     * Summary: Set Config for a differents types of modal: Add New Bot, Modify or Delete the existing Bot.
     */
    $scope.botModal = function (type='A', object_bot=null, index=null) {
        selExchangeBitinka($scope.ID_BITINKA);
        //showAllUsersByExchange($scope.ID_BITINKA); // only bitinka id=?
        type = ($scope.ID_BITINKA>=0? type: 'X');
        $('#swich1').click();
        switch(type) {
            case 'A':
                $scope.modalTitle = 'Add Bots';
                $scope.modificando = false;
                $scope.click_btnBuyVar = false;
                $scope.click_btnSellVar = false;
                $scope.waiting = true;
                $scope.isDisabled_usersSelect=false;

                $scope.ngTiempo['horas'] = 0;
                $scope.ngTiempo['minutos'] = 0;
                $scope.ngTiempo['segundos'] = 0;
                $scope.ngUser = {};
                $scope.ngPair = {};
                $scope.ngBot = {};
                $scope.ngBot['buySpread'] = 0;
                $scope.ngBot['sellSpread'] = 0;
                $scope.ngBot['buyPercent'] = 0;
                $scope.ngBot['sellPercent'] = 0;
                $scope.ngBot['minAmount'] = 0;
                $scope.ngBot['maxAmount'] = 0;
                $scope.ngBot['minUSD'] = 0;
                $scope.ngBot['maxUSD'] = 0;
                $scope.ngPriceMarket = {};
                $scope.ngExchange = {};
                findBotAndTradingType_By_Default();
                break;
            case 'M':
                $scope.modalTitle = 'Modify Bot';
                $scope.modificando = true;
                $scope.isDisabled_usersSelect=true;

                $scope.ngTiempo['horas'] = 0;
                $scope.ngTiempo['minutos'] = 0;
                $scope.ngTiempo['segundos'] = 0;
                $scope.ngUser = {};
                $scope.ngPair = {};
                $scope.ngBot = {};
                $scope.ngPriceMarket = {};
                $scope.ngExchange = {};

                $scope.ngPair.idPair = object_bot.bot['idPair'];
                for(var i=0;i<$scope.users.length;i++){
                    $scope.ngUser.idUser = ($scope.bots[index].general['exchangeUsername']==$scope.users[i].username?$scope.users[i].idUser:$scope.ngUser.idUser);
                }

                $scope.selMarketPricesExchange($scope.ngPair.idPair);
                for(var key in object_bot.bot) $scope.ngBot[key] = object_bot.bot[key];
                for(var key in object_bot.general) $scope.ngBot[key] = object_bot.general[key];
                $scope.selPairTypeCoins($scope.ngPair.idPair);

                $scope.ngTiempo.horas = 0;
                $scope.ngTiempo.minutos = object_bot.general['executeTime'];
                $scope.ngTiempo.segundos = 0;
                $scope.switchStatus = ($scope.ngBot.status==1)?true:false;
                break;
            case 'X':
                (new PNotify({
                    title: 'Exchange Bitinka doesn\'t found',
                    text: ' <center><h5>Bitinka Exchange module is not available.</h5> </center>',
                    icon: 'fa fa-trash fa-spin  fa-fw text-danger',
                    hide: false,
                    type: 'success',
                    styling: 'bootstrap3',
                    confirm: {
                        confirm: true,
                        buttons:[
                            {text:'Aceptar'},
                            {text:'cancelar',addClass :'btn btn-danger'}
                        ]   
                    },
                    buttons: {
                        closer: false,
                        sticker: false,
                    },
                    addclass: 'stack-modal',
                    stack: {
                        'dir1': 'down',
                        'dir2': 'right',
                        'modal': false
                    }
                })).get().on('pnotify.confirm', function() {
                    //delExchange($scope.exchanges[index].general.idExchange);
                }).on('pnotify.cancel', function() {
                    //
                });
            default:            
                break;
        }
    }

    /* Function: selMarketPricesExchange
     * Arguments: idPair
     * Output: -
     * Method: -
     * Summary: Set Config for a differents types of modal: Add New Bot, Modify or Delete the existing Bot.
     */
    $scope.selMarketPricesExchange = function(id_pair) {
        $scope.waiting = true;
        $http({
            url: selMarketPricesExchangeUri,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            data: {'idPair':id_pair}
        })
        .then(function (exito) {
            $scope.waiting = false;
            $scope.ngPriceMarket = exito.data['data'][0];
            $scope.ngPriceMarket['buyMarketPrice'] = $scope.ngPriceMarket['buyMarketPrice'];
            $scope.ngPriceMarket['sellMarketPrice'] = $scope.ngPriceMarket['sellMarketPrice'];
            selExchange($scope.ngPriceMarket.idExchange);
        }, function (error) {
            Notify('Error in show Market Prices by Exchange.','warning'); 
        })
    } 

    /* Function: selPairTypeCoins
     * Arguments: idPair
     * Output: -
     * Method: -
     * Summary: Set Config for a differents types of modal: Add New Bot, Modify or Delete the existing Bot.
     */
    $scope.selPairTypeCoins = function(id_pair) {
        var par = {}
        $scope.pairs.forEach(function(element){
            par = (element['idPair']==id_pair) ? element : par;
        });

        $http({
            url: selPairTypeCoins,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            data: par
        })
        .then(function (exito) {
            $scope.current_type_coins = exito.data['data'];
            //console.log($scope.current_type_coins);
        }, function (error) {
            Notify('Error in show params coins of pair.','warning'); 
        })
    } 

    /* Function: btn_BuyVar
     * Arguments: [,,,,] ngModels
     * Output: -
     * Method: -
     * Summary: Btn Calculate
     */
     $scope.btn_BuyVar = function(tipo) {
        if($scope.ngPriceMarket.buyMarketPrice!=null && $scope.ngBot.buySpread!=null){
            var pos_btn = (document.getElementById("btn_BuyVar")).getBoundingClientRect();
            if($scope.ngBot['idBotType']=='D'){
                var diferencia = parseFloat($scope.ngPriceMarket.buyMarketPrice)*parseFloat($scope.ngBot.buySpread)/100;
                var rango_variacion = parseFloat($scope.ngPriceMarket.buyMarketPrice)+parseFloat(diferencia); 
                var referencia = 'Buy price';
                var refVal = $scope.ngPriceMarket.buyMarketPrice;
            } else {
                var diferencia = parseFloat($scope.ngPriceMarket.sellMarketPrice)*parseFloat($scope.ngBot.buySpread)/100;
                var rango_variacion = parseFloat($scope.ngPriceMarket.sellMarketPrice)+parseFloat(diferencia);   
                var referencia = 'Sell price';
                var refVal = $scope.ngPriceMarket.sellMarketPrice;
            }
            switch(tipo) {
                case 'show':
                    if($('.ui-pnotify').length<1) {
                        tooltip = new PNotify({
                            title: "Buy's Spread:",
                            text:  "Buy price: " + rango_variacion.toFixed(8) + "<br>" +
                                   "Percentage: " + $scope.ngBot.buySpread + "% <br>" +
                                   "Difference: " + diferencia.toFixed(8) + "<br>" +
                                   "Reference:  " + referencia + "<br>" +
                                   "Reference value: " +  refVal,
                            hide: false,
                            styling: 'bootstrap3',
                            type: 'info',
                            buttons: {
                                closer: true,
                                sticker: false
                            },
                            history: {
                                history: false
                            },
                            animate_speed: "fast",
                            opacity: .5,
                            icon: "fa fa-calculator",
                            stack: false,
                            auto_display: false
                        });    
                        tooltip.get().css({
                            'top': pos_btn.top + 12, 
                            'left': pos_btn.left + 12
                        });
                        tooltip.open();

                        tooltip.get().click(function(e) {
                            tooltip.remove();
                        });
                    }

                    break;
                case 'destroy':
                    //tooltip.remove();
                    var pnotifies = document.getElementsByClassName('ui-pnotify');
                    while(pnotifies.length>0){
                        pnotifies[0].parentNode.removeChild(pnotifies[0]);
                    }
                    break;
                default:
                    break;
            }
        } else {

        }
     }

     /* Function: btn_SellVar
     * Arguments: [,,,,] ngModels
     * Output: -
     * Method: -
     * Summary: Btn Calculate
     */
     $scope.btn_SellVar = function(tipo) {
        if($scope.ngPriceMarket.sellMarketPrice!=null && $scope.ngBot.sellSpread!=null){
            var pos_btn = (document.getElementById("btn_SellVar")).getBoundingClientRect();
            if($scope.ngBot['idBotType']=='D'){
                var diferencia = parseFloat($scope.ngPriceMarket.sellMarketPrice)*parseFloat($scope.ngBot.sellSpread)/100;
                var rango_variacion = parseFloat($scope.ngPriceMarket.sellMarketPrice)+parseFloat(diferencia);
                var referencia = 'Sell price';
                var refVal = $scope.ngPriceMarket.sellMarketPrice;
            } else {
                var diferencia = parseFloat($scope.ngPriceMarket.buyMarketPrice)*parseFloat($scope.ngBot.sellSpread)/100;
                var rango_variacion = parseFloat($scope.ngPriceMarket.buyMarketPrice)+parseFloat(diferencia);
                var referencia = 'Buy price';
                var refVal = $scope.ngPriceMarket.buyMarketPrice;
            }
            switch(tipo) {
                case 'show':
                    if($('.ui-pnotify').length<1) {
                        tooltip = new PNotify({
                            title: "Sell's Spread:",
                            text:  "Sell price: " + rango_variacion.toFixed(8) + "<br>" +
                                   "Percentage: " + $scope.ngBot.sellSpread + "% <br>" +
                                   "Difference: " + diferencia.toFixed(8) + "<br>" +
                                   "Reference:  " + referencia + "<br>" +
                                   "Reference value: " +  refVal,
                            hide: false,
                            styling: 'bootstrap3',
                            type: 'info',
                            buttons: {
                                closer: true,
                                sticker: false
                            },
                            history: {
                                history: false
                            },
                            animate_speed: "fast",
                            opacity: .5,
                            icon: "fa fa-calculator",
                            stack: false,
                            auto_display: false
                        })
                        tooltip.get().css({
                            'top': pos_btn.top + 12, 
                            'left': pos_btn.left + 12
                        });
                        tooltip.open();

                        tooltip.get().click(function(e) {
                            tooltip.remove();
                        });
                    }

                    break;
                case 'destroy':
                    //tooltip.remove();
                    var pnotifies = document.getElementsByClassName('ui-pnotify');
                    while(pnotifies.length>0){
                        pnotifies[0].parentNode.removeChild(pnotifies[0]);
                    }
                    break;
                default:
                    break;
            }
        } else {
            
        }
     }

    /* Function: addBot
     * Arguments: [,,,,] ngModels
     * Output: -
     * Method: -
     * Summary: Send HTTP request for add new Bot
     */
     $scope.addBot = function() {
        $("#closeModalBots").click();

        $scope.ngBot['idExchange'] = $scope.ngExchange.general.idExchange;
        $scope.ngBot['idPair'] = $scope.ngPair.idPair;
        $scope.ngBot['status'] = 1;
        $scope.ngBot['idUserExchange'] = $scope.ngUser.idUser;
        $scope.ngBot.executeTime = 0;
        $scope.ngBot.completeTime = 0;      
        $scope.ngBot['buySpread'] = parseFloat($scope.ngBot['buySpread']);
        $scope.ngBot['sellSpread'] = parseFloat($scope.ngBot['sellSpread']);

        if($scope.ngBot['buyPercent']>=0 && $scope.ngBot['sellPercent']>=0){
            $http({
                url: addBotUri,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                data: $scope.ngBot
            })
            .then(function (exito) {
                var bot_creado = exito.data['data'];
                bot_creado['play_status'] = false;
                $scope.bots.push(bot_creado);
                setWaitings($scope.bots);
                Notify('New Bot created successfully','success');
            }, function (error) {
                Notify('Error in add new Bot.','warning'); 
            })
        } else {
            Notify('% Cancellations can\'t have negative values.','warning'); 
        }
     }

     /* Function: addPlay
     * Arguments: [,,,,] ngModels
     * Output: -
     * Method: -
     * Summary: Send HTTP request for add new Bot Play
     */
     $scope.addPlay = function(index,obj_play, bot_exec_time) {

        // Actualizar precio de BTC en USD:
        //getPriceBTCinUSD();  // Refresh price btc in usd
                        
        // Actualizar Bot Configuration - Execute Time:
        var general = $scope.bots[index].general
        var bot = $scope.bots[index].bot;
        for (var key in general) {
            $scope.ngBot[key] = general[key]; 
        }
        for (var key in bot) {
            $scope.ngBot[key] = bot[key]; 
        }
        
        //findIdUserByUsername($scope.bots[index].general.username);
        $scope.ngBot['idUser'] = $scope.bots[index].general.idUser;
        $scope.ngBot['completeTime'] = 0;
        $scope.ngBot['executeTime'] = parseInt(bot_exec_time);
        $scope.switchStatus=true;

        // Agregar Bot Play:
        $scope.ngPlay = obj_play;
        $scope.ngPlay['idUser'] = parseInt($scope.idUser);
        $scope.ngPlay['idBot'] = $scope.bots[index].general.idBot;

        if($scope.ngPlay['orderType']) {
            if(Object.keys($scope.ngPlay).length>=6) {
                if($scope.ngPlay['altExecuteTime']>0 && $scope.ngBot['executeTime']>0) {
                    // Actualizar Bot Configuration:
                    $scope.modificando=false;
                    
                    // Agregar Bot Play:
                    $scope.waiting_play[index] = true;
                    $http({
                        url: addPlayUri,
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        data: $scope.ngPlay
                    })
                    .then(function (exito) {
                        // Refresh ngBot with new prices crypto

                        if($scope.ngBot['minAmount']!=0 && $scope.ngBot['maxAmount']!=0) {
                            if($scope.ngBot['minUSD']!=0 && $scope.ngBot['maxUSD']!=0) {
                                $scope.updBot();
                            } else {
                                refreshPrices();
                            }
                        }

                        if($scope.click_btnPlayStop == true) {
                            Notify('Bot started successfully.','success');
                        } else {
                            if($http.pendingRequests.length<=0) {
                                Notify('All Bots were Started successfully.','success');   
                            }
                        }

                        $scope.bots[index]['play_status'] = true;
                        $scope.bots[index].play['idBotPlay'] = exito.data['data'][0][0];
                        $scope.bots[index].play['playDate'] = ( moment().format() ).toString();

                        $scope.waiting_play[index] = false;
                        $scope.waiting_editar[index] = false;

                    }, function (error) {
                        Notify('Bot cann\'t be started.','warning');
                    })
                } else {
                    Notify('Times cann\'t be zero','warning');  
                }
            } else {
                Notify('Alternatives doesn\'t were setted','warning');    
            }
        } else {
            Notify('Invalid Order Type selected','warning');
        }

     }

    /* Function: updBot
     * Arguments: [,,,,] ngModels
     * Output: -
     * Method: -
     * Summary: Send HTTP request for update exists Bot
     */
     $scope.updBot = function() {
        $("#closeModalBots").click();
        if ($scope.switchStatus==true) {
            $scope.ngBot['idPair'] = ($scope.ngPair.idPair?$scope.ngPair.idPair:$scope.ngBot['idPair']);

            if($scope.ngBot['buyPercent']>=0 && $scope.ngBot['sellPercent']>=0){
                
                var contador=0;
                $scope.bots.forEach(function(element){
                    if(element.general['idBot']==$scope.ngBot.idBot){
                        $scope.waiting_editar[contador] = true;
                    }
                    contador=contador+1;
                });

                $scope.ngBot['TypeCoinsPair'] = $scope.current_type_coins;
                $scope.ngBot['buy_btc_in_usd'] = $scope.priceBTCinUSD;
 
                $http({
                    url: updBotUri,
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    data: $scope.ngBot
                })
                .then(function (exito) {
                    var objeto = exito.data['data'][0];
                    var campos = ['buySpread','sellSpread','minAmount','maxAmount','minUSD','maxUSD','buyPercent','sellPercent','idTradingType','idBotType'];
                    var bot_actualizado;

                    var contador=0;
                    $scope.bots.forEach(function(element) {
                        if(element.general.idBot == objeto['idBot']){
                            campos.forEach(function(c){
                                element.general[c] = objeto[c];
                            });
                            bot_actualizado = element;
                            $scope.waiting_editar[contador] = false;
                        }
                        contador=contador+1;
                    });
                    ($scope.modificando==true)?Notify('Bot\'s changes saved successfully','success'):0;
                }, function (error) {
                    Notify('Error in update Bot.','warning'); 
                })
            }else {
                Notify('% Cancellations can\'t have negative values.','warning'); 
            }
        } else {
            $http({
                url: delBotUri,
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                data: {
                        'idBot':$scope.ngBot.idBot,
                        'status':2,
                        'idUser':$scope.ngBot['idUser']
                      }
            })
            .then(function (exito) {
                $("#closeModalBots").click();
                for(var i=0;i<$scope.bots.length;i++){
                    ($scope.bots[i].general.idBot==$scope.ngBot.idBot)?($scope.bots.splice(i,1)):0;
                }
                Notify('Bot deleted successfully','success');
            }, function (error) {
                Notify('Error in delete Bot.','warning'); 
            })
        }
     }

     /* Function: updBot
     * Arguments: [,,,,] ngModels
     * Output: -
     * Method: -
     * Summary: Send HTTP request for update exists Bot
     */
     $scope.updPlay = function(index,obj_play, bot_exec_time) {
        var dic = {};
        dic['idBotPlay'] =  $scope.bots[index].play.idBotPlay;
        dic['idUser'] = $scope.idUser;
        $scope.waiting_play[index] = true;
        $http({
            url: updPlayUri,
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            data: dic
        })
        .then(function (exito) {
            if($scope.click_btnPlayStop == true){
                Notify('Bot stopped successfully.','success');
            } else {
                if($http.pendingRequests.length<=0) {
                    Notify('All Bots were Stopped successfully.','success');               
                }
            }

            delete $scope.bots[index].play['idBotPlay'];
            $scope.bots[index]['play_status'] = false;
            $scope.waiting_play[index] = false;

        }, function (error) {
            Notify('Bot cann\'t be stopped.','warning');
        })
     }

    /* Function: clickBtn_PlayStop
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: Verified individual click in Btn for Play and Stop Bot
     */
     $scope.clickBtn_PlayStop = function() {
        $scope.click_btnPlayStop = true;
     }

    /* Function: playAllBots
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: Play All Bots in View FE
     */
     $scope.playAllBots = function() {
        $scope.click_btnPlayStop = false;

        setTimeout(function fin() {
            var where_is_plays = [];
            for (var i=0; i<$scope.bots_filtrados.length; i++){
                if(!$scope.bots_filtrados[i].play['idBotPlay'] && $scope.bots_filtrados[i].play.orderType!=null && $scope.bots_filtrados[i].play.altExecuteTime>0) {
                    where_is_plays.push($scope.bots.indexOf($scope.bots_filtrados[i]));
                }
            }

            var tam = where_is_plays.length;
            var cont = 0;
            while(tam>0){
                $scope.addPlay(where_is_plays[cont],$scope.bots[where_is_plays[cont]].play,$scope.bots[where_is_plays[cont]].general.executeTime);
                tam = tam-1;
                cont = cont + 1;
            }
        },200);
     }

    /* Function: stopAllBots
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: Stop All Bots in View FE
     */
     $scope.stopAllBots = function() {
        $scope.click_btnPlayStop = false;

        setTimeout(function fin() {
            var where_is_stops = [];
            for (var i=0; i<$scope.bots_filtrados.length; i++){
                if($scope.bots_filtrados[i].play['idBotPlay']) {
                    where_is_stops.push($scope.bots.indexOf($scope.bots_filtrados[i]));
                }
            }

            var tam = where_is_stops.length;
            var cont = 0;
            while(tam>0){
                $scope.updPlay(where_is_stops[cont],$scope.bots[where_is_stops[cont]].play,$scope.bots[where_is_stops[cont]].general.executeTime);
                tam = tam-1;
                cont = cont + 1;
            }
        },200);
     }

    /* Function: onChangeSwitchAll
     * Arguments: [,,,,] ngModels
     * Output: -
     * Method: -
     * Summary: Send HTTP request for update exists Bot
     */
    $scope.onChangeSwitchAll = function () {
        ($http.pendingRequests.length>0)?$scope.canceler.resolve():0;
        $scope.paginas_bots = 0;
        $scope.bots_all = [];
        $scope.bots = [];
        ($scope.switchVerTodos) ? showAllBotYPlay(0,1,'active',$scope.usernameByExchange,$scope.paginas_bots) : showAllBotYPlay(1,1,'active',$scope.usernameByExchange,$scope.paginas_bots);
    }

    /* Function: btn_alternatives
     * Arguments: [,,,,] ngModels
     * Output: -
     * Method: -
     * Summary: Btn Alternatives
     */
     $scope.btn_alternatives = function(id_bot) {

        var idBots = [];
        $scope.bots.forEach(function(element){
           idBots.push(element.general.idBot);
        });


        idBots.forEach(function(element){
            if(document.getElementById("btn_alternatives1_"+element)) {
               document.getElementById("btn_alternatives1_"+element).disabled=true;
            }
        })
        var pos_btn = (document.getElementById("btn_alternatives1_"+id_bot)).getBoundingClientRect();
        var form = ('<form class="text-form" id="text_form">'
                    +   '<div class="form-group form-group-sm">'
                    +       '<div class="row" style="border-top: 1px solid #e5e5e5; padding-top: 10px">'
                    +           '<div class="col-md-6 col-sm-6 col-xs-6">'
                    +               '<input type="radio" name="chooseTime" id="seg" checked="checked"><label>In seconds</label>'
                    +           '</div>'
                    +           '<div class="col-md-6 col-sm-6 col-xs-6">'
                    +               '<input type="radio" name="chooseTime" id="min"><label>In minutes</label>'
                    +           '</div>'
                    +       '</div>'
                    +       '<div class="row">'       
                    +           '<div class="col-md-6 col-sm-6 col-xs-6">'
                    +               '<label>Exec. Time:</label> <input type="number" class="form-control" id="ExecuteTime">'
                    +           '</div>'
                    +           '<div class="col-md-6 col-sm-6 col-xs-6">'
                    +               '<label>Alt Time:</label> <input type="number" class="form-control" id="altExecuteTime">'
                    +           '</div>'
                    +       '</div>'
                    +       '<div class="row" style="border-bottom: 1px solid #e5e5e5; padding-bottom: 10px">'       
                    +           '<div class="col-md-6 col-sm-6 col-xs-6">'
                    +               '<label>Buy (%):</label> <input type="number" class="form-control" id="altBuySpread">'
                    +           '</div>'
                    +           '<div class="col-md-6 col-sm-6 col-xs-6">'
                    +               '<label>Sell (%):</label> <input type="number" class="form-control" id="altSellSpread">'
                    +           '</div>'
                    +       '</div>'
                    +   '</div>'
                    +'</form>'
                    );
        var indice = 0;
        for(var i=0;i<$scope.bots.length;i++){
            if($scope.bots[i].general.idBot==id_bot) {
                if ($scope.bots[i].general.executeTime>0 && $scope.bots[i].play.altExecuteTime>0) {
                document.getElementById("btn_alternatives2_"+id_bot).innerText =  $scope.bots[i].general.executeTime + "s / " + 
                                                                                  $scope.bots[i].play.altExecuteTime + "s / " +
                                                                                  $scope.bots[i].play.altBuySpread + "% / " +
                                                                                  $scope.bots[i].play.altSellSpread + "%"   
                }
                indice = i;
            }
        }

        var stack_topleft = {"dir1": "down", "dir2": "right", "push": "top"};
        var stack_bottomleft = {"dir1": "right", "dir2": "up", "push": "top"};
        var stack_bar_top = {"dir1": "down", "dir2": "right", "push": "top", "spacing1": 0, "spacing2": 0};
        var stack_bar_bottom = {"dir1": "up", "dir2": "right", "spacing1": 0, "spacing2": 0};

        // Begin - Creacion PNotify
        tooltip = new PNotify({
            title: '<center><label>Add Time, % Buy, % Sell</label><div id="idbott"></div>',
            text: form,
            icon: 'fa fa-question',
            hide: false,
            type: 'success',
            addclass: 'customWeb',
            styling: 'bootstrap3',
            confirm: {
                confirm: true,
                buttons: [
                    {text: 'Accept', addClass: 'btn btn-success btn-md'},
                    {text: 'Cancel', addClass: 'btn btn-danger btn-md'}
                ]
            },
            buttons: {
                closer: false,
                sticker: false
            },
            history: {
                history: false
            },
            stack: false,
            animate_speed: "fast",
            opacity: .5,
            icon: "fa fa-calculator",
            auto_display: false
        });


        tooltip.open();
         document.getElementById("idbott").innerText =  "ID Bot seleccionado: " + id_bot;

        tooltip.get().on('pnotify.confirm',function(){
            idBots.forEach(function(element){
                if(document.getElementById("btn_alternatives1_"+element)) {
                    document.getElementById("btn_alternatives1_"+element).disabled=false;
                }
            })
            var ExecuteTime = (document.getElementById('seg').checked ? document.getElementById("ExecuteTime").value : 60*parseInt(document.getElementById("ExecuteTime").value));
            var altExecuteTime = (document.getElementById('seg').checked ? document.getElementById("altExecuteTime").value : 60*parseInt(document.getElementById("altExecuteTime").value));
            var altBuySpread = document.getElementById("altBuySpread").value;
            var altSellSpread = document.getElementById("altSellSpread").value;

            for(var i=0;i<$scope.bots.length;i++){
                if($scope.bots[i].general.idBot==id_bot) {
                    $scope.bots[i].general.executeTime = parseInt(ExecuteTime);
                    $scope.bots[i].play.altExecuteTime = parseInt(altExecuteTime); 
                    $scope.bots[i].play.altBuySpread = parseFloat(altBuySpread);
                    $scope.bots[i].play.altSellSpread = parseFloat(altSellSpread);
                }
            }

            if (ExecuteTime!="" && altExecuteTime!="" && altBuySpread!="" && altSellSpread!="") {
                document.getElementById("btn_alternatives2_"+id_bot).innerText = ExecuteTime+"s / "+altExecuteTime+"s / "+altBuySpread+"% / "+altSellSpread + "%";    
            }            
        });
        tooltip.get().on('pnotify.cancel',function(){
            idBots.forEach(function(element){
                if(document.getElementById("btn_alternatives1_"+element)){
                    document.getElementById("btn_alternatives1_"+element).disabled=false;   
                }
            })
        });
        // End - Creacion PNotify

        document.getElementById("ExecuteTime").value = ($scope.bots[indice].general.executeTime == null ?  0 : $scope.bots[indice].general.executeTime);
        document.getElementById("altExecuteTime").value = ($scope.bots[indice].play.altExecuteTime == null ?  0 : $scope.bots[indice].play.altExecuteTime);
        document.getElementById("altBuySpread").value = ($scope.bots[indice].play.altBuySpread == null? 0 : $scope.bots[indice].play.altBuySpread);
        document.getElementById("altSellSpread").value = ($scope.bots[indice].play.altSellSpread ==null ? 0 : $scope.bots[indice].play.altSellSpread );
     }

    /* Function: selectOrderTypeAllBots
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: select Order Type (Compra, Venta, Ambos) for all bots
     */
     $scope.selectOrderTypeAllBots = function() {
        for(var i=0; i<$scope.bots.length;i++){
            $scope.bots_filtrados[i].play.orderType = $scope.orderTypeAllBots;
        }
     }

     /* Function: setAlternativesAll
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: set config for Play Bot in All Bots
     */
     $scope.setAlternativesAll = function(buy_spread,sell_spread,cancel_purch,cancel_sale,min_amount,max_amount,exec_time, alt_exec_time, alt_buy_spr, alt_sell_spr) {
            
        var radBtn_porcentual = document.getElementById('porcentual');
        var radBtn_unitario = document.getElementById('unitario');

        var campos_general = ['buySpread','sellSpread','minAmount','maxAmount','buyPercent','sellPercent'];
        var campos_play = ['altBuySpread','altSellSpread'];

        if(radBtn_porcentual.checked){
            for(var i=0;i<$scope.bots.length;i++){

                var temps_general = [];
                campos_general.forEach(function(c){
                    temps_general.push($scope.bots_filtrados[i].general[c]); 
                });
                var temps_play = [];
                campos_play.forEach(function(c){
                    temps_play.push($scope.bots_filtrados[i].play[c]); 
                });

                $scope.bots_filtrados[i].general['buySpread'] = (buy_spread)? ($scope.bots_filtrados[i].general['buySpread']+$scope.bots_filtrados[i].general['buySpread']*parseFloat(buy_spread)/100) :$scope.bots_filtrados[i].general['buySpread'];
                $scope.bots_filtrados[i].general['sellSpread'] = (sell_spread)? ($scope.bots_filtrados[i].general['sellSpread']+$scope.bots_filtrados[i].general['sellSpread']*parseFloat(sell_spread)/100) :$scope.bots_filtrados[i].general['sellSpread'];
                $scope.bots_filtrados[i].general['minAmount'] = (min_amount)? ($scope.bots_filtrados[i].general['minAmount']+$scope.bots_filtrados[i].general['minAmount']*parseFloat(min_amount)/100) :$scope.bots_filtrados[i].general['minAmount'];
                $scope.bots_filtrados[i].general['maxAmount'] = (max_amount)? ($scope.bots_filtrados[i].general['maxAmount']+$scope.bots_filtrados[i].general['maxAmount']*parseFloat(max_amount)/100) :$scope.bots_filtrados[i].general['maxAmount'];
                $scope.bots_filtrados[i].general['buyPercent'] = (cancel_purch)? ($scope.bots_filtrados[i].general['buyPercent']+$scope.bots_filtrados[i].general['buyPercent']*parseFloat(cancel_purch)/100) :$scope.bots_filtrados[i].general['buyPercent'];
                $scope.bots_filtrados[i].general['sellPercent'] = (cancel_sale)? ($scope.bots_filtrados[i].general['sellPercent']+$scope.bots_filtrados[i].general['sellPercent']*parseFloat(cancel_sale)/100) :$scope.bots_filtrados[i].general['sellPercent'];                    

                $scope.bots_filtrados[i].general['executeTime'] = (exec_time)?exec_time:$scope.bots_filtrados[i].general['executeTime'];
                $scope.bots_filtrados[i].play['altExecuteTime'] = (alt_exec_time)?alt_exec_time:$scope.bots_filtrados[i].play['altExecuteTime'];
                if(alt_buy_spr){
                    if($scope.bots_filtrados[i].play['altBuySpread']){
                        $scope.bots_filtrados[i].play['altBuySpread'] = $scope.bots_filtrados[i].play['altBuySpread']+$scope.bots_filtrados[i].play['altBuySpread']*parseFloat(alt_buy_spr)/100;  
                    }  else{
                        $scope.bots_filtrados[i].play['altBuySpread'] = parseFloat(alt_buy_spr)/100;                        
                    }
                }
                if(alt_sell_spr){
                    if($scope.bots_filtrados[i].play['altSellSpread']){
                        $scope.bots_filtrados[i].play['altSellSpread'] = $scope.bots_filtrados[i].play['altSellSpread']+$scope.bots_filtrados[i].play['altSellSpread']*parseFloat(alt_sell_spr)/100;      
                    }  else{
                        $scope.bots_filtrados[i].play['altSellSpread'] = parseFloat(alt_sell_spr)/100;                        
                    }
                }

                var cont=0;
                campos_general.forEach(function(c){
                    $scope.bots_filtrados[i].general[c] = ($scope.bots_filtrados[i].general[c]>=0)? ($scope.bots_filtrados[i].general[c]) : temps_general[cont];
                    $scope.bots_filtrados[i].general[c] = parseFloat($scope.bots_filtrados[i].general[c]);
                    cont=cont+1;
                });

                var cont=0;
                campos_play.forEach(function(c){
                    $scope.bots_filtrados[i].play[c] = ($scope.bots_filtrados[i].play[c]>=0)? ($scope.bots_filtrados[i].play[c]) : temps_play[cont];
                    $scope.bots_filtrados[i].play[c] = parseFloat($scope.bots_filtrados[i].play[c]);
                    cont=cont+1;
                });
            }
        } else {
            if(radBtn_unitario.checked){
                for(var i=0;i<$scope.bots.length;i++){
                    $scope.bots_filtrados[i].general['buySpread'] = (buy_spread)?parseFloat(buy_spread):$scope.bots_filtrados[i].general['buySpread'];
                    $scope.bots_filtrados[i].general['sellSpread'] = (sell_spread)?parseFloat(sell_spread):$scope.bots_filtrados[i].general['sellSpread'];
                    $scope.bots_filtrados[i].general['minAmount'] = (min_amount)?parseFloat(min_amount):$scope.bots_filtrados[i].general['minAmount'];
                    $scope.bots_filtrados[i].general['maxAmount'] = (max_amount)?parseFloat(max_amount):$scope.bots_filtrados[i].general['maxAmount'];
                    $scope.bots_filtrados[i].general['buyPercent'] = (cancel_purch)?parseFloat(cancel_purch):$scope.bots_filtrados[i].general['buyPercent'];
                    $scope.bots_filtrados[i].general['sellPercent'] = (cancel_sale)?parseFloat(cancel_sale):$scope.bots_filtrados[i].general['sellPercent'];                    

                    $scope.bots_filtrados[i].general['executeTime'] = (exec_time)?exec_time:$scope.bots_filtrados[i].general['executeTime'];
                    $scope.bots_filtrados[i].play['altExecuteTime'] = (alt_exec_time)?alt_exec_time:$scope.bots_filtrados[i].play['altExecuteTime'];
                    $scope.bots_filtrados[i].play['altBuySpread'] = (alt_buy_spr)?parseFloat(alt_buy_spr):$scope.bots_filtrados[i].play['altBuySpread'];
                    $scope.bots_filtrados[i].play['altSellSpread'] = (alt_sell_spr)?parseFloat(alt_sell_spr):$scope.bots_filtrados[i].play['altSellSpread']; 
                }
            }
        }

     }

     /* Function: setAlternativesAll_Bot
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: set config for Play Bot in All Bots
     */
     $scope.setAlternativesAll_Bot = function(buy_spread,sell_spread,cancel_purch,cancel_sale,min_amount,max_amount) {
        $scope.switchStatus=true;
        var radBtn_porcentual = document.getElementById('porcentual');
        var radBtn_unitario = document.getElementById('unitario');
        var campos_general = ['buySpread','sellSpread','minAmount','maxAmount','buyPercent','sellPercent'];

        if(radBtn_porcentual.checked){
            $scope.bots_filtrados.forEach(function(element){
                var temps_general = [];
                campos_general.forEach(function(c){
                    temps_general.push(element.general[c]); 
                });

                element.general['buySpread'] = (buy_spread)? (element.general['buySpread']+element.general['buySpread']*parseFloat(buy_spread)/100) :element.general['buySpread'];
                element.general['sellSpread'] = (sell_spread)? (element.general['sellSpread']+element.general['sellSpread']*parseFloat(sell_spread)/100) :element.general['sellSpread'];
                element.general['minAmount'] = (min_amount)? (element.general['minAmount']+element.general['minAmount']*parseFloat(min_amount)/100) :element.general['minAmount'];
                element.general['maxAmount'] = (max_amount)? (element.general['maxAmount']+element.general['maxAmount']*parseFloat(max_amount)/100) :element.general['maxAmount'];
                element.general['buyPercent'] = (cancel_purch)? (element.general['buyPercent']+element.general['buyPercent']*parseFloat(cancel_purch)/100) :element.general['buyPercent'];
                element.general['sellPercent'] = (cancel_sale)? (element.general['sellPercent']+element.general['sellPercent']*parseFloat(cancel_sale)/100) :element.general['sellPercent'];                    

                var cont=0;
                campos_general.forEach(function(c){
                    element.general[c] = (element.general[c]>=0)? (element.general[c]) : temps_general[cont];
                    element.general[c] = parseFloat(element.general[c]);
                    cont=cont+1;
                });

                // Update for All Bots:
                $scope.ngBot = element.general;
                $scope.ngBot['TradingName'] = element.bot['TradingName'];
                $scope.ngBot['idExchange'] = element.bot['idExchange'];
                $scope.ngBot['idPair'] = element.bot['idPair'];
                $scope.ngBot['nameExchange'] = element.bot['nameExchange'];
                $scope.ngBot['pair'] = element.bot['pair'];
                $scope.ngBot['status'] = element.bot['status'];
                $scope.updBot();
            });
        } else {
            if(radBtn_unitario.checked){
                $scope.bots_filtrados.forEach(function(element){
                    element.general['buySpread'] = (buy_spread)?parseFloat(buy_spread):element.general['buySpread'];
                    element.general['sellSpread'] = (sell_spread)?parseFloat(sell_spread):element.general['sellSpread'];
                    element.general['minAmount'] = (min_amount)?parseFloat(min_amount):element.general['minAmount'];
                    element.general['maxAmount'] = (max_amount)?parseFloat(max_amount):element.general['maxAmount'];
                    element.general['buyPercent'] = (cancel_purch)?parseFloat(cancel_purch):element.general['buyPercent'];
                    element.general['sellPercent'] = (cancel_sale)?parseFloat(cancel_sale):element.general['sellPercent'];                    

                    // Update for All Bots:
                    $scope.ngBot = element.general;
                    $scope.ngBot['TradingName'] = element.bot['TradingName'];
                    $scope.ngBot['idExchange'] = element.bot['idExchange'];
                    $scope.ngBot['idPair'] = element.bot['idPair'];
                    $scope.ngBot['nameExchange'] = element.bot['nameExchange'];
                    $scope.ngBot['pair'] = element.bot['pair'];
                    $scope.ngBot['status'] = element.bot['status'];
                    $scope.updBot();
                });
            }
        }

        var inputs_botsconfig_all = document.getElementsByName("BotConfiguration_All");
        inputs_botsconfig_all.forEach(function(element){
            element.value = "";
            element.text = "";
        });
     }

     /* Function: setAlternativesAll_Play
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: set config for Play Bot in All Bots
     */
     $scope.setAlternativesAll_Play = function(exec_time, alt_exec_time, alt_buy_spr, alt_sell_spr) {
        $scope.switchStatus=true;           
        var radBtn_porcentual = document.getElementById('porcentual');
        var radBtn_unitario = document.getElementById('unitario');
        var campos_play = ['altBuySpread','altSellSpread'];

        $scope.bots_filtrados.forEach(function(element){
            element.general['executeTime'] = (exec_time)?exec_time:element.general['executeTime'];
            element.play['altExecuteTime'] = (alt_exec_time)?alt_exec_time:element.play['altExecuteTime'];
            element.play['altBuySpread'] = (alt_buy_spr)?parseFloat(alt_buy_spr):element.play['altBuySpread'];
            element.play['altSellSpread'] = (alt_sell_spr)?parseFloat(alt_sell_spr):element.play['altSellSpread']; 

            // Update for All Bots:
            $scope.ngBot = element.general;
            $scope.ngBot['TradingName'] = element.bot['TradingName'];
            $scope.ngBot['idExchange'] = element.bot['idExchange'];
            $scope.ngBot['idPair'] = element.bot['idPair'];
            $scope.ngBot['nameExchange'] = element.bot['nameExchange'];
            $scope.ngBot['pair'] = element.bot['pair'];
            $scope.ngBot['status'] = element.bot['status'];
            $scope.updBot();
        });

        var inputs_botsplay_all = document.getElementsByName("BotPlay_All");
        inputs_botsplay_all.forEach(function(element){
            element.value = "";
            element.text = "";
        });
     }


     /* Function: resetAlternativesAll
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: reset config for Play Bot in All Bots
     */
     $scope.resetAlternativesAll = function() {
        ($scope.switchVerTodos) ? showAllBotYPlay(0,1,'active',$scope.usernameByExchange,$scope.paginas_bots) : showAllBotYPlay(1,1,'active',$scope.usernameByExchange,$scope.paginas_bots);
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

    /* Function: NotifyApplyAll_Bots 
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: show a message with error in proccess
     */
     $scope.NotifyApplyAll = function(tipo,buy_spread,sell_spread,cancel_purch,cancel_sale,min_amount,max_amount,exec_time, alt_exec_time, alt_buy_spr, alt_sell_spr) {
        var form = ('<div class="clickPlayAllBots">'
                    +   '<center>'
                    +       'Are you sure save changes for all your Bots?<br>'
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
            title: '<br><center><label>Apply for All Bots</label></div>',
            text: form,
            icon: 'fa fa-question',
            hide: false,
            type: 'success',
            addclass: 'customWeb pnotify-center',
            styling: 'bootstrap3',
            confirm: {
                confirm: true,
                buttons: [{text: 'Accept', addClass: 'btn btn-success btn-md'},
                          {text: 'Cancel', addClass: 'btn btn-danger btn-md'}]
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
            switch(tipo){
                case 'Bots':
                    $scope.setAlternativesAll_Bot(buy_spread,sell_spread,cancel_purch,cancel_sale,min_amount,max_amount);
                    break;
                case 'Plays':
                    $scope.setAlternativesAll_Play(exec_time, alt_exec_time, alt_buy_spr, alt_sell_spr);
                    break;
                default:
                    break;
            }
        });
     }

     /* Function: NotifyFailConnection (Error/Success)
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: show a message with error in proccess
     */
     $scope.showActiveOrders = function(index, id_bot,pair, id_bot_type) {
        $scope.filterPrice="";
        $scope.tipoFiltro="";
        $scope.dataFiltros=[];
        $scope.waiting_modal=false;
        $scope.listarActiveOrder = [];
        $scope.listarActiveOrder = [index,id_bot,pair,id_bot_type];
        $scope.waiting_order[index] = true;
        $scope.PairByBot = pair;
        var i =0;
        $scope.dataBot = [];
        $scope.bots.forEach(function(element){
            $scope.dataBot = ($scope.bots[i].general.idBot == id_bot)?$scope.bots[i]:$scope.dataBot;
            i =i +1;
        });
        if($http.pendingRequests.length<=0){
            document.getElementsByClassName("selectAllChecks")[0].checked=false;

            $scope.idBot_selected = id_bot;
            var post_order = {'idBot':id_bot,
                              'pair':pair,
                              'idBotType':id_bot_type};
            $http({
                    url: getHistorialOrdersUri,
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    data: post_order,
                    timeout: $scope.canceler.promise
                })
                .then(function (exito) {
                    $scope.waiting_order[index] = false;
                    if(exito.data['code']==203){
                        $scope.existOrder = false;
                        exito.data['data']['status']?Notify(exito.data['data']['status'],'warning'):Notify(exito.data['data']['error'],'warning');
                    } else {
                        $scope.existOrder = true;
                        $scope.activeOrders = exito.data['data'][0]['history'];
                        $scope.dataFiltros=$scope.activeOrders;

                        $("#ordersModal").modal();
                    }
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

            document.getElementsByClassName("selectAllChecks")[0].checked=false;

            $scope.idBot_selected = id_bot;
            var post_order = {'idBot':id_bot,
                              'pair':pair,
                              'idBotType':id_bot_type};
            $http({
                    url: getHistorialOrdersUri,
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    data: post_order,
                    timeout: $scope.canceler.promise
                })
                .then(function (exito) {
                    $scope.waiting_order[index] = false;
                    if(exito.data['code']==203){
                        $scope.existOrder = false;
                        exito.data['data']['status']?Notify(exito.data['data']['status'],'warning'):Notify(exito.data['data']['error'],'warning');
                    } else {
                        $scope.existOrder = true;
                        $scope.activeOrders = exito.data['data'][0]['history'];
                        $scope.dataFiltros=$scope.activeOrders;
                        $("#ordersModal").modal();
                    }

                    httpRequestOrder();
                }, function (error) {
                    if(r_1==r_2){
                        Notify('Error in show History of Active Orders.','warning'); 
                    }
                })
        }
     }

     /* Function: NotifyFailConnection (Error/Success)
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: show a message with error in proccess
     */
     $scope.cancelOrders = function() {
        $scope.waiting_modal=true;
        var select_orders = $('.check_orders:checked');
        var active_orders = [];

        for(i=0;i<select_orders.length;i++){
            active_orders.push(select_orders[i].id);
        }

        var orderstocancel = [];
        active_orders.forEach(function(element) {
            var id_order = parseInt(element.replace("check_order_",""));
            orderstocancel.push(id_order);
        });

        if (orderstocancel.length == 0) {
            new PNotify({text: 'Checkbox can\'t be empty.', type: 'warning', hide: true, styling: 'bootstrap3', buttons:{
                sticker: false
            }});
            $scope.waiting_modal=false;
            return false;
        }
        $http({
            url: sendOrdersToCancelUri,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            data: {
                    "idBot": $scope.idBot_selected,
                    "idOrders": orderstocancel,
                    "pair": $scope.PairByBot
                  }
        })
        .then(function (exito) {
            $scope.waiting_modal=false;
            $scope.showActiveOrders($scope.listarActiveOrder[0],$scope.listarActiveOrder[1],$scope.listarActiveOrder[2],$scope.listarActiveOrder[3]);
            
            (exito.data['code']==200) ? Notify('Orders cancelled successfully.','success') : Notify('Error in send cancel order request.','warning'); 
        }, function (error) {
            Notify('Error in send cancel order request.','warning'); 
        })
    }

    /* Function: filtroBotsPorEstado
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: show a message with error in proccess
     */
    $scope.filtroBotsPorEstado = function(){
        switch ($scope.show_BotsByState) {
            case 'show_plays':
                $scope.stateBots = true;
                break;
            case 'show_stops':
                $scope.stateBots = false;
                break;
            case 'show_all':
                $scope.stateBots = '';
                break;
            default:
                $scope.stateBots = '';
                break;
        }
    }

    /* Function: filtroBotsPorUsernameExchange
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: show a message with error in proccess
     */
    $scope.filtroBotsPorUsernameExchange = function(){
        $scope.show_BotsByUsernameExchange = ($scope.show_BotsByUsernameExchange=='' || $scope.show_BotsByUsernameExchange=='AllBots')?'':$scope.show_BotsByUsernameExchange;
        $scope.usernameExchange = $scope.show_BotsByUsernameExchange;
    }

    /* Function: filtroBotsPorUsernameExchange
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: show a message with error in proccess
     */
    $scope.filtroBotsPorTipo = function(){
        $scope.show_BotsByType = ($scope.show_BotsByType=='' || $scope.show_BotsByType=='AllBots')?'':$scope.show_BotsByType;
        $scope.botType = $scope.show_BotsByType;
    }

    /* Function: scrollFunction
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: bring to user to header web page
     */
    window.onscroll = function() {scrollFunction()};
    function scrollFunction() {
        if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
            document.getElementById("Btn_top_webpage").style.display = "block";
        } else {
            document.getElementById("Btn_top_webpage").style.display = "none";
        }
    }

    /* Function: bring_me_to_topWebPage
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: bring to user to header web page
     */
    $scope.bring_me_to_topWebPage = function() {
        document.body.scrollTop = 0;
        document.documentElement.scrollTop = 0;
    }

    /* Function: check_decheck_all
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: bring to user to header web page
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

    /* Function: check_decheck_all
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: bring to user to header web page
     */
     function setWaitings(vec_bots) {
        $scope.waiting_play = [];
        $scope.waiting_cycle = [];
        $scope.waiting_editar = [];
        $scope.waiting_order = [];
        for(var i=0;i<vec_bots.length;i++){
            $scope.waiting_play.push(false);   
            $scope.waiting_cycle.push(false);
            $scope.waiting_editar.push(false);
            $scope.waiting_order.push(false);   
        }
     }      

     /* Function: reorderRows
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: bring to user to header web page
     */
     $scope.reorderRows = function(cabecera) {
        if(!(cabecera=='Pair' || cabecera=='Check')){
            if(cabecera==$scope.headerOrder || $scope.headerOrder==''){
                $scope.order_reverse[cabecera] = !$scope.order_reverse[cabecera];                
            } else {
                $scope.order_reverse[cabecera] = true;
                $scope.order_reverse[$scope.headerOrder] = !$scope.order_reverse[cabecera];
            }
            $scope.order_reverse_flag = !$scope.order_reverse_flag;
            $scope.headerOrder = cabecera;
        }
     }

     /* Function: viewBotsPage
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: bring to user to header web page
     */
    $scope.viewBotsPage = function(page,tipo){
        $scope.inac_pagIzq = (page<=0) ? true : false;
        $scope.paginas_bots = (page<=0) ? 0 : page;
        $scope.inac_pagDer = ($scope.bots_all.length%11==0) ? false : true;
        $scope.paginas_bots = ($scope.bots_all.length%11==0) ? page : page-1;
        if(tipo=='LEFT'){
            $scope.bots_all = $scope.bots_all.slice(0, -11); 
            $scope.bots = $scope.bots.slice(0, -10);
        } else {
            ($scope.switchVerTodos) ? showAllBotYPlay(0,1,'active',$scope.usernameByExchange,$scope.paginas_bots) : showAllBotYPlay(1,1,'active',$scope.usernameByExchange,$scope.paginas_bots);
        }
    }

    /* Function: convertCurrency
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: convert value of first_currency to second_currency
     */
    $scope.convertCurrency = function(max_or_min,cantidad_currency,type, price_in_second_currency){
        
        var e = document.getElementById("select_pairs");
        var strpair = e.options[e.selectedIndex].text;
        var pair_separate = strpair.split("/");

        first_currency = pair_separate[0];
        second_currency = pair_separate[1]; 
        buy_btc_in_usd = $scope.priceBTCinUSD;
    
        if($scope.current_type_coins=='F/F'){

            var par = {};
            $scope.pairs.forEach(function(element){
                par = (element['pair']==first_currency+'/USD') ? element: par;
            });

            $http({
                url: selMarketPricesExchangeUri,
                method: 'POST',
                headers: {
                'Content-Type': 'application/json'
                },
                data: {'idPair':par['idPair']}
            }).then(function (exito) {

                var precio = exito.data['data'][0]['buyMarketPrice'];
                if(type=='CRYP') {
                    $scope.ngBot.maxUSD = precio*$scope.ngBot.maxAmount;
                    $scope.ngBot.minUSD = precio*$scope.ngBot.minAmount;
                } else {
                    $scope.ngBot.maxAmount = $scope.ngBot.maxUSD/precio;
                    $scope.ngBot.minAmount = $scope.ngBot.minUSD/precio;
                }

            },function(error) {
                Notify('Error in get price of '+first_currency+'/BTC.','warning'); 
            })

        } else {

            if(type=='CRYP'){

                // **** MAX TRADING - TO - USD ****
                if(first_currency=='BTC'){
                    convert_to_usd = cantidad_currency*buy_btc_in_usd;
                    $scope.ngBot.maxUSD = (max_or_min=='max')? Math.round(convert_to_usd*100)/100 : $scope.ngBot.maxUSD;
                    $scope.ngBot.minUSD = (max_or_min=='min')? Math.round(convert_to_usd*100)/100 : $scope.ngBot.minUSD;
                }else {
                    switch(second_currency){
                        case 'BTC':
                            convert_to_btc = cantidad_currency*price_in_second_currency;
                            convert_to_usd = convert_to_btc*buy_btc_in_usd;
                            $scope.ngBot.maxUSD = (max_or_min=='max')? Math.round(convert_to_usd*100)/100 : $scope.ngBot.maxUSD;
                            $scope.ngBot.minUSD = (max_or_min=='min')? Math.round(convert_to_usd*100)/100 : $scope.ngBot.minUSD;
                            break;
                        case 'USD':
                            convert_to_usd = cantidad_currency*price_in_second_currency;
                            $scope.ngBot.maxUSD = (max_or_min=='max')? Math.round(convert_to_usd*100)/100 : $scope.ngBot.maxUSD;
                            $scope.ngBot.minUSD = (max_or_min=='min')? Math.round(convert_to_usd*100)/100 : $scope.ngBot.minUSD;
                            break;
                        default:
                            id_first_currency_btc_pair = 0;
                            $scope.pairs.forEach(function(element){
                                id_first_currency_btc_pair = (element['firstCurrency']==first_currency && element['secondCurrency']=='BTC')? element['idPair']:id_first_currency_btc_pair;
                            });
                            $http({
                                url: selMarketPricesExchangeUri,
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                data: {'idPair':id_first_currency_btc_pair}
                            }).then(function (exito) {
                                price_first_currency_in_btc = exito.data['data'][0]['buyMarketPrice'];
                                convert_to_usd = cantidad_currency*price_first_currency_in_btc*buy_btc_in_usd;
                                $scope.ngBot.maxUSD = (max_or_min=='max')? Math.round(convert_to_usd*100)/100 : $scope.ngBot.maxUSD;
                                $scope.ngBot.minUSD = (max_or_min=='min')? Math.round(convert_to_usd*100)/100 : $scope.ngBot.minUSD;
                            },function(error) {
                                Notify('Error in get price of '+first_currency+'/BTC.','warning'); 
                            })
                            break;
                    }    

                }
                // **** MAX TRADING - TO - USD ****

            } else {

                // **** USD - TO - MAX TRADING ****
                if(first_currency=='BTC'){
                    convert_to_cryp = cantidad_currency/buy_btc_in_usd;
                    $scope.ngBot.maxAmount = (max_or_min=='max')? Number(Math.round(convert_to_cryp+'e'+8)+'e-'+8) : $scope.ngBot.maxAmount;
                    $scope.ngBot.minAmount = (max_or_min=='min')? Number(Math.round(convert_to_cryp+'e'+8)+'e-'+8) : $scope.ngBot.minAmount;
                } else {
                    switch(second_currency){
                        case 'BTC':
                            convert_to_btc = cantidad_currency/price_in_second_currency;
                            convert_to_cryp = convert_to_btc/buy_btc_in_usd;
                            $scope.ngBot.maxAmount = (max_or_min=='max')? Number(Math.round(convert_to_cryp+'e'+8)+'e-'+8) : $scope.ngBot.maxAmount;
                            $scope.ngBot.minAmount = (max_or_min=='min')? Number(Math.round(convert_to_cryp+'e'+8)+'e-'+8) : $scope.ngBot.minAmount;
                            break;
                        case 'USD':
                            convert_to_cryp = cantidad_currency/price_in_second_currency;
                            $scope.ngBot.maxAmount = (max_or_min=='max')? Number(Math.round(convert_to_cryp+'e'+8)+'e-'+8) : $scope.ngBot.maxAmount;
                            $scope.ngBot.minAmount = (max_or_min=='min')? Number(Math.round(convert_to_cryp+'e'+8)+'e-'+8) : $scope.ngBot.minAmount;
                            break;
                        default:
                            id_first_currency_btc_pair = 0;
                            $scope.pairs.forEach(function(element){
                                id_first_currency_btc_pair = (element['firstCurrency']==first_currency && element['secondCurrency']=='BTC')? element['idPair']:id_first_currency_btc_pair;
                            });
                            $http({
                                url: selMarketPricesExchangeUri,
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                data: {'idPair':id_first_currency_btc_pair}
                            }).then(function (exito) {
                                price_first_currency_in_btc = exito.data['data'][0]['buyMarketPrice'];
                                convert_to_cryp = cantidad_currency/(price_first_currency_in_btc*buy_btc_in_usd);
                                $scope.ngBot.maxAmount = (max_or_min=='max')? Number(Math.round(convert_to_cryp+'e'+8)+'e-'+8) : $scope.ngBot.maxAmount;
                                $scope.ngBot.minAmount = (max_or_min=='min')? Number(Math.round(convert_to_cryp+'e'+8)+'e-'+8) : $scope.ngBot.minAmount;
                            },function(error) {
                                Notify('Error in get price of '+first_currency+'/BTC.','warning'); 
                            })
                            break;
                    }
                }
                // **** USD - TO - MAX TRADING ****

            }

        }

    }

    /* Function: getPairPorNombre
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: obtain data of pair from name pair
     */
    function getPriceBTCinUSD(){
        $http({
            url:selPairPorNombre,
            method:'POST',
            headers: {
                'Content-Type':'application/json'
            },
            data: {
                    'pair': 'BTC/USD',
                  },
        }).then(function(exito) {
            idpair_btcusd = exito.data['data'];
            $http({
                url: selMarketPricesExchangeUri,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                data: {'idPair':idpair_btcusd}
            }).then(function (exito) {
                $scope.priceBTCinUSD = exito.data['data'][0]['buyMarketPrice'];
            },function(error) {
                Notify('Error in get price of BTC/USD.','warning'); 
            })
        },function(error) {
            Notify('Error in obtain data pair BTC/USD.','warning'); 
        })
    }

    /* Function: cleanAmounts
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: clean min,max amount and min,max usd
     */
    $scope.cleanAmounts = function(){
        if($scope.modificando==false && $scope.ngPair.idPair!=null){        
            $scope.ngBot.minUSD = 0;
            $scope.ngBot.maxUSD = 0;
            $scope.ngBot.minAmount = 0;
            $scope.ngBot.maxAmount = 0;
        }   
    }

    /* Function: refreshPrices
     * Arguments: 
     * Output: -
     * Method: -
     * Summary: vuelve a realizar el calculo USD al par configurado y actualizad el bot config
     */
    function refreshPrices(){

        /*
        * NOTA: Se actualizaran los precios de minAmount y maxAmount segun la actualizacion
        *       de precios de mercado del par y los minUSD y maxUSD se mantendran.
        */

        var pair_selected = $scope.ngBot.pair.split('/');
        var first_currency = pair_selected[0];
        var second_currency = pair_selected[1];

        var price_in_second_currency = $scope.ngPriceMarket.buyMarketPrice;
        var buy_btc_in_usd = $scope.priceBTCinUSD;

        // **** USD - TO - MAX TRADING ****
        if(first_currency=='BTC'){
            var convert_to_cryp_min = $scope.ngBot.minUSD/buy_btc_in_usd;
            var convert_to_cryp_max = $scope.ngBot.maxUSD/buy_btc_in_usd;
            $scope.ngBot.minAmount = Number(Math.round(convert_to_cryp_min+'e'+8)+'e-'+8);
            $scope.ngBot.maxAmount = Number(Math.round(convert_to_cryp_max+'e'+8)+'e-'+8); 
            $scope.updBot();
        } else {
            switch(second_currency){
                case 'BTC':
                    var convert_to_btc_min = $scope.ngBot.minUSD/price_in_second_currency;
                    var convert_to_btc_max = $scope.ngBot.maxUSD/price_in_second_currency;
                    var convert_to_cryp_min = convert_to_btc_min/buy_btc_in_usd;
                    var convert_to_cryp_max = convert_to_btc_max/buy_btc_in_usd;
                    $scope.ngBot.minAmount = Number(Math.round(convert_to_cryp_min+'e'+8)+'e-'+8);
                    $scope.ngBot.maxAmount = Number(Math.round(convert_to_cryp_max+'e'+8)+'e-'+8);
                    $scope.updBot();
                    break;
                case 'USD':
                    var convert_to_cryp_min = $scope.ngBot.minUSD/price_in_second_currency;
                    var convert_to_cryp_max = $scope.ngBot.maxUSD/price_in_second_currency;
                    $scope.ngBot.minAmount = Number(Math.round(convert_to_cryp_min+'e'+8)+'e-'+8);
                    $scope.ngBot.maxAmount = Number(Math.round(convert_to_cryp_max+'e'+8)+'e-'+8);
                    $scope.updBot();
                    break;
                default:
                    var id_first_currency_btc_pair = 0; 
                    $scope.pairs.forEach(function(element){
                        id_first_currency_btc_pair = (element['firstCurrency']==first_currency && element['secondCurrency']=='BTC')? element['idPair']:id_first_currency_btc_pair;
                    });
                    $http({
                        url: selMarketPricesExchangeUri,
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        data: {'idPair':id_first_currency_btc_pair}
                    }).then(function (exito) {
                        var price_first_currency_in_btc = exito.data['data'][0]['buyMarketPrice'];
                        var convert_to_cryp_min = $scope.ngBot.minUSD/(price_first_currency_in_btc*buy_btc_in_usd);
                        var convert_to_cryp_max = $scope.ngBot.maxUSD/(price_first_currency_in_btc*buy_btc_in_usd);
                        $scope.ngBot.minAmount = Math.round(convert_to_cryp_min*100)/100;
                        $scope.ngBot.maxAmount = Math.round(convert_to_cryp_max*100)/100;
                        $scope.updBot();
                    },function(error) {
                        Notify('Error in get price of '+first_currency+'/BTC.','warning'); 
                    })
                    break;
            }
        }
        // **** USD - TO - MAX TRADING ****
    }

    // END BLOQUE 2: AVG - FUNCIONES 


    $scope.updBotConf = function () {
        if ($scope.config.origin === 'F')
            $scope.config.id_coin_fiat = $scope.fiatCoins[$scope.config.id_coin_fiat].id;
        if ($scope.config.origin === 'C')
            $scope.config.id_coin_fiat = $scope.criptoCoins[$scope.config.id_coin_fiat].id;

        $scope.config.tim_trading = $("#timeTrading").val();
        $scope.config.tim_trading = Number($scope.config.tim_trading);
        $scope.config.mar_buy = Number($scope.config.mar_buy);
        $scope.config.mar_sell = Number($scope.config.mar_sell);
        $scope.config.var_sell = Number($scope.config.var_sell);
        $scope.config.var_buy = Number($scope.config.var_buy);
        $scope.config.max_btc = Number($scope.config.max_btc);
        $scope.config.min_btc = Number($scope.config.min_btc);

        if ($scope.switchStatus === true)
            $scope.config.status = 'A';
        else
            $scope.config.status = 'S';

        $http({
            url: apiBotConfig,
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            data: $scope.config
        })
        .then(function (exito) {
            var b = exito.data.datos;
            var obj1 = Object.assign({}, $scope.bots[$scope.indexUpdate], b);
            var obj2 = Object.assign({}, $scope.botsO[$scope.bots[$scope.indexUpdate].index - 1], b);

            $scope.bots[$scope.indexUpdate] = obj1;
            $scope.botsO[$scope.bots[$scope.indexUpdate].index - 1] = obj2;

            $(".select_tipo_trading").select2({
                placeholder: "Tipo Trading",
                allowClear: true
            });
            new PNotify({
                text: 'Bot Modificado con exito.',
                type: 'success',
                hide: true,
                styling: 'bootstrap3'
            });
            $scope.config = {};
            $scope.modificando = false;
            $("#botonCerrarModal").click();
        }, function (error) {
            new PNotify({text: error.data.mensaje, type: 'warning', hide: true, styling: 'bootstrap3'});
        })
    }

    $scope.start = function (index) {
        $('#timer_' + index).timer({
            seconds: 100
        });
    }

    $scope.con_modal = function (type='A', bot=null, index=null) {
        $scope.config = {};
        $scope.apiUsers = [];
        $scope.fiatCoins = [];
        $scope.criptoCoins = [];
        $scope.selectedBot = bot;
        $scope.modificando = false;

        if (type == 'A') {
            $scope.modalTitle = 'Agregar Bots';
        }
        else {
            $scope.indexUpdate = index;
            $scope.modalTitle = 'Modificar Bots';

            $scope.config.id = bot.id;
            $scope.config.status = bot.status;
            $scope.config.max_btc = bot.max_btc;
            $scope.config.min_btc = bot.min_btc;
            $scope.config.var_buy = bot.var_buy;
            $scope.config.var_sell = bot.var_sell;
            $scope.config.id_pair = bot.id_pair;
            $scope.config.name_pair = bot.name_pair;
            $scope.config.id_exchange = bot.id_exchange;
            $scope.config.name_exchange = bot.name_exchange;

            $scope.idApiUserForSeach = bot.id_exchange;
            $scope.idCoinForSearch = $scope.selectedBot.id_coin_fiat;
            $scope.modificando = true;

            $("#timeTrading").val(bot.tim_trading);
            $scope.config.cicleTradingMin = bot.tim_trading;
            $("#timeCompleted").val(bot.tim_completed);
            $scope.config.cicleTradingMin = bot.tim_completed;
            if ((bot.status == 'A') && ($scope.switchStatus != true))
                $("#swich1").click();
            if ((bot.status == 'D') && ($scope.switchStatus == true))
                $("#swich1").click();
        }
        busApiUser();
        busTypeBot();
        busTypeTrading();
    }

    function busCoinID(coin, index) {
        if (coin.id === $scope.idCoinForSearch) {
            $scope.config.id_coin_fiat = angular.copy(index);
            return true;
        }
        else
            return false;
    }

    function busApiUserID(apiUser, index) {
        if (apiUser.id === $scope.idApiUserForSeach) {
            $scope.config.id_api_user = $scope.selectedBot.id_api_user;
            return true;
        }
        else
            return false;
    }

    $scope.onChangeSwichAll = function () {
        ($scope.switchVerTodos) ? getBots(true) : getBots();
    }

    function getBots(all=false) {

        url = apiBotConfig;
        if (all) url = apiBotConfig + '/A';
        $http({
            url: url,
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(function (exito) {
            $scope.bots = exito.data.datos;
        }, function (error) {
            new PNotify({
                text: "Ocurrio un error al obtener los bots",
                type: 'warning',
                hide: true,
                styling: 'bootstrap3',
                animate: {
                    animate: true,
                    in_class: 'bounceInLeft',
                    out_class: 'bounceOutRight'
                }
            });
        })
    }


    function busApiUser(type='P') {
        url = apiApiUser;
        if (type !== 'P')
            url += '/' + type;
        $http({
            url: url,
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(function (exito) {
            $scope.apiUsers = exito.data.datos;
            if ($scope.modificando) {
                $scope.apiUsers.find(busApiUserID);
            }
        }, function (error) {
            new PNotify({
                text: "Ocurrio un error al obtener las monedas",
                type: 'warning',
                hide: true,
                styling: 'bootstrap3'
            });
        })
    }

    function busTypeTrading () {
        $http({
            url: getTypesTrading,
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(function (exito) {
            $scope.TypeTrading = exito.data;
        }, function (error) {
            new PNotify({
                text: "Ocurrio un error al obtener los tipos de bots.",
                type: 'warning',
                hide: true,
                styling: 'bootstrap3'
            });
        })
    }

    function busTypeBot () {
        $http({
            url: getTypesBot,
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(function (exito) {
            $scope.Typebots = exito.data;
        }, function (error) {
            new PNotify({
                text: "Ocurrio un error al obtener los tipos de bots.",
                type: 'warning',
                hide: true,
                styling: 'bootstrap3'
            });
        })
    }

    function busCoin(type='A') {
        factory_coins.getFiatCoins()
        .then(function (response) {
            $scope.fiatCoins = response;
            if ($scope.modificando) {
                c = $scope.fiatCoins.find(busCoinID);
                $scope.config.priceBuyBtc = (c.con_buy * $scope.pricePromedio).toFixed(2);
                $scope.config.priceSellBtc = (c.con_sell * $scope.pricePromedio).toFixed(2);
            }
        });
    }

    function busPlayBot(idBot, index, indice) {
        $scope.listPlayBot = [];
        if($http.pendingRequests.length<=0){
            $http({
                url: listPlayBot,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                data: {"idBot": idBot},
                async: true,
                cache: false,
                timeout: $scope.canceler.promise
            })
            .then(function (exito) {
                $scope.waiting_cycle[indice] = false;
                $(".bs-log-modal-lg").modal();
                $scope.listPlayBot = (exito.data.datos);
                activarTiempoTrading(index);

            }, function (error) {
                var r = $scope.canceler.promise.$$state['status'];
                if(r==1){
                    new PNotify({
                        text: "Ocurrio un error al obtener la lista de plays",
                        type: 'warning',
                        hide: true,
                        styling: 'bootstrap3'
                    });   
                }
            })   
        } else {
            $scope.canceler.resolve();
            var r_1 = $scope.canceler.promise.$$state['status'];
            $scope.canceler = $q.defer();
            var r_2 = $scope.canceler.promise.$$state['status'];
            $http({
                url: listPlayBot,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                data: {"idBot": idBot},
                async: true,
                cache: false,
                timeout: $scope.canceler.promise
            })
            .then(function (exito) {
                $scope.waiting_cycle[indice] = false;
                $(".bs-log-modal-lg").modal();
                $scope.listPlayBot = (exito.data.datos);
                activarTiempoTrading(index);

            }, function (error) {
                if(r_1==r_2){
                    new PNotify({
                        text: "Ocurrio un error al obtener la lista de plays",
                        type: 'warning',
                        hide: true,
                        styling: 'bootstrap3'
                    });
                }
            })
        }

    }

    function activarTiempoTrading(index) {
        var segundos = $scope.bots[index].tim_seconds;
        var tiempo1 = armarDate($scope.bots[index].time_query);
        var tiempo2 = armarDate();
        var dif = tiempo1.getTime() - tiempo2.getTime();
        var segundos_de_T1_a_T2 = dif / 1000;
        var segundos_entre_fechas = Math.abs(segundos_de_T1_a_T2);
    }

    $scope.clickPlayBot = function (index) {
        $scope.listLogPlay = $scope.listPlayBot[index].logs;
        $scope.playData = $scope.listPlayBot[index];
        $scope.verLog = true;
    };

    $scope.gestinarListPlay = function (indice,idBot, index) {
        for(var i=0;i<$scope.waiting_cycle.length;i++){
            $scope.waiting_cycle[i] = false;
        }
        $scope.waiting_cycle[indice] = true;
        $scope.listLogPlay = [];
        $scope.playData = [];

        busPlayBot(idBot, index, indice);
        $scope.botLog = $scope.bots[index];
    };

    $scope.getPairs = function () {
        url = apiApiUser;
        url += '/getPairsExchange'
        $http({
            url: url,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            data: $scope.config.id_exchange
        })
        .then(function (exito) {
            $scope.Pairs = exito.data
        }, function (error) {
            new PNotify({
                text: error.data.mensaje,
                type: 'warning',
                hide: true,
                styling: 'bootstrap3'
            });
        })
    };

    $scope.calcularPrecios = function () {
        getPricesEx($scope.config.id_pair);
        $http({
            url: getMarketPrice,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            //data: $scope.config.id_pair
            data: $scope.exchange.idPair
        })
        .then(function (exito) {
            var info = exito.data;
            $scope.pricesBtc = false;
            if (info.success === true){
                $scope.config.priceBuyBtc = info.datos[0].buy_marketprice;
                $scope.config.priceSellBtc = info.datos[0].sell_marketprice;
                var promedio = info.datos[0].buy_marketprice + info.datos[0].sell_marketprice;
                promedio = promedio/2
                $scope.pricePromedio = promedio
            }
        }, function (error) {
            new PNotify({
                text: "Ocurrio un error al obtener los precios del btc",
                type: 'warning',
                hide: true,
                styling: 'bootstrap3',
                animate: {
                    animate: true,
                    in_class: 'bounceInLeft',
                    out_class: 'bounceOutRight'
                }
            });
        })
    };

    function getPricesEx(id_pair) {
        $http({
            url: getPricesExchange,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            data: id_pair
        })
        .then(function (exito) {
            for (var i = 0; i < exito.data.length; i++) {
                if (i == 0){
                    $scope.linkApiOne = exito.data[i].link;
                    $scope.priceApiOne = exito.data[i].price
                }else if (i == 1){
                    $scope.linkApiTwo = exito.data[i].link;
                    $scope.priceApiTwo = exito.data[i].price
                }else{
                    $scope.linkApiThre = exito.data[i].link;
                    $scope.priceApiThre = exito.data[i].price
                }
            }
        }, function (error) {
            new PNotify({
                text: "Ocurrio un error al obtener los precios del btc",
                type: 'warning',
                hide: true,
                styling: 'bootstrap3',
                animate: {
                    animate: true,
                    in_class: 'bounceInLeft',
                    out_class: 'bounceOutRight'
                }
            });
        })
    }

    function acivarNotificacionSockect(order) {
    }

    function procesarRespuestaSockect(respuesta) {
        if (respuesta.buy) {
            response = respuesta.buy.response;
            response = JSON.parse(response);
            if (respuesta.buy.status == 'E') {
                $scope.bots[botsId[respuesta.buy.id_bot_config]].noti += 1;
                new PNotify({
                    text: response.order.msg,
                    type: 'warning',
                    hide: true,
                    styling: 'bootstrap3'
                });
            } else {
                $scope.bots[botsId[respuesta.buy.id_bot_config]].noti += 1;
                new PNotify({
                    text: response.order.msg,
                    type: 'success',
                    hide: true,
                    styling: 'bootstrap3'
                })
            }
        }
        if (respuesta.sell) {
            response = respuesta.sell.response;
            response = JSON.parse(response);
            if (respuesta.sell.status == 'E') {
                $scope.bots[botsId[respuesta.sell.id_bot_config]].noti += 1;
                new PNotify({
                    text: response.order.msg,
                    type: 'warning',
                    hide: true,
                    styling: 'bootstrap3'
                });
            } else {
                $scope.bots[botsId[respuesta.sell.id_bot_config]].noti += 1;
                new PNotify({
                    text: response.order.msg,
                    type: 'success',
                    hide: true,
                    styling: 'bootstrap3'
                });
            }
        }
    }

    $(document).ready(function () {
        var connection = new autobahn.Connection({
            url: urlWebSocket,
            realm: 'realm1'
        });

        $(".select_api_user").select2({
            placeholder: "Select Exchange",
            allowClear: true
        });

        $(".select_pairs").select2({
            placeholder: "Select Pairs",
            allowClear: true
        });

        $(".select_typebots").select2({
            placeholder: "Select Type Bot",
            allowClear: true
        });

        $(".select_typetrading").select2({
            placeholder: "Select Type Trading",
            allowClear: true
        });

        $(".select2-container--default").css("width", "100%");

        $(".select2-search__field").css("z-index", "110000");
    });

    $(".knob").knob({
        min: 1,
        max: 360,
        change: function (value) {
        },
        release: function (value) {
        },
        cancel: function () {
        },

        draw: function () {
            if (this.$.data('skin') == 'tron') {

                this.cursorExt = 0.3;

                var a = this.arc(this.cv) // Arc
                    ,
                    pa // Previous arc
                    , r = 1;

                this.g.lineWidth = this.lineWidth;

                if (this.o.displayPrevious) {
                    pa = this.arc(this.v);
                    this.g.beginPath();
                    this.g.strokeStyle = this.pColor;
                    this.g.arc(this.xy, this.xy, this.radius - this.lineWidth, pa.s, pa.e, pa.d);
                    this.g.stroke();
                }

                this.g.beginPath();
                this.g.strokeStyle = r ? this.o.fgColor : this.fgColor;
                this.g.arc(this.xy, this.xy, this.radius - this.lineWidth, a.s, a.e, a.d);
                this.g.stroke();

                this.g.lineWidth = 2;
                this.g.beginPath();
                this.g.strokeStyle = this.o.fgColor;
                this.g.arc(this.xy, this.xy, this.radius - this.lineWidth + 1 + this.lineWidth * 2 / 3, 0, 2 * Math.PI, false);
                this.g.stroke();

                return false;
            }
        }
    });

    $("#boton1").hover(
        function () {
            calVarCompra("Calculo de variación de compra", parseFloat($scope.config.priceBuyBtc ? $scope.config.priceBuyBtc : 0), $scope.config.var_buy ? ($scope.config.var_buy / 100) : 0);
        }, function () {
            tooltip.remove();
        }
    );

    $("#boton2").hover(
        function () {
            calVarCompra("Calculo de variación de venta", parseFloat($scope.config.priceSellBtc ? $scope.config.priceSellBtc : 0), $scope.config.var_sell ? ($scope.config.var_sell / 100) : 0);
        }, function () {
            tooltip.remove();
        }
    );

    $("#boton3").hover(
        function () {
            calLimites("Límite para Cancelar Órdenes de Compra", parseFloat($scope.config.priceBuyBtc ? $scope.config.priceBuyBtc : 0), $scope.config.mar_buy ? ($scope.config.mar_buy / 100) : 0);
        }, function () {
            tooltip.remove();
        }
    );

    $("#boton4").hover(
        function () {
            calLimites("Límite para Cancelar Órdenes de Venta", parseFloat($scope.config.priceSellBtc ? $scope.config.priceSellBtc : 0), $scope.config.mar_sell ? ($scope.config.mar_sell / 100) : 0);
        }, function () {
            tooltip.remove();
        }
    );

    $(".hoverTrading").hover(
        function () {
            hoverTimeTradin(332, 1);
        }, function () {
            tooltip.remove();
        }
    );

    $scope.addBotConfig = function () {
        $scope.config.tim_trading = Number($("#timeTrading").val());
        $scope.config.tim_completed = Number($("#timeCompleted").val());
        $scope.config.id_pair = Number($scope.config.id_pair);
        $scope.config.id_exchange = Number($scope.config.id_exchange);
        $scope.config.var_sell = Number($scope.config.var_sell);
        $scope.config.var_buy = Number($scope.config.var_buy);
        $scope.config.max_btc = Number($scope.config.max_btc);
        $scope.config.min_btc = Number($scope.config.min_btc);
        // $scope.config.type_bot = $scope.config.type_bot;
        $scope.config.type_trading = Number($scope.config.type_trading);

        $http({
            url: apiBotConfig,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            data: $scope.config
        })
        .then(function (exito) {
            var succBots = exito.data.datos;
            $scope.bots.push(succBots);
            $scope.config = {};
            $scope.fiatCoins = [];
            $scope.apiUsers = [];
            $("#timeTrading").val(1);
            new PNotify({
                text: 'Bot agregado con exito.',
                type: 'success',
                hide: true,
                styling: 'bootstrap3'
            });
            $("#closeModalBots").click();
        }, function (error) {
            new PNotify({
                text: error.data.mensaje,
                type: 'warning',
                hide: true,
                styling: 'bootstrap3'
            });
        })
    };

    function calLimites(title, precio, por) {
        diferencia = por * precio;
        min = precio - diferencia;
        max = precio + diferencia;
        tooltip = new PNotify({
            title: title,
            text:
            "Maximo:" + max.toFixed(2) + " <br>"
            + "Minimo:" + min.toFixed(2),
            hide: false,
            styling: 'bootstrap3',
            type: 'success',
            buttons: {
                closer: false,
                sticker: false
            },
            history: {
                history: false
            },
            animate_speed: "fast",
            opacity: .5,
            icon: "fa fa-calculator",
            stack: false,
            auto_display: false
        });
        tooltip.get().mouseout(function () {
            tooltip.remove();
        });
        tooltip.open();
    }

    function calVarCompra(title, precio, por) {
        diferencia = por * precio;
        var vario = precio + diferencia;
        vario = vario.toFixed(2);
        tooltip = new PNotify({
            title: title,
            text: "Variación de " + precio + " a " + vario + " <br>"
            + "Porcentaje:" + por * 100 + "% <br>"
            + "Diferencia de:" + diferencia.toFixed(2),
            hide: false,
            styling: 'bootstrap3',
            type: 'info',
            buttons: {
                closer: false,
                sticker: false
            },
            history: {
                history: false
            },
            animate_speed: "fast",
            opacity: .5,
            icon: "fa fa-calculator",
            stack: false,
            auto_display: false
        });
        tooltip.get().mouseout(function () {
            tooltip.remove();
        });
        tooltip.open();
    }

    $scope.hoverDataSend = function (index) {
        info = {
            hide: false, buttons: {closer: false, sticker: false}, history: {history: false},
            styling: 'bootstrap3', animate_speed: "fast", opacity: .5, stack: false, auto_display: false,
            type: 'info', icon: 'fa fa-list'
        };

        info.title = "<center>Data enviada APINKA</center>";
        info.text = '{"key":"' + $scope.listLogPlay[index].response.order.dataSend.key + '", <br>';
        info.text += '"secret":"' + $scope.listLogPlay[index].response.order.dataSend.key + '", <br>';
        info.text += '"new":{"amount":' + $scope.listLogPlay[index].response.order.dataSend.new.amount + ',"currency":"' + $scope.listLogPlay[index].response.order.dataSend.new.currency + '",<br>';
        info.text += '"price":' + $scope.listLogPlay[index].response.order.dataSend.new.price + ',"type":"' + $scope.listLogPlay[index].response.order.dataSend.new.type + '"}}';
        tooltip = new PNotify(info);
        tooltip.open();
    };

    $scope.hoverOrderCancel = function (index) {
        info = {
            hide: false, buttons: {closer: false, sticker: false}, history: {history: false},
            styling: 'bootstrap3', animate_speed: "fast", opacity: .5, stack: false, auto_display: false,
            type: 'danger', icon: 'fa fa-list'
        };

        ordenes = "";
        if ($scope.listLogPlay[index].response.cancel.data === undefined)
            ordenes = 'Sin ordenes';
        else {
            for (i = 0; $scope.listLogPlay[index].response.cancel.data.length > i; i++) {
                if (i % 2 === 0)
                    ordenes += $scope.listLogPlay[index].response.cancel.data[i] + ','
                if (i % 4 === 0)
                    ordenes += "<br>"
            }
        }

        ($scope.listLogPlay[index].response.cancel.response === undefined) ? mensaje = "No se cancelaron las ordenes" : mensaje = $scope.listLogPlay[index].response.cancel.response;

        if ($scope.listLogPlay[index].response.cancel.dataSend === undefined)
            dataSend = "{}";
        else {
            dataSend = '{';
            dataSend += '"key":"' + $scope.listLogPlay[index].response.cancel.dataSend.key + '", <br>';
            dataSend += '"secret":"' + $scope.listLogPlay[index].response.cancel.dataSend.secret + '", <br>';
            dataSend += '"type":"' + $scope.listLogPlay[index].response.cancel.dataSend.type + '", <br>';
            dataSend += '"Currency":"' + $scope.listLogPlay[index].response.cancel.dataSend.Currency + '"}';
        }

        info.title = "<center>Ordenes canceladas APINKA</center>";
        info.text = 'Mensaje:"' + mensaje + '", <br>';
        info.text += 'Ordenes Canceladas:' + ordenes + ' <br>';
        info.text += 'DataSend:' + dataSend + ' <br>';
        tooltip = new PNotify(info);
        tooltip.open();
    };

    function armarDate(fecha=null) {
        if (fecha != null) {
            var res = fecha.split(" ");
            var fecha = res[0];
            var hora = res[1];
            var fechaDiv = fecha.split("-");
            var horaDiv = hora.split(":");
            var date1 = new Date(
                fechaDiv[0],
                fechaDiv[1] - 1,
                fechaDiv[2],
                horaDiv[0],
                horaDiv[1],
                horaDiv[2],
                0
            );
        } else {
            var now = new Date();
            var nowyear = now.getFullYear();
            var nowmonth = now.getMonth();
            var nowday = now.getDate();
            var nowhour = now.getHours();
            var nowminute = now.getMinutes();
            var nowsecond = now.getSeconds();
            var date1 = new Date(nowyear, nowmonth, nowday, nowhour, nowminute, nowsecond, 0);
        }
        return date1
    }

    $scope.hoverPlay = function () {
        info = {
            hide: false, buttons: {closer: false, sticker: false}, history: {history: false},
            styling: 'bootstrap3', animate_speed: "fast", opacity: .5, stack: false, auto_display: false,
            type: 'success', icon: 'fa fa-info',addclass: 'infoEnPlay'
        };
        info.title = "<center>Información Play Bot</center>";
        info.text = " <center>Al darle play al bot este se encargara de generar ";
        info.text += "ordener de compra, venta o ambas dependiendo de la configuración ";
        info.text += "que tenga el bot en el select de tipo de trading, estas ordenes ";
        info.text += "se generaran consecutivamente pase el tiempo de trading que el bot tiene ";
        info.text += "configurado. ";
        tooltip = new PNotify(info);
        tooltip.open();
    };

    var sum = function(id){
        $scope.timeIds[id] = {time: ++$scope.timeIds[id].time};
    };

    $scope.hoverTradin = function (index) {
        const id = $scope.bots[index].general.idBot;
        // setInterval(sum(id), 8000);
        info = {
            hide: false, buttons: {closer: false, sticker: false}, history: {history: false},
            styling: 'bootstrap3', animate_speed: "fast", opacity: .5, stack: false, auto_display: false,
            type: 'info', icon: 'fa fa-list', addclass: 'infoEnPlay'
        };
        info.title  =  "<center>Información de trading</center>";
        info.text   =  "<center>Tiempo de bot en play:";
        info.text   += "<div id=htime"+id+"><div></center>";
        info.text   += "<br><center>Count of Plays Executed:</center>";
        info.text   += "<center>"+($scope.bots[index].play.contPlays+1)+"</center>";
        tooltip = new PNotify(info);
        tooltip.open();
        runForever(index);
        clearTimeout(runForever);
    };

    $scope.play = function (index) {

        if ($scope.bots[index].typ_trading == null){
            alert("Insert type order.")
        } else {
            $scope.setTimer(index, $scope.bots[index].idBot);
            var play = {};
            var o = $scope.bots[index];
            // if data['ATE'] < data['ET']
            // if data['ATC'] < (data['ET'] - data['CT'])

            play.id_bot_configuration = $scope.bots[index].id;
            play.order_type = $scope.bots[index].typ_trading;
            // Hardcodeado hasta nuevo aviso
            play.ATE = 1;
            play.ATC = 2;
            play.ET = 4;
            play.CT = 1;

            $http({
                url: botPlay,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                data: play
            }).then(function (exito) {
                if(exito.hasOwnProperty("config")){
                    var datPlay = exito.config;

                    $scope.bots[index].id_play = datPlay.data.id_bot_configuration;

                    if($scope.bots[index].id_play){
                        new PNotify({
                            text: 'Bot Activado.',
                            type: 'success',
                            hide: true,
                            styling: 'bootstrap3'
                        });
                    }
                } else {
                    new PNotify({
                        text: 'Oh noes! There was an error playing your bot',
                        type: 'error',
                        hide: true,
                        styling: 'bootstrap3'
                    });
                }
            }, function (error) {

                if( error.hasOwnProperty("data") && error.hasOwnProperty("mensaje")) {
                    new PNotify({
                        text: error.data.mensaje,
                        type: 'warning',
                        hide: true,
                        styling: 'bootstrap3'
                    });
                } else {
                    new PNotify({
                        text: 'Error al activar el bot, estamos trabajando en eso...',
                        type: 'warning',
                        hide: true,
                        styling: 'bootstrap3'
                    });
                }
            })
        }
    };

    function runForever(index){
        var id = ($scope.bots[index].general['idBot']?$scope.bots[index].general['idBot']:0);
        var m1 = (moment($scope.bots[index].play.playDate, 'YYYY-MM-DD HH:mm:ss'));   //var m1 = new Date($scope.bots[index].play.playDate);
        var m2 = (moment(moment().format(), 'YYYY-MM-DD HH:mm:ss'));                  //var m2 = new Date();
        var diff = moment.preciseDiff(m1,m2);
        $('#htime' + id).text(diff);
        setTimeout(runForever, 1000, index);
    }

    $scope.setTimer = function(rowIndex, idbot, isStop=false){
        //setTimeIdsElement(idbot, $scope.bots[rowIndex].bot_play_date);
        setTimeIdsElement(idbot, '2018-08-17 20:05:20');
    };

    var setTimeIdsElement = function (id, date) {
        $scope.timeIds[id] = {time: date};
    };

    $scope.getTimeIdsElement = function (id) {
        return $scope.timeIds[id].time;
    };

    $scope.stop = function (index) {

        var stop = {};
        var o = $scope.bots[index];
        stop.idPlay = $scope.bots[index].id_play;

        $http({
            url: botStop,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            data: stop
        }).then(function (exito) {
            $scope.setTimer(index, $scope.bots[index].id, true);
            // var datStop = exito.data.datos;
            // $scope.bots[index].id_play = null;
            $scope.bots[index].typ_trading = '';
            $scope.bots[index].tim_seconds = 0;
            new PNotify({
                text: 'Bot Desactivado.',
                type: 'success',
                hide: true,
                styling: 'bootstrap3'
            });
        }, function (error) {
            new PNotify({
                text: error.data.mensaje,
                type: 'warning',
                hide: true,
                styling: 'bootstrap3'
            });
        })
    };

    $scope.hoverMovimiento = function () {
        tooltip.get().css({'top': event.clientY + 12, 'left': event.clientX + 12})
    };

    $scope.hoverTradinD = function () {
        $('.infoEnPlay').remove();
    };

    // BEGIN BLOQUE 3: AVG - FUNCIONES INI 

    // Funciones al cargar WebPage:
    findExchangeBitinka();

    // END BLOQUE 3: AVG - FUNCIONES INI

    var elem2 = document.querySelector('#swich1');
    var init2 = new Switchery(elem2, {color: '#26B99A'});
    var elem3 = document.querySelector('#swichVerBots');
    var init3 = new Switchery(elem3, {color: '#26B99A'});
    
    function clearData() {
        delete $scope.listPlayBot;
        delete $scope.playData;
    }

    $scope.campoPrice = function(){
        if($scope.filterPrice.length>0 && $scope.tipoFiltro.length>0){
            $scope.filtros($scope.filterPrice,$scope.tipoFiltro);
        }else{
            $scope.activeOrders=$scope.dataFiltros;
        }
    }

    $scope.filtros =function(number,tipoFiltro){
        $scope.dataFiltros;
        var output=[];
      
        if(tipoFiltro=="mayor"){
            $scope.activeOrders=$scope.dataFiltros;
            if(isNaN(number) || number=="" || number.length==0){
                new PNotify({text: 'Price can\'t be empty.', type: 'warning', hide: true, styling: 'bootstrap3', buttons:{
                sticker: false
                }});
                return false;
            }else{
                for(item in $scope.activeOrders){
                    if(number<$scope.activeOrders[item].Price){
                        output.push($scope.activeOrders[item]);
                    }
                }
                return $scope.activeOrders=output;
            }
        }else if(tipoFiltro=="menor"){
            $scope.activeOrders=$scope.dataFiltros;
            if(isNaN(number) || number=="" || number.length==0){
                new PNotify({text: 'Price can\'t be empty.', type: 'warning', hide: true, styling: 'bootstrap3', buttons:{
                sticker: false
                }});
                return false;
            }else{
                for(item in $scope.activeOrders){
                    if(number>$scope.activeOrders[item].Price){
                        output.push($scope.activeOrders[item]);
                    }
                }
                return $scope.activeOrders=output;
            }
        }else if(tipoFiltro=="mayor" && $scope.filterPrice.length>0){
                for(item in $scope.activeOrders){
                    if(number<$scope.activeOrders[item].Price){
                        output.push($scope.activeOrders[item]);
                    }
                }
                return $scope.activeOrders=output;
            
        }else if(tipoFiltro=="menor" && $scope.filterPrice.length>0){
                            for(item in $scope.activeOrders){
                    if(number>$scope.activeOrders[item].Price){
                        output.push($scope.activeOrders[item]);
                    }
                }
                return $scope.activeOrders=output;
        }else if(tipoFiltro=="salir"){
            $scope.filterPrice="";
            $scope.tipoFiltro="";
            $scope.activeOrders=$scope.dataFiltros;
            return $scope.activeOrders;
        }else{
            $scope.activeOrders=$scope.dataFiltros;
            return $scope.activeOrders;
        }
}


}]);

angular.element(function () {
    angular.bootstrap(document, ['coreModule']);
});