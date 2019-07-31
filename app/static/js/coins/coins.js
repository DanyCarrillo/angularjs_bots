app.config(function ($routeProvider) {
    $routeProvider
        .when('/', {
            templateUrl: '../static/html/coinsListar.html',
            controller: 'coinsController'
        })
});

app.controller('coinsController', ["$scope", "$http", "factory_coins", "factory_endPoints", function ($scope, $http, factory_coins, factory_endPoints) {
    apiCoins = factory_endPoints.getEndPoints('coins');
    apiDelLink = factory_endPoints.getEndPoints('delLink');
    apiUpdLinks = factory_endPoints.getEndPoints('updLinks');
    apiLoadLinks = factory_endPoints.getEndPoints('loadLinks');
    getApiResponse = factory_endPoints.getEndPoints('getApiResponse');

    $scope.co = {};
    $scope.coins = [];
    $scope.dataApi = [];
    $scope.switchStatus = false;
    $scope.coin_refHide=false;

    coords = []

    getAllCoins();

    function getAllCoins() {

        factory_coins.getAllCoins().then(function (response) {
            $scope.coins = response;
            if ($scope.operatingAfill == true) {
                $scope.abrirPantalla('M', $scope.coins[$scope.indexCoinSelected], $scope.indexCoinSelected);
                $scope.operatingAfill = false;
                $scope.gestionarMoneda = false;
            }
        })
    };

    $scope.abrirPantalla = function (tipo='A', coin=null, index) {
        $scope.responseApiShow = false;
        if ($scope.eliCoin != true) {
            if (tipo == "M" || ($scope.modCoin == true && tipo == 'A')) {

                $scope.gestionarMoneda = false;
                $scope.modCoin = false;
                $scope.swichModCoin = false;
                $scope.co = {};
                if ($scope.switchStatus == true) {
                    $scope.switchStatus = false;
                    $("#swich1").click();
                }

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 }
            if ($scope.gestionarMoneda != true) {
                $scope.swichModCoin = false;
                $scope.gestionarMoneda = true;
                if (tipo == 'A') {
                    $scope.titleOperacion = 'Add new currency';
                    $scope.switchForced = false;
                    $scope.modificando = false;
                    $scope.disable_coName=false;
                } else {
                    $scope.co.links = {};
                    $scope.co.links.one = {};
                    $scope.modificando = true;
                    $scope.coinModif = coin;
                    $scope.api_links = coin.api_links;
                    $scope.titleOperacion = 'Edit currency';
                    $scope.indexCoinSelected = index;
                    $scope.co.id = coin.id;
                    $scope.swichModCoin = true;
                    $scope.modCoin = true;
                    $scope.disable_coName=true;
                    $scope.co.name = coin.name;
                    $scope.co.type = coin.type;
                    $scope.co.con_buy = coin.con_buy;
                    $scope.co.con_sell = coin.con_sell;
                    $scope.co.meth = coin.meth;
                    $scope.co.coin_ref = coin.coin_ref;
                    $scope.co.param = coin.param;
                    $scope.co.data_type = coin.data_type;

                    $scope.co.marGain = coin.mar_gain;
                    $scope.co.marAboveMarket = coin.mar_abo_market;
                    $scope.co.status = coin.status;
                    if (coin.status == 'A') {
                        $scope.switchStatus = true;
                        $("#swich1").click();
                    } else
                        $scope.switchStatus = false;
                    }
                    /*if($scope.co.type=="F" && $scope.co.type!=null){
                        $scope.coin_refHide=true;
                    }else{
                        $scope.coin_refHide=true;
                    }*/

            }
        }
    };

    $scope.enviarMoneda = function () {
        if ($scope.co.name == null) {
            new PNotify({text: 'Currency name can\'t be empty.', type: 'warning', hide: true, styling: 'bootstrap3', buttons:{
                    sticker: false
                }});
            return false;
        }else if($scope.co.con_buy==null){
            new PNotify({text: 'Buy price can\'t be empty.', type: 'warning', hide: true, styling: 'bootstrap3', buttons:{
                    sticker: false
                }});
            return false;
        }else if($scope.co.con_sell == null){
              new PNotify({text: 'Sell price can\'t be empty.', type: 'warning', hide: true, styling: 'bootstrap3', buttons:{
                    sticker: false
                }});
            return false;
        }else if($scope.co.type=='C' && $scope.co.data_type==null){
            new PNotify({text: 'Structure can\'t be empty.', type: 'warning', hide: true, styling: 'bootstrap3', buttons:{
                    sticker: false
                }});
            return false;
        }else if($scope.co.type=='C' && $scope.co.meth==null){
            new PNotify({text: 'Method can\'t be empty.', type: 'warning', hide: true, styling: 'bootstrap3', buttons:{
                sticker: false
            }});
            return false;
        }else if($scope.co.type=='C' && $scope.co.links==null){
            new PNotify({text: 'Api link can\'t be empty.', type: 'warning', hide: true, styling: 'bootstrap3', buttons:{
                sticker: false
            }});
            return false;
        }

        links = [];

        if ($scope.co.links){
            links.push($scope.co.links.one);
            for (index in links) {
                if (links[index]){
                    if (links[index].status == 'OK'){
                        links[index].acepted = true;
                        links[index].coin_ref = $scope.co.coin_ref;
                        links[index].data_type = $scope.co.data_type;
                        links[index].link = links[index].linkCrip;
                        links[index].meth = $scope.co.meth;
                        links[index].param = $scope.co.param == undefined ? '' : $scope.co.param;
                    }else
                        links[index].acepted = false
                    delete $scope.co.param;
                    delete $scope.co.coin_ref;
                    delete $scope.co.data_type;
                    delete $scope.co.meth;
                    delete links[index].linkCrip;
                    delete links[index].status;
                }
            }
        }
        $scope.co.links = links;
        $http({
            url: apiCoins,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            data: $scope.co
        })
        .then(function (exito) {
            if(exito.data.success==true){
            //$scope.coins = [];
            //$scope.coins.push(exito.data.datos[0]);
            new PNotify({text: 'Currency has been save successfully.', type: 'success', hide: true, styling: 'bootstrap3', buttons:{
                    sticker: false
                }});
            $scope.co = {};
            $scope.gestionarMoneda = false;
            getAllCoins();

            }else if(exito.data.success==false){
                $scope.co = {};
                new PNotify({text: exito.data.msg[0][0], type: 'warning', hide: true, styling: 'bootstrap3', buttons:{
                    sticker: false
                }});
            }else{
                $scope.co = {};
                new PNotify({text: 'Currency can\'t be save.', type: 'warning', hide: true, styling: 'bootstrap3', buttons:{
                    sticker: false
                }});
            }
        }, function (error) {
            $scope.co = {};
            new PNotify({text: 'Api link can\'t be save.' , type: 'warning', hide: true, styling: 'bootstrap3', buttons:{
                    sticker: false
                }});
            getAllCoins();
        });
    };

    $scope.modificarMoneda = function () {
        if($scope.co.con_buy==null){
            new PNotify({
                text: 'Buy price can\'t be empty.', 
                type: 'warning', 
                hide: true, 
                styling: 'bootstrap3', 
                buttons:{
                    sticker: false
                }
            });
            return false;
        }else if($scope.co.con_sell == null){
            new PNotify({
                text: 'Sell price can\'t be empty.', 
                type: 'warning', 
                hide: true, 
                styling: 'bootstrap3', 
                buttons:{
                    sticker: false
                }
            });
            return false;
        }
        ($scope.switchStatus == true) ? $scope.co.status = 'A' : $scope.co.status = 'S';
        ($scope.switchForced == true) ? $scope.co.forced = true : $scope.co.forced = false;
        $http({
            url: apiCoins,
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            data: $scope.co
        })
            .then(function (exito) {
                if(exito.data.datos!=null){
                $scope.coins[$scope.indexCoinSelected] = exito.data.datos;
                new PNotify({text: 'Currency has been save successfully.', type: 'success', hide: true, styling: 'bootstrap3', buttons:{
                    sticker: false
                }});
                $scope.co = {};
                $scope.modCoin = false;
                $scope.indexCoinSelected = null;
                $scope.gestionarMoneda = false;
                getAllCoins();
                }else{
                     new PNotify({text: 'No se pudo modificar.', type: 'warning', hide: true, styling: 'bootstrap3', buttons:{
                    sticker: false
                }});
                }
            }, function (error) {
                new PNotify({text: error.data.mensaje, type: 'warning', hide: true, styling: 'bootstrap3', buttons:{
                    sticker: false
                }});
            })
    }

    $scope.veriLink = function (num) {
        if ($scope.co.meth == null) {
            alert('Unregistered method.');
            return false;
        }

        var link = '';
        if (num == 1 && $scope.co.links.one.linkCrip.length > 0) {
            link = $scope.co.links.one.linkCrip;
            $scope.co.links.one.status = 'B';
        }
        if (link.length > 0) {
           var data = {
                    'params': $scope.co.param,
                    'method': $scope.co.meth,
                    'link': link
                };
            $http({
                        url: getApiResponse,
                        method: 'POST',
                        data: data,
                        headers: {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*',
                            'accept': 'application/json, application/xml',
                        },
                    }).then(function (exito) {
                        if (num == 1) {
                            $scope.co.links.one.status = 'OK';
                            $scope.dataApi[1] = exito.data;
                        }
                    }, function (error) {
                        if (num == 1)
                            $scope.co.links.one.status = 'E'
                    });
        } else {
            if (num == 1)
                $scope.co.links.one.status = null
        }
    }

    $scope.getApiValue = function (apiNum) {
        getApiValue(apiNum)

    };

    $scope.nextKey = function (key) {
        var msj="";
        var val_coord=$scope.responseApiBtc[key];
        var confirmar;
        var cancel;
        coords.push(key);
        valueApiShow = $scope.initValueApi;
        if ($scope.valueApi == true) {
            responseApiShow = false;
            if ($scope.apiCoord.buy == undefined){
                $scope.apiCoord.buy = coords;

                $scope.responseApiBtc = $scope.initValueApi;
                $scope.co.links.one.coordinates = {'buy':$scope.apiCoord.buy};
                msj = 'The coordinate of Buy is: ';
                confirmar=1;
                cancel=1;
                coords = [];
                getApiValue(1, true);
            }else{
                $scope.responseApiBtc = $scope.initValueApi;
                $scope.apiCoord.sell = coords;
                $scope.co.links.one.coordinates = {'sell':$scope.apiCoord.sell} ;
                msj = 'The coordinate of Sell is: ';
                coords = [];
                getApiValue(1, true);
                confirmar=2;
                cancel=2;
            }
            (new PNotify({
                title: 'Add api values',
                text:  msj+val_coord,
                icon: 'fa fa-plus',
                hide: false,
                type: 'success',
                styling: 'bootstrap3',
                confirm: {
                    confirm: true,
                    buttons: [{text: 'Accept'}, {text: 'Cancel', addClass: 'btn btn-danger'}]
                },
                buttons: {
                    closer: false,
                    sticker: false,
                },
                addclass: 'stack-modal',
                stack: {
                    'dir1': 'down',
                    'dir2': 'right',
                    'modal': true
                }
            })).get().on('pnotify.confirm', function () {
                $('.ui-pnotify-modal-overlay').remove();
                if(confirmar==2){
                    $scope.responseApiShow = false;
                    $scope.co.links.one.coordinates = {'buy':$scope.apiCoord.buy, 'sell':$scope.apiCoord.sell} ;
                    $scope.apiCoord = [];
                    $scope.responseApiBtc = $scope.initValueApi;
                }else{
                    $scope.co.links.one.coordinates;
                    $scope.responseApiShow = true;
                }
            }).on('pnotify.cancel', function () {
                if(cancel==1){
                    $scope.responseApiBtc = $scope.initValueApi;
                    $scope.apiCoord=[];
                }else if(cancel==2){
                    $scope.responseApiBtc = $scope.initValueApi;
                    $scope.co.links.one.coordinates;
                    $scope.apiCoord.pop();
                }
                $('.ui-pnotify-modal-overlay').remove();
            });

        }
        else {
            $scope.responseApiBtc = $scope.responseApiBtc[key];

        }
    };

    $scope.checkKeyType = function (key) {
        $scope.valueApi = null;
        if (angular.isObject($scope.responseApiBtc[key]) || Array.isArray($scope.responseApiBtc[key]))
            $scope.valueApi = false;
        else if (typeof $scope.responseApiBtc[key] == 'string' || typeof $scope.responseApiBtc[key] == 'number')
            $scope.valueApi = true;
        else
            $scope.valueApi = null;
    };

    $scope.backObjectApi = function () {
        $scope.responseApiBtc = $scope.initValueApi;
        $scope.apiCoord = [];
    };

    function getApiValue(apiNum, flag=false) {
        $scope.apiNum = apiNum;
        if (flag == false){
            $scope.apiCoord = [];
            coords = [];
        }
        $scope.responseApiBtc = $scope.dataApi[apiNum];
        $scope.initValueApi = $scope.responseApiBtc;
        linkApi = apiNum;
        $scope.responseApiShow = true;
    };
    
    function setApiValue() {
        if ($scope.apiNum == 1)
            $scope.co.links.one.coordinates = {'buy':$scope.apiCoord.buy, 'sell':$scope.apiCoord.sell} ;
        //$scope.responseApiShow = false;
        $scope.apiCoord = [];
        $scope.responseApiBtc = $scope.initValueApi;
    };

    $scope.addApiLink = function () {
        $scope.co.data_type=null;
        $scope.co.meth=null;
        $scope.co.param=null;
        $scope.co.coin_ref=null
        $scope.responseApiShow = false;
        $scope.affiliating = true;
        $scope.co.links.one.linkCrip = null;
        $scope.co.links.one.status = null;
        $scope.co.links.one.coordinates=null;

    };

    $scope.saveApiLink = function () {
        links = [];
        objectAffiliation = {};
        $scope.operatingAfill = true;

        links.push($scope.co.links.one);

        for (index in links) {
            links[index].link = links[index].linkCrip;
            if (links[index].status == 'OK'){
                links[index].acepted = true;
                links[index].meth = $scope.co.meth;
                links[index].param = $scope.co.param == undefined ? '' : $scope.co.param;
                links[index].data_type = $scope.co.data_type;
                links[index].coin_ref = $scope.co.coin_ref == null ? '' : $scope.co.coin_ref;
            }
            else
                links[index].acepted = false;
            delete links[index].linkCrip;
            delete links[index].status;
        }

        objectAffiliation.links = links;
        objectAffiliation.id_criptocoin = $scope.co.id;
        objectAffiliation.id_coin_fiat = $scope.co.id_coin_fiat;
        $http({
            url: apiLoadLinks,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            data: objectAffiliation
        }).then(function (exito) {
            if(exito.data.success===true){
                $scope.gestionarMoneda = false;
                getAllCoins();
                $scope.gestionarMoneda = false;
            new PNotify({text: "Api link has been add successfully", type: 'success', hide: true, styling: 'bootstrap3', buttons:{
                    sticker: false
                }});
            }else if(exito.data.success===false){
                $scope.gestionarMoneda = false;
                new PNotify({text: exito.data.datos.data[0], type: 'warning', hide: true, styling: 'bootstrap3', buttons:{
                    sticker: false
                }});
            }
            else{
                $scope.gestionarMoneda = false;
               new PNotify({text: "Api link can\'t be add", type: 'warning', hide: true, styling: 'bootstrap3', buttons:{
                    sticker: false
                }}); 
            }       

        }, function (error) {
            $scope.gestionarMoneda = false;
            new PNotify({text: "can\'t be add, please try again", type: 'warning', hide: true, styling: 'bootstrap3', buttons:{
                    sticker: false
                }});
        });
        $scope.gestionarMoneda = false;
        $("#modal_close").click();
    };

    $scope.updateApiLink = function (api_link, index) {
        $scope.co.data_type = api_link.data_type;
        $scope.co.meth = api_link.meth;
        $scope.co.param = api_link.param;
        $scope.co.coin_ref = api_link.coin_ref
        $scope.affiliating = false;
        $scope.links = api_link;
        if ($scope.links) {
            ($scope.links.link === undefined) ? $scope.co.links.one.linkCrip = '' : $scope.co.links.one.linkCrip = $scope.links.link[0];
            $scope.co.links.one.status = 'E';
            $scope.co.links.one.meth = $scope.co.meth;
            $scope.co.links.one.data_type = $scope.co.data_type;
            $scope.co.links.one.coordinates = $scope.links.coordinates;
            $scope.co.links.one.param = $scope.co.param == undefined ? '' : $scope.co.param;
            $scope.co.links.one.coin_ref = $scope.co.coin_ref;
        }
        else {
            $scope.co.links.one.status = null;
            $scope.co.links.one.linkCrip = null;
            $scope.co.links.one.coordinates = null;
        }

        linkNumber = 0;
        for (key in $scope.links) {
            linkNumber += 1;
            $scope.veriLink(linkNumber);
        }
    };

    $scope.updApiLink = function () {
        links = [];
        objectUpdate = {};
        $scope.operatingAfill = true;
        objectUpdate.coin_id=$scope.co.id;
        objectUpdate.id = $scope.links.id;
        links.push($scope.co.links.one);
        for (index in links) {
            links[index].link = links[index].linkCrip;
            if (links[index].status == 'OK'){
                links[index].acepted = true;
                links[index].meth = $scope.co.meth;
                links[index].data_type = $scope.co.data_type;
                links[index].param = $scope.co.param == undefined ? '' : $scope.co.param;
                links[index].coin_ref = $scope.co.coin_ref;
            }
            else
                links[index].acepted = false;
            delete links[index].linkCrip;
            delete links[index].status;
        }
        objectUpdate.links = links;
        $http({
            url: apiUpdLinks,
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            data: objectUpdate
        }).then(function (exito) {
            if(exito.data.success===true){
                $scope.gestionarMoneda = false;
                new PNotify({
                    text: "Api link has been update successfully", 
                    type: 'success', 
                    hide: true, 
                    styling: 'bootstrap3', 
                    buttons:{
                        sticker: false
                    }
                });
                getAllCoins();
            }else if(exito.data.success===false){
                new PNotify({
                    text: exito.data.datos.data[0], 
                    type: 'warning', 
                    hide: true, 
                    styling: 'bootstrap3', 
                    buttons:{
                        sticker: false
                    }      
                });
            }
            else{
                new PNotify({
                    text: "Api link can\'t be update", 
                    type: 'warning', 
                    hide: true, 
                    styling: 'bootstrap3', 
                    buttons:{
                        sticker: false
                    }
                }); 
            }       
        }, function (error) {
            new PNotify({
                text: "can\'t be update, please try again", 
                type: 'warning', 
                hide: true, 
                styling: 'bootstrap3', 
                buttons:{
                    sticker: false
                }
            });
        });
        $("#modal_close").click();
        //$scope.gestionarMoneda = false;
    };

    var elem = document.querySelector('#swich1');
    var init = new Switchery(elem, {color: '#26B99A'});
}]);
angular.element(function () {
    angular.bootstrap(document, ['coreModule']);
});