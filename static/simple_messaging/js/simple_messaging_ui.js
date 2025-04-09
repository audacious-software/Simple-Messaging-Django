/* global moment, alert, FormData */

$(document).ready(function () {
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

  const cachedMessages = {}

  const loadMessages = function (messages, loadMore = false) {
    const toScroll = []

    $.each(messages, function (index, message) {
      let itemHtml = ''

      const formattedTime = moment(message.timestamp * 1000).format('MMMM Do YYYY, h:mm:ss a')

      if (message.direction === 'from-user') {
        itemHtml += '<div class="row mt-3" data-timestamp="' + message.timestamp + '">'
        itemHtml += '    <div class="col-md-8">'
        itemHtml += '      <div class="card text-white bg-secondary">'
        itemHtml += '        <div class="card-body">'

        if (message.message !== undefined && message.message !== '') {
          itemHtml += '          <p class="card-text">' + message.message + '</p>'
        }

        $.each(message.media_urls, function (index, mediaUrl) {
          if (mediaUrl[1].startsWith('image/')) {
            itemHtml += '          <p class="card-text"><img src="' + mediaUrl[0] + '" class="w-100"></p>'
          } else if (mediaUrl[1].startsWith('audio/')) {
            itemHtml += '          <p class="card-text"><audio controls class="w-100"><source src="' + mediaUrl[0] + '" type="' + mediaUrl[1] + '"></audio></p>'
          } else if (mediaUrl[1].startsWith('video/')) {
            itemHtml += '          <p class="card-text"><video controls class="w-100"><source src="' + mediaUrl[0] + '" type="' + mediaUrl[1] + '"></video></p>'
          } else {
            itemHtml += '          <p class="card-text"><a href="' + mediaUrl[0] + '">' + mediaUrl[1] + '</a></p>'
          }
        })

        itemHtml += '          <small>' + formattedTime + '</small>'
        itemHtml += '        </div>'
        itemHtml += '      </div>'
        itemHtml += '    </div>'
        itemHtml += '    <div class="col-md-4">'
        itemHtml += '    </div>'
        itemHtml += '  </div>'
        itemHtml += '</div>'
      } else {
        itemHtml += '<div class="row mt-3"  data-timestamp="' + message.timestamp + '">'
        itemHtml += '    <div class="col-md-4">'
        itemHtml += '    </div>'
        itemHtml += '    <div class="col-md-8">'
        itemHtml += '      <div class="card text-white bg-primary">'
        itemHtml += '        <div class="card-body">'

        if (message.message !== undefined && message.message !== '') {
          itemHtml += '          <p class="card-text">' + message.message + '</p>'
        }

        $.each(message.media_urls, function (index, mediaUrl) {
          if (mediaUrl[1].startsWith('image/')) {
            itemHtml += '          <p class="card-text"><img src="' + mediaUrl[0] + '" class="w-100"></p>'
          } else if (mediaUrl[1].startsWith('audio/')) {
            itemHtml += '          <p class="card-text"><audio controls class="w-100"><source src="' + mediaUrl[0] + '" type="' + mediaUrl[1] + '"></audio></p>'
          } else if (mediaUrl[1].startsWith('video/')) {
            itemHtml += '          <p class="card-text"><video controls class="w-100"><source src="' + mediaUrl[0] + '" type="' + mediaUrl[1] + '"></video></p>'
          } else {
            itemHtml += '          <p class="card-text"><a href="' + mediaUrl[0] + '">' + mediaUrl[1] + '</a></p>'
          }
        })

        itemHtml += '          <small>' + formattedTime + '</small>'
        itemHtml += '        </div>'
        itemHtml += '      </div>'
        itemHtml += '    </div>'
        itemHtml += '  </div>'
        itemHtml += '</div>'
      }

      $('#message_box_' + message.channel).append(itemHtml)

      if (toScroll.includes(message.channel) === false) {
        toScroll.push(message.channel)
      }

      if ($('#outgoing_earcon')[0].paused || $('#outgoing_earcon')[0].ended) {
        $('#incoming_earcon')[0].play()
      }
    })

    toScroll.forEach(function (channel) {
      if (loadMore) {
        let itemHtml = ''

        itemHtml += '<div class="row mt-3 messages_load_more" data-timestamp="0">'
        itemHtml += '  <div class="col-md-12" style="padding-bottom: 16px;">'
        itemHtml += '    <center>'
        itemHtml += '      <button class="btn btn-dark button_load_messages" type="button">'
        itemHtml += '        <span class="spinner-grow spinner-grow-sm loading_spinner" role="status" aria-hidden="true"></span>'
        itemHtml += '        <span class="sr-only loading_message">Load older messages</span>'
        itemHtml += '      </button>'
        itemHtml += '    <center>'
        itemHtml += '  </div>'
        itemHtml += '</div>'

        $('#message_box_' + channel).append(itemHtml)
        $('.loading_spinner').hide()

        $('.button_load_messages').click(function (event) {
          event.preventDefault()

          $('.loading_message').html('Loading older messages&#8230;')
          $('.loading_spinner').show()

          fetchMessages(window.lastPhone, function () {
            $('.messages_load_more').hide()
          }, -1)
        })
      }

      const messageBox = $('#message_box_' + channel)

      const messageElements = messageBox.find('div[data-timestamp]')

      messageElements.sort(function (one, two) {
        return parseFloat($(one).data('timestamp')) - parseFloat($(two).data('timestamp'))
      }).each(function () {
        messageBox.append(this)
      })

      $('#message_box_' + channel).each(function (index, element) {
        $(element).scrollTop(element.scrollHeight)
      })
    })
  }

  const fetchMessages = function (phone, success, since = 0) {
    const payload = {
      phone: phone,
      since: since
    }

    let loadMore = false

    if (cachedMessages[phone] !== undefined) {
      const messages = cachedMessages[phone]

      if (since === 0 && messages.length > 0) {
        payload.since = messages[messages.length - 1].timestamp
      }
    } else {
      const now = Date.now() / 1000

      const windowStart = now - (2 * 7 * 24 * 60 * 60) // Two weeks

      payload.since = windowStart

      loadMore = true
    }

    $.post('messages.json', payload, function (data) {
      if (cachedMessages[phone] === undefined) {
        cachedMessages[phone] = []
      }

      const toLoad = []

      data.forEach(function (message) {
        const index = cachedMessages[phone].findIndex(stored => (stored.message === message.message) && (stored.timestamp === message.timestamp))

        if (index === -1) {
          cachedMessages[phone].push(message)

          toLoad.push(message)
        }
      })

      toLoad.sort(function (a, b) {
        return a.timestamp - b.timestamp
      })

      cachedMessages[phone].sort(function (a, b) {
        return a.timestamp - b.timestamp
      })

      loadMessages(toLoad, loadMore)

      success()
    })
  }

  const refreshIDs = []

  const refresh = function () {
    if (window.lastPhone.length >= 0) {
      fetchMessages(window.lastPhone, function () {
        while (refreshIDs.length > 0) {
          const refreshID = refreshIDs.pop()

          window.clearTimeout(refreshID)
        }

        refreshIDs.push(window.setTimeout(refresh, 5000))
      })
    }
  }

  const controlHeight = $('#control-bar').height() + 168

  $('.simple_message_ui_box').height($(window).height() - controlHeight)

  $('.simple_message_ui_box').click(function (event) {
    $('.simple_message_ui_box').removeClass('border-primary')
    $('.simple_message_ui_box').removeClass('border-3')

    $(this).addClass('border-primary')
    $(this).addClass('border-3')

    window.selectedMessagingChannel = $(this).attr('id').replace('message_box_', '')
  })

  $('.simple_message_ui_box')[0].click()

  const toggleSend = function () {
    const phone = $('#phone_number').val()
    const message = $('#message').val().trim()

    const attachment = $('#attachment')[0].files[0]

    if (attachment === undefined && (message.length === 0 || phone.length === 0)) {
      $('#send_button').prop('disabled', true)
    } else {
      $('#send_button').prop('disabled', false)
    }
  }

  $('#phone_number').on('keyup change', function (e) {
    const phone = $('#phone_number').val()

    if (phone !== window.lastPhone) {
      $('#message_box').html('')
      window.lastPhone = phone

      if (cachedMessages[phone] !== undefined) {
        loadMessages(cachedMessages[phone])
      } else {
        refresh()
      }

      window.lastPhone = phone
    }

    toggleSend()
  })

  const updateCount = function () {
    const message = $('#message').val().trim()

    $('#character_count').html('Length: ' + message.length)

    if (message.length >= 140) {
      $('#character_count').addClass('text-danger')
    } else {
      $('#character_count').removeClass('text-danger')
    }
  }

  $('#message').on('keydown change', function (event) {
    if (event.key === 'Enter') {
      event.preventDefault()

      $('#send_button').click()
    } else {
      toggleSend()
      updateCount()
    }
  })

  $('#send_button').click(function (eventObj) {
    eventObj.preventDefault()

    const message = $('#message').val().trim()
    const phone = $('#phone_number').val() // .replace(/[^\d]/g, '');

    const attachment = $('#attachment')[0].files[0]

    const formData = new FormData()

    formData.append('phone', phone)
    formData.append('message', message)
    formData.append('channel', window.selectedMessagingChannel)
    formData.append('attachment', attachment)

    window.messageExtensionFunctions.forEach(function(extensionFunction) {
      extensionFunction(formData)
    })

    $.ajax({
      url: 'send.json',
      type: 'POST',
      success: function (data) {
        $('#message').val('')
        $('#attachment').val('')
        $('#upload_button').html('backup')

        updateCount()

        fetchMessages(phone, function () {})
      },
      data: formData,
      cache: false,
      processData: false,
      contentType: false,
      enctype: 'multipart/form-data'
    })
  })

  if (window.lastPhone !== '') {
    $('#phone_number').val(window.lastPhone)

    window.lastPhone = ''

    $('#phone_number').change()
  }

  $('.precomposed-message').click(function (eventObj) {
    eventObj.preventDefault()

    $('#message').val($(this).attr('data-message'))

    toggleSend()
  })

  $('#upload_button').click(function (eventObj) {
    $('#attachment').click()
  })

  $('#attachment').on('change', function (e) {
    if (this.files[0].size > 5 * 1024 * 1024) {
      alert('Cannot send a file larger than 5 MB. Please select another.')
      $(this).val('')
    } else {
      $('#upload_button').html('cloud_done')

      toggleSend()
    }
  })

  updateCount()
})
