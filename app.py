from flask import Flask, request, send_file, jsonify
from pocketbase import PocketBase
from ipinfo import getHandler
from user_agents import parse
from base64 import b64decode
from io import BytesIO

app = Flask(__name__)
blank_px = b64decode('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7')
pb = PocketBase('https://pb.marcusj.tech')
ipinfo = getHandler('<IPINFO_TOKEN>')

@app.route('/blog/<string:post_slug>/image.png')
def app_analytics(post_slug: str):
    user_agent = parse(request.headers.get('User-Agent'))
    ip_addr = request.headers.get('X-Forwarded-For', request.remote_addr)
    location = ipinfo.getDetails(ip_addr)

    data = {
        'post_slug': post_slug,
        'user_agent': request.headers.get('User-Agent'),
        'browser': user_agent.browser.family,
        'os': user_agent.os.family,
        'device': user_agent.device.family,

        'ip_addr': ip_addr,
        'city': getattr(location, 'city', None),
        'region': getattr(location, 'region', None),
        'country': getattr(location, 'country', None),
    }

    doc = pb.collection('analytics').create(data)
    print(f'[Hit: {doc.id}] > From {data["country"]} on {data["browser"]} {data["os"]} {data["device"]}')

    return send_file(
        BytesIO(blank_px),
        mimetype='image/png',
        as_attachment=True,
        attachment_filename='image.png'
    )

@app.route('/blog/<string:post_slug>/analytics')
@app.route('/blog/<string:post_slug>/analytics.json')
@app.route('/api/<string:post_slug>/analytics')
def app_analytics_get(post_slug: str):
    data = pb.collection('analytics').where('post_slug', '==', post_slug).get()
    return jsonify(data)

@app.route('/')
def app_index():
    return 'Hello, World!'

app.run(host='127.0.0.1', port=8080)