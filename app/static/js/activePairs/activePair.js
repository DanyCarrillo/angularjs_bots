    /*
     * @Date: 05/10/2018
     * @autor: dcarrillo.
     */
app.config(function ($routeProvider) {
    $routeProvider
    .when('/', {
        templateUrl: '../static/html/activePairsListar.html',
        controller: 'activePairsController'
    })
})

app.controller('activePairsController', ["$scope", "$http", "factory_endPoints",function ($scope, $http, factory_endPoints) {
// Spinner
$scope.$on('LOAD',function(){$scope.loading=true});
$scope.$on('UNLOAD',function(){$scope.loading=false});
//Endpoints
listar_Pairs=factory_endPoints.getEndPoints("getListPairs");
marketPricesExchangeUri = factory_endPoints.getEndPoints('selMarketPricesExchange');
apiBlockPair = factory_endPoints.getEndPoints('blockPair');
//variables globales
$scope.listPairs=[]
$scope.pairs = [];
$scope.selection=[];
$scope.lote_suspender=[];
$scope.lote_activar=[];
$scope.dataSuspender=[];
$scope.dataActivar=[];

$scope.checkall=false;
$scope.waiting = true;

$scope.data_suspender={};
$scope.data_activar={};

    /* @Function: showDataAllPairs
     * @Date: 05/10/2018
     * @autor: dcarrillo
     * @Summary: Muestra lista de pares en tabla .
     */
	function showDataAllPairs(){
        $scope.$emit('LOAD');
    	$http({
    			url:listar_Pairs,
    			method:'GET',
    			headers:{
    				'Content-Type': 'application/json'
    			}
    		}).then(function(exito){
                $scope.$emit('UNLOAD');
                //head de tabla
                $scope.head={'id':'Id',
                            'pair':'pair',
                            'status_id':'Status',
                            'created_date':'Created date',
                            'modified_date':'Modified date'
                            }
    	        
               for (i in exito.data['datos']) {
                    var dict={}
                    dict['id_pair'] = exito.data['datos'][i].id_pair;
                    dict['FirstCurrency'] = exito.data['datos'][i].FirstCurrency;
                    dict['SecondCurrency'] = exito.data['datos'][i].SecondCurrency;
                    dict['pair'] = exito.data['datos'][i].pair;
                    dict['status_id'] = exito.data['datos'][i].status_id==1?'Active':'Inactive';
                    dict['buy_marketprice'] =parseFloat(exito.data['datos'][i].buy_marketprice);
                    dict['sell_marketprice'] = parseFloat(exito.data['datos'][i].sell_marketprice);
                    dict['created_date'] = exito.data['datos'][i].created_date;
                    dict['modified_date'] = exito.data['datos'][i].modified_date;
                    dict['cant_bots'] = exito.data['datos'][i].cant_bots;
                    $scope.listPairs.push(dict);  
                }
    		}, function (error){
                $scope.$emit('UNLOAD');
    		 new PNotify({
    	            text: "Something is wrong getting this pairs information.",
    	            type: 'warning',
    	            hide: true,
    	            styling: 'bootstrap3',
    	            buttons:{
    	                sticker: false
    	            },
    	        });
    	   })
	}

/* @Function: selectedCls() / changeSorting
 * @Date: 09/10/2018
 * @autor: dcarrillo
 * @Summary: Ordena tabla ASC y DESC.
 */
    $scope.sort = {
        column: 'pair',
        descending: false
    };

    $scope.selectedCls = function(column) {
        return column == $scope.sort.column && 'sort-' + $scope.sort.descending;
    };
    
    $scope.changeSorting = function(column) {
        var sort = $scope.sort;
        if (sort.column == column) {
            sort.descending = !sort.descending;
        } else {
            sort.column = column;
            sort.descending = false;
        }
    };

/* Function: selMarketPricesView()
 * Arguments: idPair
 * Date: 15/10/2018
 * Output: -
 * Method: -
 * Summary: al dar click en btn, se mostrara en select el par con el precio de compra y venta
 */
     $scope.selMarketPricesView = function(id_pair) {
        $scope.ngPair={}
        $scope.waiting = true;
        for(var key in $scope.listPairs){
            for (var value in $scope.listPairs[key]){
                if($scope.listPairs[key]['id_pair']==id_pair){
                    if($scope.listPairs[key]['status_id']=="Active"){
                    $scope.ngPair={}
                    $scope.ngPair['id_pair']=id_pair;
                    }else{
                        new PNotify({text: 'Pair '+$scope.listPairs[key]['pair']+' is inactived.', type: 'warning', hide: true, styling: 'bootstrap3', buttons:{
                        sticker: false
                        }});
                        return false;
                    }

                }

                       
            }

        } 

        $scope.selMarketPricesExchange(id_pair);

        }

/* Function: selMarketPricesExchange
 * Arguments: idPair
 * Date: 05/10/2018
 * Output: -
 * Method: -
 * Summary: Set Config for a differents types of modal: Add New Bot, Modify or Delete the existing Bot.
 */
    $scope.selMarketPricesExchange = function(id_pair) {
        //$scope.ngPair={}
        $scope.waiting = true;
        for(var key in $scope.listPairs){
            for (var value in $scope.listPairs[key]){
                if($scope.listPairs[key]['id_pair']==id_pair && $scope.listPairs[key]['status_id']=="Inactive"){
                    new PNotify({text: 'Pair can\'t be inactive.', type: 'warning', hide: true, styling: 'bootstrap3', buttons:{
                    sticker: false
                    }});
                    return false;
                }

            }

                   
        }

        $http({
            url: marketPricesExchangeUri,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            data: {'idPair':id_pair}
	   })
	    .then(function (exito) {
            $scope.waiting = false;
            $scope.ngPriceMarket = exito.data['data'][0];
            $scope.ngPriceMarket['buyMarketPrice'] = parseFloat($scope.ngPriceMarket['buyMarketPrice']);
            $scope.ngPriceMarket['sellMarketPrice'] = parseFloat($scope.ngPriceMarket['sellMarketPrice']);
	   }, function (error) {
            new PNotify({
                text: "Error in show Market Prices by Exchange, please try again.",
                type: 'warning',
                hide: true,
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                    },
            });
       })
    }

/* Function: toggleSelection
 * Arguments: pair
 * Date: 10/10/2018
 * Output: -
 * Method: -
 * Summary: Agregar o quita la seleccion de checkbox 
 */
  $scope.toggleSelection = function toggleSelection(pair) {
    var idx = $scope.selection.indexOf(pair);
    if (idx > -1) {
      // Quita par seelccionado de array $scope.selection
      $scope.selection.splice(idx, 1);
     }
     else {
       // agrega par seleccionado $scope.selection
       $scope.selection.push(pair);
     }
  };

/* Function: toggleSelect
 * Arguments: pair
 * Date: 10/10/2018
 * Output: -
 * Method: -
 * Summary: Selecciona todos los checkbox 
 */
    $scope.toggleSelect = function(){
        $scope.waitingCheckbox=false;
        $scope.selection=[];
        $scope.selection=$scope.pares_filtrados;
        var a=document.getElementsByClassName("check");
        if($scope.checkall==true){
            for(y in $scope.selection){
                for(var x=0;x<a.length;x++){
                    if(a[x].value==$scope.selection[y]['id_pair']){
                        a[x].checked=true;
                     }
                }

            }
        }else{
            $scope.selection=[]
             for(var x=0;x<a.length;x++){
                    a[x].checked=false;
                }
        }
    }

/* Function: confiActivate(pairs)
 * Arguments: 
 * Date: 15/10/2018
 * Output: -
 * Method: -
 * Summary: al confirmar llama a funcion enviarActivar(pair).
 */
    $scope.confiActivatePair=function(pairs){
        (new PNotify({
            title: 'Activate pair',
            text: 'Are you sure want\'s activate pair ? '+pairs.pair,
            icon: 'fa fa-lock fa-spin  fa-fw text-danger',
            hide: false,
            type: 'info',
            styling: 'bootstrap3',
            confirm: {
                confirm: true,
                buttons: [{text: 'Accept'}, {text: 'Cancel', addClass: 'btn btn-danger'}]
            },
            buttons: {
                closer: true,
                sticker: false,
            },
            history: {
                history: false
            },
            addclass: 'stack-modal',
            stack: {
                'dir1': 'down',
                'dir2': 'right',
                'modal': false
            }
        })).get().on('pnotify.confirm', function () {
            enviarActivarPair(pairs);
        }).on('pnotify.cancel', function () {
        });
    }

/* Function: enviarActivarPair()
 * Arguments: lista
 * Date: 15/10/2018
 * Output: -
 * Method: -
 * Summary: cuando el usuario de click a btn, Envia data ha python para activar par.
 */
    function enviarActivarPair(lista) {
        $scope.dataActivar=[];
        $scope.data_activar={};
        $scope.data_activar['id_pair']=lista['id_pair'];
        $scope.data_activar['status_id']=lista['status_id']=='Inactive'? 1:1;
        $scope.dataActivar.push($scope.data_activar);
        $scope.selection=[];
        $http({
            url: apiBlockPair,
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            data: $scope.dataActivar
        })
        .then(function (exito) {
            var check = document.getElementsByClassName("check");
            for(var i=0;i<check.length;i++){
                check[i].checked=false;
            }
            if (exito.data.datos) {
                for(i in $scope.listPairs){
                    for(x in exito.data.datos){
                    if($scope.listPairs[i]['id_pair']==exito.data.datos[x]['id_pair']){
                        $scope.checkall=false;
                        $scope.listPairs[i]['id_pair']=exito.data.datos[x].id_pair;
                        $scope.listPairs[i]['FirstCurrency']=exito.data.datos[x].FirstCurrency;
                        $scope.listPairs[i]['SecondCurrency']=exito.data.datos[x].SecondCurrency;
                        $scope.listPairs[i]['pair']=exito.data.datos[x].pair;
                        $scope.listPairs[i]['status_id']=exito.data.datos[x].status_id==1?'Active':'Inactive';
                        $scope.listPairs[i]['modified_date']=exito.data.datos[x].modified_date;
                        $scope.listPairs[i]['created_date']=exito.data.datos[x].created_date;
                        $scope.listPairs[i]['buy_marketprice'] =parseFloat(exito.data.datos[x].buy_marketprice);
                        $scope.listPairs[i]['sell_marketprice'] = parseFloat(exito.data.datos[x].sell_marketprice);
                        $scope.listPairs[i]['cant_bots'] = exito.data.datos[x].cant_bots;
                    }
                    }
                }
                new PNotify({
                    text: 'Pairs activated successfully.',
                    type: 'success',
                    hide: true,
                    styling: 'bootstrap3',
                    buttons:{
                        sticker: false
                    },
                })
            }else{
                new PNotify({
                    text: "Pair be can't activated.",
                    type: 'danger',
                    hide: true,
                    styling: 'bootstrap3',
                    buttons:{
                        sticker: false
                    },
                })
            }
        }, function (error) {
            new PNotify({
                text: "", 
                type: 'warning', 
                hide: true, 
                styling: 'bootstrap3',
                buttons:{
                        sticker: false
                },
            });
        })
    }

/* Function: confiActivate(pairs)
 * Arguments: 
 * Date: 15/10/2018
 * Output: -
 * Method: -
 * Summary: al confirmar llama a funcion enviarActivar(pair).
 */
    $scope.confiInactivePair=function(pairs){
        (new PNotify({
            title: 'Inactivate pair',
            text: 'Are you sure want\'s inactivate pair ? '+pairs.pair,
            icon: 'fa fa-lock fa-spin  fa-fw text-danger',
            hide: false,
            type: 'info',
            styling: 'bootstrap3',
            confirm: {
                confirm: true,
                buttons: [{text: 'Accept'}, {text: 'Cancel', addClass: 'btn btn-danger'}]
            },
            buttons: {
                closer: true,
                sticker: false,
            },
            history: {
                history: false
            },
            addclass: 'stack-modal',
            stack: {
                'dir1': 'down',
                'dir2': 'right',
                'modal': false
            }
        })).get().on('pnotify.confirm', function () {
            enviarInacitvePair(pairs);
        }).on('pnotify.cancel', function () {
        });
    }

/* Function: enviarInacitvePair()
 * Arguments: lista
 * Date: 15/10/2018
 * Output: -
 * Method: -
 * Summary: cuando el usuario de click a btn, Envia data ha python para inactivar par.
 */
    function enviarInacitvePair(lista) {
        $scope.dataSuspender=[];
        $scope.data_suspender={};
        $scope.data_suspender['id_pair']=lista['id_pair'];
        $scope.data_suspender['status_id']=lista['status_id']=='Active'? 2:2;
        $scope.dataSuspender.push($scope.data_suspender);
        $scope.selection=[];
        
        $http({
            url: apiBlockPair,
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            data: $scope.dataSuspender
        })
        .then(function (exito) {
            
            var check = document.getElementsByClassName("check");
            for(var i=0;i<check.length;i++){
                check[i].checked=false;
            }
            if (exito.data.datos) {
                for(i in $scope.listPairs){
                    for(x in exito.data.datos){
                    if($scope.listPairs[i]['id_pair']==exito.data.datos[x]['id_pair']){
                        $scope.checkall=false;
                        $scope.listPairs[i]['id_pair']=exito.data.datos[x].id_pair;
                        $scope.listPairs[i]['FirstCurrency']=exito.data.datos[x].FirstCurrency;
                        $scope.listPairs[i]['SecondCurrency']=exito.data.datos[x].SecondCurrency;
                        $scope.listPairs[i]['pair']=exito.data.datos[x].pair;
                        $scope.listPairs[i]['status_id']=exito.data.datos[x].status_id==1?'Active':'Inactive';
                        $scope.listPairs[i]['modified_date']=exito.data.datos[x].modified_date;
                        $scope.listPairs[i]['created_date']=exito.data.datos[x].created_date;
                        $scope.listPairs[i]['buy_marketprice'] =parseFloat(exito.data.datos[x].buy_marketprice);
                        $scope.listPairs[i]['sell_marketprice'] = parseFloat(exito.data.datos[x].sell_marketprice);
                        $scope.listPairs[i]['cant_bots'] = exito.data.datos[x].cant_bots;
                    }
                    }
                }
                new PNotify({
                    text: 'Pair inactivated successfully.',
                    type: 'success',
                    hide: true,
                    styling: 'bootstrap3',
                    buttons:{
                        sticker: false
                    },
                })
            }else{
                new PNotify({
                    text: "Pair be can't inactivated.",
                    type: 'danger',
                    hide: true,
                    styling: 'bootstrap3',
                    buttons:{
                        sticker: false
                    },
                })
            }
        }, function (error) {
            
            new PNotify({
                text: "", 
                type: 'warning', 
                hide: true, 
                styling: 'bootstrap3',
                buttons:{
                        sticker: false
                },
            });
        })
    }

/* Function: confiActivateAll()
 * Arguments: lista
 * Date: 09/10/2018
 * Output: -
 * Method: -
 * Summary: al confirmar llama a funcion enviarActivarAll(pair).
 */
    $scope.confiActivateAll=function(){
        (new PNotify({
            title: 'Activate pairs',
            text: 'Are you sure want\'s activate pairs ?',
            icon: 'fa fa-lock fa-spin  fa-fw text-danger',
            hide: false,
            type: 'info',
            styling: 'bootstrap3',
            confirm: {
                confirm: true,
                buttons: [{text: 'Accept'}, {text: 'Cancel', addClass: 'btn btn-danger'}]
            },
            buttons: {
                closer: true,
                sticker: false,
            },
            history: {
                history: false
            },
            addclass: 'stack-modal',
            stack: {
                'dir1': 'down',
                'dir2': 'right',
                'modal': false
            }
        })).get().on('pnotify.confirm', function () {
            enviarActivarAll($scope.selection);
        }).on('pnotify.cancel', function () {
        });
    }

/* Function: enviarActivarAll()
 * Arguments: lista
 * Date: 09/10/2018
 * Output: -
 * Method: -
 * Summary: Envia data ha python para activar pares seleccionados.
 */
    function enviarActivarAll(lista) {
        if ($scope.selection.length == 0) {
            new PNotify({text: 'Checkbox can\'t be empty.', type: 'warning', hide: true, styling: 'bootstrap3', buttons:{
                sticker: false
            }});
            return false;
        }
        $scope.$emit('LOAD');
        for(i in lista){
            $scope.data_activar={};
            $scope.data_activar['id_pair']=lista[i]['id_pair'];
            $scope.data_activar['FirstCurrency']=lista[i]['FirstCurrency'];
            $scope.data_activar['SecondCurrency']=lista[i]['SecondCurrency'];
            $scope.data_activar['pair']=lista[i]['pair'];
            $scope.data_activar['status_id']=lista[i]['status_id']=='Inactive'? 1:1;
            $scope.lote_activar.push($scope.data_activar);
        }
        $scope.selection=[];
        $http({
            url: apiBlockPair,
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            data: $scope.lote_activar
        })
        .then(function (exito) {
            
            $scope.$emit('UNLOAD');
            var check = document.getElementsByClassName("check");
            for(var i=0;i<check.length;i++){
                check[i].checked=false;
            }
            if (exito.data.datos) {
                for(i in $scope.listPairs){
                    for(x in exito.data.datos){
                    if($scope.listPairs[i]['id_pair']==exito.data.datos[x]['id_pair']){
                        $scope.checkall=false;
                        $scope.listPairs[i]['id_pair']=exito.data.datos[x].id_pair;
                        $scope.listPairs[i]['FirstCurrency']=exito.data.datos[x].FirstCurrency;
                        $scope.listPairs[i]['SecondCurrency']=exito.data.datos[x].SecondCurrency;
                        $scope.listPairs[i]['pair']=exito.data.datos[x].pair;
                        $scope.listPairs[i]['status_id']=exito.data.datos[x].status_id==1?'Active':'Inactive';
                        $scope.listPairs[i]['modified_date']=exito.data.datos[x].modified_date;
                        $scope.listPairs[i]['created_date']=exito.data.datos[x].created_date;
                        $scope.listPairs[i]['buy_marketprice'] =parseFloat(exito.data.datos[x].buy_marketprice);
                        $scope.listPairs[i]['sell_marketprice'] = parseFloat(exito.data.datos[x].sell_marketprice);
                        $scope.listPairs[i]['cant_bots'] = exito.data.datos[x].cant_bots;
                    }
                    }
                }
                new PNotify({
                    text: 'Pairs activated successfully.',
                    type: 'success',
                    hide: true,
                    styling: 'bootstrap3'
                })
            }else{
                new PNotify({
                    text: "Pairs can't be activated.",
                    type: 'danger',
                    hide: true,
                    styling: 'bootstrap3'
                })
            }
        }, function (error) {
            new PNotify({
                text: "Pairs can't be activated.", 
                type: 'warning', 
                hide: true, 
                styling: 'bootstrap3'
            });
        })
    }

/* Function: confirmarInactivateAll()
 * Arguments: lista
 * Date: 09/10/2018
 * Output: -
 * Method: -
 * Summary: al confirmar llama a funcion enviarInactivarAll(lista).
 */

    $scope.confirmarInactivateAll=function(){
        (new PNotify({
            title: 'Inactivate pairs',
            text: 'Are you sure want\'s inactivate all pairs ?',
            icon: 'fa fa-lock fa-spin  fa-fw text-danger',
            hide: false,
            type: 'info',
            styling: 'bootstrap3',
            confirm: {
                confirm: true,
                buttons: [{text: 'Accept'}, {text: 'Cancel', addClass: 'btn btn-danger'}]
            },
            buttons: {
                closer: true,
                sticker: false,

            },
            history: {
                history: false
            },
            addclass: 'stack-modal',
            stack: {
                'dir1': 'down',
                'dir2': 'right',
                'modal': false
            }
        })).get().on('pnotify.confirm', function () {
            enviarInactivarAll($scope.selection);
        }).on('pnotify.cancel', function () {
        });
    }

/* Function: enviarInactivarAll()
 * Arguments: lista
 * Date: 09/10/2018
 * Output: -
 * Method: -
 * Summary: Envia data a python para inactivar todos los pares
 */
    function enviarInactivarAll(lista) {
        if ($scope.selection.length == 0) {
            new PNotify({text: 'Checkbox can\'t be empty.', type: 'warning', hide: true, styling: 'bootstrap3', buttons:{
                sticker: false
            }});
            return false;
        }
        $scope.$emit('LOAD');
        for(i in lista){

            $scope.data_suspender={};
            $scope.data_suspender['id_pair']=lista[i]['id_pair'];
            $scope.data_suspender['FirstCurrency']=lista[i]['FirstCurrency'];
            $scope.data_suspender['SecondCurrency']=lista[i]['SecondCurrency'];
            $scope.data_suspender['pair']=lista[i]['pair'];
            $scope.data_suspender['status_id']=lista[i]['status_id']=='Active'? 2:2;
            $scope.lote_suspender.push($scope.data_suspender);
        }
        $scope.selection=[];
        $http({
            url: apiBlockPair,
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            data: $scope.lote_suspender
        })
        .then(function (exito) {
            $scope.$emit('UNLOAD');
            var check = document.getElementsByClassName("check");
            for(var i=0;i<check.length;i++){
                check[i].checked=false;
            }
            if (exito.data.datos) {
                for(i in $scope.listPairs){
                    for(x in exito.data.datos){
                    if($scope.listPairs[i]['id_pair']==exito.data.datos[x]['id_pair']){
                        $scope.listPairs[i]['id_pair']=exito.data.datos[x].id_pair;
                        $scope.listPairs[i]['FirstCurrency']=exito.data.datos[x].FirstCurrency;
                        $scope.listPairs[i]['SecondCurrency']=exito.data.datos[x].SecondCurrency;
                        $scope.listPairs[i]['pair']=exito.data.datos[x].pair;
                        $scope.listPairs[i]['status_id']=exito.data.datos[x].status_id==1?'Active':'Inactive';
                        $scope.listPairs[i]['modified_date']=exito.data.datos[x].modified_date;
                        $scope.listPairs[i]['created_date']=exito.data.datos[x].created_date;
                        $scope.listPairs[i]['buy_marketprice'] =parseFloat(exito.data.datos[x].buy_marketprice);
                        $scope.listPairs[i]['sell_marketprice'] = parseFloat(exito.data.datos[x].sell_marketprice);
                        $scope.listPairs[i]['cant_bots'] = exito.data.datos[x].cant_bots;
                    }
                    }
                }
                    new PNotify({
                    text: 'Pairs inactivated successfully.',
                    type: 'success',
                    hide: true,
                    styling: 'bootstrap3'
                })
            }else{
                    new PNotify({
                    text: 'Error in data return.',
                    type: 'danger',
                    hide: true,
                    styling: 'bootstrap3'
                })
            }
        }, function (error) {
            new PNotify({
                text: "Pairs can't be inactivated.", 
                type: 'warning', 
                hide: true, 
                styling: 'bootstrap3'
            });
        })
    }

/* 
 * Date: /10/2018
 * Summary: Escuchador de scroll
 */
window.onscroll = function() {scrollFunction()};
function scrollFunction() {
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        document.getElementById("myBtn").style.display = "block";
    } else {
        document.getElementById("myBtn").style.display = "none";
    }
}

/*Date: /10/2018
*Summary: Envia a la parte inicial de la pagina
*/
$scope.topFunction=function() {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
};

//Funciones para la primera carga
showDataAllPairs();
//howAllPairs();


}]);


angular.element(function () {
    angular.bootstrap(document, ['coreModule']);
});

