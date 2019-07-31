app.config(function($routeProvider){
    $routeProvider
    .when('/',{
        templateUrl: 'static/html/packagesCoins.html',
        controller: 'packagesCoinsController'
    });
})
app.controller('packagesCoinsController',["$scope", "$http","factory_coins", "factory_endPoints", function($scope, $http, factory_coins, factory_endPoints){
    apiCountryCripto = factory_endPoints.getEndPoints('countryCripto');
    apiGetPackages = factory_endPoints.getEndPoints('getPackages');
    apiGetTransaction = factory_endPoints.getEndPoints('getTransaction');
    apiPackagesCoins = factory_endPoints.getEndPoints('packagesCoins');
    $scope.newPackage = {};
    $scope.modalModif = false;
    $scope.indexPackage = null;
    function getCountries(){
        $http({
            url: apiCountryCripto,
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(function (response){
            $scope.countries = response.data.datos;
        }, function(error){
            new PNotify({ text: error.data.mensaje, type: 'error', hide: true, styling: 'bootstrap3'});
        });
    };
    getCountries();
    $scope.getPackages = function(id_coin_fiat, id_criptocoin){
        var objectCoins = {};
        objectCoins = {
            "id_criptocoin":id_criptocoin,
            "id_coin_fiat":id_coin_fiat
        };
        $http({
            url: apiGetPackages,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            data: objectCoins
        }).then( function(response){
            $scope.packages = response.data.datos;
        },function(error){
            new PNotify({ text: error.data.mensaje, type: 'error', hide: true, styling: 'bootstrap3'});
        });
     };
      $scope.getTransactionPackages = function(id_package){
        changeBut = $('#but-' + id_package).attr('class');
        if(id_package != $scope.butIdPackage)
            $('#but-' + $scope.butIdPackage).removeClass('fa-angle-up').addClass('fa-angle-down');
        $scope.butIdPackage = id_package;
        if(changeBut.indexOf('fa-angle-down')>0){
            $('#but-' + id_package).removeClass('fa-angle-down').addClass('fa-angle-up');
            $scope.transactionsDetails = [];
            var objectPackages;
            objectPackages = {
                "id": id_package
            };
            $http({
                url: apiGetTransaction,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                data: objectPackages
            }).then( function(response){
                $scope.transactionsDetails = response.data.datos;
            },function(error){
                new PNotify({ text: error.data.mensaje, type: 'error', hide: true, styling: 'bootstrap3'});
            });
        }
        else
            $('#but-' + id_package).removeClass('fa-angle-up').addClass('fa-angle-down');
        
     };
     $scope.formNewPackage = function(){
        $scope.newPackage.type = ($scope.modalModif)?$scope.newPackage.type:"B";
        amount = $scope.newPackage.amount_order;
        $scope.newPackage.amount_order = ($scope.newPackage.type == "S")?$scope.newPackage.amount_order*-1:$scope.newPackage.amount_order;
        typeTransaction = ($scope.newPackage.type == "S")? ' debitó':' acreditó';
        $http({
            url: apiPackagesCoins,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            data: $scope.newPackage
            }).then(function(response){
            for (key in $scope.criptoCoins){
                if ($scope.criptoCoins[key].id == $scope.newPackage.id_criptocoin){
                    criptoName = $scope.criptoCoins[key].name;
                    break;
                }
            };
            for (key in $scope.fiatCoins){
                if ($scope.fiatCoins[key].id == $scope.newPackage.id_coin_fiat){
                    fiatName = $scope.fiatCoins[key].name;
                    break;
                }
            };
            new PNotify({
                text: 'Transaccion agregada con éxito al paquete de ' + $scope.newPackage.price + ' ' + fiatName +  
                      ' , se' + typeTransaction + ' un total de ' + amount + '(' + criptoName +')', 
                type: 'success', 
                hide: true, 
                styling: 'bootstrap3'});
            if($scope.modalModif){
                $scope.getPackages($scope.packageSelected.id_coin_fiat,$scope.packageSelected.id_criptocoin);
                $scope.newPackage.amount_order = null;
                $scope.newPackage.type = null;
                $scope.newPackage.description = null;
            }
            else{
                $scope.newPackage = {};
                getCountries();
                $scope.packages = {};
            }
            $('#closeModal').click();
         },function(error){
             new PNotify({ text: error.data.mensaje, type: 'error', hide: true, styling: 'bootstrap3'});
         });
     }; 
     $scope.openModal = function(modificando=false){         
         if(!modificando){
            $scope.newPackage = {};
            $scope.modalModif = false;
         }
        factory_coins.getCriptoCoins().then( function(response){
            $scope.criptoCoins = [];
            $scope.criptoCoins = response;
            if(modificando){
                $scope.newPackage.id_criptocoin = $scope.packageSelected.id_criptocoin;
            };           
        });
        factory_coins.getFiatCoins().then(function(response){
            $scope.fiatCoins = [];
            $scope.fiatCoins = response;
            if(modificando){
                $scope.newPackage.id_coin_fiat = $scope.packageSelected.id_coin_fiat;
            };
        });
     };
    $scope.packageSelection = function(package, index = null){
        $scope.indexPackage = index;
        $scope.criptoCoins = [];
        $scope.fiatCoins = [];
        $scope.modalModif = true;
        $scope.newPackage = {};        
        $scope.openModal(true); 
        $scope.packageSelected = package;        
        $scope.newPackage.price = package.price;
        $scope.newPackage.id_criptocoin = package.id_criptocoin;
        $scope.newPackage.id_coin_fiat = package.id_coin_fiat;
    };
     $scope.getTransactionsPackage = function(idPackage){
        packageJson = {};
        packageJson.id = idPackage;
        $http({
            url:apiGetTransaction,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            data: packageJson
        }).then(function(response){
            $scope.packages[$scope.indexPackage] = response;
        }, function(error){
            new PNotify({ text: error.data.mensaje, type: 'error', hide: true, styling: 'bootstrap3'});
        });
     }
     $scope.addTransaction = function(){
        typeTransaction = ($scope.newPackage.type == "S")? ' debitar':' acreditar';
        for (key in $scope.criptoCoins){
            if ($scope.criptoCoins[key].id == $scope.newPackage.id_criptocoin){
                criptoName = $scope.criptoCoins[key].name;
                break;
            }
        };
        for (key in $scope.fiatCoins){
            if ($scope.fiatCoins[key].id == $scope.newPackage.id_coin_fiat){
                fiatName = $scope.fiatCoins[key].name;
                break;
            }
        };
        (new PNotify({
            title: 'Confirmar transacción',
            text: 'Desea '+ typeTransaction + ' ' + $scope.newPackage.amount_order + '(' + criptoName +')' + 
                'al paquete de' +  $scope.newPackage.price + ' ' + fiatName + ' ?',
            icon: 'fa fa-trash fa-spin  fa-fw text-danger',
            hide: false,
            type: 'success',
            styling: 'bootstrap3',
            confirm: {
                confirm: true,
                buttons:[{text:'Aceptar'},{text:'cancelar',addClass :'btn btn-danger'}]   
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
                $scope.formNewPackage();
            }).on('pnotify.cancel', function() { });
        };
    }
]);

angular.element(function() {
      angular.bootstrap(document, ['coreModule']);
});