app.config(function ($routeProvider) {
    $routeProvider
    .when('/', {
        templateUrl: '../static/html/logUsersListar.html',
        controller: 'logUsersController'
    })
})

app.controller('logUsersController', ["$scope", "$http", "factory_endPoints",function ($scope, $http, factory_endPoints) {
// Spinner
$scope.$on('LOAD',function(){$scope.loading=true});
$scope.$on('UNLOAD',function(){$scope.loading=false});
//Endpoints
all_userLogs = factory_endPoints.getEndPoints('getUserLogs');
//variables globales
$scope.userLogs=[]
function showLogs(){
    $scope.$emit('LOAD');
	$http({
		url:all_userLogs,
		method:'GET',
		headers:{
			'Content-Type': 'application/json'
		}
	}).then(function(exito){
        $scope.$emit('UNLOAD');
               var action=[];
               var data=[]
               var change=[]
               for (i in exito.data['datos']) {
                for(x in exito.data['datos'][i] ){
                    var dict={}
                    dict['action'] = [exito.data['datos'][i][x].description.split('"')][0][3];
                    dict['created_date'] = exito.data['datos'][i][x].created_date;
                    if(exito.data['datos'][i][x].id_table!=0){
                    	dict['id_table']=exito.data['datos'][i][x].id_table;
                    	dict['description']=exito.data['datos'][i][x].description;
                    }else{
                    	dict['id_table']="";
                    	dict['data_description']="";
                    }
                    dict['stored_proc']=exito.data['datos'][i][x].stored_proc;
                    dict['username']=exito.data['datos'][i][x].username;
                    dict['id_user_logs']=exito.data['datos'][i][x].id_user_logs;
                	$scope.userLogs.push(dict);
                }
               }

	}, function (error){
    $scope.$emit('UNLOAD');
	 new PNotify({
            text: "Something is wrong getting this tickers information",
            type: 'warning',
            hide: true,
            styling: 'bootstrap3',
            buttons:{
                sticker: false
            },
        });
})

}
showLogs();


//Escuchador de scroll
window.onscroll = function() {scrollFunction()};
function scrollFunction() {
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        document.getElementById("myBtn").style.display = "block";
    } else {
        document.getElementById("myBtn").style.display = "none";
    }
}

// envia a la posicion inicial de la pagina
$scope.topFunction=function() {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
};


}]);


angular.element(function () {
    angular.bootstrap(document, ['coreModule']);
});