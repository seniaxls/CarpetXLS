from django.shortcuts import render, redirect

def telegram_browser_info(request):
    # Если заголовок X-Requested-With отсутствует, значит, это внешний браузер
    if not request.headers.get('X-Requested-With') == 'org.telegram.messenger':
        return redirect('/')  # Переадресация на главную страницу

    return render(request, 'telegram_browser_info.html', {
        'site_header': 'carpetxls',
        'site_title': 'carpetxls',
        'index_title': 'carpetxls',
        'page_title': 'carpetxls',

    })