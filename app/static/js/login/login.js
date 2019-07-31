app.config(function ($routeProvider) {
    $routeProvider
    .when('/', {
        templateUrl: '../static/html/login.html',
        controller: 'loginController'
    });
})
app.controller('loginController', ["$scope", "$http", "factory_endPoints", function ($scope, $http, factory_endPoints) {
    $scope.apiLogin = factory_endPoints.getEndPoints('login');
    $scope.username;
    $scope.password;

    $scope.loguear = function () {
        var user = $scope.formLogin.username;
        var pass = $scope.formLogin.password;
        if (user == null || user == 0 || /^\s+$/.test(user)) {
            new PNotify({
                title: 'Error',
                text: 'El campo username no debe ser vacio',
                addclass: 'custom',
                icon: 'fa fa-hand-paper-o iconcolor',
                nonblock: {
                    nonblock: true
                }
            });
            return false
        }
        if (pass == null || pass == 0 || pass.length > 12) {
            new PNotify({
                title: 'Error',
                text: 'El campo password no debe ser vacio o supera el maximo de 12 caracteres',
                addclass: 'custom',
                icon: 'fa fa-hand-paper-o iconcolor',
                nonblock: {
                    nonblock: true
                }
            });
            return false
        }
        else {
            //var datos;
            //datos={"username": $scope.username, "password":$scope.password};
            //efecto de caer pantalla login
            $('.login').addClass('test');
            //muevea a un lado la pantalla de login
            setTimeout(function () {
                $('.login').addClass('testtwo')
            }, 300);
            //coloca pantalla de atenticando
            setTimeout(function () {
                    $(".authent").show().animate({right: -320}, {easing: 'easeOutQuint', duration: 600, queue: false});
                    $(".authent").animate({opacity: 1}, {duration: 200, queue: false}).addClass('visible');
                },
                300);
            //quita pantallita de autenticando
            setTimeout(function () {
                $(".authent").show().animate({right: 90}, {easing: 'easeOutQuint', duration: 600, queue: false});
                $(".authent").animate({opacity: 0}, {duration: 200, queue: false}).addClass('visible');
                $('.login').removeClass('testtwo')
            }, 2500);
            $http({
                url: $scope.apiLogin,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                data: $scope.formLogin
            })
            .then(function (exito) {
                var datoStorages = exito.data.datos.first_name;
                localStorage.setItem("key", datoStorages);
                localStorage.setItem("welcome","true");
                localStorage.setItem("idUserSession",exito.data.datos.id_user);
                $('.ui-pnotify-text').addClass('iconcolor');
                $('.ui-pnotify').addClass('iconcolor');
                setTimeout(function () {
                    new PNotify({
                        title: 'Success',
                        text: 'Checking redirection.',
                        addclass: 'custom',
                        icon: 'fa fa-hand-paper-o iconcolor',
                        nonblock: {
                            nonblock: true
                        }
                    });
                },950)
                setTimeout(function () {
                    location.href = '/';
                }, 2800);
            }, function (error) {
                $scope.mensajeAutenticate = error.data.mensaje;
                setTimeout(function () {
                    $('.login').removeClass('test');
                    $(".authent").hide();
                    new PNotify({
                        title: 'Error Autentication',
                        text: error.data.mensaje,
                        addclass: 'custom',
                        icon: 'fa fa-hand-paper-o iconcolor',
                        nonblock: {
                            nonblock: true
                        }
                    });
                    $('.ui-pnotify-text').addClass('iconcolor');
                    $('.ui-pnotify').addClass('iconcolor');
                }, 2800);
            })
        }

        $('input[type="submitd"]').click(function () {
            $('.login').addClass('test')
            setTimeout(function () {
                $('.login').addClass('testtwo')
            }, 300);
            setTimeout(function () {
                    $(".authent").show().animate({right: -320}, {easing: 'easeOutQuint', duration: 600, queue: false});
                    $(".authent").animate({opacity: 1}, {duration: 200, queue: false}).addClass('visible');
                },500);
            setTimeout(function () {
                $(".authent").show().animate({right: 90}, {easing: 'easeOutQuint', duration: 600, queue: false});
                $(".authent").animate({opacity: 0}, {duration: 200, queue: false}).addClass('visible');
                $('.login').removeClass('testtwo')
            }, 2500);
            setTimeout(function () {
                $('.login').removeClass('test')
                $('.login div').fadeOut(123);
            }, 2800);
            setTimeout(function () {
                $('.success').fadeIn();
            }, 3200);
        });

        $('input[type="text"],input[type="password"]').focus(function () {
            $(this).prev().animate({'opacity': '1'}, 200)
        });

        $('input[type="text"],input[type="password"]').blur(function () {
            $(this).prev().animate({'opacity': '.5'}, 200)
        });

        $('input[type="text"],input[type="password"]').keyup(function () {
            if (!$(this).val() == '') {
                $(this).next().animate({'opacity': '1', 'right': '30'}, 200)
            } else {
                $(this).next().animate({'opacity': '0', 'right': '20'}, 200)
            }
        });

        var open = 0;
        $('.tab').click(function () {
            $(this).fadeOut(200, function () {
                $(this).parent().animate({'left': '0'})
            });
        });
    }
}]);

angular.element(function () {
    angular.bootstrap(document, ['coreModule']);
});
