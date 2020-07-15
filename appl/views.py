from os import linesep

import googlemaps
from flask import Flask, request, render_template, redirect
from flask_googlemaps import GoogleMaps, Map

from .models import process_data

application = app = Flask(__name__)
# you can also pass the key here if you prefer
# GoogleMaps(application, key="AIzaSyC8MW5oXjMx2Ww8HMymFwcNhilKmcbedlw")
# gmaps = googlemaps.Client(key="AIzaSyC8MW5oXjMx2Ww8HMymFwcNhilKmcbedlw")
GoogleMaps(application, key="AIzaSyAB_iD63VLnlliq6Q877RzcQH7RctN597c")
gmaps = googlemaps.Client(key="AIzaSyAB_iD63VLnlliq6Q877RzcQH7RctN597c")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process_pdf', methods=['POST', 'GET'])
def process_pdf():
    if request.method == 'POST':
        url = request.form['url']
        foreclosures = process_data(url)

        markers = []
        for foreclosure in foreclosures:
            address = foreclosure.address
            output = gmaps.geocode(address)
            foreclosure.lat = output[0]['geometry']['location'].get('lat')
            foreclosure.lng = output[0]['geometry']['location'].get('lng')
            marker = {}
            if foreclosure.status != 'Scheduled':
                marker['icon'] = 'http://maps.google.com/mapfiles/ms/icons/orange-dot.png'
            elif foreclosure.type == 'TAX':
                marker['icon'] = 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'
            elif foreclosure.type == 'MTG':
                marker['icon'] = 'http://maps.google.com/mapfiles/ms/icons/green-dot.png'
            else:
                marker['icon'] = 'http://maps.google.com/mapfiles/ms/icons/yellow-dot.png'
            marker['lat'] = foreclosure.lat
            marker['lng'] = foreclosure.lng
            marker['infobox'] = "<div><h4>"+address+"</h4>" \
                                "<div><ul style=\"list-style: none; padding-left: 0;\">" \
                                "   <li>Type : <b>"+foreclosure.type+"</b></li>" \
                                "   <li>Price : <b>"+foreclosure.principal+"</b></li>" \
                                "   <li>Status : <b>"+foreclosure.status+"</b></li>" \
                                "  </ul></div>" \
                                "</div> "
            markers.append(marker)

        sndmap = Map(
            zoom=11,
            style="height:500px;width:800px;margin:0;",
            identifier="sndmap",
            lat=39.707744,
            lng=-75.631155,
            markers=markers
        )
        return render_template('index.html', foreclosures=foreclosures, sndmap=sndmap)

    else:
        return redirect('/')
