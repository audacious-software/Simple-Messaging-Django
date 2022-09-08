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

  const loadMessages = function (messages) {
    $.each(messages, function (index, message) {
      let itemHtml = ''

      const formattedTime = moment(message.timestamp * 1000).format('MMMM Do YYYY, h:mm:ss a')

      if (message.direction === 'from-user') {
        itemHtml += '<div class="row mt-3">'
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
        itemHtml += '<div class="row mt-3">'
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

      $('#message_box').append(itemHtml)
    })

    if (messages.length > 0) {
      $('#message_box').scrollTop($('#message_box')[0].scrollHeight)
    };
  }

  const fetchMessages = function (phone, success) {
    const payload = {
      phone: phone
    }

    if (cachedMessages[phone] !== undefined) {
      const messages = cachedMessages[phone]

      if (messages.length > 0) {
        payload.since = messages[messages.length - 1].timestamp
      }
    }

    $.post('messages.json', payload, function (data) {
      if (cachedMessages[phone] === undefined) {
        cachedMessages[phone] = []
      }

      cachedMessages[phone] = cachedMessages[phone].concat(data)

      let cacheSize = cachedMessages[phone].length

      if (cacheSize > 1) {
        while (cachedMessages[phone][cacheSize - 1] === cachedMessages[phone][cacheSize - 2]) {
          cachedMessages[phone].pop()

          cacheSize = cachedMessages[phone].length
        }
      }

      data.sort(function (a, b) {
        return a.timestamp - b.timestamp
      })

      cachedMessages[phone].sort(function (a, b) {
        return a.timestamp - b.timestamp
      })

      loadMessages(data)

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

  $('#message_box').height($(window).height() - 240)

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

  $('#message').on('keyup change', function (event) {
    toggleSend()

    updateCount()

    if (event.key === 'Enter') {
      $('#send_button').click()
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
    formData.append('attachment', attachment)

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
