/* global requirejs */

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
    cookie: '/static/simple_dashboard/vendor/js.cookie',
    broadcast: '/static/simple_messaging/js/app/dashboard_message_broadcast'
  }
})

requirejs(['material', 'jquery', 'base', 'broadcast'], function (mdc) {
	const doSearch = function(query) {
		const url = URL.parse(window.location.href)
		url.searchParams.set('limit', select.value)
		url.searchParams.set('offset', '0')
		url.searchParams.set('q', query)

		window.location.href = url.href
	}

	const searchField = mdc.textField.MDCTextField.attachTo(document.getElementById('topbar_search'));

	$('#topbar_search_field').on('keypress', function(eventObj) {
		if (eventObj.which == 13) {
			eventObj.preventDefault();

			doSearch(searchField.value)
		}
	})

	$('#topbar_search_icon').on('click', function(eventObj) {
		doSearch(searchField.value)
	})

	const select = mdc.select.MDCSelect.attachTo(document.querySelector('.mdc-select'));

	const url = URL.parse(window.location.href)

	if (url.searchParams.get('limit') !== null) {
		select.value = url.searchParams.get('limit')
	} else {
		select.value = '25'
	}

	if (url.searchParams.get('q') !== null) {
		searchField.value = url.searchParams.get('q')
	}

  select.listen('MDCSelect:change', () => {
		const url = URL.parse(window.location.href)
		url.searchParams.set('limit', select.value)
		window.location.href = url.href
	});

  mdc.dataTable.MDCDataTable.attachTo(document.getElementById('messages_table'))

	$('.mdc-data-table__pagination-button').click(function(eventObj) {
		eventObj.preventDefault()

		const url = $(this).attr('data-url')

		window.location.href = url
	})
})
