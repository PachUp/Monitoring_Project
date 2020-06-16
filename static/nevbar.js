$('.dropdown-nevbar').on('show.bs.dropdown', function() {
    $(this).find('.dropdown-menu-nevbar').first().stop(true, true).slideDown();
});
  $('.dropdown-nevbar').on('hide.bs.dropdown', function() {
    $(this).find('.dropdown-menu-nevbar').first().stop(true, true).slideUp();
});