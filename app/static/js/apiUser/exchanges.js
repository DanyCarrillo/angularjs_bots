/* ***************************************
 * Module: Exchanges
 * Plattform: Controlador (Vista Cliente)
 * Framework: Angular
 * Version: 1.x.x
 * Last Date Update: August, 03 2018
 * ***************************************
 */
app.config(function($routeProvider){
    $routeProvider
    .when('/', {
        templateUrl : '../static/html/apiUserListar.html',
        controller  : 'apiUserController'
    }) 
});

app.controller('apiUserController',["$scope","$http","factory_endPoints", function($scope,$http,factory_endPoints) {
    // ------- [CHANGED] Begin Added: Angular 1.0 -------
     $scope.$on('LOAD',function(){$scope.loading=true});
    $scope.$on('UNLOAD',function(){$scope.loading=false});
    // Rutas URLs --> Apunta a: app/static/js/app.js
    showExchangeUri = factory_endPoints.getEndPoints('showExchange');
    viewAllExchangeUri = factory_endPoints.getEndPoints('viewAllExchange');
    addExchangeUri = factory_endPoints.getEndPoints('addExchange');
    addExchangeUserApilinkUri = factory_endPoints.getEndPoints('addExchangeUserApilink');
    updExchangeUserApilinkUri = factory_endPoints.getEndPoints('updExchangeUserApilink');
    updExchangeUri = factory_endPoints.getEndPoints('updExchange');
    delExchangeUri = factory_endPoints.getEndPoints('delExchange');
    showPairUri = factory_endPoints.getEndPoints('showPair');
    showFormatsUri = factory_endPoints.getEndPoints('showFormat');

    // Variables Globales:
    $scope.idUser = localStorage.getItem("idUserSession");

    $scope.exchanges = [];
    $scope.pairs = [];
    $scope.salidaExchangeSelect=[];

    $scope.exchange = {};
    $scope.user = {};    
    $scope.paircoin = {};
    
    $scope.angular_users = [];
    $scope.angular_userpairs = [];
    $scope.angular_apilinks = [];
    $scope.mensajes="";
    $scope.bloquear_save=false;
    
    $scope.styleWeb = {"background-color":'#2A3F54'};
    $scope.styleTextWeb = {"color":'#2A3F54'};
    $scope.bgInvalid = '#FCD6D6';
    $scope.bgValid = '#F7FCEE';

    $scope.exchange2send = {};

    // Funciones:

    /* Function: str2json
     * Arguments: 'str' (Cadena de texto con esquema JSON)
     * Output: jason (Local variable)
     * Method: -
     * Summary: Convert a string to JSON. Option for prevent JSON.parse function that appears with errors.
     */
    function str2json(str,list_fields) {
        $scope.jason = {};
        var aux = str.split(/[:,]+/); //var aux = str.split('u');
        for (var i=0; i<list_fields.length; i++) {
            //var str_field = ( (i!=list_fields.length-1) ? (aux[(i*2+2)].replace(',','')).replace(/'/g,"") : (aux[(i*2+2)].replace('}','')).replace(/'/g,"") );
            var str_field = aux[i*2+1].replace(/[}']/g,'');
            $scope.jason[list_fields[i]] = str_field;
        }
    }

    /* Function: showAllExchanges
     * Arguments: -
     * Output: $scope.exchange {,,[],,}
     * Method: GET
     * Summary: Lists all Exchange items created by Administrator
     */
    
    $scope.$emit('LOAD');
    function showAllExchanges(){
        $scope.$emit('LOAD');
        $http({
            url:viewAllExchangeUri,
            method:'GET',
            headers: {
                'Content-Type':'application/json'
            },
        }).then(function(exito) {
            $scope.$emit('UNLOAD');
            $scope.exchanges = [];
            for (var i=0; i<exito.data['data'].length; i++) {
                var exch = exito.data['data'][i];
                $scope.exchanges.push(exch);
            }
           

        },function(error) {
            new PNotify({
                text: "Something goes wrong, reloading",
                type: 'warning',
                hide: true,
                styling: 'bootstrap3'
            });
        })
    }

    /* Function: exchangeModal
     * Arguments: 'A'/'M'/'D' (Add/Modify/Delete)
     * Output: -
     * Method: -
     * Summary: Set Config for a differents types of modal: Add New Exchange, Modify or Delete the existing Exchange.
     */
    $scope.exchangeModal = function(mode='A', exchange=null, index=null) {
        switch(mode) {
            case 'A':
                $scope.modalTitle ='Add Exchange';
                $scope.isDisabled=false;
                // Clean ng-models:
                $scope.exchange = {}; // general
                $scope.user = {};
                $scope.paircoin = {};
                $scope.apilink = {};

                // Clean vectors with ng-models accumulate:
                $scope.salidaExchangeSelect=[];
                $scope.angular_users = [];
                $scope.angular_apilinks = [];
                $scope.angular_userpairs = [];
                showSelectExchange();

                // Reset counts:
                $scope.counter_usu = 0;
                $scope.counter_pair = 0;
                $scope.counter_link = 0;
                $scope.mensaje=true;
                $scope.mensajes="Select Exchange";
                $scope.modExchange= false;
                $scope.showOtherEchange=false;
                $scope.showEchange=false;
                $scope.show_form=false;
                $scope.show_selectExchange=true;
                $scope.exchange_types = [ {'key':'I','value':'Internal'}, {'key':'E','value':'External'} ];
                $scope.apilink_methods = ['GET','POST'];
                $scope.apilink_datatypes = ['JSON','form-data'];
                break;
            case 'M':
                $scope.modalTitle = 'Modify Exchange';

                // Clean ng-models:
                $scope.exchange = {}; // general
                $scope.user = {};
                $scope.paircoin = {};
                $scope.apilink = {};

                // Clean vectors with ng-models accumulate:
                $scope.angular_users = [];
                $scope.angular_apilinks = [];
                $scope.angular_userpairs = [];

                // Reset counts:
                $scope.counter_usu = 0;
                $scope.counter_pair = 0;
                $scope.counter_link = 0;
                $scope.modExchange= true;
                $scope.mensaje=false;
                $scope.exchange_types = [ {'key':'I','value':'Internal'}, {'key':'E','value':'External'} ];
                $scope.apilink_methods = ['GET','POST'];
                $scope.apilink_datatypes = ['JSON','form-data'];
                
                // Data from Exchange - Charging ...
                $scope.exchange = $scope.exchanges[index];
                $scope.show_form=true;
                $scope.isDisabled=true;
                $scope.show_selectExchange=false;
                $scope.showOtherEchange=true;
                $scope.showEchange=false;
                $scope.exchange.general.nombre=$scope.exchanges[index]['general']['name'];
                if($scope.exchanges[index]['general']['type']=='I'){
                    $scope.exchange.general.tipo="I";
                }else{
                    $scope.exchange.general.tipo="E";
                }
                $scope.exchange.general.prioridad=$scope.exchanges[index]['general']['priority'];
                $scope.angular_users = $scope.exchanges[index].users;
                $scope.angular_apilinks = $scope.exchanges[index].formats;
                if($scope.exchanges[index]['general']['idExchange']>1 && $scope.exchanges[index]['general']['idExchange']<7){
                    $scope.show_form=false;
                }else{
                    $scope.show_form=true;
                }
                // Set Counters:
                $scope.counter_usu = $scope.angular_users.length;
                $scope.counter_link = $scope.angular_apilinks.length;
                
                break;
            case 'D':
                (new PNotify({
                    title: 'Eliminar Exchange',
                    text: ' <center><h5>Be sure to remove the Exchange '+$scope.exchanges[index].general.name+'? </h5> </center>',
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
                    delExchange($scope.exchanges[index].general.idExchange);
                }).on('pnotify.cancel', function() {
                    
                });
                break;
            default:
                break;
        }
    }   
    
    /* Function: Muestra Exchanges(Bitstamp,Binance,Okex, Huobi,Other) in select
     * Arguments: -
     * Output: 
     * Method: 
     * Summary: 
     */
    function showSelectExchange(){
        var salida={};
        for(i in $scope.exchanges){
            if($scope.exchanges[i]['general']['idExchange']>1 && $scope.exchanges[i]['general']['idExchange']<7){
                $scope.salidaExchangeSelect.push({'idExchange':$scope.exchanges[i]['general']['idExchange'],'name':$scope.exchanges[i]['general']['name']});
        }}

    }
  /* Function: Limpia campos, contadores y arreglos
     * Arguments: -
     * Output: 
     * Method: 
     * Summary: 
     */
function clearExchange(){
    $scope.angular_users = [];
    $scope.angular_apilinks = [];
    $scope.angular_userpairs = [];
    $scope.exchange.general.prioridad="";
    $scope.exchange.general.nombre="";
    $scope.counter_usu = 0;
    $scope.counter_pair = 0;
    $scope.counter_link = 0;
    $scope.paircoin = {};
    $scope.user = {};

    

}

    /* Function: click Select Exchange name(Bitstamp,Binance,Okex, Huobi,Other)
     * Arguments: -
     * Output: 
     * Method: 
     * Summary:  
     */
 $scope.showExchangeSelect = function(exchange_select) {
        var seleccionado=$scope.exchange.general.seleccionado;
        if (exchange_select!=null) { 
            if(exchange_select=='Other'){
                clearExchange();
               //form other Exchange 
               $scope.showOtherEchange=true;
               //form Exchanges(Bitstamp,Binance,Okex, Huobi,Other)
               $scope.showEchange=false;
               //form add apilink
               $scope.show_form=true;
               //Clean form vector's
               
               $scope.exchange.general.tipo=null;
               //mensaje
               $scope.mensaje=true;
               $scope.mensajes="add user pairs is empty, please enter pair for add user.";
            } else {
                $scope.isDisabledTypeExchange=true;

                clearExchange();
                 //mensaje
               $scope.mensaje=true;
               $scope.mensajes="add user pairs is empty, please enter pair for add user.";
                //form other Exchange 
                $scope.showOtherEchange=false;
                //form Exchanges(Bitstamp,Binance,Okex, Huobi,Other)
                $scope.showEchange=true;
                //form add apilink
                $scope.show_form=false;
                for(i in $scope.exchanges){
                      if($scope.exchanges[i]['general']['idExchange']==seleccionado){
                            if($scope.exchanges[i]['general']['type']=='I'){
                                $scope.exchange.general.tipo="I";
                                }else{
                                $scope.exchange.general.tipo="E";
                                    }
                    }}    
           }    
        } else { 
        $scope.mensje=false;
        $scope.showOtherEchange=false;
        $scope.showEchange=false;
        $scope.show_form=false;

        }
        
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
            new PNotify({
                text: "Something goes wrong, reloading",
                type: 'warning',
                hide: true,
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                },
            });
        })
    }

    /* Function: addmodUserPair
     * Arguments: -
     * Output: $scope.angular_userpairs
     * Method: -
     * Summary: 
     */
    $scope.addmodUserPair = function() {
        // Verificar si el elemento ya existe:
        var flag_existe=false;
        for(var i=0; i<$scope.angular_userpairs.length; i++){
            flag_existe = ( ($scope.angular_userpairs[i].idPair == $scope.paircoin.idPair) ? true : flag_existe );
        }

        // Proceder a la accion:
        if (flag_existe==false) {
            var indice=0;
            for(var i=0; i<$scope.pairs.length; i++){
                indice = ( ($scope.paircoin.idPair==$scope.pairs[i].idPair)? i : indice );
            }
            $scope.paircoin.pair = $scope.pairs[indice].pair;
            $scope.angular_userpairs.push($scope.paircoin);
            $scope.counter_pair++;

        } else {
            $scope.angular_userpairs[indice] = $scope.paircoin;
        }

        if($scope.angular_userpairs.length>0){
           $scope.mensaje=true;
            $scope.mensajes="add user is empty, please add user."; 
        }else{
          $scope.mensaje=true;
            $scope.mensajes="add user pairs is empty, please enter pair for add user.";   
        }
        // Clean Variables:
        $scope.paircoin = {};
    }

    /* Function: showUserPair
     * Arguments: idPair ($scope.angular_pairs)
     * Output: 
     * Method: -
     * Summary: 
     */
    $scope.showUserPair = function(idpair) {
        $scope.paircoin = {};
        var indice = "";
        for(var i=0; i<$scope.angular_userpairs.length; i++){
            indice = ( ($scope.angular_userpairs[i].idPair==idpair)? i : indice );   
        }
        
        $scope.paircoin = $scope.angular_userpairs[indice];

    }

    /* Function: delUserPair
     * Arguments: idPair ($scope.angular_pairs)
     * Output: 
     * Method: -
     * Summary: 
     */
    $scope.delUserPair = function(idpair) {

        $scope.paircoin = {};
        var indice = "";
        for(var i=0; i<$scope.angular_userpairs.length; i++){
            indice = ( ($scope.angular_userpairs[i].idPair==idpair)? i : indice );   
        }
        $scope.angular_userpairs.splice(indice,1);

        $scope.counter_pair = ($scope.counter_pair>0)?$scope.counter_pair-1:0

    }

    /* Function: addmodUser
     * Arguments: -
     * Output: $scope.angular_users
     * Method: -
     * Summary: 
     */
    $scope.addmodUser = function() {
        // Verificar si el elemento ya existe:
        var flag_existe=false;
        var indice = 0;
        for(var i=0; i<$scope.angular_users.length; i++){
            if ($scope.angular_users[i].username == $scope.user.username) {
                flag_existe = true
                indice = i;
            }
        }
        
        // Proceder a la accion:
        if (flag_existe==false) {
            $scope.user.pairs = $scope.angular_userpairs; 
            $scope.angular_users.push($scope.user);
            $scope.counter_usu++;
        } else {
            $scope.angular_users[indice] = $scope.user;

        }
        //mensaje
        if($scope.exchange.general.seleccionado!='Other'){
            $scope.mensaje=false;
            $scope.mensajes="";
        }else{
            if($scope.counter_usu>0 && $scope.counter_link<2){
               $scope.mensaje=true;
                $scope.mensajes="Please add 2 api link's as a minimum."; 
            }else if($scope.counter_usu>0 && $scope.angular_apilinks.length>2){
                $scope.mensaje=false;
                $scope.mensajes=""; 

            }else{
              $scope.mensaje=false;
                $scope.mensajes="";   
            }
        }
        // Clean Variables:
        $scope.user = {};
        $scope.paircoin = {};
        $scope.angular_userpairs = [];
        $scope.counter_pair = 0;
    }

    /* Function: showUser
     * Arguments: username ($scope.angular_users)
     * Output: 
     * Method: -
     * Summary: 
     */
    $scope.showUser = function(username) {
        $scope.user = {};
        $scope.paircoin = {};
        var indice = "";
        for(var i=0; i<$scope.angular_users.length; i++){
            indice = ( ($scope.angular_users[i].username==username)? i : indice );   
        }
        $scope.user = $scope.angular_users[indice];
        $scope.angular_userpairs = $scope.angular_users[indice].pairs;
        $scope.counter_pair = $scope.angular_userpairs.length;

    }

    /* Function: delUser
     * Arguments: username ($scope.angular_users)
     * Output: 
     * Method: -
     * Summary: 
     */
    $scope.delUser = function(username) {
        $scope.user = {};
        $scope.paircoin = {};
        var indice = "";
        for(var i=0; i<$scope.angular_users.length; i++){
            indice = ( ($scope.angular_users[i].username==username)? i : indice );   
        }
        $scope.angular_users.splice(indice,1);
        $scope.angular_userpairs = [];
        $scope.counter_pair = 0;
        $scope.counter_usu = ($scope.counter_usu>0)?$scope.counter_usu-1:0;
    }

    /* Function: showAllTradingTypes
     * Arguments: -
     * Output: $scope. {,,[],,}
     * Method: GET
     * Summary: Lists all Exchange items created by Administrator
     */
    function showAllFormats(){
        $http({
            url:showFormatsUri,
            method:'GET',
            headers: {
                'Content-Type':'application/json'
            },
        }).then(function(exito) {
            $scope.formats = [];
            for (var i=0; i<exito.data['data'].length; i++) {
                var exch = exito.data['data'][i];
                var dic = {};
                var items = ['idFormat','name'];
                for (var j=0; j<items.length; j++) {
                    dic[items[j]] = exch[j];
                }
                $scope.formats.push(dic);
            }
        },function(error) {
            new PNotify({
                text: "Something goes wrong, reloading",
                type: 'warning',
                hide: true,
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                },
            });
        })
    }

    /* Function: addmodapilink
     * Arguments: -
     * Output: $scope.angular_apilinks
     * Method: -
     * Summary: 
     */
    $scope.addmodApiLink = function() {
        // Verificar si el elemento ya existe:
        var flag_existe=false;
        var indice = 0;
        for(var i=0; i<$scope.angular_apilinks.length; i++){
            if ($scope.angular_apilinks[i].format == $scope.apilink.format) {
                flag_existe = true
                indice = i;
            }
        }

        // Proceder a la accion:
        if (flag_existe==false) {
            $scope.apilink.reference = $scope.counter_link+1;
            $scope.angular_apilinks.push($scope.apilink);
            $scope.counter_link++;
        } else {
            $scope.angular_apilinks[indice] = $scope.apilink;
        }
        //mensaje 
        if($scope.counter_link<2){
           $scope.mensaje=true;
            $scope.mensajes="Please add 2 api link's as a minimum."; 
        }else if($scope.counter_usu>0 ){
            $scope.mensaje=false;
            $scope.mensajes=""; 
        }
        else if($scope.counter_usu==0){
           $scope.mensaje=true;
            $scope.mensajes="add user pairs is empty, please enter pair for add user."; 
        }
        else{
          $scope.mensaje=false;
            $scope.mensajes="";   
        }

        // Clean Variables:
        $scope.apilink = {};
    }
    /* Function: showUser
     * Arguments: username ($scope.angular_users)
     * Output: 
     * Method: -
     * Summary: 
     */
    $scope.showApiLink = function(refer) {
        $scope.apilink = {};
        var indice = "";
        for(var i=0; i<$scope.angular_apilinks.length; i++){
            indice = ( ($scope.angular_apilinks[i].reference==refer)? i : indice );   
        }
        $scope.apilink = $scope.angular_apilinks[indice];
    }

    /* Function: delApiLink
     * Arguments: refer ($scope.angular_apilinks)
     * Output: 
     * Method: -
     * Summary: 
     */
    $scope.delApiLink = function(refer) {
        $scope.apilink = {};
        var indice = "";
        for(var i=0; i<$scope.angular_apilinks.length; i++){
            indice = ( ($scope.angular_apilinks[i].reference==refer)? i : indice );   
        }
        $scope.counter_link = ($scope.counter_link>0)?$scope.counter_link-1:0;
        $scope.angular_apilinks.splice(indice,1);
    }

    /* Function: cleanModeluserPair
     * Arguments: username ($scope.angular_users)
     * Output: 
     * Method: -
     * Summary: 
     */
    $scope.cleanModeluserPair = function() {
        $scope.paircoin = {};
    }

    /* Function: cleanModelUser
     * Arguments: username ($scope.angular_users)
     * Output: 
     * Method: -
     * Summary: 
     */
    $scope.cleanModelUser = function() {
        $scope.user = {};
        $scope.paircoin = {};
        $scope.counter_pair = 0;
        $scope.angular_userpairs = [];
    }

    /* Function: cleanModelApiLink
     * Arguments: username ($scope.angular_users)
     * Output: 
     * Method: -
     * Summary: 
     */
    $scope.cleanModelApiLink = function() {
        $scope.apilink = {};
    }

    /* Function: verJSONExchange
     * Arguments: username ($scope.angular_users)
     * Output: 
     * Method: -
     * Summary: Funcion auxiliar para verificar el JSON de Exchange que se enviara por HTTP POST 
     */
    $scope.verJSONExchange = function() {
        // Arreglo General:
        $scope.exchange.general.status = ($scope.exchange.general.status? ($scope.exchange.general['status']=="active" || $scope.exchange.general['status']==1 ? 1:2) : 1);
        $scope.exchange2send.general = $scope.exchange.general;

        // Arreglo Users:
        for(var i=0; i<$scope.angular_users.length; i++) {
            $scope.angular_users[i].status = 1;
        }
        $scope.exchange2send.users = $scope.angular_users;

        // Arreglo Pairs:
        for(var i=0; i<$scope.exchange2send.users.length; i++) {
            for(var j=0; j<$scope.exchange2send.users[i].pairs.length; j++) {
                delete $scope.exchange2send.users[i].pairs[j].pair
            }
        }

        // Arreglo Apilinks:
        for(var i=0; i<$scope.angular_apilinks.length; i++){
            delete $scope.angular_apilinks[i].reference;
        }
        $scope.exchange2send.apilinks = $scope.angular_apilinks;

        // Visualizacion final de JSON:
    }

    // HTTP Requests:

    /* Function: addExchange()
     * Arguments: -
     * Output: -
     * Method: POST
     * Summary: Send POST data JSON for add new Exchange
     */
    $scope.addExchange = function() {        
            
        // Exchange Constructor for POST HTTP:   Object { general: Object, users: Array[2], apilink: Array[2] }    
        $scope.verJSONExchange();

        // Send JSON - HTTP Request:
        var exchange = {};
        var data_exchange2send={};

        if($scope.exchange.general.seleccionado>1 && $scope.exchange.general.seleccionado<7){
            for(i in $scope.exchanges){
            if($scope.exchanges[i]['general']['idExchange']==$scope.exchange.general.seleccionado){
                if($scope.exchange2send.general.prioridad.length==0){
                 new PNotify({text: "Priority can't be empty.", type: 'warning', hide: true, styling: 'bootstrap3',buttons:{
                        sticker: false
                    }});
                 return false;
                }

                exchange = {
                'idExchange':$scope.exchange.general.seleccionado,
                "name" :        $scope.exchanges[i]['general']['name'],
                "type" :        $scope.exchange2send.general.tipo,
                "status":       $scope.exchange2send.general.status,
                "priority" :    $scope.exchange2send.general.prioridad,
                "idModifyUser": parseInt($scope.idUser)
                }
            }
        }
            $scope.exchange2send.general = exchange;
        }else{

            if($scope.exchange2send.general.nombre.length==0){
                new PNotify({text: "Exchange name can't be empty.", type: 'warning', hide: true, styling: 'bootstrap3',buttons:{
                        sticker: false
                    }});
                return false;
            }else if($scope.exchange2send.general.tipo==null){
                new PNotify({text: "Exchange type can't be empty.", type: 'warning', hide: true, styling: 'bootstrap3',buttons:{
                        sticker: false
                    }});
                return false;
            }else if($scope.exchange2send.general.prioridad.length==0){
                 new PNotify({text: "Priority can't be empty.", type: 'warning', hide: true, styling: 'bootstrap3',buttons:{
                        sticker: false
                    }});
                 return false;
            }
            
            exchange = {
            "name" :        $scope.exchange2send.general.nombre,
            "type" :        $scope.exchange2send.general.tipo,
            "priority" :    $scope.exchange2send.general.prioridad,
            "status":       $scope.exchange2send.general.status
            }
            $scope.exchange2send.general = exchange;
            
        }
        
        $http({
            url:addExchangeUserApilinkUri,
            method:'POST',
            headers: {
                'Content-Type':'application/json'
            },
            data:$scope.exchange2send
        })

        .then(function(exito) {
            $("#botonCerrarModal").click();
            if (exito.data['data'][0]==true) {
                new PNotify({text: "Exchange already exists.", type: 'warning', hide: true, styling: 'bootstrap3'});
            } else if (exito.data['data'][1]==true){
                new PNotify({text: "Internal Exchange already exists (only one is permitted).", type: 'warning', hide: true, styling: 'bootstrap3'});
            } else {
                showAllExchanges();
                new PNotify({ 
                    text: 'Exchange added successfully.',
                    type: 'success',
                    hide: true,
                    styling: 'bootstrap3',
                    buttons:{
                        sticker: false
                    },
                });
            }
        }, function(error) {
            new PNotify({
                text: "Exchange can't be added.",
                type: 'warning',
                hide: true,
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                },
            });
        })
    }

    /* Function: updExchange()
     * Arguments: -
     * Output: -
     * Method: PUT
     * Summary: Send PUT data JSON for modify an Exchange
     */
    $scope.updExchange = function() {
        // Exchange Constructor for POST HTTP: 
        $scope.verJSONExchange();
        
        // Send JSON - HTTP Request:
        var exchange = {};
           
        exchange = {
            "idExchange" :  $scope.exchange2send.general.idExchange,
            "name" :        $scope.exchange2send.general.nombre,
            "type" :        $scope.exchange2send.general.tipo,
            "priority" :    $scope.exchange2send.general.prioridad,
            "status":       $scope.exchange2send.general.status,
            "idModifyUser": parseInt($scope.idUser)
        }
        $scope.exchange2send.general = exchange;

        for(var i=0;i<$scope.exchange2send.apilinks.length;i++){
            $scope.exchange2send.apilinks[i]['status'] = 1;
            $scope.exchange2send.apilinks[i]['idModifyUser'] = parseInt($scope.idUser);
        }

        for(var i=0;i<$scope.exchange2send.users.length;i++){
            $scope.exchange2send.users[i]['status'] = 1;
            $scope.exchange2send.users[i]['idModifyUser'] = parseInt($scope.idUser);   

            for(var j=0;j<$scope.exchange2send.users[i].pairs.length;j++){
                $scope.exchange2send.users[i].pairs[j]['status'] = 1;
            }
        }
        $http({
            url:updExchangeUserApilinkUri,
            method:'PUT',
            headers: {
                'Content-Type':'application/json'
            },
            data:$scope.exchange2send
        })
        .then(function(exito) {
            $("#botonCerrarModal").click();
             if (exito.data[0]==true) {
                new PNotify({text: "Exchange already exists.", type: 'warning', hide: true, styling: 'bootstrap3',buttons:{
                    sticker: false
                }});
            } else if (exito.data[1]==true){
                new PNotify({text: "Internal Exchange already exists (only one is permitted).", type: 'warning', hide: true, styling: 'bootstrap3',buttons:{
                    sticker: false
                }});
            } else if((exito.data[0]!=true && exito.data[1]!=true) ) {
            new PNotify({ 
                text: 'Successfully updated exchange.',
                type: 'success',
                hide: true,
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                }
            });
            $scope.exchange={};
            showAllExchanges();

             }else{
            new PNotify({text: "Exchange can't be updated", type: 'warning', hide: true, styling: 'bootstrap3',buttons:{
                    sticker: false
                }});
        }
        }, function(error) {
            new PNotify({
                text: "Exchange can't be updated.",
                type: 'warning',
                hide: true,
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                },
            });
        })
    }

    /* Function: delExchange()
     * Arguments: -
     * Output: -
     * Method: PUT
     * Summary: Send DELET data JSON for erase an Exchange
     */
    function delExchange(id_exchange) {
        $http({
            url:delExchangeUri,
            method:'PUT',
            headers: {
                'Content-Type':'application/json'
            },
            data:{
                'idExchange':id_exchange,
                'status' : 2
            }
        })
        .then(function(exito) {
            $("#botonCerrarModal").click();
            new PNotify({ 
                text: 'Successfully eliminated exchange.',
                type: 'success',
                hide: true,
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                },
            });
            $scope.exchange={};
            showAllExchanges();
        }, function(error) {
            new PNotify({
                text: error.data.mensaje,
                type: 'warning',
                hide: true,
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                },
            });
        })
    }

    // ------ [CHANGED] End Added: Angular 1.0 -------

    apiApiUser = factory_endPoints.getEndPoints('apiUser');
    getPairsUri = factory_endPoints.getEndPoints('getPairs');
    getFormatNamesUri = factory_endPoints.getEndPoints('getFormatNames');

    $scope.apiUser={};
    $scope.apiUsers=[];
    $scope.switchStatus=false;
    $scope.switchVerTodos=false;

    function busApiUser(){
        var url= apiApiUser;
        $http({
            url:url,
            method:'GET',
            headers: {
                'Content-Type':'application/json'
            }
        })
        .then(function(exito) {
            $scope.apiUsers=exito.data.datos;
        },function(error) {
            new PNotify({ 
                text: "Something goes wrong, reloading",
                type: 'warning',
                hide: true,
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                },
            });
            busApiUser();
        })
    }

    $scope.con_modal = function(type='A', apiUser=null, index=null){
        $scope.apiUser={};
        $scope.cleanModal();
        if (type=='A') {
            getFormatNames();
            $scope.counter_usu = 0;
            $scope.counter_link = 0;
            $scope.counter_pair = 0;

            $scope.apiUser={};
            $scope.modApiUser= false;
            $scope.apiUser.pairs  = []; 
            $scope.apiUser.usersExchange = []; 
            $scope.apiUser.formatsExchange = []; 
            $scope.modalTitle ='Add Exchange';
        }
        if (type == 'M') {
            $scope.counter_usu = 0;
            $scope.counter_link = 0;
            $scope.counter_pair = 0;

            $scope.modApiUser = true;
            $scope.apiUser.pairs  = [];
            $scope.apiUser.usersExchange  = [];
            $scope.apiUser.formatsExchange  = [];
            $scope.modalTitle = 'Modify Api User';

            $scope.indexApiUSer = index;
            
            $scope.apiUser.pairs.push(apiUser.pairs);
            $scope.apiUser.general.push(apiUser.general);
            $scope.apiUser.usersExchange.push(apiUser.usersExchange);
            $scope.apiUser.formatsExchange.push(apiUser.formatsExchange);

            if ((apiUser.general.status == 'active') && ($scope.switchStatus != true))
                $("#swich1").click();
            if ((apiUser.general.status == 'inactive') && ($scope.switchStatus == true))
                $("#swich1").click();
        }
        getCoins();
    }

    $scope.add_list_scope = function(type){
        if (type == 'users'){
            $scope.apiUser.usersExchange.push($scope.apiUser.user);
            $scope.apiUser.user = {};
            delete $scope.apiUser.user;
        } else if (type == 'formats') {
            $scope.apiUser.formatsExchange.push($scope.apiUser.format);
            $scope.apiUser.format = {};
            delete $scope.apiUser.format;
        }else if (type == 'pairs'){
            $scope.apiUser.pairs.push($scope.apiUser.pair);
            $scope.apiUser.pair = {};
            delete $scope.apiUser.pair;
        }else{
            new PNotify({ 
                text: 'Not valid type add',
                type: 'warning',
                hide: true,
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                },
            });
        }
    }

    $scope.addApiUser = function(){
        var exchange = document.getElementsByName("exchange")[0].value;
        var exchangetype = document.getElementsByName("exchangetype")[0].value;
        var priority = document.getElementsByName("priority")[0].value;
        if (exchange!='' && exchangetype!='' && priority!='') {
            $scope.blankGeneralForm();
            var nUsers = $scope.lst_username.length;
            var nApiLinks = $scope.lst_reference.length;
            var nPairs = $scope.lst_pair.length;

            if(nUsers>=1 && nApiLinks>=2 && nPairs>=1) {

                // ------ Fill DATA ApiUser to send HTTP POST: -----
                var i;
                for (i=0; i<nUsers; i++) {
                    var usuario = {
                        "username" : $scope.lst_username[i],
                        "credentials" : {
                            "secret":$scope.lst_apisecret[i],
                            "key":$scope.lst_apikey[i]
                        }
                    }
                    $scope.apiUser.usersExchange.push(usuario);
                }

                var i;
                for (i=0; i<nApiLinks; i++) {
                    var apilink = {
                        //"reference" : $scope.lst_reference[i],
                        "formatName" : $scope.lst_tradetype[i], 
                        "url" : $scope.lst_url[i],
                        "method" : $scope.lst_method[i],
                        "params" : $scope.lst_params[i],
                        "dataType" : $scope.lst_datatype[i] 
                    }
                    $scope.apiUser.formatsExchange.push(apilink);
                }

                var i;
                for (i=0; i<nPairs; i++) {
                    var pair = {
                        "pair" : $scope.lst_pair[i]
                    }
                    $scope.apiUser.pairs.push(pair);
                }
                // -------------------------------------------------
                $http({
                    url:apiApiUser,
                    method:'POST',
                    headers: {
                        'Content-Type':'application/json'
                    },
                    data:$scope.apiUser
                })
                .then(function(exito) {
                    new PNotify({ 
                        text: 'Exchange added successfully.',
                        type: 'success',
                        hide: true,
                        styling: 'bootstrap3',
                        buttons:{
                            sticker: false
                        },
                    });
                    $scope.apiUser={};
                    $("#botonCerrarModal").click();
                    busApiUser();
                },function(error) {
                    new PNotify({
                        text: error.data.mensaje,
                        type: 'warning',
                        hide: true,
                        styling: 'bootstrap3',
                        buttons:{
                            sticker: false
                        },
                    });
                })
                // -----------------------------------------------
            } else {
                window.alert("It's neccessary fill as minimum:\n\t- 1 register for User\n\t- 2 registers for ApiLink.\n\t- 1 register for Pairs");
            }    
        } else {
            $scope.bgCol_exchange = ((exchange=='')?'#FFCCCC':'#FFFFFF');
            $scope.bgCol_exchangetype = ((exchangetype=='')?'#FFCCCC':'#FFFFFF');
            $scope.bgCol_priority = ((priority=='')?'#FFCCCC':'#FFFFFF');
        }
    }

    $scope.updApiUser = function(){
        if ($scope.switchStatus==true)
            $scope.apiUser.general.status = "active"
        else
            $scope.apiUser.general.status = 'inactive'

        $http({
            url:apiApiUser,
            method:'PUT',
            headers: {
                'Content-Type':'application/json'
            },
            data:$scope.apiUser
        })
        .then(function(exito) {
            $scope.apiUsers[$scope.indexApiUSer]=exito.data.datos;
            new PNotify({ 
                text: 'Successfully modified ApiUser.',
                type: 'success',
                hide: true,
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                },
            });
            $scope.apiUser={};
            $("#botonCerrarModal").click();
            busApiUser();
        },function(error) {
            new PNotify({ 
                text: error.data.mensaje,
                type: 'warning',
                hide: true,
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                },                
            });
        })
    }

    $scope.confirEliminar = function(apiUser, index){
        $scope.indexApiUSer=index;
        
        (new PNotify({
            title: 'Eliminar Api User',
            text: ' <center><h5>Be sure to remove the ApiUser '+ apiUser.name+'? </h5> </center>',
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
            enviarEliminar(apiUser);
        }).on('pnotify.cancel', function() {
            
        });
    }

    function enviarEliminar(apiUser){
        $http({
            url:apiApiUser,
            method:'DELETE',
            headers: {
                'Content-Type':'application/json'
            },
            data:{"id":apiUser.id}
        })
        .then(function(exito) {
            if (exito.data.datos){
                $scope.apiUsers.splice($scope.indexApiUSer,1);
                new PNotify({ 
                    text: 'Successfully eliminated ApiUser.',
                    type: 'success',
                    hide: true,
                    styling: 'bootstrap3',
                    buttons:{
                        sticker: false
                    },
                })
            }
            else
                new PNotify({ 
                    text: 'An error occurred when removing the ApiUser.',
                    type: 'danger',
                    hide: true,
                    styling: 'bootstrap3',
                    buttons:{
                        sticker: false
                    },
                })
        },function(error) {
            new PNotify({ 
                text: error.data.mensaje,
                type: 'warning',
                hide: true,
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                },
            });
        })
    }

    function getCoins(){
        $http({
            url:getPairsUri,
            method:'GET',
            headers: {
                'Content-Type':'application/json'
            },
        }).then(function(exito) {
            if (typeof exito.data.success === 'undefined'){
                $scope.pairs = exito.data;
            }else {
                new PNotify({
                    text: exito.data.mensaje, 
                    type: 'danger', 
                    hide: true, 
                    styling: 'bootstrap3',
                    buttons:{
                        sticker: false
                    },
                })
            }
        },function(error) {
            // new PNotify({ text: error.data.mensaje,type: 'warning',hide: true,styling: 'bootstrap3'});
        })
    }

    function getFormatNames(){
        $http({
            url:getFormatNamesUri,
            method:'GET',
            headers: {
                'Content-Type':'application/json'
            },
        }).then(function(exito) {
            //if (typeof exito.data.success === 'undefined'){
            //    $scope.formatnames = exito.data;
            //}else {
            //   new PNotify({text: exito.data.mensaje, type: 'danger', hide: true, styling: 'bootstrap3'})
            //}
            $scope.formatnames = [];
            $scope.formatnames = JSON.parse(exito.data);
        },function(error) {
             // new PNotify({ text: error.data.mensaje,type: 'warning',hide: true,styling: 'bootstrap3'});
        })
    }

    $scope.cambiarLista = function(){
        if ($scope.switchVerTodos==true){
            $scope.listDue=true;
        }else{
            $scope.listDue=false;
        }
    }

    $scope.openModal = function(type){
        if (type=='U') {
            $scope.inputTemplate = {
                id: $scope.counter_usu,
                value: ''
            };
            $scope.counter_usu += 1;
            $scope.apiUser.usersExchange.push($scope.inputTemplate);
        }
        else if(type=='L'){
            $scope.inputTemplate = {
                id: $scope.counter_link,
                value: ''
            };
            $scope.counter_link += 1;
            $scope.apiUser.formatsExchange.push($scope.inputTemplate);
        }else{
            $scope.inputTemplate = {
                id: $scope.counter_pair,
                value: ''
            };
            $scope.counter_pair += 1;
            $scope.apiUser.pairs.push($scope.inputTemplate);
        }
    }

    function addclone($scope) {
        $scope.inputCounter = 0;
        $scope.inputs = [{id:'input'}];
        
        $scope.add = function() {
            $scope.inputTemplate = {
                id: 'input-' + $scope.inputCounter,
                name: ''
            };
            $scope.inputCounter += 1;
            $scope.inputs.push($scope.inputTemplate);
        };
    }

    //busApiUser();

    // Funciones al cargar WebPage:
    showAllExchanges();
    showAllPairs();
    showAllFormats();

    var elem = document.querySelector('#swich2');
    var init = new Switchery(elem,{ color:'#26B99A' });
    var elem2 = document.querySelector('#swich1');
    var init2 = new Switchery(elem2,{ color:'#26B99A' });

}]);

angular.element(function() {
    angular.bootstrap(document, ['coreModule']);
});