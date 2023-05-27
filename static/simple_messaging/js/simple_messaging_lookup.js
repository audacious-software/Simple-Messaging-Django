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

  $('#lookup_button').click(function (eventObj) {
    eventObj.preventDefault()

    const payload = {
      numbers: $('#phone_numbers').val()
    }

    $.post('lookup.json', payload, function (data) {
      for (const result of data) {
        let htmlString = '<div class="card mb-3 w-100">'
        htmlString += '  <div class="card-body">'
        htmlString += '    <p class="card-text"><strong>' + result.number + '</strong></p>'
        htmlString += '    <p class="card-text">Number Type: <strong>' + result.type + '</strong></p>'
        htmlString += '    <p class="card-text">Carrier: <strong>' + result.carrier + '</strong></p>'

        if (result.notes !== undefined) {
          htmlString += '    <p class="card-text">Notes: <strong>' + result.notes + '</strong></p>'
        }

        htmlString += '  </div>'
        htmlString += '</div>'

        $('#lookup_results').prepend(htmlString)
      }

      $('#phone_numbers').val('')
    })
  })
})
