from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import PIL
from PIL import Image
from io import BytesIO

PORT = 8000  # Define your desired port number

class CompareHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Generate HTML form
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Image Size Comparison</title>
        </head>
        <body>
            <h1>Compare Image Size</h1>
            <form action="" method="post" enctype="multipart/form-data">
                <label for="image">Select image:</label>
                <input type="file" name="image" id="image" required accept="image/*">
                <br>
                <button type="submit">Compare</button>
            </form>
        </body>
        </html>
        """
        self.wfile.write(html.encode())

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        content_type = self.headers.get('Content-Type')

        # Get form data length
        try:
            content_length = int(self.headers['Content-Length'])
        except (KeyError, ValueError):
            self.wfile.write(b"Error: Invalid content length!")
            return

        # Check for max file size
        if content_length > 10 * 1048576:
            self.wfile.write(b"Error: File size exceeds 10MB limit!")
            return

        try:
            # Read data and decode based on content type (assuming UTF-8 for form data)
            post_data = self.rfile.read(content_length).decode(content_type.split(';')[0] if content_type else 'utf-8')
            form_data = dict(x.split('=') for x in post_data.split('&'))

            # Get image file from form data
            image_file = form_data.get('image')
            if not image_file:
                self.wfile.write(b"Error: No image selected!")
                return

            # Open image
            with open(image_file.filename, 'rb') as f:
                image = Image.open(f)

            # Get original image size
            original_size = os.path.getsize(image_file.filename)

            # Reduce image quality for compression (adjust as needed)
            buffer = BytesIO()
            image.save(buffer, format=image.format, quality=50)

            # Get compressed image size and data
            compressed_size = buffer.tell()
            compressed_data = buffer.getvalue()

            # Reset buffer pointer for download link
            buffer.seek(0)

            # Generate HTML content
            html_content = f"""
            <h1>Image Size Comparison</h1>
            <p>Original image size: {original_size} bytes</p>
            <p>Compressed image size: {compressed_size} bytes</p>
            <img src="data:image/{image.format};base64,{compressed_data.decode('base64')}">
            <br>
            <a href="data:image/{image.format};base64,{compressed_data.decode('base64')}" download="compressed.{image.format}">Download Compressed Image</a>
            """
            self.wfile.write(html_content.encode())

        except (UnicodeDecodeError, FileNotFoundError, PermissionError, PIL.UnidentifiedImageError) as e:
            # Handle specific exceptions with informative error messages
            error_message = {
                UnicodeDecodeError: b"Error: Could not decode uploaded data!",
                FileNotFoundError: b"Error: File not found!",
                PermissionError: b"Error: Insufficient permissions to access file!",
                PIL.UnidentifiedImageError: b"Error: Unsupported image format!",
            }.get(type(e), b"Error: An error occurred!")
            self.wfile.write(error_message)
            
        except Exception as e:
            print(f"Error: {e}")
            self.wfile.write(b"Error: An unexpected error occurred!")


with HTTPServer(('', PORT), CompareHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()