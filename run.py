import os
from app import create_app
from whitenoise import WhiteNoise

app = create_app()

# Wrap your app with WhiteNoise for lightning-fast static file serving
# This caches your CSS and JS so they load instantly after the first visit
if not app.debug:
    # 'app/static' is where your CSS/JS files live
    app.wsgi_app = WhiteNoise(app.wsgi_app, root=os.path.join(os.path.dirname(__file__), 'app', 'static'))
    # Set a cache expiration of 1 year for static files
    app.wsgi_app.max_age = 31536000

if __name__ == '__main__':
    app.run()