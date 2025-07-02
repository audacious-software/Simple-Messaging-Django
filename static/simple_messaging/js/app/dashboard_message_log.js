/* global requirejs, FormData */

requirejs.config({
  shim: {
    jquery: {
      exports: '$'
    },
    bootstrap: {
      deps: ['jquery']
    },
    cookie: {
      exports: 'Cookies'
    }
  },
  baseUrl: '/static/simple_dashboard/js/app',
  paths: {
    app: '/static/simple_dashboard/js/app',
    material: '/static/simple_dashboard/vendor/material-components-web.min',
    jquery: '/static/simple_dashboard/vendor/jquery',
    moment: '/static/simple_dashboard/vendor/moment',
    cookie: '/static/simple_dashboard/vendor/js.cookie'
  }
})

requirejs(['material', 'moment', 'jquery', 'base'], function (mdc, moment) {
  mdc.dataTable.MDCDataTable.attachTo(document.getElementById('messages_table'))
})
