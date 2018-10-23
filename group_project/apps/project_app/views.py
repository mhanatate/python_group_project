from django.shortcuts import render, redirect
from django.contrib import messages
from apps.project_app.models import User
import bcrypt
import argparse
import json
import pprint
import requests
import sys
import urllib

API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
api_key = '8fJisUcWi6_6M8q1TqXwV64duaoO7p6rs5Sh4xI9b6abzOxLgAHFW_OrD2jgX7rRH0a2bwm4Uhio4-5JiVQCbTHyvrzs8667unV_strpWIR6xq-CLwuT5V-uBH3KW3Yx'
# BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.


def index(request):
    if 'id' not in request.session or request.session['id'] == None:
        return render(request, "project_app/index.html")
    else:
        return redirect('/wheel')

def validate_register(request):
    errors = User.objects.basic_validator(request.POST)
    if len(errors):
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/')
    else:
        pw_hash = bcrypt.hashpw(
            request.POST['password'].encode(), bcrypt.gensalt())
        User.objects.create(
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            email=request.POST['email'],
            password=pw_hash,
        )
        user = User.objects.get(email=request.POST['email'])
        request.session['id'] = user.id
        request.session['message'] = "registered"
        return redirect("/login_success")

def validate_login(request):
    request.session['error'] = ""
    try:
        User.objects.get(email=request.POST['login_email'])
    except:
        request.session['error'] += "Incorrect Email"
        return redirect("/")
    user = User.objects.get(email=request.POST['login_email'])
    if user:
        if bcrypt.checkpw(request.POST['login_password'].encode(), user.password.encode()):
            request.session['message'] = "logged in"
            request.session['id'] = user.id
            return redirect("/wheel")
        else:
            request.session['error'] += "Incorrect Password"
            return redirect("/")

def wheel(request):
    restaurant_type = request.session['type']
    restaurant_location = request.session['city']
    restaurant_price = request.session['price']
    request.session['data'] = search(request, api_key, restaurant_type, restaurant_location, restaurant_price)
    return render(request, "project_app/wheel.html")

def process_wheel(request):
    return redirect("/results")

def preferences(request):
    return render(request, "project_app/preferences.html")

def process_preferences(request):
    request.session['type'] = request.POST['type']
    request.session['price'] = request.POST['price']
    request.session['city'] = request.POST["city"]
    return redirect('/wheel')

def results(request):
    print(request.session['data'])
    return render(request, "project_app/testsubject.html")

def success(request):
    data = User.objects.get(id=request.session['id'])
    userdict = {
        "datakey": data
    }
    return render(request, "project_app/success.html", userdict)

def logout(request):
    request.session['id'] = None
    return redirect('/')

def yelpAPI(request):
    is_cached = ('business' in request.session)

    if not is_cached:
        zip_code = 98006
        response = requests.get('https://api.yelp.com/v3/businesses/search/%s' % zip_code)
        request.session['business'] = response.json()

    business = request.session['business']

    return render(request, 'project_app/testsubject.html', {
        'mileradius' : business['radius'],
        'location' : business['location'],
        'latitude': business['latitude'],
        'longitude': business['longitude'],
        'phone' : business['phone'],
        'url' : business['url'],
        'rating' : business[ 'rating'],
        'review_count' : business[ 'review_count'],
        'price' : business['price'],
        'name': business['name'],
        'categories': business['categories'],
        'is_cached': is_cached,
        'api_key': 'AIzaSyCX4x-GRqo8LUQQyYnCy6rgmC5PsefMtes',  # Don't do this! This is just an example. Secure your keys properly.\
    })

def call(host, path, api_key, url_params=None):
    # """Given your API_KEY, send a GET request to the API.
    # Args:
    #     host (str): The domain host of the API.
    #     path (str): The path of the API after the domain.
    #     API_KEY (str): Your API Key.
    #     url_params (dict): An optional set of query parameters in the request.
    # Returns:
    #     dict: The JSON response from the request.
    # Raises:
    #     HTTPError: An error occurs from the HTTP request.
    # """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }

    print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()


def search(request, api_key, term, location, price):
    restaurant_type = request.session['type']
    restaurant_location = request.session["city"]
    restaurant_price = request.session['price']
    url_params = {
        'term': term.replace(f'{restaurant_type}', '+'),
        'location': location.replace(f'{restaurant_location}', '+'),
        'price': price.replace(f'{restaurant_price}', '+'),
        'limit': 30
    }
    return call(API_HOST, SEARCH_PATH, api_key, url_params=url_params)


def query_api(request, term, location, price):
    """Queries the API by the input values from the user.
    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    response = search(request, api_key, term, location, price)

    # businesses = response.get('businesses')

    # if not businesses:
    #     print(u'No businesses for {0} in {1} found.'.format(term, location))
    #     return

    # business_id = businesses[0]['id']

    # print(u'{0} businesses found, querying business info ' \
    #     'for the top result "{1}" ...'.format(
    #         len(businesses), business_id))
    # response = get_business(api_key, business_id)

    # print(u'Result for business "{0}" found:'.format(business_id))
    pprint.pprint(response, indent=2)