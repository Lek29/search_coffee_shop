from json import loads
import os
import requests
from geopy import distance
import folium
from flask import Flask


apikey_1 = os.getenv('API_KEY_TOKEN')


def fetch_coordinates(apikey_1, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey_1,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def create_map():
    with open('coffe_shops_map.html', 'r', encoding='utf-8') as file:
        template = file.read()
        return template


def main():
    with open('coffee.json', 'r') as file:
        file_contents = file.read()

    file_with_list = loads(file_contents)

    name_place = input('Где вы находитесь? ')
    start_coords = fetch_coordinates(apikey_1, name_place)

    cofee_shop_with_distance = []

    for resulting_dict in file_with_list:
        name_coffe_shop = resulting_dict.get('Name', 'Нет такого ключа')
        coorinates_cofee_shop = resulting_dict.get('geoData', 'Ключ остутствует').get('coordinates', 'Нет ключа')

        if coorinates_cofee_shop != 'Ключ отсутствует' or 'Нет ключа':
            lotitude_coffee_shop, longitude_coffee_shop = coorinates_cofee_shop[1], coorinates_cofee_shop[0]
            coords_finish_place = lotitude_coffee_shop, longitude_coffee_shop

        standart_coords_start_place = tuple(list(start_coords)[::-1])
        distance_beetwin_places = distance.distance(standart_coords_start_place, coords_finish_place).km
        cofee_shop_with_distance.append(
            {
                'title': name_coffe_shop,
                'distance': distance_beetwin_places,
                'latitude': lotitude_coffee_shop,
                'longitude': longitude_coffee_shop
            }
        )
        five_near_coffee_shop = sorted(cofee_shop_with_distance, key=lambda distance: distance['distance'])[:5:]

    map_coffee_shop = folium.Map(location=start_coords, zoom_start=12)

    for cofee_shop in five_near_coffee_shop:
        folium.Marker(
            location=[cofee_shop['latitude'], cofee_shop['longitude']],
            popup=cofee_shop['title'],
            icon=folium.Icon(color='blue'),
        ).add_to(map_coffee_shop)

    map_coffee_shop.save('coffe_shops_map.html')

    app = Flask(__name__)
    app.add_url_rule('/', 'HELLO', create_map)
    app.run('0.0.0.0')


if __name__ == '__main__':
    main()


