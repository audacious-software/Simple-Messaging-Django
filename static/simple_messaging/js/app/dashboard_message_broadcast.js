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
  window.broadcastDestinationsField = mdc.textField.MDCTextField.attachTo(document.getElementById('broadcast_destinations'))
  const broadcastMessageField = mdc.textField.MDCTextField.attachTo(document.getElementById('broadcast_message_field'))

  const broadcastWhenMessageField = mdc.textField.MDCTextField.attachTo(document.getElementById('broadcast_when_field'))

  const confirmBroadcastDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('confirm_broadcast'))

  $('#button_attach_click').click(function (eventObj) {
    eventObj.preventDefault()

    $('#attachment').click()
  })

  $('#attachment').on('change', function (eventObj) {
    if ($('#attachment').val()) {
      $('#label_attach_click').html($('#attachment').val())
    } else {
      $('#label_attach_click').html('<em>No file selected.</em>')
    }
  })

  $('#button_broadcast_click').click(function (eventObj) {
    eventObj.preventDefault()

    const identifiers = []

    window.broadcastDestinationsField.value.split(',').forEach(function (destination) {
      if (destination.trim() !== '') {
        identifiers.push(destination.trim())
      }
    })

    const attachment = $('#attachment')[0].files[0]

    const formData = new FormData()

    formData.append('identifiers', JSON.stringify(identifiers))
    formData.append('message', broadcastMessageField.value)
    formData.append('when', broadcastWhenMessageField.value)
    formData.append('attachment', attachment)

    const dateString = broadcastWhenMessageField.value.replace('T', ' ')

    let when = moment()

    if (dateString !== '') {
      when = moment(dateString)
    }

    const now = moment()

    if (when <= now) {
      $('#warning-in-past').show()
    } else {
      $('#warning-in-past').hide()
    }

    $('#confirm-broadcast-count').html('' + identifiers.length)

    $('#confirm-broadcast-when').html(when.format('LLLL'))

    if (when < now) {
      $('#confirm-broadcast-when').css('color', '#800000')
    } else {
      $('#confirm-broadcast-when').removeAttr('style')
    }

    $('#confirm-broadcast-message').html(broadcastMessageField.value)

    const confirmListener = function (event) {
      const action = event.detail.action

      confirmBroadcastDialog.unlisten('MDCDialog:closed', confirmListener)

      if (action === 'close') {
        // Do nothing - just close
      } else if (action === 'schedule') {
        $.ajax({
          url: '/messages/dashboard/messages/broadcast.json',
          type: 'POST',
          success: function (data) {
            if (data.message !== undefined) {
              window.alert(data.message)
            }

            if (data.reset) {
              broadcastMessageField.value = ''
              $('#button_broadcast_click').attr('disabled', 'true')
              $('#button_attach_click i').html('attach_file')
              $('#label_attach_click').html('<i>No file selected</i>')
              $('#attachment').val('')
            }

            if (data.reload) {
              window.location.reload()
            }
          },
          data: formData,
          cache: false,
          processData: false,
          contentType: false,
          enctype: 'multipart/form-data'
        })
      }
    }

    confirmBroadcastDialog.listen('MDCDialog:closed', confirmListener)

    confirmBroadcastDialog.open()
  })
})
