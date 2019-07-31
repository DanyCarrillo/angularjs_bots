app.config(function ($routeProvider) {
    $routeProvider
    .when('/', {
        templateUrl: '../static/html/userListar.html',
        controller: 'userController'
    })
})

app.controller('userController', ["$scope", "$http", "factory_endPoints", function ($scope, $http, factory_endPoints) {
    apiUser = factory_endPoints.getEndPoints('user');
    apiBlockUser = factory_endPoints.getEndPoints('blockUser');
    $scope.users2 = [];
    $scope.modalTitle;
    $scope.usuario = {};
    $scope.modUser = false;

    $scope.con_modal = function (type='A', user=null, index=null) {
        if (type == 'A') {
            $scope.modalTitle = 'Add user ';
            $scope.modUser = false;
            $scope.isDisable = false;
            $scope.usuario.firstname = "";
            $scope.usuario.lastname = "";
            $scope.usuario.username = "";
            $scope.usuario.email = "";
            $scope.usuario.password = "";
            $scope.usuario.pass_confirm = "";
        }
        if (type == 'M') {
            $scope.modalTitle = 'Edit user ';
            $scope.usuario.id_user = user.id_user;
            $scope.usuario.firstname = user.name.split(' ')[0];
            $scope.usuario.lastname = user.name.split(' ')[1];
            $scope.usuario.username = user.username;
            $scope.usuario.email = user.email;
            $scope.usuario.password = "";
            $scope.usuario.pass_confirm = "";
            $scope.modUser = true;
            $scope.isDisable = true;
            $scope.indexUser = index;
            if ($scope.switchCamPass == true)
                $("#swich1").click();
        }
    }

    function validacionEmail(email){
        if(/^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(email)){
            return true;
        }else{  
            return false;
        }
    }

    $scope.modUserGeneral = function () {
        var user = {};
        user.firstname = $scope.usuario.firstname;
        user.lastname = $scope.usuario.lastname;
        if(validacionEmail($scope.usuario.email)==true){ 
            user.email = $scope.usuario.email;
        }else{
            new PNotify({
                text: "Invalid email",
                type: 'danger',
                hide: true,
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                },
            });
            return false
        }
        user.username = $scope.usuario.username;
        user.id_user = $scope.usuario.id_user;
        if (user.firstname == null || user.firstname == 0 || /^\s+$/.test(user.firstname)) {
            new PNotify({
                text: "Filed firstname can't be empty", 
                type: 'warning', 
                hide: true, 
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                },
            });
            return false
        }
        if (user.lastname == null || user.lastname == 0 || /else^\s+$/.test(user.lastname)) {
            new PNotify({
                text: "Filed lastname can't be empty", 
                type: 'warning', 
                hide: true, 
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                },
            });
            return false
        }
        if (user.email == null || user.email == 0 || /^\s+$/.test(user.email)) {
            new PNotify({
                text: "Filed email can't be empty", 
                type: 'warning', 
                hide: true, 
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                },
            });
            return false
        }
        if (user.username == null || user.username == 0 || /^\s+$/.test(user.username)) {
            new PNotify({
                text: "Filed username can't be empty", 
                type: 'warning', 
                hide: true, 
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                },
            });
            return false
        }else{
            if ($scope.switchCamPass == true) {
                user.password = $scope.usuario.password;
                user.pass_confirm = $scope.usuario.pass_confirm;
                if (user.password == 0 || user.password == null || user.password.length > 12) {
                    new PNotify({
                        text: "The password is empty or exceeds the range of 12 characters",
                        type: 'warning',
                        hide: true,
                        styling: 'bootstrap3',
                        buttons:{
                            sticker: false
                        },
                    });
                    return false
                }
                if (user.pass_confirm == 0 || user.pass_confirm == null || user.pass_confirm.length > 12) {
                    new PNotify({
                        text: "The password is empty or exceeds the range of 12 characters",
                        type: 'warning',
                        hide: true,
                        styling: 'bootstrap3',
                        buttons:{
                            sticker: false
                        },
                    });
                    return false
                }
                if (user.password != user.pass_confirm || user.pass_confirm != user.password) {
                    new PNotify({
                        text: "The password does not match", 
                        type: 'warning', 
                        hide: true, 
                        styling: 'bootstrap3',
                        buttons:{
                            sticker: false
                        },
                    });
                    return false
                }
            }
            $http({
                url: apiUser,
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                data: user
            })
            .then(function (exito) {
                if (exito.data[0].success == true) {
                    $scope.users2[$scope.indexUser] = exito.data[0].datos;
                    new PNotify({
                        text: 'User has been modified successfully.',
                        type: 'success',
                        hide: true,
                        styling: 'bootstrap3',
                        buttons:{
                            sticker: false
                        },
                    });
                }else{
                    new PNotify({
                        text: exito.data[0].mensaje, 
                        type: 'warning', 
                        hide: true, 
                        styling: 'bootstrap3',
                        buttons:{
                            sticker: false
                        },
                    });
                }
            }, function (error) {
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
    }

    function enviarEliminar(user) {
        $http({
            url: apiUser,
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            data: {"id_user": user.id_user}
        })
        .then(function (exito) {
            if (exito.data.datos) {
                $scope.users2.splice($scope.indexUser, 1);
                new PNotify({
                    text: 'Suspended user.',
                    type: 'success',
                    hide: true,
                    styling: 'bootstrap3',
                    buttons:{
                        sticker: false
                    },
                })
            }else{
                new PNotify({
                    text: 'Something is wrong with the user\'s suspension.',
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

    $scope.confirEliminar = function (user, index) {
        $scope.indexUser = index;
        (new PNotify({
            title: 'Deleted user',
            text: 'Are you sure want\'s delete the user ' + user.username + '?',
            icon: 'fa fa-trash fa-spin  fa-fw text-danger',
            hide: false,
            type: 'success',
            styling: 'bootstrap3',
            confirm: {
                confirm: true,
                buttons: [
                    {text: 'Accept'}, 
                    {text: 'Cancel', addClass: 'btn btn-danger'}
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
        })).get().on('pnotify.confirm', function () {
            enviarEliminar(user);
        }).on('pnotify.cancel', function () {
        });
    }

    $scope.confirSuspender = function (user, index) {
        $scope.indexUser = index;
        (new PNotify({
            title: 'Suspend user',
            text: 'Are you sure want\'s suspend the user ' + user.username + '?',
            icon: 'fa fa-lock fa-spin  fa-fw text-danger',
            hide: false,
            type: 'info',
            styling: 'bootstrap3',
            confirm: {
                confirm: true,
                buttons: [
                    {text: 'Accept'}, 
                    {text: 'Cancel', addClass: 'btn btn-danger'}
                ]
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
            enviarSuspender(user);
        }).on('pnotify.cancel', function () {
        });
    }

    function enviarSuspender(user) {
        $http({
            url: apiBlockUser,
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            data: {"id_user": user.id_user}
        })
        .then(function (exito) {
            if (exito.data.datos) {
                $scope.users2[$scope.indexUser].status = 'inactive';
                new PNotify({
                    text: 'User suspended successfully.',
                    type: 'success',
                    hide: true,
                    styling: 'bootstrap3', buttons:{
                    sticker: false
                }
                })
            }else{
                new PNotify({
                    text: exito.data[0].mensaje,
                    type: 'danger',
                    hide: true,
                    styling: 'bootstrap3'
                })
            }
        }, function (error) {
            new PNotify({
                text: error.data.mensaje, 
                type: 'warning', 
                hide: true, 
                styling: 'bootstrap3', 
                buttons:{
                    sticker: false
                }
            });
        })
    }

    $scope.confirActivar = function (user, index) {
        $scope.indexUser = index;
        (new PNotify({
            title: 'Active user',
            text: 'Are you sure want\'s active the user ' + user.username + '?',
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
            enviarActivar(user);
        }).on('pnotify.cancel', function () {
        });
    }

    function enviarActivar(user) {
        $http({
            url: apiBlockUser,
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            data: {"id_user": user.id_user}
        })
        .then(function (exito) {
            if (exito.data.datos) {
                $scope.users2[$scope.indexUser].status = 'active';
                new PNotify({
                    text: 'User activated successfully.',
                    type: 'success',
                    hide: true,
                    styling: 'bootstrap3'
                })
            }else{
                new PNotify({
                    text: exito.data[0].mensaje,
                    type: 'danger',
                    hide: true,
                    styling: 'bootstrap3'
                })
            }
        }, function (error) {
            new PNotify({
                text: error.data.mensaje, 
                type: 'warning', 
                hide: true, 
                styling: 'bootstrap3'
            });
        })
    }

    $scope.addUser = function () {
        var firstname = $scope.usuario.firstname;
        var lastname = $scope.usuario.lastname;
        if(validacionEmail($scope.usuario.email)==true){ 
            var email = $scope.usuario.email;
        }else{
            new PNotify({
                text: "Email invalid",
                type: 'danger',
                hide: true,
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                },
            });
            return false
        }
        var username = $scope.usuario.username;
        var password = $scope.usuario.password;
        var confir_password = $scope.usuario.pass_confirm;

        if (firstname == null || firstname == 0 || /^\s+$/.test(firstname)) {
            new PNotify({
                title: 'Error', 
                text: 'Field firstname can\'t be null',
                hide: true, 
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                },
            });
            return false
        }
        if (lastname == null || lastname == 0 || /^\s+$/.test(lastname)) {
            new PNotify({
                title: 'Error', 
                text: 'Field lastname can\'t be null',
                hide: true, 
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                },
            });
            return false
        }
        if (email == null || email == 0 || /^\s+$/.test(email)) {
            new PNotify({
                title: 'Error', 
                text: 'Field email can\'t be null',
                hide: true, 
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                },
            });
            return false
        }
        if (username == null || username == 0 || /^\s+$/.test(username)) {
            new PNotify({
                title: 'Error', 
                text: 'Field username can\'t be null',
                hide: true, 
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                },
            });
            return false
        }
        if (password == null || password == 0 || password.length > 12) {
            new PNotify({
                title: 'Error',
                text: 'The password must not have a range greater than 12 characters or the field is empty',
                hide: true,
                styling: 'bootstrap3', 
                buttons:{
                    sticker: false
                }
            });
            return false
        }
        if (confir_password == null || confir_password == 0 || confir_password.length > 12) {
            new PNotify({
                title: 'Error',
                text: 'The password must not have a range greater than 12 characters or the field is empty',
                hide: true,
                styling: 'bootstrap3', 
                buttons:{
                    sticker: false
                }
            });
            return false
        }
        if (confir_password != password || password != confir_password) {
            new PNotify({
                title: 'Error', 
                text: 'The password confirmation does not match',
                hide: true, 
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                },
            });
            return false
        } else {
            $http({
                url: apiUser,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                data: $scope.usuario
            })
            .then(function (exito) {
               if (exito.data.success == true) {
                    $scope.users2.push(exito.data.datos);
                    new PNotify({
                        text: 'The user has been created.',
                        type: 'success',
                        hide: true,
                        styling: 'bootstrap3',
                        buttons:{
                            sticker: false
                        },
                    });
                }else{
                    new PNotify({
                        text: exito.data.mensaje, 
                        type: 'warning', 
                        hide: true, 
                        styling: 'bootstrap3',
                        buttons:{
                            sticker: false
                        },
                    });
                }
            }, function (error) {
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
    }

    function busUsuarios() {
        $http({
            url: apiUser,
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(function (exito) {
            $scope.users2 = exito.data.datos;
        }, function (error) {
            new PNotify({
                text: "Something is wrong getting this user information",
                type: 'warning',
                hide: true,
                styling: 'bootstrap3',
                buttons:{
                    sticker: false
                },
            });
        })
    }

    busUsuarios()
    var elem = document.querySelector('.js-switch');
    var init = new Switchery(elem, {color: '#26B99A'});
}]);

angular.element(function () {
    angular.bootstrap(document, ['coreModule']);
});