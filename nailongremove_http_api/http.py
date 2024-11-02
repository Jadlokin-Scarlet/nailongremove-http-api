import requests
from flask import Flask, request, jsonify

from handler import transform_image, check_frames

app = Flask(__name__)

@app.route('/check_image', methods=['POST'])
async def check_image():
    image_url = request.args.get('image_url')
    if not image_url or not image_url.startswith('http'):
        print(f"image_url({image_url!r}) is error")
        return

    image = get_image_bytes(image_url)

    try:
        frames = transform_image(image)
        check_ok, checked_image = await check_frames(frames)
        return jsonify({'check_ok': check_ok})
    except Exception:
        print(f"Failed to process image: {image_url!r}")



def get_image_bytes(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Failed to retrieve image. Status code: {response.status_code}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
