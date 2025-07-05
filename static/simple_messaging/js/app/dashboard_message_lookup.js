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
    moment: '/static/simple_dashboard/vendor/moment',
    cookie: '/static/simple_dashboard/vendor/js.cookie'
  }
})

requirejs(['material', 'jquery', 'base'], function (mdc) {
  const csrftoken = $('[name=csrfmiddlewaretoken]').val()

  function csrfSafeMethod (method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method))
  }

  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader('X-CSRFToken', csrftoken)
      }
    }
  })

  const lookupField = mdc.textField.MDCTextField.attachTo(document.getElementById('phonenumbers_field'))

  $('#button_lookup').click(function (eventObj) {
    eventObj.preventDefault()

    const payload = {
      numbers: lookupField.value
    }

    $.post('/messages/lookup.json', payload, function (data) {
      if ($('#lookup_results').html().includes('No results yet')) {
        $('#lookup_results').html('')
      }

      if (data.length === 0) {
        $('#lookup_results').html('<em>No results found. Check your phone number and if the server is configured for lookups.</em>')
      } else {
        for (const result of data) {
          let htmlString = '<div>'
          htmlString += `   <div class="mdc-typography--subtitle1"><strong>${result.number}</strong></div>`
          htmlString += `   <div class="mdc-typography--body1">Number Type: ${result.type}</div>`
          htmlString += `   <div class="mdc-typography--body1">Carrier: ${result.carrier}</div>`

          if (result.notes !== undefined) {
            htmlString += `  <div class="mdc-typography--body2">Notes: ${result.notes}</div>`
          }

          htmlString += '<div>'

          $('#lookup_results').prepend(htmlString)
        }
      }

      lookupField.value = ''
    })
  })
})
