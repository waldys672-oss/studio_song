# Routes package
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

# This automatically looks for the CLOUDINARY_URL environment variable
cloudinary.config(secure=True)