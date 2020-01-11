'use strict';

angular.module('todoListApp')
.controller('todoCtrl', function($scope, Todo) {
/* Rewrote this so it splices correct item. It was often splicing the wrong
   index if items had been marked as complete, because that reorders them.

  $scope.deleteTodo = function(todo, index) {
    $scope.todos.splice(index, 1);
    todo.$delete();
  };
*/
  $scope.deleteTodo = function(todo) {
    $scope.todos.splice($scope.todos.indexOf(todo), 1);
    todo.$delete();
  };
  $scope.saveTodos = function() {
    var filteredTodos = $scope.todos.filter(function(todo){
      if(todo.edited) {
        return todo;
      };
    });
    filteredTodos.forEach(function(todo) {
      if (todo.id) {
        todo.$update();
      } else {
        todo.$save();
      }

    });
  }; 
});