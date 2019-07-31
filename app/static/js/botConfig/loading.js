angular.module('load', []).directive('loading', ["$http",function ($http) {
var template="";
template+=' <div class="modal in" id="modal_basic2" style="z-index:10000"><div class="modal-backdrop  in"></div>';

template+='<center><img src="/img/loader150px.gif" style="margin-top:20%"></center>';

template+=' </div>';
    return {
        restrict: 'A',
        template:template,
        scope:{},
        link: function (scope, elm, iAttrs) {
          
                scope.isLoading = function () {
                    return $http.pendingRequests.length > 0;
                };

                scope.$watch(scope.isLoading, function (v)
                {
                  if (!v){ $("#modal_basic2").hide();}
                  else {$("#modal_basic2").show();};
                });
        }
    };
}])