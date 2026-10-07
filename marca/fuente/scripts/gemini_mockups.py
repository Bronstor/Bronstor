"""Genera mockups fotorrealistas con la API de Gemini usando el logo real como referencia.

Uso:  GEMINI_API_KEY=... python3 gemini_mockups.py [nombre ...]
Sin nombres, genera todos. Salida: marca/fotos/<nombre>-<n>.png
"""
import base64
import json
import os
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
MARCA = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(MARCA, 'fotos')
MODELS = [m for m in [os.environ.get('GEMINI_IMAGE_MODEL'),
                      'gemini-3-pro-image-preview', 'gemini-2.5-flash-image'] if m]

REGLA = (' The attached image is the official logo: reproduce it EXACTLY, same letters "E&M", same shapes and '
         'colors (red #D7141A, black #111111, white), do not add, remove or redraw any letter. '
         'Photorealistic, professional commercial product photography, natural fabric texture, no extra text.')

TRABAJOS = {
    'polo': ('simbolo-principal.png',
             'A black pique polo shirt on an invisible mannequin, light grey studio background, soft lighting. '
             'Thin red (#D7141A) tipping on collar and sleeve cuffs. The attached logo is embroidered on the left '
             'chest, about 8 cm wide, with real raised thread texture.'),
    'polo-espalda': ('logo-vertical-negativo.png',
                     'Back view of a black pique polo shirt with red collar tipping on an invisible mannequin, light '
                     'grey studio background. The attached logo is screen printed centered on the upper back, '
                     'about 28 cm wide.'),
    'camisa': ('simbolo-principal.png',
               'A long sleeve charcoal grey work shirt with black shoulder yoke separated by a thin red piping, two '
               'chest pockets with flaps. The attached logo is embroidered above the left pocket, a black name patch '
               'with red border above the right pocket. Hanging on a hanger in a clean auto parts workshop, '
               'natural light.'),
    'gorra': ('simbolo-principal.png',
              'A black structured 6-panel baseball cap, three-quarter view, on a dark wooden table. The attached logo '
              'is 3D puff embroidered on the front panel, about 6 cm wide. Thin red trim on the visor edge.'),
    'vendedor': ('simbolo-principal.png',
                 'A smiling Latin American salesman behind the counter of a tidy auto parts store with shelves of '
                 'parts in the background, wearing a black polo shirt with red collar tipping and the attached logo '
                 'embroidered on the left chest. Warm professional lighting, shallow depth of field.'),
    'letrero': ('logo-horizontal-negativo.png',
                'Facade of an auto parts store at dusk. Above the entrance a black backlit lightbox sign showing the '
                'attached logo in white with a red stripe along the bottom of the sign. Glass storefront with parts '
                'shelves visible inside.'),
}


def llamar(modelo, logo_path, prompt, key):
    with open(logo_path, 'rb') as f:
        img = base64.b64encode(f.read()).decode()
    body = {'contents': [{'parts': [{'inline_data': {'mime_type': 'image/png', 'data': img}},
                                    {'text': prompt + REGLA}]}],
            'generationConfig': {'responseModalities': ['TEXT', 'IMAGE']}}
    req = urllib.request.Request(
        f'https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent',
        data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', 'x-goog-api-key': key})
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.load(r)
    imgs = []
    for c in data.get('candidates', []):
        for p in c.get('content', {}).get('parts', []):
            d = p.get('inline_data') or p.get('inlineData')
            if d:
                imgs.append(base64.b64decode(d['data']))
    return imgs


def main():
    key = os.environ.get('GEMINI_API_KEY')
    if not key:
        sys.exit('Falta la variable de entorno GEMINI_API_KEY')
    os.makedirs(OUT, exist_ok=True)
    nombres = sys.argv[1:] or list(TRABAJOS)
    for n in nombres:
        logo, prompt = TRABAJOS[n]
        for modelo in MODELS:
            try:
                imgs = llamar(modelo, os.path.join(MARCA, 'logo', 'png', logo), prompt, key)
            except urllib.error.HTTPError as e:
                print(n, modelo, 'HTTP', e.code, e.read()[:300].decode(errors='replace'))
                continue
            if imgs:
                for i, b in enumerate(imgs):
                    p = os.path.join(OUT, f'{n}-{i + 1}.png')
                    open(p, 'wb').write(b)
                    print('ok', modelo, p)
                break
            print(n, modelo, 'sin imagen en la respuesta')


if __name__ == '__main__':
    main()
