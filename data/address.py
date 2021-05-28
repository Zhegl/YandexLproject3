import requests as req


def create(name):
    geocoder_request = "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=" + name.about + "&format=json"

    # Выполняем запрос.
    response = req.get(geocoder_request)
    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()

        # Получаем первый топоним из ответа геокодера.
        # Согласно описанию ответа, он находится по следующему пути:
        try:
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            # Полный адрес топонима:
            toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
            # Координаты центра топонима:
            toponym_coodrinates = toponym["Point"]["pos"]
            map_request = "https://static-maps.yandex.ru/1.x/?l=map&pt=" + ','.join(toponym_coodrinates.split()) + '&z=15'
            response = req.get(map_request)

            if not response:
                print("Ошибка выполнения запроса:")
                print(map_request)
                print("Http статус:", response.status_code, "(", response.reason, ")")

            map_file = 'static/img/' + name.name + '.png'
            with open(map_file, "wb") as file:
                file.write(response.content)
        except Exception:
            pass
    if not response:
        print("Ошибка выполнения запроса:")
