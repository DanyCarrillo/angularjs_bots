angular.module('paginator', []).directive('pagination', ['$http','$filter',function ($http,$filter) {
    var template="";
    template+=' <ul class="pagination pagination-sm pull-right" style="margin:0;margin-right:1em;margin-left:1em;"> ';
    template+='     <li ng-class="{\'\disabled\'\:cant2}" ng-click="prenext(false,current)"><a>«</a></li> ';            
    template+='     <li href="" ng-repeat="num in topindex_array track by $index" ng-show="limits(num)" ng-class="{\'\active\'\:(current===(num))}"  ng-click="prenext(null,null,(num))"><a href="">{{(num)}}</a></li>                                  ';
    template+='     <li ng-class="{\'\disabled\'\:cant}" ng-click="prenext(true,current)"><a  >»</a></li>';
    template+=' </ul> ';

    return {
        restrict: 'E',
        replace: true,
        transclude: true,
        scope:{
            data:"=data",
            /*indice actual de la pagina por defecto debe ir en 1*/
            current:"=current",
            /*numero de resultados a mostrar por pagina*/
            totalresult:"=totalresult",
            /*numero de opciones a mostrar si pongo 4 me mostrara  << 1,2,3,4 >>*/
            topindex:"=topindex",
            /*arreglo completo con todos los registros sin filtrar*/
            actual:"=?actual",
            /*arreglo principal el cual utilizaremos para mostrar las listas*/
            arreglo:"=arreglo",
            /*-----*/
            clean:"=?clean",
            /*url de la ruta para obtener la informacion a paginar*/
            url:"=url",
            /*De ahora en adelante el paginador sera quien filtre la informacion, osea que la variable
            que utilizan en el ng-repeat para filtrar debera ser asignado a este atributo*/
            filtering:"=filter",
            /*en el caso de que el paginador necesite otra informacion extra para resolver los resultados*/
            parametros:"=parametros",
            /**/
        },
        template:template,
        link: function (scope, iElement, iAttrs) {
            if (!scope.actual) {scope.actual=[]};
            scope.limits=function(val) {
                var bol=false;
                
                if (val>scope.top) bol=false;
                else bol=true;
                return bol;
            }

            scope.safeApply = function(fn) {
              var phase = scope.$$phase;
              if(phase !== '$apply' && phase !== '$digest')
                scope.$apply();
        };
        scope.$watch("actual", function (newval) {
            scope.not=false;
            scope.actual=(scope.actual)?scope.actual:[];
            if ($.map(scope.actual,function (val,ind) {scope.actual[ind].index=ind+1;})) {  
                scope.total=scope.actual.length;
                scope.range();
            } 
            
            },true);
        scope.call=function() {
            $http({url:scope.url/*+"?paginator="+JSON.stringify({page:scope.current,page_results:scope.totalresult})*/,
                params:scope.parametros
                ,method:"GET"})
            .then(function(exito) {

                scope.data=exito.data;       
                scope.actual=exito.data.result;       
               

            },function(error) {
              
                alert("Ha ocurrido un error al obtener la informacion, verifique que tenga acceso a internet o consulte a su operador","Aceptar");
                
            })
        }
        if (scope.url) scope.call();
        scope.total=scope.total || 1;
        scope.prenext=function(bol,current,set) {
            scope.not=false;
            if (!set) {

             if (bol) 
             {
                if (scope.top>scope.current) {scope.current++;scope.cant=false;
                
                if (scope.current>scope.topindex && scope.current<=scope.top) {
                    $.map(scope.topindex_array,function(val,ind) {
                        scope.topindex_array[ind]=++val;
                    })
                    
                }
            }
            else scope.cant=true;
        }else
        {
            if (scope.current>1) {
                scope.current--;scope.cant2=false}
                if (scope.current<scope.topindex_array[0]) {
                    $.map(scope.topindex_array,function(val,ind) {
                        scope.topindex_array[ind]=--val;
                    })
                    
                }
                else scope.cant2=true;

            }
        }else{scope.current=parseInt(set);scope.cant2=false;scope.cant=false;}

        scope.range();
    }
    scope.current=scope.current || 1;
    scope.$watch('filtering', function(newValue, oldValue, scope) {
       scope.not=false;
       scope.range();
   },true);


    scope.range=function() {
            if (scope.not)return false;
            scope.arreglo=angular.copy($filter('filter')(scope.actual, scope.filtering))
            scope.total=scope.arreglo.length;
            scope.clean=angular.copy(scope.arreglo);
            scope.arreglo=scope.arreglo.slice(((scope.current*scope.totalresult)-scope.totalresult),((scope.current*scope.totalresult)-scope.totalresult)+scope.totalresult);
            scope.top=Math.ceil(scope.total/scope.totalresult);

    }

    scope.$watch('topindex', function(){
        scope.gentopindex(scope.topindex);
    });
    scope.gentopindex = function(i){
        scope.topindex_array = [];
        $.map(new Array(i), function(v,i){
          scope.topindex_array.push(i+1);
      });
    };


    scope.getNumber = function(num) {
        return new Array(num);   
    }

}
};
}])